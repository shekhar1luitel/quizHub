import sys
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.routes import practice as practice_routes  # noqa: E402
from app.api.routes import quizzes as quizzes_routes  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.models.bookmark import Bookmark  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.organization import Organization, OrgMembership  # noqa: E402
from app.models.question import Option, Question, QuizQuestion  # noqa: E402
from app.models.quiz import Quiz  # noqa: E402
from app.models.user import LearnerUser, User  # noqa: E402


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def seed_questions(db: Session) -> Organization:
    db.query(QuizQuestion).delete()
    db.query(Quiz).delete()
    db.query(OrgMembership).delete()
    db.query(LearnerUser).delete()
    db.query(User).delete()
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Category).delete()
    db.query(Organization).delete()

    organization = Organization(name="Acme Academy", slug="acme-academy", status="active")
    db.add(organization)
    db.flush()

    category = Category(
        name="General Knowledge",
        slug="general-knowledge",
        description="World geography, history, science, and current events",
        icon="🌍",
        organization_id=organization.id,
    )

    db.add(category)
    db.flush()

    general_question = Question(
        prompt="Capital of Nepal is Kathmandu.",
        explanation="Kathmandu is the capital city of Nepal.",
        subject="General Knowledge",
        difficulty="Easy",
        is_active=True,
        category_id=category.id,
        organization_id=organization.id,
    )
    mixed_question = Question(
        prompt="Select the odd number.",
        explanation="19 is a prime number while the others are even.",
        subject="General Knowledge",
        difficulty="Medium",
        is_active=True,
        category_id=category.id,
        organization_id=organization.id,
    )

    db.add_all([general_question, mixed_question])
    db.flush()

    db.add_all(
        [
            Option(question_id=general_question.id, text="Kathmandu", is_correct=True),
            Option(question_id=general_question.id, text="Pokhara", is_correct=False),
            Option(question_id=general_question.id, text="Lalitpur", is_correct=False),
            Option(question_id=general_question.id, text="Biratnagar", is_correct=False),
            Option(question_id=mixed_question.id, text="12", is_correct=False),
            Option(question_id=mixed_question.id, text="16", is_correct=False),
            Option(question_id=mixed_question.id, text="18", is_correct=False),
            Option(question_id=mixed_question.id, text="19", is_correct=True),
        ]
    )

    db.commit()
    return organization


def create_learner(db: Session, organization: Organization) -> User:
    learner = User(
        email="learner@example.com",
        username="learner",
        role="user",
        status="active",
        account_type="organization_member",
        hashed_password="not-used",
        organization_id=organization.id,
    )
    db.add(learner)
    db.flush()
    db.add(LearnerUser(user_id=learner.id, primary_org_id=organization.id))
    db.add(
        OrgMembership(
            organization_id=organization.id,
            user_id=learner.id,
            status="active",
            org_role="member",
        )
    )
    db.commit()
    db.refresh(learner)
    return learner


def create_b2c_learner(db: Session) -> User:
    learner = User(
        email="solo@example.com",
        username="solo",
        role="user",
        status="active",
        account_type="individual",
        hashed_password="not-used",
        organization_id=None,
    )
    db.add(learner)
    db.flush()
    db.add(LearnerUser(user_id=learner.id, primary_org_id=None))
    db.commit()
    db.refresh(learner)
    return learner


def seed_global_questions(db: Session) -> Category:
    db.query(QuizQuestion).delete()
    db.query(Quiz).delete()
    db.query(OrgMembership).delete()
    db.query(LearnerUser).delete()
    db.query(User).delete()
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Category).delete()
    db.query(Organization).delete()

    category = Category(
        name="General Knowledge",
        slug="general-knowledge",
        description="World geography, history, science, and current events",
        icon="🌍",
        organization_id=None,
    )
    db.add(category)
    db.flush()

    general_question = Question(
        prompt="Capital of Nepal is Kathmandu.",
        explanation="Kathmandu is the capital city of Nepal.",
        subject="General Knowledge",
        difficulty="Easy",
        is_active=True,
        category_id=category.id,
        organization_id=None,
    )
    mixed_question = Question(
        prompt="Select the odd number.",
        explanation="19 is a prime number while the others are even.",
        subject="General Knowledge",
        difficulty="Medium",
        is_active=True,
        category_id=category.id,
        organization_id=None,
    )
    db.add_all([general_question, mixed_question])
    db.flush()

    db.add_all(
        [
            Option(question_id=general_question.id, text="Kathmandu", is_correct=True),
            Option(question_id=general_question.id, text="Pokhara", is_correct=False),
            Option(question_id=general_question.id, text="Lalitpur", is_correct=False),
            Option(question_id=general_question.id, text="Biratnagar", is_correct=False),
            Option(question_id=mixed_question.id, text="12", is_correct=False),
            Option(question_id=mixed_question.id, text="16", is_correct=False),
            Option(question_id=mixed_question.id, text="18", is_correct=False),
            Option(question_id=mixed_question.id, text="19", is_correct=True),
        ]
    )
    db.commit()
    return category


def seed_questions_without_items(db: Session) -> tuple[Organization, Category]:
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Category).delete()
    db.query(Organization).delete()

    organization = Organization(name="News Academy", slug="news-academy", status="active")
    db.add(organization)
    db.flush()

    category = Category(
        name="General Knowledge",
        slug="general-knowledge",
        description="World geography, history, science, and current events",
        icon="🌍",
        organization_id=organization.id,
    )

    db.add(category)
    db.commit()

    return organization, category


