from .base import BaseMCPTaskTool, ToolCallResponse
from sqlmodel import Session, select
from ..models.task import Task
from ..database import get_session
from typing import Dict, Any
from pydantic import BaseModel
from contextlib import contextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddTaskTool(BaseMCPTaskTool):
    """
    MCP tool to add a new task for a user
    """
    
    @property
    def name(self) -> str:
        return "add_task"
    
    @property
    def description(self) -> str:
        return "Creates a new task for the user"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the task"},
                "description": {"type": "string", "description": "Optional description of the task"}
            },
            "required": ["title"]
        }
    
    @contextmanager
    def get_db_session(self):
        """Context manager to get database session"""
        session_gen = get_session()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()
    
    async def execute(self, user_id: str, **kwargs) -> ToolCallResponse:
        """
        Execute the add_task operation

        Args:
            user_id: The ID of the user adding the task
            **kwargs: Contains 'title' and optional 'description'

        Returns:
            ToolCallResponse containing the result of the operation
        """
        try:
            title = kwargs.get("title")
            description = kwargs.get("description", "")

            if not title:
                return ToolCallResponse(
                    success=False,
                    error="Title is required to create a task",
                    status="error"
                )

            # Validate input length
            if len(title.strip()) < 1:
                return ToolCallResponse(
                    success=False,
                    error="Task title must be at least 1 character long",
                    status="error"
                )

            if len(title) > 200:
                return ToolCallResponse(
                    success=False,
                    error="Task title must be no more than 200 characters",
                    status="error"
                )

            if len(description) > 1000:
                return ToolCallResponse(
                    success=False,
                    error="Task description must be no more than 1000 characters",
                    status="error"
                )

            with self.get_db_session() as session:
                # Create new task
                task = Task(
                    title=title.strip(),
                    description=description,
                    user_id=user_id
                )

                session.add(task)
                session.commit()
                session.refresh(task)

                return ToolCallResponse(
                    success=True,
                    result={
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed
                    },
                    status="success"
                )

        except Exception as e:
            logger.error(f"Error in add_task: {str(e)}")
            return ToolCallResponse(
                success=False,
                error=f"An error occurred while adding the task: {str(e)}",
                status="error"
            )


class ListTasksTool(BaseMCPTaskTool):
    """
    MCP tool to list tasks for a user
    """
    
    @property
    def name(self) -> str:
        return "list_tasks"
    
    @property
    def description(self) -> str:
        return "Lists tasks for the user, optionally filtered by status"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "default": "all",
                    "description": "Filter tasks by status: 'all', 'pending', or 'completed'"
                }
            },
            "required": []
        }
    
    @contextmanager
    def get_db_session(self):
        """Context manager to get database session"""
        session_gen = get_session()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()
    
    async def execute(self, user_id: str, **kwargs) -> ToolCallResponse:
        """
        Execute the list_tasks operation

        Args:
            user_id: The ID of the user listing tasks
            **kwargs: Contains optional 'status' filter

        Returns:
            ToolCallResponse containing the result of the operation
        """
        try:
            status_filter = kwargs.get("status", "all")

            # Validate status filter
            valid_filters = ["all", "pending", "completed"]
            if status_filter not in valid_filters:
                return ToolCallResponse(
                    success=False,
                    error=f"Invalid status filter '{status_filter}'. Valid options are: {', '.join(valid_filters)}",
                    status="error"
                )

            with self.get_db_session() as session:
                # Build query based on status filter
                query = select(Task).where(Task.user_id == user_id)

                if status_filter == "pending":
                    query = query.where(Task.completed == False)
                elif status_filter == "completed":
                    query = query.where(Task.completed == True)

                tasks = session.exec(query).all()

                task_list = [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "updated_at": task.updated_at.isoformat() if task.updated_at else None
                    }
                    for task in tasks
                ]

                return ToolCallResponse(
                    success=True,
                    result={
                        "tasks": task_list,
                        "count": len(task_list)
                    },
                    status="success"
                )

        except Exception as e:
            logger.error(f"Error in list_tasks: {str(e)}")
            return ToolCallResponse(
                success=False,
                error=f"An error occurred while listing tasks: {str(e)}",
                status="error"
            )


