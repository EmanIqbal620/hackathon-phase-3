from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from ..config import config

security = HTTPBearer()

class TokenData(BaseModel):
    user_id: str
    email: str
    exp: Optional[float] = None

class UserIdentity(BaseModel):
    """Represents the identity of an authenticated user."""
    user_id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

def create_access_token(data: dict) -> str:
    """
    Create a new access token with the given data.

    Args:
        data: Dictionary containing the claims to include in the token

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    # Set expiration time
    expire = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire.timestamp(), "type": "access"})

    # Encode the token
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a new refresh token with the given data.

    Args:
        data: Dictionary containing the claims to include in the token

    Returns:
        Encoded JWT refresh token as string
    """
    to_encode = data.copy()

    # Set refresh token expiration (typically longer than access token)
    refresh_expire_hours = config.JWT_EXPIRATION_HOURS * 24  # 24x longer than access token
    expire = datetime.utcnow() + timedelta(hours=refresh_expire_hours)
    to_encode.update({"exp": expire.timestamp(), "type": "refresh"})

    # Encode the token
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """
    Verify a JWT token and return the decoded data.

    Args:
        token: JWT token to verify

    Returns:
        TokenData object containing the decoded token information

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Decode the token with strict validation
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": False,
                "verify_iat": False,
                "verify_aud": False,
            }
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        token_type: str = payload.get("type")

        # Verify required claims exist
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify this is an access token, not a refresh token
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = TokenData(user_id=user_id, email=email, exp=payload.get("exp"))

        # Additional check if token is expired (double-check with our own validation)
        if token_data.exp and datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data

    except JWTError as e:
        # Log the specific JWT error for debugging (but don't expose details to client)
        print(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def extract_user_identity_from_token(token: str) -> UserIdentity:
    """
    Extract user identity from a JWT token.

    Args:
        token: JWT token to extract user identity from

    Returns:
        UserIdentity object with the user's information
    """
    token_data = verify_token(token)
    return UserIdentity(
        user_id=token_data.user_id,
        email=token_data.email
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get the current user from the JWT token in the request.

    This function extracts the JWT token from the Authorization header,
    verifies it, and returns the user information.

    Args:
        credentials: HTTP authorization credentials from the request header

    Returns:
        TokenData object containing the authenticated user's information
    """
    token = credentials.credentials
    return verify_token(token)

async def get_current_user_identity(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserIdentity:
    """
    Dependency to get the current user identity from the JWT token in the request.

    This function extracts the JWT token from the Authorization header,
    verifies it, and returns a UserIdentity object.

    Args:
        credentials: HTTP authorization credentials from the request header

    Returns:
        UserIdentity object containing the authenticated user's information
    """
    token = credentials.credentials
    return extract_user_identity_from_token(token)