def test_practice_categories_reflect_active_questions():
    with TestingSessionLocal() as session:
        organization = seed_questions(session)
        learner = create_learner(session, organization)
        categories = practice_routes.list_practice_categories(db=session, current_user=learner)

    assert any(category.slug == "general-knowledge" for category in categories)
    general = next(category for category in categories if category.slug == "general-knowledge")
    assert general.total_questions == 2
    assert general.difficulty == "Mixed"
    assert general.icon == "🌍"
    assert general.description is not None


def test_practice_categories_include_quiz_id_when_available():
    with TestingSessionLocal() as session:
        organization = seed_questions(session)
        questions = session.query(Question).all()
        quiz = Quiz(
            title="Category Mock Exam",
            description=None,
            is_active=True,
            organization_id=organization.id,
        )
        session.add(quiz)
        session.flush()

        for position, question in enumerate(questions, start=1):
            session.add(QuizQuestion(quiz_id=quiz.id, question_id=question.id, position=position))

        session.commit()

        learner = create_learner(session, organization)
        categories = practice_routes.list_practice_categories(db=session, current_user=learner)

    summary = next(item for item in categories if item.slug == "general-knowledge")
    assert summary.quiz_id == quiz.id


def test_practice_category_detail_returns_questions():
    with TestingSessionLocal() as session:
        organization = seed_questions(session)
        learner = create_learner(session, organization)
        detail = practice_routes.get_practice_category(
            slug="general-knowledge",
            limit=10,
            db=session,
            current_user=learner,
        )

    assert detail.name == "General Knowledge"
    assert detail.total_questions == 2
    assert len(detail.questions) == 2
    assert detail.icon == "🌍"
    assert all(len(question.options) == 4 for question in detail.questions)
    assert any(option.is_correct for option in detail.questions[0].options)


def test_practice_category_without_questions_returns_empty_list():
    with TestingSessionLocal() as session:
        organization, category = seed_questions_without_items(session)
        learner = create_learner(session, organization)

        detail = practice_routes.get_practice_category(
            slug="general-knowledge",
            db=session,
            current_user=learner,
        )

    assert detail.total_questions == 0
    assert detail.questions == []
    assert detail.difficulty == "Mixed"
    assert detail.slug == "general-knowledge"


def test_practice_categories_support_global_scope():
    with TestingSessionLocal() as session:
        category = seed_global_questions(session)
        learner = create_b2c_learner(session)
        categories = practice_routes.list_practice_categories(db=session, current_user=learner)

    assert any(item.slug == category.slug for item in categories)
    summary = next(item for item in categories if item.slug == category.slug)
    assert summary.total_questions == 2
    assert summary.organization_id is None


def test_practice_category_detail_global_scope():
    with TestingSessionLocal() as session:
        seed_global_questions(session)
        learner = create_b2c_learner(session)
        detail = practice_routes.get_practice_category(
            slug="general-knowledge",
            db=session,
            current_user=learner,
        )

    assert detail.organization_id is None
    assert detail.total_questions == 2
    assert len(detail.questions) == 2


def test_practice_bookmarks_returns_questions():
    with TestingSessionLocal() as session:
        organization = seed_questions(session)
        learner = create_learner(session, organization)
        questions = session.query(Question).all()

        for question in questions:
            session.add(Bookmark(user_id=learner.id, question_id=question.id))
        session.commit()

        detail = practice_routes.get_bookmark_revision_set(
            db=session,
            current_user=learner,
            limit=10,
        )

    assert detail.slug == "bookmarks"
    assert detail.name == "Bookmarks revision"
    assert detail.total_questions == len(questions)
    assert len(detail.questions) == len(questions)


def test_list_quizzes_returns_global_for_unassigned_learners():
    with TestingSessionLocal() as session:
        seed_global_questions(session)
        questions = session.query(Question).all()

        quiz = Quiz(
            title="Global Mock Exam",
            description="Full-length mock test",
            is_active=True,
            organization_id=None,
        )
        session.add(quiz)
        session.flush()

        for position, question in enumerate(questions, start=1):
            session.add(QuizQuestion(quiz_id=quiz.id, question_id=question.id, position=position))

        private_org = Organization(name="Private Prep", slug="private-prep", status="active")
        session.add(private_org)
        session.flush()
        session.add(Quiz(title="Org Exclusive Quiz", description=None, is_active=True, organization_id=private_org.id))
        session.commit()

        learner = create_b2c_learner(session)
        summaries = quizzes_routes.list_quizzes(db=session, current_user=learner)

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.id == quiz.id
    assert summary.organization_id is None
    assert summary.question_count == len(questions)


def test_list_quizzes_defaults_to_primary_organization():
    with TestingSessionLocal() as session:
        organization = seed_questions(session)
        question = session.query(Question).first()

        quiz = Quiz(
            title="Organization Mock Exam",
            description="Weekly mock test",
            is_active=True,
            organization_id=organization.id,
        )
        session.add(quiz)
        session.flush()
        session.add(QuizQuestion(quiz_id=quiz.id, question_id=question.id, position=1))
        session.commit()

        learner = create_learner(session, organization)
        summaries = quizzes_routes.list_quizzes(db=session, current_user=learner)

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.id == quiz.id
    assert summary.organization_id == organization.id


def test_unknown_category_returns_not_found():
    with TestingSessionLocal() as session:
        organization = seed_questions(session)
        learner = create_learner(session, organization)
        try:
            practice_routes.get_practice_category(slug="non-existent", db=session, current_user=learner)
        except Exception as exc:  # noqa: BLE001
            from fastapi import HTTPException

            assert isinstance(exc, HTTPException)
            assert exc.status_code == 404
        else:
            raise AssertionError("Expected HTTPException for unknown category")