class CompleteTaskTool(BaseMCPTaskTool):
    """
    MCP tool to mark a task as completed
    """
    
    @property
    def name(self) -> str:
        return "complete_task"
    
    @property
    def description(self) -> str:
        return "Marks a task as completed"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID of the task to complete"}
            },
            "required": ["task_id"]
        }
    
    @contextmanager
    def get_db_session(self):
        """Context manager to get database session"""
        session_gen = get_session()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()
    
    async def execute(self, user_id: str, **kwargs) -> ToolCallResponse:
        """
        Execute the complete_task operation

        Args:
            user_id: The ID of the user completing the task
            **kwargs: Contains 'task_id' of the task to complete

        Returns:
            ToolCallResponse containing the result of the operation
        """
        try:
            task_id = kwargs.get("task_id")

            if not task_id:
                return ToolCallResponse(
                    success=False,
                    error="Task ID is required to complete a task",
                    status="error"
                )

            # Validate task_id is an integer
            try:
                task_id = int(task_id)
            except (TypeError, ValueError):
                return ToolCallResponse(
                    success=False,
                    error="Task ID must be a valid number",
                    status="error"
                )

            with self.get_db_session() as session:
                # Find the task
                task = session.get(Task, task_id)

                if not task:
                    return ToolCallResponse(
                        success=False,
                        error=f"Task with ID {task_id} not found",
                        status="error"
                    )

                # Verify user owns the task
                if task.user_id != user_id:
                    return ToolCallResponse(
                        success=False,
                        error="Access denied: You can only modify your own tasks",
                        status="error"
                    )

                # Check if task is already completed
                if task.completed:
                    return ToolCallResponse(
                        success=False,
                        error=f"Task with ID {task_id} is already marked as completed",
                        status="error"
                    )

                # Update task as completed
                task.completed = True
                session.add(task)
                session.commit()
                session.refresh(task)

                return ToolCallResponse(
                    success=True,
                    result={
                        "task_id": task.id,
                        "title": task.title,
                        "completed": task.completed
                    },
                    status="success"
                )

        except Exception as e:
            logger.error(f"Error in complete_task: {str(e)}")
            return ToolCallResponse(
                success=False,
                error=f"An error occurred while completing the task: {str(e)}",
                status="error"
            )


class DeleteTaskTool(BaseMCPTaskTool):
    """
    MCP tool to delete a task
    """
    
    @property
    def name(self) -> str:
        return "delete_task"
    
    @property
    def description(self) -> str:
        return "Deletes a task"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID of the task to delete"}
            },
            "required": ["task_id"]
        }
    
    @contextmanager
    def get_db_session(self):
        """Context manager to get database session"""
        session_gen = get_session()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()
    
    async def execute(self, user_id: str, **kwargs) -> ToolCallResponse:
        """
        Execute the delete_task operation

        Args:
            user_id: The ID of the user deleting the task
            **kwargs: Contains 'task_id' of the task to delete

        Returns:
            ToolCallResponse containing the result of the operation
        """
        try:
            task_id = kwargs.get("task_id")

            if not task_id:
                return ToolCallResponse(
                    success=False,
                    error="Task ID is required to delete a task",
                    status="error"
                )

            # Validate task_id is an integer
            try:
                task_id = int(task_id)
            except (TypeError, ValueError):
                return ToolCallResponse(
                    success=False,
                    error="Task ID must be a valid number",
                    status="error"
                )

            with self.get_db_session() as session:
                # Find the task
                task = session.get(Task, task_id)

                if not task:
                    return ToolCallResponse(
                        success=False,
                        error=f"Task with ID {task_id} not found",
                        status="error"
                    )

                # Verify user owns the task
                if task.user_id != user_id:
                    return ToolCallResponse(
                        success=False,
                        error="Access denied: You can only modify your own tasks",
                        status="error"
                    )

                # Delete the task
                session.delete(task)
                session.commit()

                return ToolCallResponse(
                    success=True,
                    result={
                        "task_id": task_id,
                        "message": "Task deleted successfully"
                    },
                    status="success"
                )

        except Exception as e:
            logger.error(f"Error in delete_task: {str(e)}")
            return ToolCallResponse(
                success=False,
                error=f"An error occurred while deleting the task: {str(e)}",
                status="error"
            )


