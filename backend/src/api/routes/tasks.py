import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ...dependencies.auth import get_current_user
from ...database import get_session
from ...models.task import Task
from ...models.user import User
from ...exceptions.auth import InsufficientPermissionsException
from ...services.task_service import TaskService

# Set up logging for task operations
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Pydantic models for request/response
from pydantic import BaseModel

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    is_completed: bool
    user_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]


@router.get("/", response_model=TaskListResponse)
def get_user_tasks(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user.
    """
    logger.info(f"User {current_user.user_id} requesting all tasks")

    # Use the task service to get user's tasks
    tasks = TaskService.get_user_tasks(session, current_user.user_id)

    # Convert to response model
    task_responses = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]

    logger.info(f"Returning {len(tasks)} tasks for user {current_user.user_id}")
    return TaskListResponse(tasks=task_responses)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_request: TaskCreateRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    logger.info(f"User {current_user.user_id} creating new task with title: {task_request.title}")

    # Use the task service to create the task
    task = TaskService.create_task(
        session,
        task_request.title,
        task_request.description,
        current_user.user_id
    )

    logger.info(f"Task {task.id} created successfully for user {current_user.user_id}")
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID for the authenticated user.
    """
    logger.info(f"User {current_user.user_id} requesting task {task_id}")

    # Use the task service to get the task
    task = TaskService.get_task_by_id(session, task_id, current_user.user_id)

    if not task:
        logger.warning(f"Task {task_id} not found for user {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Task {task_id} retrieved successfully for user {current_user.user_id}")
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_request: TaskUpdateRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID for the authenticated user.
    """
    logger.info(f"User {current_user.user_id} updating task {task_id}")

    # Use the task service to update the task
    updated_task = TaskService.update_task(
        session,
        task_id,
        current_user.user_id,
        title=task_request.title,
        description=task_request.description,
        is_completed=task_request.is_completed
    )

    if not updated_task:
        logger.warning(f"Task {task_id} not found for user {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Task {task_id} updated successfully for user {current_user.user_id}")
    return TaskResponse(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description,
        is_completed=updated_task.is_completed,
        user_id=updated_task.user_id,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at,
        completed_at=updated_task.completed_at
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID for the authenticated user.
    """
    logger.info(f"User {current_user.user_id} deleting task {task_id}")

    # Use the task service to delete the task
    deleted = TaskService.delete_task(session, task_id, current_user.user_id)

    if not deleted:
        logger.warning(f"Task {task_id} not found for user {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Task {task_id} deleted successfully for user {current_user.user_id}")
    # Return 204 No Content
    return


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task_completion(
    task_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle a specific task's completion status for the authenticated user.
    """
    logger.info(f"User {current_user.user_id} toggling completion status for task {task_id}")

    # Use the task service to toggle the task completion status
    updated_task = TaskService.toggle_task_completion(session, task_id, current_user.user_id)

    if not updated_task:
        logger.warning(f"Task {task_id} not found for user {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Task {task_id} completion status toggled successfully for user {current_user.user_id}")
    return TaskResponse(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description,
        is_completed=updated_task.is_completed,
        user_id=updated_task.user_id,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at,
        completed_at=updated_task.completed_at
    )