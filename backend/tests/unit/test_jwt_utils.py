"""
Unit tests for JWT utilities.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from src.utils.jwt_utils import encode_token, decode_token, validate_token_expiration, is_token_valid, get_user_id_from_token
from src.config import config


def test_encode_decode_token():
    """Test that we can encode and decode a token correctly."""
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "name": "Test User"
    }

    # Encode token
    token = encode_token(payload)

    # Decode token
    decoded_payload = decode_token(token)

    # Assert the payload is correct (without exp since it's added during encoding)
    assert decoded_payload["sub"] == "test-user-id"
    assert decoded_payload["email"] == "test@example.com"
    assert decoded_payload["name"] == "Test User"
    assert "exp" in decoded_payload  # exp should have been added


def test_token_expiration_validation():
    """Test that token expiration validation works correctly."""
    # Create a token that expires in 1 hour
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com"
    }

    token = encode_token(payload)

    # This token should not be expired yet
    assert validate_token_expiration(token) is True


def test_expired_token_validation():
    """Test that expired tokens are detected correctly."""
    # Create an expired token manually
    expired_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "exp": (datetime.utcnow() - timedelta(seconds=1)).timestamp()  # Expired 1 second ago
    }

    expired_token = jwt.encode(expired_payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    # This token should be expired
    assert validate_token_expiration(expired_token) is False


def test_is_token_valid():
    """Test the overall token validity check."""
    # Create a valid token
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com"
    }

    token = encode_token(payload)

    # This token should be valid
    assert is_token_valid(token) is True


def test_invalid_token_not_valid():
    """Test that invalid tokens are correctly identified as not valid."""
    # Create an invalid token (manually with missing required fields)
    invalid_payload = {
        "sub": "test-user-id"
        # Missing email
    }

    token = encode_token(invalid_payload)

    # This token should not be valid (missing required fields)
    assert is_token_valid(token) is False


def test_get_user_id_from_token():
    """Test extracting user ID from a valid token."""
    # Create a token with user data
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com"
    }

    token = encode_token(payload)

    # Extract user ID
    user_id = get_user_id_from_token(token)

    # Assert the user ID is correct
    assert user_id == "test-user-id"


def test_get_user_id_from_expired_token():
    """Test that None is returned for expired tokens."""
    # Create an expired token manually
    expired_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "exp": (datetime.utcnow() - timedelta(seconds=1)).timestamp()  # Expired 1 second ago
    }

    expired_token = jwt.encode(expired_payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    # Extract user ID from expired token should return None
    user_id = get_user_id_from_token(expired_token)

    # Assert the user ID is None
    assert user_id is None