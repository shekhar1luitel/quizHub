from __future__ import annotations

from typing import Iterable, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import (
    get_db_session,
    require_admin,
    require_content_manager,
    require_superuser,
    resolve_content_organization,
)
from app.core.security import get_password_hash
from app.models.subject import Subject
from app.models.organization import OrgMembership, Organization
from app.models.question import Option, Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import LearnerUser, OrganizationUser, PlatformUser, User
from app.schemas.admin import AdminSubjectSnapshot, AdminOverview, AdminRecentQuiz, AdminTotals
from app.schemas.management import (
    AdminNotificationCreate,
    AdminNotificationResult,
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserOut,
    AdminUserStatusUpdate,
    EmailDispatchResult,
    MailConfigIn,
    MailConfigOut,
)
from app.schemas.bulk_import import (
    BulkSubjectPayload,
    BulkSubjectPreview,
    BulkImportCommit,
    BulkImportPreview,
    BulkImportResult,
    BulkQuestionOption,
    BulkQuestionPayload,
    BulkQuestionPreview,
    BulkQuizPayload,
    BulkQuizPreview,
)
from app.services.config_service import ConfigService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from app.services.bulk_import_service import (
    BulkImportFormatError,
    ExportSubject,
    ExportQuestion,
    ExportQuestionOption,
    ExportQuiz,
    build_bulk_import_template,
    build_bulk_import_workbook,
    parse_workbook,
)
from app.core.strings import slugify

router = APIRouter(prefix="/admin", tags=["admin"])

EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/overview", response_model=AdminOverview)
def get_admin_overview(
    _: None = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> AdminOverview:
    active_org_condition = or_(Quiz.organization_id.is_(None), Organization.status == "active")

    totals = AdminTotals(
        total_quizzes=int(
            db.scalar(
                select(func.count())
                .select_from(Quiz)
                .join(Organization, Organization.id == Quiz.organization_id, isouter=True)
                .where(active_org_condition)
            ) or 0
        ),
        active_quizzes=int(
            db.scalar(
                select(func.count())
                .select_from(Quiz)
                .join(Organization, Organization.id == Quiz.organization_id, isouter=True)
                .where(active_org_condition)
                .where(Quiz.is_active.is_(True))
            )
            or 0
        ),
        total_questions=int(db.scalar(select(func.count()).select_from(Question)) or 0),
        inactive_questions=int(
            db.scalar(select(func.count()).select_from(Question).where(Question.is_active.is_(False))) or 0
        ),
        total_subjects=int(db.scalar(select(func.count()).select_from(Subject)) or 0),
        total_users=int(db.scalar(select(func.count()).select_from(User)) or 0),
    )

    recent_rows = db.execute(
        select(
            Quiz.id,
            Quiz.title,
            Quiz.is_active,
            Quiz.created_at,
            func.count(QuizQuestion.question_id).label("question_count"),
        )
        .join(QuizQuestion, QuizQuestion.quiz_id == Quiz.id, isouter=True)
        .join(Organization, Organization.id == Quiz.organization_id, isouter=True)
        .where(active_org_condition)
        .group_by(Quiz.id)
        .order_by(Quiz.created_at.desc())
        .limit(8)
    ).all()

    recent_quizzes: List[AdminRecentQuiz] = [
        AdminRecentQuiz(
            id=row.id,
            title=row.title,
            question_count=int(row.question_count or 0),
            is_active=bool(row.is_active),
            created_at=row.created_at,
        )
        for row in recent_rows
    ]

    top_subject_rows = db.execute(
        select(
            Subject.id,
            Subject.name,
            func.count(Question.id).label("question_count"),
        )
        .join(Question, Question.subject_id == Subject.id, isouter=True)
        .group_by(Subject.id)
        .order_by(func.count(Question.id).desc(), Subject.name.asc())
        .limit(6)
    ).all()

    top_subjects = [
        AdminSubjectSnapshot(
            id=row.id,
            name=row.name,
            question_count=int(row.question_count or 0),
        )
        for row in top_subject_rows
    ]

    return AdminOverview(
        totals=totals,
        recent_quizzes=recent_quizzes,
        top_subjects=top_subjects,
    )


def _apply_user_filters(
    stmt,
    *,
    role: str | None,
    status_value: str | None,
    account_type: str | None,
    organization_id: int | None,
    search: str | None,
):
    if role:
        stmt = stmt.where(User.role == role)
    if status_value:
        stmt = stmt.where(User.status == status_value)
    if account_type:
        stmt = stmt.where(User.account_type == account_type)
    if organization_id:
        stmt = stmt.where(User.organization_id == organization_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(like),
                User.email.ilike(like),
            )
        )
    return stmt


