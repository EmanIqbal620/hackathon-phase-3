#!/usr/bin/env python3
"""Debug script to test database operations without the full API"""

from sqlmodel import Session, select
from src.database import sync_engine
from src.models.user import User
from src.api.routes.auth import get_password_hash

from src.models import *
from sqlmodel import SQLModel

def test_database():
    print("Testing database operations...")

    # Create tables
    SQLModel.metadata.create_all(sync_engine)
    print("Tables created successfully")

    # Create a session
    with Session(sync_engine) as session:
        print("Session created successfully")

        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == "test@example.com")).first()
        print(f"Existing user check: {existing_user}")

        if not existing_user:
            # Create a new user
            print("Creating new user...")
            password_hash = get_password_hash("testpassword")
            user = User(
                email="test@example.com",
                password_hash=password_hash,
                name="Test User"
            )

            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"User created successfully: {user.id}")
        else:
            print(f"User already exists: {existing_user.id}")

if __name__ == "__main__":
    test_database()