from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import (
    Category,
    Option,
    OrgMembership,
    Organization,
    Question,
    Quiz,
    QuizQuestion,
    User,
    UserProfile,
)

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD = "password"
_SLUGIFY_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(slots=True)
class QuizSpec:
    title: str
    description: str
    organization_slug: str | None
    question_keys: list[str]


ORGANIZATIONS = [
    {"slug": "acme-academy", "name": "Acme Academy", "type": "education"},
]

USERS = [
    {
        "email": "superuser@example.com",
        "username": "superuser",
        "role": "superuser",
        "account_type": "staff",
        "organization_slug": None,
        "membership_role": None,
        "profile": {"name": "Super Admin"},
    },
    {
        "email": "admin@acme.test",
        "username": "acmeadmin",
        "role": "org_admin",
        "account_type": "organization_admin",
        "organization_slug": "acme-academy",
        "membership_role": "org_admin",
        "profile": {"name": "Asha Admin"},
    },
    {
        "email": "instructor@acme.test",
        "username": "acmeinstructor",
        "role": "admin",
        "account_type": "staff",
        "organization_slug": "acme-academy",
        "membership_role": "instructor",
        "profile": {"name": "Ian Instructor"},
    },
    {
        "email": "learner@acme.test",
        "username": "acmelearner",
        "role": "user",
        "account_type": "organization_member",
        "organization_slug": "acme-academy",
        "membership_role": "member",
        "profile": {"name": "Lina Learner"},
    },
]

CATEGORIES = [
    {"name": "Mathematics", "description": "Numbers, algebra, and problem solving."},
    {"name": "Science", "description": "Physics, chemistry, and general science topics."},
    {"name": "General Knowledge", "description": "Everyday facts and current affairs."},
]

QUESTIONS = [
    {
        "key": "math_addition",
        "category": "mathematics",
        "prompt": "What is 12 + 7?",
        "explanation": "12 + 7 equals 19.",
        "subject": "Mathematics",
        "topic": "Arithmetic",
        "difficulty": "easy",
        "options": [
            {"text": "17", "is_correct": False},
            {"text": "18", "is_correct": False},
            {"text": "19", "is_correct": True},
            {"text": "20", "is_correct": False},
        ],
    },
    {
        "key": "math_equation",
        "category": "mathematics",
        "prompt": "Solve for x: 3x + 9 = 21",
        "explanation": "Subtract 9 from both sides and divide by 3 to get x = 4.",
        "subject": "Mathematics",
        "topic": "Algebra",
        "difficulty": "medium",
        "options": [
            {"text": "3", "is_correct": False},
            {"text": "4", "is_correct": True},
            {"text": "5", "is_correct": False},
            {"text": "6", "is_correct": False},
        ],
    },
    {
        "key": "science_planet",
        "category": "science",
        "prompt": "Which planet is known as the Red Planet?",
        "explanation": "Mars appears red due to iron oxide on its surface.",
        "subject": "Science",
        "topic": "Astronomy",
        "difficulty": "easy",
        "options": [
            {"text": "Mercury", "is_correct": False},
            {"text": "Venus", "is_correct": False},
            {"text": "Earth", "is_correct": False},
            {"text": "Mars", "is_correct": True},
        ],
    },
    {
        "key": "science_water",
        "category": "science",
        "prompt": "What is the chemical formula for water?",
        "explanation": "Two hydrogen atoms and one oxygen atom form water.",
        "subject": "Science",
        "topic": "Chemistry",
        "difficulty": "easy",
        "options": [
            {"text": "CO₂", "is_correct": False},
            {"text": "H₂O", "is_correct": True},
            {"text": "O₂", "is_correct": False},
            {"text": "NaCl", "is_correct": False},
        ],
    },
    {
        "key": "gk_capital",
        "category": "general-knowledge",
        "prompt": "What is the capital city of Nepal?",
        "explanation": "Kathmandu is the capital and largest city of Nepal.",
        "subject": "General Knowledge",
        "topic": "Geography",
        "difficulty": "easy",
        "options": [
            {"text": "Pokhara", "is_correct": False},
            {"text": "Kathmandu", "is_correct": True},
            {"text": "Biratnagar", "is_correct": False},
            {"text": "Lalitpur", "is_correct": False},
        ],
    },
    {
        "key": "gk_language",
        "category": "general-knowledge",
        "prompt": "Which language has the most native speakers worldwide?",
        "explanation": "Mandarin Chinese has the highest number of native speakers.",
        "subject": "General Knowledge",
        "topic": "Culture",
        "difficulty": "medium",
        "options": [
            {"text": "English", "is_correct": False},
            {"text": "Spanish", "is_correct": False},
            {"text": "Mandarin Chinese", "is_correct": True},
            {"text": "Hindi", "is_correct": False},
        ],
    },
]