@router.get("/users", response_model=AdminUserListResponse)
def list_admin_users(
    role: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    account_type: str | None = Query(default=None),
    organization_id: int | None = Query(default=None),
    search: str | None = Query(default=None, min_length=2, max_length=255),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminUserListResponse:
    search_value = search.strip() if search else None

    base_stmt = select(User).order_by(User.created_at.desc())
    base_stmt = _apply_user_filters(
        base_stmt,
        role=role,
        status_value=status_value,
        account_type=account_type,
        organization_id=organization_id,
        search=search_value,
    ).limit(limit).offset(offset)
    users = db.scalars(base_stmt).all()

    count_stmt = select(func.count()).select_from(User)
    count_stmt = _apply_user_filters(
        count_stmt,
        role=role,
        status_value=status_value,
        account_type=account_type,
        organization_id=organization_id,
        search=search_value,
    )
    total = int(db.scalar(count_stmt) or 0)
    return AdminUserListResponse(items=users, total=total)


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    data: AdminUserCreate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminUserOut:
    username = data.username
    email = data.email.strip().lower()

    duplicate = (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )

    organization_id = data.organization_id
    if data.role == "org_admin":
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="organization_id is required for org_admin role.",
            )
        organization = db.get(Organization, organization_id)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
        if organization.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is disabled. Reactivate it before assigning administrators.",
            )
    else:
        organization = None
        organization_id = None

    if data.role in {"admin", "superuser"}:
        account_type = "staff"
    elif data.role == "org_admin":
        account_type = "organization_admin"
    else:
        account_type = "individual"

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        status="active",
        account_type=account_type,
        organization_id=organization_id,
    )
    db.add(user)
    db.flush()

    if user.role in {"admin", "superuser"}:
        db.add(PlatformUser(user_id=user.id))
    elif user.role == "org_admin":
        db.add(OrganizationUser(user_id=user.id, organization_id=organization_id))
    elif user.role == "user":
        db.add(LearnerUser(user_id=user.id, primary_org_id=user.organization_id))

    if organization:
        membership = (
            db.query(OrgMembership)
            .filter(
                OrgMembership.organization_id == organization.id,
                OrgMembership.user_id == user.id,
            )
            .first()
        )
        if membership is None:
            membership = OrgMembership(
                organization_id=organization.id,
                user_id=user.id,
                org_role="org_admin",
                status="active",
            )
            db.add(membership)
        else:
            membership.org_role = "org_admin"
            membership.status = "active"

    if data.send_notification:
        notification_service = NotificationService(db)
        notification_service.create(
            user_id=user.id,
            type="admin_access",
            title="Admin access granted",
            body="You have been granted admin privileges. Sign in to configure your workspace.",
        )

    if data.send_invite_email:
        email_service = EmailService(db)
        email_service.enqueue(
            to_email=user.email,
            template="admin_user_invite",
            payload={"username": user.username},
        )

    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/status", response_model=AdminUserOut)
