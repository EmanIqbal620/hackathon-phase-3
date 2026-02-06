from datetime import timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from typing import Optional
from passlib.context import CryptContext
from sqlmodel import Session, select

from ...dependencies.auth import create_access_token, create_refresh_token, get_current_user, TokenData
from ...exceptions.auth import InvalidCredentialsException, DuplicateUserException
from ...config import config
from ...database import get_session
from ...src.models.user import User

# Set up logging for authentication operations
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Request/Response Models
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserRegistrationResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    created_at: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user: UserRegistrationResponse

class LogoutResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password, truncating to 72 characters if needed."""
    # Truncate password to 72 characters to avoid bcrypt 72-byte limit
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password, truncating to 72 characters if needed."""
    # Truncate password to 72 characters to avoid bcrypt 72-byte limit
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)

@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        409: {"model": ErrorResponse, "description": "Email already exists"}
    }
)
async def register_user(request: UserRegistrationRequest, session: Session = Depends(get_session)):
    """
    Register a new user account.

    Args:
        request: User registration details including email, password, and optional name
        session: Database session dependency

    Returns:
        UserRegistrationResponse with user details

    Raises:
        HTTPException: If email already exists (409) or input is invalid (400)
    """
    logger.info(f"Registration attempt for email: {request.email}")

    # Check if user already exists in the database
    existing_user = session.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        logger.warning(f"Registration failed: Email already exists: {request.email}")
        raise DuplicateUserException(detail="Email already registered")

    # Hash the password
    password_hash = get_password_hash(request.password)

    # Create a new user
    user = User(
        email=request.email,
        password_hash=password_hash,
        name=request.name
    )

    # Add the user to the database
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"User registered successfully: {user.id}")

    # Return the user information
    return UserRegistrationResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        created_at=str(user.created_at)
    )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    }
)
async def login_user(request: UserLoginRequest, session: Session = Depends(get_session)):
    """
    Authenticate user and return JWT token.

    Args:
        request: User login credentials (email and password)
        session: Database session dependency

    Returns:
        UserLoginResponse with access token and user information

    Raises:
        HTTPException: If credentials are invalid (401) or input is invalid (400)
    """
    logger.info(f"Login attempt for email: {request.email}")

    # Query the database for the user
    user = session.exec(select(User).where(User.email == request.email)).first()

    # Check if user exists and password is correct
    if not user or not verify_password(request.password, user.password_hash):
        logger.warning(f"Login failed: Invalid credentials for email: {request.email}")
        raise InvalidCredentialsException()

    # Create access token with user information
    token_data = {
        "sub": user.id,
        "email": user.email,
        "name": user.name
    }
    access_token = create_access_token(token_data)

    # Create refresh token with user information
    refresh_token_value = create_refresh_token(token_data)

    # Calculate expiration time in seconds
    expires_in = int(timedelta(hours=config.JWT_EXPIRATION_HOURS).total_seconds())

    logger.info(f"User logged in successfully: {user.id}")

    # Return token and user information
    return UserLoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=expires_in,
        refresh_token=refresh_token_value,
        user=UserRegistrationResponse(
            user_id=user.id,
            email=user.email,
            name=user.name,
            created_at=str(user.created_at)
        )
    )


# Token refresh request/response models
class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid refresh token"},
        401: {"model": ErrorResponse, "description": "Expired or invalid refresh token"}
    }
)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh an expired access token using a refresh token.

    Args:
        request: Contains the refresh token to use for generating a new access token

    Returns:
        TokenRefreshResponse with new access token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    logger.info(f"Token refresh requested")

    # In a real implementation, we would validate the refresh token against a database
    # For now, we'll just decode the refresh token and create a new access token
    # In a production system, refresh tokens should be stored and validated securely

    # This is a simplified implementation - in a real app, you'd have a proper refresh token system
    try:
        payload = jwt.decode(request.refresh_token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])

        # Check if this is actually a refresh token (would have a specific claim)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )

        # Create a new access token with the user data from the refresh token
        user_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name")
        }

        new_access_token = create_access_token(user_data)
        expires_in = int(timedelta(hours=config.JWT_EXPIRATION_HOURS).total_seconds())

        logger.info(f"Token refreshed successfully for user: {payload.get('sub')}")

        return TokenRefreshResponse(
            access_token=new_access_token,
            token_type="Bearer",
            expires_in=expires_in
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired or invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or missing token"}
    }
)
async def logout_user(current_user: TokenData = Depends(get_current_user)):
    """
    Logout user and invalidate session.

    Args:
        current_user: The currently authenticated user (extracted from JWT)

    Returns:
        LogoutResponse with success message

    Raises:
        HTTPException: If token is invalid or missing (401)
    """
    logger.info(f"Logout initiated for user: {current_user.user_id}")

    # In a real application, this might involve adding the token to a blacklist
    # or storing it in a revoked tokens database
    return LogoutResponse(message="Successfully logged out")