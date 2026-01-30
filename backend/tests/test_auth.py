"""
Basic tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from unittest.mock import patch
from src.main import app
from src.database import get_session
from src.models.user import User

# Create an in-memory SQLite database for testing
def get_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

# Override the database session dependency for tests
@pytest.fixture(scope="module")
def client():
    def get_test_session_override():
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_endpoint(client):
    """Test the registration endpoint"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert data["email"] == "test@example.com"


def test_login_endpoint(client):
    """Test the login endpoint"""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "email": "login_test@example.com",
            "password": "password123",
            "name": "Login Test User"
        }
    )

    # Then try to log in
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login_test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_duplicate_registration(client):
    """Test registering with an already existing email"""
    # Register a user first
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate_test@example.com",
            "password": "password123",
            "name": "Duplicate Test User"
        }
    )

    # Try to register again with the same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate_test@example.com",
            "password": "password123",
            "name": "Duplicate Test User 2"
        }
    )
    assert response.status_code == 409


def test_get_user_profile(client):
    """Test getting user profile (requires authentication)"""
    # Register a user first
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "profile_test@example.com",
            "password": "password123",
            "name": "Profile Test User"
        }
    )
    user_id = register_response.json()["user_id"]

    # Login to get a token
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "profile_test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]

    # Get profile with valid token
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["email"] == "profile_test@example.com"


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])