"""
MCP Tool for deleting tasks
This tool allows the AI agent to delete tasks for users.
"""
from pydantic import BaseModel, Field
from typing import List
from mcp.types import TextContent
import logging
from sqlmodel import Session, select, delete
from ..models import Task
from ...database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeleteTaskParams(BaseModel):
    """Parameters for the delete_task MCP tool"""
    task_id: str = Field(..., description="ID of the task to delete")
    user_id: str = Field(..., description="ID of the user deleting the task")


def delete_task(params: DeleteTaskParams) -> List[TextContent]:
    """MCP tool to delete a task for a user"""
    logger.info(f"Deleting task {params.task_id} for user {params.user_id}")

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

            # Delete the task
            session.delete(task)
            session.commit()

            # Prepare success response
            response = {
                "success": True,
                "message": f"Task '{task.title}' deleted successfully"
            }

            logger.info(f"Task {task.id} deleted successfully")
            return [TextContent(type="text", text=str(response))]

    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to delete task: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


# Mock function for testing purposes
def mock_delete_task(params: DeleteTaskParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Deleting task {params.task_id} for user {params.user_id}")

    # In a real implementation, this would connect to the database
    # For now, we return a mock response
    response = {
        "success": True,
        "message": f"Task '{params.task_id}' deleted successfully"
    }

    return [TextContent(type="text", text=str(response))]