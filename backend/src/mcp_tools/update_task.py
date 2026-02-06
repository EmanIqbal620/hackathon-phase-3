"""
MCP Tool for updating tasks
This tool allows the AI agent to update existing tasks for users.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from ..models.task import Task
from ..database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateTaskParams(BaseModel):
    """Parameters for the update_task MCP tool"""
    task_id: str = Field(..., description="ID of the task to update")
    user_id: str = Field(..., description="ID of the user updating the task")
    title: Optional[str] = Field(None, description="New title for the task")
    description: Optional[str] = Field(None, description="New description for the task")
    completed: Optional[bool] = Field(None, description="New completion status for the task")


def update_task(params: UpdateTaskParams) -> List[TextContent]:
    """MCP tool to update an existing task for a user"""
    logger.info(f"Updating task {params.task_id} for user {params.user_id}")

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

            # Update the task with provided parameters
            if params.title is not None:
                task.title = params.title
            if params.description is not None:
                task.description = params.description
            if params.completed is not None:
                task.is_completed = params.completed

            # Update the updated_at timestamp
            from datetime import datetime
            task.updated_at = datetime.utcnow()

            # Commit the changes
            session.add(task)
            session.commit()
            session.refresh(task)

            # Prepare success response
            response = {
                "success": True,
                "message": f"Task '{task.id}' updated successfully",
                "task_details": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.is_completed,
                    "updated_at": task.updated_at.isoformat()
                }
            }

            logger.info(f"Task {task.id} updated successfully")
            return [TextContent(type="text", text=str(response))]

    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to update task: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


# Mock function for testing purposes
def mock_update_task(params: UpdateTaskParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Updating task {params.task_id} for user {params.user_id}")

    # In a real implementation, this would connect to the database
    # For now, we return a mock response
    response = {
        "success": True,
        "message": f"Task '{params.task_id}' updated successfully",
        "task_details": {
            "id": params.task_id,
            "title": params.title or "Existing Title",
            "description": params.description or "Existing Description",
            "completed": params.completed if params.completed is not None else False,
            "updated_at": "2026-01-23T00:00:00Z"
        }
    }

    return [TextContent(text=str(response))]