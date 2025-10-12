from __future__ import annotations

from typing import List

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import (
    get_current_user_optional,
    get_db_session,
    resolve_content_organization,
    require_content_manager,
)
from app.models.question import Question, QuizQuestion
from app.models.organization import OrgMembership, Organization
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate,
    QuizDetail,
    QuizQuestion as QuizQuestionSchema,
    QuizQuestionOption,
    QuizSummary,
    QuizUpdate,
)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


def _resolve_default_org_id(user: User) -> int | None:
    if user.organization_id is not None:
        return user.organization_id
    learner_account = user.learner_account
    if learner_account and learner_account.primary_org_id is not None:
        return learner_account.primary_org_id
    return None


@router.get("/", response_model=List[QuizSummary])
def list_quizzes(
    organization_id: Annotated[int | None, Query(ge=1)] = None,
    db: Session = Depends(get_db_session),
    current_user: User | None = Depends(get_current_user_optional),
) -> List[QuizSummary]:
    restrict_to_global = False

    if organization_id is None and current_user is not None:
        if current_user.role in {"user", "org_admin"}:
            default_org_id = _resolve_default_org_id(current_user)
            if default_org_id is not None:
                organization_id = default_org_id
            else:
                restrict_to_global = True
        # admins and superusers may browse global quizzes without additional scope

    stmt = (
        select(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.is_active,
            func.count(QuizQuestion.question_id).label("question_count"),
            Quiz.organization_id,
        )
        .join(QuizQuestion, QuizQuestion.quiz_id == Quiz.id, isouter=True)
        .join(Organization, Organization.id == Quiz.organization_id, isouter=True)
        .group_by(Quiz.id)
        .order_by(Quiz.title)
    )

    if organization_id is not None:
        organization = db.get(Organization, organization_id)
        if organization is None or organization.status != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

        if current_user.role not in {"admin", "superuser"}:
            membership = (
                db.query(OrgMembership)
                .filter(
                    OrgMembership.organization_id == organization_id,
                    OrgMembership.user_id == current_user.id,
                    OrgMembership.status == "active",
                )
                .first()
            )
            if membership is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not enrolled in this organization.",
                )

        stmt = stmt.where(Quiz.organization_id == organization_id)
    else:
        if current_user is None:
            return []
        if restrict_to_global or current_user.role == "user":
            stmt = stmt.where(Quiz.organization_id.is_(None))
        else:
            stmt = stmt.where(or_(Quiz.organization_id.is_(None), Organization.status == "active"))

    rows = db.execute(stmt).all()
    return [
        QuizSummary(
            id=row.id,
            title=row.title,
            description=row.description,
            is_active=row.is_active,
            question_count=int(row.question_count or 0),
            organization_id=row.organization_id,
        )
        for row in rows
    ]


@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db_session),
    current_user: User | None = Depends(get_current_user_optional),
) -> QuizDetail:
    quiz = (
        db.query(Quiz)
        .options(
            selectinload(Quiz.questions)
            .selectinload(QuizQuestion.question)
            .selectinload(Question.options)
        )
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    if quiz.organization and quiz.organization.status != "active":
        if current_user is None or current_user.role not in {"admin", "superuser"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    if not quiz.is_active and (current_user is None or current_user.role not in {"admin", "superuser"}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    if quiz.organization_id is not None:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        if current_user.role == "user" and quiz.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        if current_user.role == "org_admin" and quiz.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    questions: List[QuizQuestionSchema] = []
    for link in sorted(quiz.questions, key=lambda q: q.position):
        question = link.question
        if question is None:
            continue
        if not question.is_active and (current_user is None or current_user.role != "admin"):
            continue
        questions.append(
            QuizQuestionSchema(
                id=question.id,
                prompt=question.prompt,
                subject=question.subject,
                difficulty=question.difficulty,
                options=[
                    QuizQuestionOption(id=option.id, text=option.text) for option in question.options
                ],
            )
        )

    return QuizDetail(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        is_active=quiz.is_active,
        questions=questions,
        organization_id=quiz.organization_id,
    )


@router.post("/", response_model=QuizSummary, status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
) -> QuizSummary:
    if db.query(Quiz).filter(Quiz.title == payload.title).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz title already exists")

    target_org_id = resolve_content_organization(
        current_user,
        payload.organization_id,
        allow_global_for_admin=True,
    )

    quiz = Quiz(
        title=payload.title,
        description=payload.description,
        is_active=payload.is_active,
        organization_id=target_org_id,
    )
    db.add(quiz)
    db.flush()

    attach_questions(payload.question_ids, quiz, db, target_org_id)

    db.commit()
    db.refresh(quiz)

    question_count = len(payload.question_ids)
    return QuizSummary(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        is_active=quiz.is_active,
        question_count=question_count,
        organization_id=quiz.organization_id,
    )


@router.put("/{quiz_id}", response_model=QuizSummary)
def update_quiz(
    quiz_id: int,
    payload: QuizUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
) -> QuizSummary:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    target_org_id = _ensure_quiz_scope(quiz, current_user, payload.organization_id)

    if payload.title is not None:
        existing = (
            db.query(Quiz)
            .filter(Quiz.title == payload.title, Quiz.id != quiz_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz title already exists")
        quiz.title = payload.title

    if payload.description is not None:
        quiz.description = payload.description
    if payload.is_active is not None:
        quiz.is_active = payload.is_active
    if payload.organization_id is not None or current_user.role == "org_admin":
        quiz.organization_id = target_org_id

    if payload.question_ids is not None:
        quiz.questions.clear()
        db.flush()
        attach_questions(payload.question_ids, quiz, db, target_org_id)

    db.commit()
    db.refresh(quiz)

    question_count = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).count()
    return QuizSummary(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        is_active=quiz.is_active,
        question_count=question_count,
        organization_id=quiz.organization_id,
    )


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> None:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    _ensure_quiz_scope(quiz, current_user, organization_id)
    db.delete(quiz)
    db.commit()


def attach_questions(
    question_ids: List[int],
    quiz: Quiz,
    db: Session,
    organization_id: int | None,
) -> None:
    if not question_ids:
        return

    if len(set(question_ids)) != len(question_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate questions are not allowed in a quiz",
        )

    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    missing_ids = set(question_ids) - {question.id for question in questions}
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown question ids: {sorted(missing_ids)}",
        )

    if organization_id is not None:
        invalid = [question.id for question in questions if question.organization_id != organization_id]
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Questions {invalid} do not belong to the organization",
            )
    else:
        invalid = [question.id for question in questions if question.organization_id is not None]
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Questions {invalid} are organization scoped and cannot be added",
            )

    for position, question_id in enumerate(question_ids, start=1):
        quiz.questions.append(QuizQuestion(quiz_id=quiz.id, question_id=question_id, position=position))


def _ensure_quiz_scope(quiz: Quiz, current_user: User, organization_id: int | None) -> int | None:
    target_org_id = resolve_content_organization(
        current_user,
        organization_id if organization_id is not None else quiz.organization_id,
        allow_global_for_admin=True,
    )
    if target_org_id is not None:
        if quiz.organization_id != target_org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quiz belongs to another organization")
    elif current_user.role != "superuser" and quiz.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quiz belongs to another organization")
    return target_org_id