class UpdateTaskTool(BaseMCPTaskTool):
    """
    MCP tool to update a task
    """
    
    @property
    def name(self) -> str:
        return "update_task"
    
    @property
    def description(self) -> str:
        return "Updates a task's title or description"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID of the task to update"},
                "title": {"type": "string", "description": "New title for the task (optional)"},
                "description": {"type": "string", "description": "New description for the task (optional)"}
            },
            "required": ["task_id"]
        }
    
    @contextmanager
    def get_db_session(self):
        """Context manager to get database session"""
        session_gen = get_session()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()
    
    async def execute(self, user_id: str, **kwargs) -> ToolCallResponse:
        """
        Execute the update_task operation

        Args:
            user_id: The ID of the user updating the task
            **kwargs: Contains 'task_id' and optional 'title'/'description' to update

        Returns:
            ToolCallResponse containing the result of the operation
        """
        try:
            task_id = kwargs.get("task_id")
            title = kwargs.get("title")
            description = kwargs.get("description")

            if not task_id:
                return ToolCallResponse(
                    success=False,
                    error="Task ID is required to update a task",
                    status="error"
                )

            # Validate task_id is an integer
            try:
                task_id = int(task_id)
            except (TypeError, ValueError):
                return ToolCallResponse(
                    success=False,
                    error="Task ID must be a valid number",
                    status="error"
                )

            # At least one field to update must be provided
            if title is None and description is None:
                return ToolCallResponse(
                    success=False,
                    error="At least one field (title or description) must be provided to update",
                    status="error"
                )

            # Validate input lengths if provided
            if title is not None:
                if len(title.strip()) < 1:
                    return ToolCallResponse(
                        success=False,
                        error="Task title must be at least 1 character long",
                        status="error"
                    )

                if len(title) > 200:
                    return ToolCallResponse(
                        success=False,
                        error="Task title must be no more than 200 characters",
                        status="error"
                    )

            if description is not None and len(description) > 1000:
                return ToolCallResponse(
                    success=False,
                    error="Task description must be no more than 1000 characters",
                    status="error"
                )

            with self.get_db_session() as session:
                # Find the task
                task = session.get(Task, task_id)

                if not task:
                    return ToolCallResponse(
                        success=False,
                        error=f"Task with ID {task_id} not found",
                        status="error"
                    )

                # Verify user owns the task
                if task.user_id != user_id:
                    return ToolCallResponse(
                        success=False,
                        error="Access denied: You can only modify your own tasks",
                        status="error"
                    )

                # Store original values for response
                original_title = task.title
                original_description = task.description

                # Update task fields if provided
                if title is not None:
                    task.title = title.strip()
                if description is not None:
                    task.description = description

                session.add(task)
                session.commit()
                session.refresh(task)

                return ToolCallResponse(
                    success=True,
                    result={
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "changes": {
                            "title_changed": original_title != task.title,
                            "description_changed": original_description != task.description
                        }
                    },
                    status="success"
                )

        except Exception as e:
            logger.error(f"Error in update_task: {str(e)}")
            return ToolCallResponse(
                success=False,
                error=f"An error occurred while updating the task: {str(e)}",
                status="error"
            )


class ContextAwareMixin:
    """
    Mixin class to add context-aware capabilities to task operations
    """

    async def resolve_task_reference(self, user_id: str, task_identifier: str, session) -> Optional[Task]:
        """
        Resolve a task reference based on context clues

        Args:
            user_id: The ID of the user
            task_identifier: The identifier to resolve (could be ID, partial title, etc.)
            session: Database session

        Returns:
            Task object if found, None otherwise
        """
        # First, try exact ID match
        try:
            task_id = int(task_identifier)
            task = session.get(Task, task_id)
            if task and task.user_id == user_id:
                return task
        except ValueError:
            # Not a numeric ID, continue with other resolution methods
            pass

        # Try to match by title substring
        stmt = select(Task).where(
            Task.user_id == user_id,
            Task.title.contains(task_identifier)
        ).order_by(Task.updated_at.desc())

        tasks = session.exec(stmt).all()
        if tasks:
            # Return the most recently updated matching task
            return tasks[0]

        return None


# Create instances of all tools for registration
add_task_tool = AddTaskTool()
list_tasks_tool = ListTasksTool()
complete_task_tool = CompleteTaskTool()
delete_task_tool = DeleteTaskTool()
update_task_tool = UpdateTaskTool()