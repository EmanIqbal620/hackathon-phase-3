from typing import Dict, Any, Optional, List
from sqlmodel import Session, select
from ..models.task import Task
from ..models.conversation import Conversation, Message
from ..database import sync_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MCPTaskTools:
    """MCP tools for task operations using the official MCP SDK pattern."""

    def __init__(self):
        self.engine = sync_engine

    def add_task(self, user_id: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Add a new task using MCP tool pattern."""
        try:
            with Session(self.engine) as session:
                task = Task(
                    title=title,
                    description=description,
                    user_id=user_id,
                    is_completed=False
                )
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP tool: Added task {task.id} for user {user_id}")
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.is_completed,
                        "created_at": task.created_at.isoformat()
                    }
                }
        except Exception as e:
            logger.error(f"MCP tool error adding task for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_tasks(self, user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
        """List tasks for a user using MCP tool pattern."""
        try:
            with Session(self.engine) as session:
                query = select(Task).where(Task.user_id == user_id)

                if status:
                    if status.lower() == "completed":
                        query = query.where(Task.is_completed == True)
                    elif status.lower() == "pending":
                        query = query.where(Task.is_completed == False)

                tasks = session.exec(query).all()

                logger.info(f"MCP tool: Listed {len(tasks)} tasks for user {user_id}")
                return {
                    "success": True,
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "completed": task.is_completed,
                            "created_at": task.created_at.isoformat()
                        }
                        for task in tasks
                    ]
                }
        except Exception as e:
            logger.error(f"MCP tool error listing tasks for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """Complete a task using MCP tool pattern."""
        try:
            with Session(self.engine) as session:
                task = session.get(Task, task_id)

                if not task or task.user_id != user_id:
                    return {
                        "success": False,
                        "error": "Task not found or does not belong to user"
                    }

                task.is_completed = True
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP tool: Completed task {task_id} for user {user_id}")
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "completed": task.is_completed
                    }
                }
        except Exception as e:
            logger.error(f"MCP tool error completing task {task_id} for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """Delete a task using MCP tool pattern."""
        try:
            with Session(self.engine) as session:
                task = session.get(Task, task_id)

                if not task or task.user_id != user_id:
                    return {
                        "success": False,
                        "error": "Task not found or does not belong to user"
                    }

                session.delete(task)
                session.commit()

                logger.info(f"MCP tool: Deleted task {task_id} for user {user_id}")
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "completed": task.is_completed
                    },
                    "message": f"Task {task_id} deleted successfully"
                }
        except Exception as e:
            logger.error(f"MCP tool error deleting task {task_id} for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def update_task(self, user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update a task using MCP tool pattern."""
        try:
            with Session(self.engine) as session:
                task = session.get(Task, task_id)

                if not task or task.user_id != user_id:
                    return {
                        "success": False,
                        "error": "Task not found or does not belong to user"
                    }

                if title is not None:
                    task.title = title
                if description is not None:
                    task.description = description

                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP tool: Updated task {task_id} for user {user_id}")
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.is_completed
                    }
                }
        except Exception as e:
            logger.error(f"MCP tool error updating task {task_id} for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance for use in the API
mcp_tools = MCPTaskTools()