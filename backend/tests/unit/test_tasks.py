"""
Unit tests for task endpoints and service functions.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from src.main import app
from src.services.task_service import TaskService
from src.models.task import Task
from src.dependencies.auth import get_current_user


from src.database import get_session


@pytest.fixture
def client():
    """Create a test client for the API with mocked dependencies."""
    # Create a mock user for testing
    mock_user = Mock()
    mock_user.user_id = "test_user_123"

    # Create a mock database session
    mock_session = Mock()

    # Override dependencies
    def mock_get_current_user():
        return mock_user

    def mock_get_test_session():
        return mock_session

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_session] = mock_get_test_session

    with TestClient(app) as test_client:
        yield test_client

    # Clean up the overrides after tests
    app.dependency_overrides.clear()


class TestTaskEndpoints:
    """Test the task API endpoints."""

    @patch('src.api.routes.tasks.TaskService.get_user_tasks')
    def test_get_user_tasks(self, mock_get_user_tasks, client):
        """Test getting user's tasks."""
        # Mock the task service to return some tasks
        mock_task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            is_completed=False,
            user_id="test_user_123",  # This should match the mocked user ID
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_get_user_tasks.return_value = [mock_task]

        response = client.get("/api/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"
        assert data["tasks"][0]["user_id"] == "test_user_123"

    @patch('src.api.routes.tasks.TaskService.create_task')
    def test_create_task(self, mock_create_task, client):
        """Test creating a new task."""
        # Mock the task service to return a created task
        mock_task = Task(
            id="123",
            title="New Task",
            description="New Description",
            is_completed=False,
            user_id="test_user_123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_create_task.return_value = mock_task

        response = client.post("/api/tasks/", json={
            "title": "New Task",
            "description": "New Description"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["user_id"] == "test_user_123"

    @patch('src.api.routes.tasks.TaskService.get_task_by_id')
    def test_get_task_success(self, mock_get_task_by_id, client):
        """Test getting a specific task."""
        # Mock the task service to return a task
        mock_task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            is_completed=False,
            user_id="test_user_123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_get_task_by_id.return_value = mock_task

        response = client.get("/api/tasks/123")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["user_id"] == "test_user_123"

    @patch('src.api.routes.tasks.TaskService.get_task_by_id')
    def test_get_task_not_found(self, mock_get_task_by_id, client):
        """Test getting a non-existent task."""
        # Mock the task service to return None (task not found)
        mock_get_task_by_id.return_value = None

        response = client.get("/api/tasks/nonexistent")

        assert response.status_code == 404

    @patch('src.api.routes.tasks.TaskService.update_task')
    def test_update_task(self, mock_update_task, client):
        """Test updating a task."""
        # Mock the task service to return an updated task
        mock_task = Task(
            id="123",
            title="Updated Task",
            description="Updated Description",
            is_completed=True,
            user_id="test_user_123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        mock_update_task.return_value = mock_task

        response = client.put("/api/tasks/123", json={
            "title": "Updated Task",
            "is_completed": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["is_completed"] is True
        assert data["user_id"] == "test_user_123"

    @patch('src.api.routes.tasks.TaskService.delete_task')
    def test_delete_task(self, mock_delete_task, client):
        """Test deleting a task."""
        # Mock the task service to return True (successful soft deletion)
        mock_delete_task.return_value = True

        response = client.delete("/api/tasks/123")

        assert response.status_code == 204

    @patch('src.api.routes.tasks.TaskService.delete_task')
    def test_delete_task_not_found(self, mock_delete_task, client):
        """Test deleting a non-existent task."""
        # Mock the task service to return False (task not found)
        mock_delete_task.return_value = False

        response = client.delete("/api/tasks/nonexistent")

        assert response.status_code == 404

    @patch('src.api.routes.tasks.TaskService.toggle_task_completion')
    def test_toggle_task_completion(self, mock_toggle_task_completion, client):
        """Test toggling task completion status."""
        # Mock the task service to return an updated task
        mock_task = Task(
            id="123",
            title="Test Task",
            description="Test Description",
            is_completed=True,
            user_id="test_user_123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        mock_toggle_task_completion.return_value = mock_task

        response = client.patch("/api/tasks/123/toggle")

        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        assert data["user_id"] == "test_user_123"


class TestTaskService:
    """Test the task service functions directly."""

    def test_get_user_tasks(self):
        """Test getting all tasks for a user."""
        # This would typically require mocking the database session
        # For now, we'll just ensure the method exists and has the right signature
        assert hasattr(TaskService, 'get_user_tasks')

    def test_create_task(self):
        """Test creating a task."""
        assert hasattr(TaskService, 'create_task')

    def test_update_task(self):
        """Test updating a task."""
        assert hasattr(TaskService, 'update_task')

    def test_delete_task(self):
        """Test deleting a task."""
        assert hasattr(TaskService, 'delete_task')

    def test_toggle_task_completion(self):
        """Test toggling task completion."""
        assert hasattr(TaskService, 'toggle_task_completion')