from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db_session
from app.main import app
from app.db.base import Base
from app.db.session import get_db


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

client = TestClient(app)


def test_register_and_login_flow():
    register_response = client.post(
        "/api/auth/register",
        json={"email": "User@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["email"] == "user@example.com"
    assert data["role"] == "user"
    assert "id" in data

    login_response = client.post(
        "/api/auth/login",
        json={"email": "USER@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"]
