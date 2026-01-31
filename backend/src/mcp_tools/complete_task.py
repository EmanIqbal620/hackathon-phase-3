"""
MCP Tool for completing tasks
This tool allows the AI agent to mark tasks as completed for users.
"""
from pydantic import BaseModel, Field
from typing import List
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from ..models import Task
from ...database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteTaskParams(BaseModel):
    """Parameters for the complete_task MCP tool"""
    task_id: str = Field(..., description="ID of the task to complete")
    user_id: str = Field(..., description="ID of the user completing the task")


def complete_task(params: CompleteTaskParams) -> List[TextContent]:
    """MCP tool to mark a task as completed for a user"""
    logger.info(f"Completing task {params.task_id} for user {params.user_id}")

    try:
        with Session(sync_engine) as session:
            # Find the task
            statement = select(Task).where(
                Task.id == params.task_id,
                Task.user_id == params.user_id
            )
            task = session.exec(statement).first()

            if not task:
                error_response = {
                    "success": False,
                    "message": f"Task {params.task_id} not found or does not belong to user {params.user_id}"
                }
                return [TextContent(type="text", text=str(error_response))]

            # Update the task to completed
            task.completed = True

            # Commit the changes
            session.add(task)
            session.commit()
            session.refresh(task)

            # Prepare success response
            response = {
                "success": True,
                "message": f"Task '{task.title}' marked as completed",
                "task_details": {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "updated_at": task.updated_at.isoformat()
                }
            }

            logger.info(f"Task {task.id} marked as completed")
            return [TextContent(type="text", text=str(response))]

    except Exception as e:
        logger.error(f"Error completing task: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to complete task: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


# Mock function for testing purposes
def mock_complete_task(params: CompleteTaskParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Completing task {params.task_id} for user {params.user_id}")

    # In a real implementation, this would connect to the database
    # For now, we return a mock response
    response = {
        "success": True,
        "message": f"Task '{params.task_id}' marked as completed",
        "task_details": {
            "id": params.task_id,
            "title": "Sample Task Title",
            "completed": True,
            "updated_at": "2026-01-23T00:00:00Z"
        }
    }

    return [TextContent(type="text", text=str(response))]