"""
Integration tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.database import get_session
from src.models.user import User


@pytest.fixture
def client():
    """Create a test client for the app."""
    with TestClient(app) as c:
        yield c


def test_full_auth_flow(client):
    """Test the complete authentication flow: register, login, use token, logout."""

    # Step 1: Register a new user
    register_response = client.post("/api/auth/register", json={
        "email": "integration@test.com",
        "password": "securePassword123",
        "name": "Integration Test"
    })

    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["email"] == "integration@test.com"
    assert register_data["name"] == "Integration Test"

    # Step 2: Login with the registered user
    login_response = client.post("/api/auth/login", json={
        "email": "integration@test.com",
        "password": "securePassword123"
    })

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "Bearer"
    assert "refresh_token" in login_data  # New functionality we added
    assert login_data["user"]["email"] == "integration@test.com"

    # Step 3: Use the token to access a protected endpoint
    access_token = login_data["access_token"]
    profile_response = client.get("/api/user/profile", headers={
        "Authorization": f"Bearer {access_token}"
    })

    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["email"] == "integration@test.com"

    # Step 4: Test token refresh functionality
    refresh_token = login_data["refresh_token"]
    refresh_response = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })

    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert refresh_data["token_type"] == "Bearer"
    assert refresh_data["access_token"] != access_token  # Should be a new token

    print("✅ Full authentication flow test passed!")