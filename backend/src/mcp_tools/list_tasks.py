"""
MCP Tool for listing tasks
This tool allows the AI agent to retrieve tasks for a user.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from ..models import Task
from ...database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ListTasksParams(BaseModel):
    """Parameters for the list_tasks MCP tool"""
    user_id: str = Field(..., description="ID of the user whose tasks to list")
    status_filter: Optional[str] = Field("all", description="Filter for task status: 'all', 'pending', 'completed'")


def list_tasks(params: ListTasksParams) -> List[TextContent]:
    """MCP tool to list tasks for a user"""
    logger.info(f"Listing tasks for user {params.user_id}, filter: {params.status_filter}")

    try:
        with Session(sync_engine) as session:
            # Build query based on status filter
            query = select(Task).where(Task.user_id == params.user_id)

            if params.status_filter == "pending":
                query = query.where(Task.completed == False)
            elif params.status_filter == "completed":
                query = query.where(Task.completed == True)

            # Execute query
            tasks = session.exec(query).all()

            # Prepare response
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                task_list.append(task_dict)

            response = {
                "success": True,
                "task_count": len(task_list),
                "tasks": task_list,
                "message": f"Found {len(task_list)} tasks for user",
                "filter_applied": params.status_filter
            }

            logger.info(f"Retrieved {len(task_list)} tasks for user {params.user_id}")
            return [TextContent(type="text", text=str(response))]

    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to list tasks: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


# Mock function for testing purposes
def mock_list_tasks(params: ListTasksParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Listing tasks for user {params.user_id}, filter: {params.status_filter}")

    # In a real implementation, this would fetch from the database
    # For now, we return mock tasks
    mock_tasks = [
        {
            "id": "mock-task-1",
            "title": "Buy groceries",
            "description": "Get milk, bread, and eggs",
            "completed": False,
            "created_at": "2026-01-23T00:00:00Z",
            "updated_at": None
        },
        {
            "id": "mock-task-2",
            "title": "Call mom",
            "description": "Catch up with mom about weekend plans",
            "completed": False,
            "created_at": "2026-01-23T00:00:00Z",
            "updated_at": None
        }
    ]

    # Apply filter if needed
    if params.status_filter == "completed":
        mock_tasks = [t for t in mock_tasks if t["completed"]]
    elif params.status_filter == "pending":
        mock_tasks = [t for t in mock_tasks if not t["completed"]]

    response = {
        "success": True,
        "task_count": len(mock_tasks),
        "tasks": mock_tasks,
        "message": f"Found {len(mock_tasks)} tasks for user",
        "filter_applied": params.status_filter
    }

    return [TextContent(type="text", text=str(response))]