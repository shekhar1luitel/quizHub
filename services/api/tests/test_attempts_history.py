import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.deps import get_current_user, get_db_session  # noqa: E402
from app.main import app  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.models.attempt import Attempt, AttemptAnswer  # noqa: E402
from app.models.bookmark import Bookmark  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.question import Option, Question, QuizQuestion  # noqa: E402
from app.models.quiz import Quiz  # noqa: E402
from app.models.user import User  # noqa: E402


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_session] = override_get_db

_current_user: dict[str, User] = {}


def override_current_user():
    user = _current_user.get("user")
    if user is None:
        raise RuntimeError("Test user not configured")
    return user


app.dependency_overrides[get_current_user] = override_current_user

client = TestClient(app)


def reset_database():
    with TestingSessionLocal() as session:
        session.query(AttemptAnswer).delete()
        session.query(Attempt).delete()
        session.query(QuizQuestion).delete()
        session.query(Option).delete()
        session.query(Bookmark).delete()
        session.query(Question).delete()
        session.query(Category).delete()
        session.query(Quiz).delete()
        session.query(User).delete()
        session.commit()


def test_attempt_history_returns_data():
    reset_database()
    with TestingSessionLocal() as session:
        user = User(email="history@example.com", hashed_password="hashed", role="user")
        session.add(user)
        session.commit()
        session.refresh(user)

        _current_user["user"] = user

        category = Category(
            name="General Knowledge",
            slug="general-knowledge",
            description="General awareness",
            icon="🌍",
        )
        session.add(category)
        session.commit()
        session.refresh(category)

        question = Question(
            prompt="Capital city of Nepal?",
            explanation="Kathmandu is the capital city.",
            subject="Geography",
            difficulty="Easy",
            is_active=True,
            category_id=category.id,
        )
        session.add(question)
        session.flush()

        correct_option = Option(question_id=question.id, text="Kathmandu", is_correct=True)
        session.add_all(
            [
                correct_option,
                Option(question_id=question.id, text="Pokhara", is_correct=False),
            ]
        )
        session.flush()

        quiz = Quiz(title="Sample Quiz", description="A quick check", is_active=True)
        session.add(quiz)
        session.flush()

        session.add(QuizQuestion(quiz_id=quiz.id, question_id=question.id, position=1))

        submitted_at = datetime.now(timezone.utc)
        attempt = Attempt(
            user_id=user.id,
            quiz_id=quiz.id,
            started_at=submitted_at - timedelta(minutes=5),
            submitted_at=submitted_at,
            duration_seconds=300,
            total_questions=1,
            correct_answers=1,
            score=95.0,
        )
        session.add(attempt)
        session.flush()

        session.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option_id=correct_option.id,
                is_correct=True,
            )
        )

        session.commit()

    response = client.get("/api/attempts/history")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    entry = payload[0]
    assert entry["quiz_title"] == "Sample Quiz"
    assert entry["category_name"] == "General Knowledge"
    assert entry["difficulty"] == "Easy"
    assert entry["total_questions"] == 1
    assert entry["correct_answers"] == 1
    assert entry["duration_seconds"] == 300
    assert entry["type"] == "quiz"


def test_attempt_history_empty_when_no_attempts():
    reset_database()
    with TestingSessionLocal() as session:
        user = User(email="empty@example.com", hashed_password="hashed", role="user")
        session.add(user)
        session.commit()
        session.refresh(user)
        _current_user["user"] = user

    response = client.get("/api/attempts/history")
    assert response.status_code == 200
    assert response.json() == []
