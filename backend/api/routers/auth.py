from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv
import os

from models import User, UserCreate, UserRead
from database import sync_engine

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# -----------------------------
# Password hashing context
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# JWT Configuration
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# -----------------------------
# Helper Functions
# -----------------------------
def hash_password(password: str) -> str:
    """Hash a password using bcrypt, truncating to 72 characters if needed"""
    # Truncate password to 72 characters to avoid bcrypt 72-byte limit
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash, truncating to 72 characters if needed"""
    # Truncate password to 72 characters to match bcrypt 72-byte limit
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate a JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -----------------------------
# Pydantic Models
# -----------------------------
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserToken(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

# -----------------------------
# Routes
# -----------------------------
@router.post("/register", response_model=UserToken)
def register(user_data: UserCreate):
    """Register a new user"""
    with Session(sync_engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create the user without the name field initially to avoid schema mismatch issues
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            is_active=True
        )

        # If name is provided, try to set it (but don't fail if column doesn't exist)
        if user_data.name is not None:
            try:
                setattr(user, 'name', user_data.name)
            except AttributeError:
                # Name field not supported by the model/table, ignore
                pass

        session.add(user)
        session.commit()
        session.refresh(user)

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        # Include name in token if available
        if user.name:
            token_data["name"] = user.name

        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }


@router.post("/login", response_model=UserToken)
def login(login_data: LoginRequest):
    """Authenticate user and return access token"""
    with Session(sync_engine) as session:
        # Find user by email
        user = session.exec(select(User).where(User.email == login_data.email)).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        # Include name in token if available
        if user.name:
            token_data["name"] = user.name

        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }


@router.post("/logout")
def logout():
    """Logout user (client-side token removal is sufficient)"""
    return {"message": "Logged out successfully"}