QUIZZES: list[QuizSpec] = [
    QuizSpec(
        title="Starter Mathematics Quiz",
        description="Quick check on arithmetic and algebra basics.",
        organization_slug="acme-academy",
        question_keys=["math_addition", "math_equation"],
    ),
    QuizSpec(
        title="Science Essentials",
        description="Fundamental science facts everyone should know.",
        organization_slug="acme-academy",
        question_keys=["science_planet", "science_water"],
    ),
    QuizSpec(
        title="General Knowledge Warmup",
        description="Introductory quiz for everyday knowledge.",
        organization_slug="acme-academy",
        question_keys=["gk_capital", "gk_language"],
    ),
]


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = _SLUGIFY_PATTERN.sub("-", value)
    return value.strip("-")


class Seeder:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.organizations: dict[str, Organization] = {}
        self.categories: dict[str, Category] = {}
        self.questions: dict[str, Question] = {}

    def run(self) -> None:
        logger.info("Seeding lookup tables")
        self.seed_organizations()
        self.seed_categories()
        logger.info("Seeding users")
        self.seed_users()
        logger.info("Seeding question bank")
        self.seed_questions()
        logger.info("Seeding quizzes")
        self.seed_quizzes()
        self.session.commit()
        logger.info("Seed data applied successfully")

    def seed_organizations(self) -> None:
        for record in ORGANIZATIONS:
            slug = record["slug"]
            organization = self.session.execute(
                select(Organization).where(Organization.slug == slug)
            ).scalar_one_or_none()
            if organization is None:
                organization = Organization(
                    name=record["name"],
                    slug=slug,
                    type=record.get("type"),
                    status="active",
                )
                self.session.add(organization)
                self.session.flush()
                logger.info("Created organization %s", organization.slug)
            else:
                organization.name = record["name"]
                organization.type = record.get("type")
                organization.status = "active"
            self.organizations[slug] = organization

    def seed_categories(self) -> None:
        self._ensure_autoincrement_sequence(Category)
        for record in CATEGORIES:
            slug = slugify(record["name"])
            category = self.session.execute(
                select(Category).where(Category.slug == slug)
            ).scalar_one_or_none()
            if category is None:
                category = self.session.execute(
                    select(Category).where(Category.name.ilike(record["name"]))
                ).scalar_one_or_none()
            if category is None:
                category = Category(
                    name=record["name"],
                    slug=slug,
                    description=record.get("description"),
                    icon=record.get("icon"),
                )
                self.session.add(category)
                self.session.flush()
                logger.info("Created category %s", category.slug)
            else:
                category.name = record["name"]
                category.slug = slug
                category.description = record.get("description")
                category.icon = record.get("icon")
            self.categories[slug] = category

    def _ensure_autoincrement_sequence(self, model: type[Category]) -> None:
        bind = self.session.get_bind()
        if bind is None or bind.dialect.name != "postgresql":
            return

        table = model.__table__
        pk_columns = list(table.primary_key.columns)
        if len(pk_columns) != 1:
            return

        pk_column = pk_columns[0]
        sequence_name = self.session.execute(
            select(func.pg_get_serial_sequence(table.fullname, pk_column.name))
        ).scalar_one_or_none()

        if not sequence_name:
            return

        max_id = self.session.execute(select(func.max(pk_column))).scalar()
        if max_id is None:
            self.session.execute(
                text("SELECT setval(:seq_name, 1, false)"),
                {"seq_name": sequence_name},
            )
        else:
            self.session.execute(
                text("SELECT setval(:seq_name, :value)"),
                {"seq_name": sequence_name, "value": max_id},
            )

    def seed_users(self) -> None:
        password_hash = get_password_hash(DEFAULT_PASSWORD)
        for record in USERS:
            stmt = (
                select(User)
                .options(selectinload(User.profile), selectinload(User.memberships))
                .where(User.email == record["email"])
            )
            user = self.session.execute(stmt).scalar_one_or_none()

            org_slug = record.get("organization_slug")
            organization = self.organizations.get(org_slug) if org_slug else None

            account_type = record.get("account_type")
            if account_type is None:
                if record["role"] in {"superuser", "admin"}:
                    account_type = "staff"
                elif record["role"] == "org_admin":
                    account_type = "organization_admin"
                elif organization is not None:
                    account_type = "organization_member"
                else:
                    account_type = "individual"

            if user is None:
                user = User(
                    email=record["email"],
                    username=record["username"],
                    hashed_password=password_hash,
                    role=record["role"],
                    organization_id=organization.id if organization else None,
                    status="active",
                    account_type=account_type,
                )
                self.session.add(user)
                self.session.flush()
                logger.info("Created user %s", user.email)
            else:
                user.hashed_password = password_hash
                user.role = record["role"]
                user.organization_id = organization.id if organization else None
                user.status = "active"
                user.username = record["username"]
                user.account_type = account_type

            profile_data = record.get("profile")
            if profile_data:
                if user.profile is None:
                    profile = UserProfile(user_id=user.id, name=profile_data.get("name"))
                    self.session.add(profile)
                else:
                    user.profile.name = profile_data.get("name")

            membership_role = record.get("membership_role")
            if membership_role and organization:
                membership = next(
                    (m for m in user.memberships if m.organization_id == organization.id),
                    None,
                )
                if membership is None:
                    membership = OrgMembership(
                        organization_id=organization.id,
                        user_id=user.id,
                        org_role=membership_role,
                        status="active",
                    )
                    self.session.add(membership)
                else:
                    membership.org_role = membership_role
                    membership.status = "active"

    def seed_questions(self) -> None:
        for record in QUESTIONS:
            category_slug = record["category"]
            category = self.categories.get(category_slug)
            if category is None:
                raise ValueError(f"Category '{category_slug}' not found for question {record['key']}")

            stmt = (
                select(Question)
                .options(selectinload(Question.options))
                .where(Question.prompt == record["prompt"])
            )
            question = self.session.execute(stmt).scalar_one_or_none()

            if question is None:
                question = Question(
                    prompt=record["prompt"],
                    explanation=record.get("explanation"),
                    subject=record.get("subject"),
                    topic=record.get("topic"),
                    difficulty=record.get("difficulty"),
                    text_en=record.get("prompt"),
                    text_ne=None,
                    category_id=category.id,
                    is_active=True,
                )
                self.session.add(question)
                self.session.flush()
                logger.info("Created question %s", record["key"])
            else:
                question.explanation = record.get("explanation")
                question.subject = record.get("subject")
                question.topic = record.get("topic")
                question.difficulty = record.get("difficulty")
                question.text_en = record.get("prompt")
                question.category_id = category.id
                question.is_active = True

            existing_options = {option.text: option for option in question.options}
            for option_spec in record["options"]:
                option = existing_options.get(option_spec["text"])
                if option is None:
                    option = Option(
                        question_id=question.id,
                        text=option_spec["text"],
                        is_correct=option_spec["is_correct"],
                    )
                    self.session.add(option)
                else:
                    option.is_correct = option_spec["is_correct"]

            option_texts = [opt["text"] for opt in record["options"]]
            orphan_options = [
                option for option in question.options if option.text not in option_texts
            ]
            for option in orphan_options:
                self.session.delete(option)

            if not any(opt["is_correct"] for opt in record["options"]):
                raise ValueError(f"Question {record['key']} is missing a correct option")

            self.questions[record["key"]] = question

    def seed_quizzes(self) -> None:
        for spec in QUIZZES:
            stmt = (
                select(Quiz)
                .options(selectinload(Quiz.questions))
                .where(Quiz.title == spec.title)
            )
            quiz = self.session.execute(stmt).scalar_one_or_none()

            organization = (
                self.organizations.get(spec.organization_slug)
                if spec.organization_slug
                else None
            )

            if quiz is None:
                quiz = Quiz(
                    title=spec.title,
                    description=spec.description,
                    is_active=True,
                    organization_id=organization.id if organization else None,
                )
                self.session.add(quiz)
                self.session.flush()
                logger.info("Created quiz %s", quiz.title)
            else:
                quiz.description = spec.description
                quiz.is_active = True
                quiz.organization_id = organization.id if organization else None

            existing_map = {qq.question_id: qq for qq in quiz.questions}
            for position, question_key in enumerate(spec.question_keys, start=1):
                question = self.questions.get(question_key)
                if question is None:
                    raise ValueError(f"Question '{question_key}' missing for quiz {spec.title}")
                quiz_question = existing_map.pop(question.id, None)
                if quiz_question is None:
                    quiz_question = QuizQuestion(
                        quiz=quiz,
                        question=question,
                        position=position,
                    )
                    self.session.add(quiz_question)
                else:
                    quiz_question.position = position

            for quiz_question in existing_map.values():
                self.session.delete(quiz_question)


def validate_specifications() -> None:
    keys = [question["key"] for question in QUESTIONS]
    duplicate_keys = [item for item, count in Counter(keys).items() if count > 1]
    if duplicate_keys:
        raise ValueError(f"Duplicate question keys detected: {duplicate_keys}")

    category_slugs = {slugify(category["name"]) for category in CATEGORIES}
    missing_categories = sorted({question["category"] for question in QUESTIONS} - category_slugs)
    if missing_categories:
        raise ValueError(f"Questions reference unknown categories: {missing_categories}")

    known_question_keys = {question["key"] for question in QUESTIONS}
    for spec in QUIZZES:
        missing = [key for key in spec.question_keys if key not in known_question_keys]
        if missing:
            raise ValueError(f"Quiz '{spec.title}' references unknown questions: {missing}")


def seed(session: Session | None = None) -> None:
    validate_specifications()
    if session is None:
        with SessionLocal() as scoped_session:
            seeder = Seeder(scoped_session)
            seeder.run()
            return
    seeder = Seeder(session)
    seeder.run()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        seed()
    except Exception:  # pragma: no cover - surface full trace to the console
        logger.exception("Seeding failed")
        raise


if __name__ == "__main__":
    main()
