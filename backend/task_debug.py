#!/usr/bin/env python3
"""Debug script to test task creation"""

from sqlmodel import Session, select
from src.database import sync_engine
from src.models.user import User
from src.models.task import Task, TaskCreate

def test_task_creation():
    print("Testing task creation...")

    # Create a session
    with Session(sync_engine) as session:
        print("Session created successfully")

        # Find the user we created earlier
        user = session.exec(select(User).where(User.email == "finaltest@example.com")).first()
        if not user:
            print("User not found, creating test user...")
            from src.api.routes.auth import get_password_hash
            user = User(
                email="finaltest@example.com",
                password_hash=get_password_hash("testpassword"),
                name="Final Test"
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        print(f"Using user: {user.id}")

        # Create a task
        print("Creating task...")
        task_data = TaskCreate(
            title="Test Task",
            description="This is a test task",
            user_id=user.id
        )

        task = Task.from_orm(task_data) if hasattr(Task, 'from_orm') else Task(**task_data.dict())
        task.user_id = user.id  # Ensure user_id is set

        session.add(task)
        session.commit()
        session.refresh(task)

        print(f"Task created successfully: {task.id} - {task.title}")

if __name__ == "__main__":
    test_task_creation()