from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient  # noqa: E402

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.deps import get_current_user, get_db_session  # noqa: E402
from app.main import app  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.models.bookmark import Bookmark  # noqa: E402
from app.models.subject import Subject  # noqa: E402
from app.models.question import Question  # noqa: E402
from app.models.user import User  # noqa: E402


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_session] = override_get_db

_current_user: Dict[str, User] = {}


def override_current_user():
    user = _current_user.get("user")
    if user is None:
        raise RuntimeError("Test user not configured")
    return user


app.dependency_overrides[get_current_user] = override_current_user

client = TestClient(app)


def reset_database():
    with TestingSessionLocal() as session:
        session.query(Bookmark).delete()
        session.query(Question).delete()
        session.query(Subject).delete()
        session.query(User).delete()
        session.commit()


def seed_user_and_question():
    with TestingSessionLocal() as session:
        user = User(email="bookmark@example.com", hashed_password="hashed", role="user")
        session.add(user)
        session.commit()
        session.refresh(user)

        subject = Subject(
            name="General Knowledge",
            slug="general-knowledge",
            description="General awareness",
            icon="🌍",
        )
        session.add(subject)
        session.commit()
        session.refresh(subject)

        question = Question(
            prompt="Who is the current president?",
            explanation="The president of Nepal is Ram Chandra Poudel.",
            subject_label="Civics",
            difficulty="Medium",
            is_active=True,
            subject_id=subject.id,
        )
        session.add(question)
        session.commit()
        session.refresh(question)

        _current_user["user"] = user
        return user, subject, question


def test_bookmark_lifecycle():
    reset_database()
    user, subject, question = seed_user_and_question()

    response = client.post("/api/bookmarks", json={"question_id": question.id})
    assert response.status_code == 201
    payload = response.json()
    assert payload["question_id"] == question.id
    assert payload["subject_name"] == subject.name

    ids_response = client.get("/api/bookmarks/ids")
    assert ids_response.status_code == 200
    assert ids_response.json() == [question.id]

    list_response = client.get("/api/bookmarks")
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1
    assert items[0]["prompt"] == question.prompt

    delete_response = client.delete(f"/api/bookmarks/{question.id}")
    assert delete_response.status_code == 204

    assert client.get("/api/bookmarks").json() == []
    assert client.get("/api/bookmarks/ids").json() == []


def test_duplicate_bookmark_is_idempotent():
    reset_database()
    _, subject, question = seed_user_and_question()

    first_response = client.post("/api/bookmarks", json={"question_id": question.id})
    assert first_response.status_code == 201
    first_created = first_response.json()

    second_response = client.post("/api/bookmarks", json={"question_id": question.id})
    assert second_response.status_code == 201
    second_created = second_response.json()

    assert first_created["id"] == second_created["id"]
    assert second_created["subject_name"] == subject.name


def test_bookmark_requires_question_exists():
    reset_database()
    user, *_ = seed_user_and_question()

    response = client.post("/api/bookmarks", json={"question_id": 999})
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"
