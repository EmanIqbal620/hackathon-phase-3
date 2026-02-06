#!/usr/bin/env python3
"""Minimal server to test auth routes without other dependencies"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
import uuid

# Import from our existing modules
from src.database import get_session
from src.models.user import User
from src.dependencies.auth import create_access_token, create_refresh_token, get_current_user, TokenData
from src.config import config

# Password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)

# Request/Response Models
class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserRegistrationResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    created_at: str

# Create a minimal app
app = FastAPI()

@app.post("/api/auth/register", response_model=UserRegistrationResponse)
async def register_user(request: UserRegistrationRequest, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

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

    # Return the user information
    return UserRegistrationResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        created_at=str(user.created_at)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)