def update_admin_user_status(
    user_id: int,
    payload: AdminUserStatusUpdate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminUserOut:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.status = payload.status
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/config/mail", response_model=MailConfigOut)
def get_mail_config(
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> MailConfigOut:
    service = ConfigService(db)
    return service.get_mail_config()


@router.put("/config/mail", response_model=MailConfigOut)
def update_mail_config(
    data: MailConfigIn,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> MailConfigOut:
    service = ConfigService(db)
    config = service.save_mail_config(data)
    db.commit()
    return config


@router.post("/email/dispatch", response_model=EmailDispatchResult)
def dispatch_email_events(
    limit: int = Query(default=20, ge=1, le=100),
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> EmailDispatchResult:
    service = EmailService(db)
    try:
        result = service.dispatch_pending(limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    return result


@router.post("/notifications", response_model=AdminNotificationResult)
def create_admin_notification(
    data: AdminNotificationCreate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminNotificationResult:
    notification_service = NotificationService(db)

    target_ids: set[int] = set(data.user_ids or [])

    if data.organization_id:
        stmt = (
            select(User.id)
            .where(User.organization_id == data.organization_id)
            .where(User.status == "active")
        )
        org_user_ids = db.scalars(stmt).all()
        target_ids.update(org_user_ids)

    notified = notification_service.create_many(
        list(target_ids),
        type=data.type,
        title=data.title,
        body=data.body,
        meta=data.meta,
    )
    db.commit()
    return AdminNotificationResult(notified_users=notified)


@router.get("/bulk-import/template")
def download_bulk_import_template_route(
    _: None = Depends(require_content_manager),
) -> Response:
    workbook = build_bulk_import_template()
    headers = {"Content-Disposition": 'attachment; filename="bulk-import-template.xlsx"'}
    return Response(content=workbook, media_type=EXCEL_MEDIA_TYPE, headers=headers)


@router.get("/bulk-import/export")
def download_bulk_import_export(
    organization_id: int | None = Query(default=None),
    current_user: User = Depends(require_content_manager),
    db: Session = Depends(get_db_session),
) -> Response:
    target_org_id = resolve_content_organization(
        current_user,
        organization_id,
        allow_global_for_admin=True,
    )

    subjects = _load_export_subjects(db, target_org_id)
    quizzes, quiz_title_map = _load_export_quizzes(db, target_org_id)
    questions = _load_export_questions(db, target_org_id, quiz_title_map)

    workbook = build_bulk_import_workbook(subjects, quizzes, questions)
    headers = {"Content-Disposition": 'attachment; filename="bulk-import-export.xlsx"'}
    return Response(content=workbook, media_type=EXCEL_MEDIA_TYPE, headers=headers)


@router.post("/bulk-import/preview", response_model=BulkImportPreview)
async def preview_bulk_import(
    organization_id: int | None = Query(default=None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_content_manager),
    db: Session = Depends(get_db_session),
) -> BulkImportPreview:
    filename = (file.filename or "").lower()
    if not filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload an Excel .xlsx workbook.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty.")

    try:
        parsed = parse_workbook(content)
    except BulkImportFormatError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    target_org_id = resolve_content_organization(
        current_user,
        organization_id,
        allow_global_for_admin=True,
    )

    existing_subjects = _fetch_subject_map(db, target_org_id)
    existing_quizzes = _fetch_quiz_map(db, target_org_id)
    existing_questions = _fetch_question_map(db, target_org_id)

    subject_slug_counts: dict[str, int] = {}
    subjects_preview: list[BulkSubjectPreview] = []

    for subject in parsed.subjects:
        slug = slugify(subject.name) if subject.name else ""
        errors = list(subject.errors)
        if slug:
            subject_slug_counts[slug] = subject_slug_counts.get(slug, 0) + 1
            if subject_slug_counts[slug] > 1:
                errors.append("Duplicate subject name in the workbook.")
        elif not errors:
            errors.append("Subject name is required.")

        existing = existing_subjects.get(slug) if slug else None
        subjects_preview.append(
            BulkSubjectPreview(
                source_row=subject.source_row,
                name=subject.name,
                description=subject.description,
                icon=subject.icon,
                slug=slug,
                action="update" if existing else "create",
                errors=errors,
            )
        )

    valid_subject_slugs = {
        item.slug
        for item in subjects_preview
        if item.slug and not item.errors
    } | set(existing_subjects.keys())

    quiz_title_counts: dict[str, int] = {}
    quizzes_preview: list[BulkQuizPreview] = []
    available_prompt_keys = {
        question.prompt.strip().lower()
        for question in parsed.questions
        if question.prompt.strip()
    } | set(existing_questions.keys())

    for quiz in parsed.quizzes:
        title = quiz.title.strip() if quiz.title else ""
        title_key = title.lower()
        errors = list(quiz.errors)
        if title_key:
            quiz_title_counts[title_key] = quiz_title_counts.get(title_key, 0) + 1
            if quiz_title_counts[title_key] > 1:
                errors.append("Duplicate quiz title in the workbook.")
        else:
            errors.append("Quiz title is required.")

        existing = existing_quizzes.get(title_key) if title_key else None
        if existing and target_org_id not in {existing.organization_id, None}:
            errors.append("Quiz belongs to another organization.")

        for prompt in quiz.question_prompts:
            prompt_key = prompt.strip().lower()
            if prompt_key and prompt_key not in available_prompt_keys:
                errors.append(f"Question '{prompt}' is not defined in this import or library.")

        quizzes_preview.append(
            BulkQuizPreview(
                source_row=quiz.source_row,
                title=quiz.title,
                description=quiz.description,
                is_active=quiz.is_active,
                question_prompts=quiz.question_prompts,
                action="update" if existing else "create",
                errors=errors,
            )
        )

    quiz_titles_in_sheet = {
        quiz.title.strip().lower()
        for quiz in parsed.quizzes
        if quiz.title.strip()
    }
    quiz_titles_in_sheet |= set(existing_quizzes.keys())

    question_prompt_counts: dict[str, int] = {}
    questions_preview: list[BulkQuestionPreview] = []
    for question in parsed.questions:
        prompt = question.prompt.strip() if question.prompt else ""
        prompt_key = prompt.lower()
        errors = list(question.errors)
        if prompt_key:
            question_prompt_counts[prompt_key] = question_prompt_counts.get(prompt_key, 0) + 1
            if question_prompt_counts[prompt_key] > 1:
                errors.append("Duplicate question prompt in the workbook.")
        else:
            errors.append("Question prompt is required.")

        subject_slug = slugify(question.subject_name) if question.subject_name else ""
        if subject_slug not in valid_subject_slugs:
            errors.append(
                f"Subject '{question.subject_name or 'Unknown'}' is not defined in the Subjects sheet or existing library."
            )

        for title in question.quiz_titles:
            title_key = title.strip().lower()
            if title_key and title_key not in quiz_titles_in_sheet:
                errors.append(f"Quiz '{title}' is not defined in the Quizzes sheet or existing library.")

        existing = existing_questions.get(prompt_key) if prompt_key else None
        if existing and target_org_id not in {existing.organization_id, None}:
            errors.append("Question belongs to another organization.")

        questions_preview.append(
            BulkQuestionPreview(
                source_row=question.source_row,
                prompt=question.prompt,
                explanation=question.explanation,
                subject=question.subject_label,
                difficulty=question.difficulty,
                is_active=question.is_active,
                subject_name=question.subject_name,
                quiz_titles=question.quiz_titles,
                options=[
                    BulkQuestionOption(text=option.text, is_correct=option.is_correct)
                    for option in question.options
                ],
                action="update" if existing else "create",
                errors=errors,
            )
        )

    return BulkImportPreview(
        subjects=subjects_preview,
        quizzes=quizzes_preview,
        questions=questions_preview,
        warnings=parsed.warnings,
    )


@router.post("/bulk-import/commit", response_model=BulkImportResult)
def commit_bulk_import(
    payload: BulkImportCommit,
    organization_id: int | None = Query(default=None),
    current_user: User = Depends(require_content_manager),
    db: Session = Depends(get_db_session),
) -> BulkImportResult:
    target_org_id = resolve_content_organization(
        current_user,
        organization_id,
        allow_global_for_admin=True,
    )

    if not payload.subjects and not payload.questions and not payload.quizzes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No records to import.")

    _ensure_unique_subjects(payload.subjects)
    _ensure_valid_questions(payload.questions)
    _ensure_unique_quizzes(payload.quizzes)

    existing_subjects = _fetch_subject_map(db, target_org_id)
    existing_quizzes = _fetch_quiz_map(db, target_org_id)

    quiz_titles_defined = {quiz.title.strip().lower(): quiz for quiz in payload.quizzes if quiz.title.strip()}
    for question in payload.questions:
        for title in question.quiz_titles:
            title_key = title.strip().lower()
            if title_key and title_key not in quiz_titles_defined and title_key not in existing_quizzes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question '{question.prompt}' references quiz '{title}' that is not defined.",
                )

    quiz_prompt_requirements = _collect_quiz_prompts(payload)
    all_needed_prompts = set()
    for prompts in quiz_prompt_requirements.values():
        all_needed_prompts.update(prompts)
    all_needed_prompts.update(question.prompt for question in payload.questions)

    existing_questions = _fetch_question_map(db, target_org_id, prompts=all_needed_prompts)

    subject_lookup = dict(existing_subjects)

    result = BulkImportResult(
        subjects_created=0,
        subjects_updated=0,
        quizzes_created=0,
        quizzes_updated=0,
        questions_created=0,
        questions_updated=0,
    )

    try:
        # Subjects
        for subject in payload.subjects:
            slug = slugify(subject.name)
            existing = subject_lookup.get(slug)
            description = _normalize_optional(subject.description)
            icon = _normalize_optional(subject.icon)
            if existing is not None:
                existing.name = subject.name.strip()
                existing.description = description
                existing.icon = icon
                existing.organization_id = target_org_id
                result.subjects_updated += 1
            else:
                new_subject = Subject(
                    name=subject.name.strip(),
                    slug=slug,
                    description=description,
                    icon=icon,
                    organization_id=target_org_id,
                )
                db.add(new_subject)
                db.flush()
                subject_lookup[slug] = new_subject
                result.subjects_created += 1

        # Questions
        question_lookup = dict(existing_questions)
        for question in payload.questions:
            prompt = question.prompt.strip()
            prompt_key = prompt.lower()
            subject_slug = slugify(question.subject_name)
            subject_model = subject_lookup.get(subject_slug)
            if subject_model is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject '{question.subject_name}' is not available.",
                )

            existing_question = question_lookup.get(prompt_key)
            explanation = _normalize_optional(question.explanation)
            subject_label = _normalize_optional(question.subject_label)
            difficulty = _normalize_optional(question.difficulty)

            if existing_question is None:
                new_question = Question(
                    prompt=prompt,
                    explanation=explanation,
                    subject_label=subject_label,
                    difficulty=difficulty,
                    is_active=question.is_active,
                    subject_id=subject_model.id,
                    organization_id=target_org_id,
                )
                db.add(new_question)
                db.flush()
                for option in question.options:
                    db.add(
                        Option(
                            question_id=new_question.id,
                            text=option.text.strip(),
                            is_correct=option.is_correct,
                        )
                    )
                question_lookup[prompt_key] = new_question
                result.questions_created += 1
            else:
                existing_question.prompt = prompt
                existing_question.explanation = explanation
                existing_question.subject_label = subject_label
                existing_question.difficulty = difficulty
                existing_question.is_active = question.is_active
                existing_question.subject_id = subject_model.id
                existing_question.organization_id = target_org_id
                db.query(Option).filter(Option.question_id == existing_question.id).delete(synchronize_session=False)
                for option in question.options:
                    db.add(
                        Option(
                            question_id=existing_question.id,
                            text=option.text.strip(),
                            is_correct=option.is_correct,
                        )
                    )
                result.questions_updated += 1
                question_lookup[prompt_key] = existing_question

        db.flush()

        # Quizzes
        for quiz in payload.quizzes:
            title = quiz.title.strip()
            title_key = title.lower()
            description = _normalize_optional(quiz.description)
            existing_quiz = existing_quizzes.get(title_key)
            if existing_quiz is None:
                existing_quiz = Quiz(
                    title=title,
                    description=description,
                    is_active=quiz.is_active,
                    organization_id=target_org_id,
                )
                db.add(existing_quiz)
                db.flush()
                existing_quizzes[title_key] = existing_quiz
                result.quizzes_created += 1
            else:
                existing_quiz.description = description
                existing_quiz.is_active = quiz.is_active
                existing_quiz.organization_id = target_org_id
                result.quizzes_updated += 1

            prompts = _dedupe_preserve_order(quiz.question_prompts + quiz_prompt_requirements.get(title_key, []))
            db.query(QuizQuestion).filter(QuizQuestion.quiz_id == existing_quiz.id).delete(synchronize_session=False)
            for position, prompt in enumerate(prompts, start=1):
                prompt_key = prompt.strip().lower()
                question_obj = question_lookup.get(prompt_key)
                if question_obj is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Quiz '{quiz.title}' references question '{prompt}' that was not found.",
                    )
                db.add(
                    QuizQuestion(
                        quiz_id=existing_quiz.id,
                        question_id=question_obj.id,
                        position=position,
                    )
                )

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    return result


def _fetch_subject_map(db: Session, organization_id: int | None) -> dict[str, Subject]:
    stmt = select(Subject)
    if organization_id is None:
        stmt = stmt.where(Subject.organization_id.is_(None))
    else:
        stmt = stmt.where(Subject.organization_id == organization_id)
    return {subject.slug: subject for subject in db.scalars(stmt).all()}


def _fetch_quiz_map(db: Session, organization_id: int | None) -> dict[str, Quiz]:
    stmt = select(Quiz)
    if organization_id is None:
        stmt = stmt.where(Quiz.organization_id.is_(None))
    else:
        stmt = stmt.where(Quiz.organization_id == organization_id)
    return {quiz.title.strip().lower(): quiz for quiz in db.scalars(stmt).all()}


def _fetch_question_map(
    db: Session,
    organization_id: int | None,
    *,
    prompts: Iterable[str] | None = None,
) -> dict[str, Question]:
    stmt = select(Question)
    if prompts:
        normalized_prompts = {prompt.strip() for prompt in prompts if prompt.strip()}
        if normalized_prompts:
            stmt = stmt.where(Question.prompt.in_(normalized_prompts))
    if organization_id is None:
        stmt = stmt.where(Question.organization_id.is_(None))
    else:
        stmt = stmt.where(Question.organization_id == organization_id)
    return {question.prompt.strip().lower(): question for question in db.scalars(stmt).all()}


def _load_export_subjects(db: Session, organization_id: int | None) -> list[ExportSubject]:
    stmt = select(Subject).order_by(Subject.name.asc())
    if organization_id is None:
        stmt = stmt.where(Subject.organization_id.is_(None))
    else:
        stmt = stmt.where(Subject.organization_id == organization_id)
    subjects = db.scalars(stmt).all()
    return [
        ExportSubject(
            name=subject.name.strip(),
            description=subject.description,
            icon=subject.icon,
        )
        for subject in subjects
    ]


def _load_export_quizzes(
    db: Session, organization_id: int | None
) -> tuple[list[ExportQuiz], dict[int, str]]:
    stmt = select(Quiz).order_by(Quiz.title.asc())
    if organization_id is None:
        stmt = stmt.where(Quiz.organization_id.is_(None))
    else:
        stmt = stmt.where(Quiz.organization_id == organization_id)
    quizzes = db.scalars(stmt).all()

    quiz_ids = [quiz.id for quiz in quizzes]
    prompt_map: dict[int, list[str]] = {quiz.id: [] for quiz in quizzes}
    if quiz_ids:
        rows = db.execute(
            select(QuizQuestion.quiz_id, QuizQuestion.position, Question.prompt)
            .join(Question, Question.id == QuizQuestion.question_id)
            .where(QuizQuestion.quiz_id.in_(quiz_ids))
            .order_by(QuizQuestion.quiz_id, QuizQuestion.position)
        ).all()
        for quiz_id, _, prompt in rows:
            prompt_map.setdefault(quiz_id, []).append(prompt)

    export_quizzes = [
        ExportQuiz(
            title=quiz.title,
            description=quiz.description,
            is_active=quiz.is_active,
            question_prompts=prompt_map.get(quiz.id, []),
        )
        for quiz in quizzes
    ]
    return export_quizzes, {quiz.id: quiz.title for quiz in quizzes}


def _load_export_questions(
    db: Session,
    organization_id: int | None,
    quiz_title_map: dict[int, str],
) -> list[ExportQuestion]:
    stmt = (
        select(Question)
        .options(selectinload(Question.options), selectinload(Question.subject))
        .order_by(Question.prompt.asc())
    )
    if organization_id is None:
        stmt = stmt.where(Question.organization_id.is_(None))
    else:
        stmt = stmt.where(Question.organization_id == organization_id)
    questions = db.scalars(stmt).all()

    question_ids = [question.id for question in questions]
    quiz_assignments: dict[int, list[str]] = {question.id: [] for question in questions}
    if question_ids and quiz_title_map:
        rows = db.execute(
            select(QuizQuestion.question_id, QuizQuestion.quiz_id, QuizQuestion.position)
            .where(QuizQuestion.question_id.in_(question_ids))
            .where(QuizQuestion.quiz_id.in_(quiz_title_map.keys()))
            .order_by(QuizQuestion.question_id, QuizQuestion.position)
        ).all()
        for question_id, quiz_id, _ in rows:
            title = quiz_title_map.get(quiz_id)
            if title:
                quiz_assignments.setdefault(question_id, []).append(title)

    export_questions: list[ExportQuestion] = []
    for question in questions:
        subject_name = question.subject.name if question.subject else ""
        export_questions.append(
            ExportQuestion(
                prompt=question.prompt,
                explanation=question.explanation,
                subject=question.subject,
                difficulty=question.difficulty,
                is_active=question.is_active,
                subject_name=subject_name,
                quiz_titles=quiz_assignments.get(question.id, []),
                options=[
                    ExportQuestionOption(text=option.text, is_correct=option.is_correct)
                    for option in question.options
                ],
            )
        )
    return export_questions


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def _ensure_unique_subjects(subjects: list[BulkSubjectPayload]) -> None:
    seen: set[str] = set()
    for subject in subjects:
        name = subject.name.strip()
        if not name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject name cannot be empty.")
        slug = slugify(name)
        if slug in seen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate subject name '{subject.name}' in payload.",
            )
        seen.add(slug)


def _ensure_valid_questions(questions: list[BulkQuestionPayload]) -> None:
    seen: set[str] = set()
    for question in questions:
        prompt = question.prompt.strip()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question prompt cannot be empty.")
        key = prompt.lower()
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate question prompt '{question.prompt}' in payload.",
            )
        seen.add(key)
        options = getattr(question, "options", [])
        if len(options) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question '{question.prompt}' requires at least two options.",
            )
        if not any(option.is_correct for option in options):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question '{question.prompt}' requires a correct option.",
            )


def _ensure_unique_quizzes(quizzes: list[BulkQuizPayload]) -> None:
    seen: set[str] = set()
    for quiz in quizzes:
        title = quiz.title.strip()
        if not title:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz title cannot be empty.")
        key = title.lower()
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate quiz title '{quiz.title}' in payload.",
            )
        seen.add(key)


def _collect_quiz_prompts(payload: BulkImportCommit) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for question in payload.questions:
        for title in question.quiz_titles:
            trimmed = title.strip()
            if not trimmed:
                continue
            key = trimmed.lower()
            mapping.setdefault(key, []).append(question.prompt)
    return mapping


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        trimmed = item.strip()
        key = trimmed.lower()
        if not trimmed or key in seen:
            continue
        seen.add(key)
        result.append(trimmed)
    return result
