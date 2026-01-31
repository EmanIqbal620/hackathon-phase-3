from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from functools import wraps

# Get JWT configuration from environment
SECRET_KEY = os.getenv("JWT_SECRET", "eman_MyVeryStrongJwtSecret_123456779!@")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


class User(BaseModel):
    id: str
    username: str
    email: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify JWT token and extract user information

    Args:
        token: The JWT token to verify

    Returns:
        TokenData containing user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Get current user from JWT token in Authorization header

    Args:
        credentials: HTTP authorization credentials

    Returns:
        TokenData containing user information
    """
    token = credentials.credentials
    return verify_token(token)


def validate_user_access(current_user: TokenData, requested_user_id: str) -> bool:
    """
    Validate that the current user has access to the requested user's data

    Args:
        current_user: TokenData for the current user
        requested_user_id: ID of the user whose data is being requested

    Returns:
        True if user has access, raises HTTPException otherwise
    """
    if current_user.user_id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions"
        )
    return True


# Example usage as a decorator
def require_user_match(requested_user_id_param: str):
    """
    Decorator to ensure the authenticated user matches the requested user ID

    Args:
        requested_user_id_param: Name of the parameter containing the requested user ID
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user') or args[0]  # Assuming current_user is first param
            requested_user_id = kwargs.get(requested_user_id_param)

            if not requested_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing {requested_user_id_param} parameter"
                )

            validate_user_access(current_user, requested_user_id)
            return await func(*args, **kwargs)
        return wrapper
    return decorator