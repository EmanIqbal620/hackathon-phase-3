"""
Basic tests for task endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from src.main import app
from src.database import get_session
from src.models.user import User
from src.models.task import Task

# Override the database session dependency for tests
@pytest.fixture(scope="module")
def client():
    def get_test_session_override():
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_and_get_tasks(client):
    """Test creating and getting tasks"""
    # First register a user
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "task_test@example.com",
            "password": "password123",
            "name": "Task Test User"
        }
    )
    assert register_response.status_code == 201

    # Login to get a token
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "task_test@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a task
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    task_data = create_response.json()
    assert task_data["title"] == "Test Task"
    assert task_data["description"] == "This is a test task"
    assert task_data["is_completed"] is False

    # Get the task
    get_response = client.get(
        f"/api/tasks/{task_data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["id"] == task_data["id"]
    assert retrieved_task["title"] == "Test Task"


def test_get_all_tasks(client):
    """Test getting all tasks for a user"""
    # Login as the same user
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "task_test@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create another task
    client.post(
        "/api/tasks/",
        json={
            "title": "Second Test Task",
            "description": "Another test task"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Get all tasks
    get_all_response = client.get(
        "/api/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_all_response.status_code == 200
    tasks_data = get_all_response.json()
    assert len(tasks_data["tasks"]) >= 2  # Should have at least 2 tasks now


def test_update_task(client):
    """Test updating a task"""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "task_test@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a task first
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Original Task",
            "description": "Original description"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Update the task
    update_response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "is_completed": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Task"
    assert updated_task["is_completed"] is True


def test_complete_task(client):
    """Test completing a task"""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "task_test@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a task
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Task to Complete",
            "description": "Task for completion test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Complete the task
    complete_response = client.patch(
        f"/api/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert complete_response.status_code == 200
    completed_task = complete_response.json()
    assert completed_task["is_completed"] is True


def test_delete_task(client):
    """Test deleting a task"""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "task_test@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a task
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Task to Delete",
            "description": "Task for deletion test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Delete the task
    delete_response = client.delete(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204

    # Verify the task is gone
    get_response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])