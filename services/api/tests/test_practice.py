import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.routes import practice as practice_routes  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.models.question import Option, Question  # noqa: E402


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def seed_questions(db: Session) -> None:
    db.query(Option).delete()
    db.query(Question).delete()

    general_question = Question(
        prompt="Capital of Nepal is Kathmandu.",
        explanation="Kathmandu is the capital city of Nepal.",
        subject="General Knowledge",
        difficulty="Easy",
        is_active=True,
    )
    mixed_question = Question(
        prompt="Select the odd number.",
        explanation="19 is a prime number while the others are even.",
        subject="General Knowledge",
        difficulty="Medium",
        is_active=True,
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


def test_practice_categories_reflect_active_questions():
    with TestingSessionLocal() as session:
        seed_questions(session)
        categories = practice_routes.list_practice_categories(db=session)

    assert any(category.slug == "general-knowledge" for category in categories)
    general = next(category for category in categories if category.slug == "general-knowledge")
    assert general.total_questions == 2
    assert general.difficulty == "Mixed"


def test_practice_category_detail_returns_questions():
    with TestingSessionLocal() as session:
        seed_questions(session)
        detail = practice_routes.get_practice_category(slug="general-knowledge", limit=10, db=session)

    assert detail.name == "General Knowledge"
    assert detail.total_questions == 2
    assert len(detail.questions) == 2
    assert all(len(question.options) == 4 for question in detail.questions)
    assert any(option.is_correct for option in detail.questions[0].options)


def test_unknown_category_returns_not_found():
    with TestingSessionLocal() as session:
        seed_questions(session)
        try:
            practice_routes.get_practice_category(slug="non-existent", db=session)
        except Exception as exc:  # noqa: BLE001
            from fastapi import HTTPException

            assert isinstance(exc, HTTPException)
            assert exc.status_code == 404
        else:
            raise AssertionError("Expected HTTPException for unknown category")
