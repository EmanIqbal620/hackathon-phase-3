from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Dict, Optional, Any

from ..config import config

def encode_token(payload: Dict[str, Any]) -> str:
    """
    Encode a JWT token with the given payload.

    Args:
        payload: Dictionary containing the data to encode in the token

    Returns:
        Encoded JWT token as string
    """
    to_encode = payload.copy()

    # Set expiration time
    expire = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire.timestamp()})

    # Encode the token
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and return the payload.

    Args:
        token: JWT token to decode

    Returns:
        Dictionary containing the decoded token payload

    Raises:
        JWTError: If token is invalid or cannot be decoded
    """
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])

def validate_token_expiration(token: str) -> bool:
    """
    Validate if the JWT token has expired.

    Args:
        token: JWT token to validate

    Returns:
        True if token is valid and not expired, False otherwise
    """
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get("exp")

        if exp_timestamp is None:
            return False

        expiration_time = datetime.fromtimestamp(exp_timestamp)
        current_time = datetime.utcnow()

        return current_time < expiration_time
    except JWTError:
        return False

def is_token_valid(token: str) -> bool:
    """
    Check if a JWT token is valid (properly formatted and not expired).

    Args:
        token: JWT token to validate

    Returns:
        True if token is valid, False otherwise
    """
    try:
        # First decode the token
        payload = decode_token(token)

        # Check if it has required fields
        if "sub" not in payload or "email" not in payload:
            return False

        # Check expiration
        return validate_token_expiration(token)
    except JWTError:
        return False

def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract the user ID from a JWT token.

    Args:
        token: JWT token to extract user ID from

    Returns:
        User ID as string if found and token is valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Check expiration directly from payload to avoid double-decoding
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            return None

        expiration_time = datetime.fromtimestamp(exp_timestamp)
        current_time = datetime.utcnow()

        if current_time >= expiration_time:
            return None

        return payload.get("sub")
    except JWTError:
        return None