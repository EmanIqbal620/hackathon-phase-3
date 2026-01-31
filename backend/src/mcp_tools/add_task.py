"""
MCP Tool for adding tasks
This tool allows the AI agent to create new tasks for users.
"""
from pydantic import BaseModel, Field
from typing import List
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from ..models import Task, TaskCreate
from ...database import sync_engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddTaskParams(BaseModel):
    """Parameters for the add_task MCP tool"""
    user_id: str = Field(..., description="ID of the user creating the task")
    title: str = Field(..., description="Title of the task to create")
    description: str = Field("", description="Optional description of the task")


def add_task(params: AddTaskParams) -> List[TextContent]:
    """MCP tool to add a new task for a user"""
    logger.info(f"Adding task for user {params.user_id}: {params.title}")

    try:
        # Create a new task using SQLModel
        with Session(sync_engine) as session:
            # Create the task object
            task_create = TaskCreate(
                title=params.title,
                description=params.description,
                user_id=params.user_id,
                completed=False  # New tasks are not completed by default
            )

            # Create the task instance
            task = Task.model_validate(task_create)

            # Add to the session and commit
            session.add(task)
            session.commit()
            session.refresh(task)  # Refresh to get the generated ID

            # Prepare success response
            response = {
                "success": True,
                "task_id": task.id,
                "message": f"Task '{task.title}' added successfully",
                "task_details": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
            }

            logger.info(f"Task created successfully with ID: {task.id}")
            return [TextContent(type="text", text=str(response))]

    except Exception as e:
        logger.error(f"Error adding task: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to add task: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


# Mock function for testing purposes
def mock_add_task(params: AddTaskParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Adding task for user {params.user_id}: {params.title}")

    # In a real implementation, this would connect to the database
    # For now, we return a mock response
    response = {
        "success": True,
        "task_id": "mock-task-id-123",
        "message": f"Task '{params.title}' added successfully",
        "task_details": {
            "id": "mock-task-id-123",
            "title": params.title,
            "description": params.description,
            "completed": False,
            "created_at": "2026-01-23T00:00:00Z"
        }
    }

    return [TextContent(type="text", text=str(response))]