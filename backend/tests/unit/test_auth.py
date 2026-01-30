"""
Unit tests for authentication functionality.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from src.dependencies.auth import verify_token, create_access_token
from src.config import config
from src.models.user import User


def test_create_and_verify_token():
    """Test that we can create a token and verify it correctly."""
    # Create test user data
    user_data = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "name": "Test User"
    }

    # Create token
    token = create_access_token(user_data)

    # Verify token
    token_data = verify_token(token)

    # Assert the token data is correct
    assert token_data.user_id == "test-user-id"
    assert token_data.email == "test@example.com"


def test_token_expiration():
    """Test that expired tokens are properly rejected."""
    # Create an expired token manually for testing
    expired_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "exp": (datetime.utcnow() - timedelta(seconds=1)).timestamp(),  # Expired 1 second ago
        "type": "access"
    }

    expired_token = jwt.encode(expired_payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    # This should raise an exception when verified
    with pytest.raises(Exception):  # Could be HTTPException or JWTError
        verify_token(expired_token)


def test_invalid_token_type():
    """Test that refresh tokens are rejected when access tokens are expected."""
    # Create a refresh token (wrong type)
    refresh_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "exp": (datetime.utcnow() + timedelta(hours=24)).timestamp(),
        "type": "refresh"  # This is the wrong type
    }

    refresh_token = jwt.encode(refresh_payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    # This should raise an exception when verified as access token
    with pytest.raises(Exception):  # Should raise HTTPException for invalid token type
        verify_token(refresh_token)


def test_missing_claims():
    """Test that tokens with missing required claims are rejected."""
    # Create a token with missing required claims
    invalid_payload = {
        "sub": "test-user-id"
        # Missing "email" which is required
    }

    invalid_token = jwt.encode(invalid_payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    # This should raise an exception when verified
    with pytest.raises(Exception):  # Could be HTTPException for missing claims
        verify_token(invalid_token)