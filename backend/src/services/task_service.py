"""
Task service layer to handle business logic and data operations for tasks.
"""

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..models.task import Task


class TaskService:
    """
    Service class for handling task-related business logic and database operations.
    """

    @staticmethod
    def get_user_tasks(session: Session, user_id: str) -> List[Task]:
        """
        Get all tasks for a specific user.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of tasks belonging to the user (excluding soft-deleted ones)
        """
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.deleted_at == None)
        ).all()
        return tasks

    @staticmethod
    def get_task_by_id(session: Session, task_id: str, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID for a specific user.

        Args:
            session: Database session
            task_id: ID of the task to retrieve
            user_id: ID of the user who owns the task

        Returns:
            Task if found and belongs to user and is not deleted, None otherwise
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.deleted_at == None)
        ).first()
        return task

    @staticmethod
    def create_task(session: Session, title: str, description: Optional[str], user_id: str) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            title: Task title
            description: Task description (optional)
            user_id: ID of the user creating the task

        Returns:
            Created task
        """
        task = Task(
            title=title,
            description=description,
            user_id=user_id
        )

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def update_task(
        session: Session,
        task_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None
    ) -> Optional[Task]:
        """
        Update an existing task for a user.

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: ID of the user who owns the task
            title: New title (optional)
            description: New description (optional)
            is_completed: New completion status (optional)

        Returns:
            Updated task if successful, None if task not found or deleted
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.deleted_at == None)
        ).first()

        if not task:
            return None

        # Update fields if provided
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if is_completed is not None:
            task.is_completed = is_completed
            if is_completed and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif not is_completed:
                task.completed_at = None

        # Update the updated_at timestamp
        task.updated_at = datetime.utcnow()

        # Commit changes to database
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(session: Session, task_id: str, user_id: str) -> bool:
        """
        Soft delete a task for a user by marking it as deleted.

        Args:
            session: Database session
            task_id: ID of the task to delete
            user_id: ID of the user who owns the task

        Returns:
            True if task was marked as deleted, False if task not found
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.deleted_at == None)
        ).first()

        if not task:
            return False

        # Mark the task as deleted (soft delete)
        task.deleted_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        # Commit changes to database
        session.add(task)
        session.commit()
        session.refresh(task)

        return True

    @staticmethod
    def toggle_task_completion(session: Session, task_id: str, user_id: str) -> Optional[Task]:
        """
        Toggle the completion status of a task for a user.

        Args:
            session: Database session
            task_id: ID of the task to toggle
            user_id: ID of the user who owns the task

        Returns:
            Updated task if successful, None if task not found or deleted
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.deleted_at == None)
        ).first()

        if not task:
            return None

        # Toggle the completion status
        task.is_completed = not task.is_completed

        # Update completion timestamp based on new status
        if task.is_completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

        task.updated_at = datetime.utcnow()

        # Commit changes to database
        session.add(task)
        session.commit()
        session.refresh(task)

        return task