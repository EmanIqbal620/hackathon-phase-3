from sqlmodel import SQLModel, Field, Column, Relationship
from typing import Optional
from datetime import datetime
import uuid

class TaskBase(SQLModel):
    """
    Base class for task models containing common fields.
    """
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    priority: str = Field(default="medium", description="Priority level: 'low', 'medium', 'high'")
    due_date: Optional[datetime] = Field(default=None)
    user_id: str = Field(foreign_key="user.id", nullable=False)  # Foreign key to User


class Task(TaskBase, table=True):
    """
    Task model representing a todo item in the system.
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)  # For soft delete capability

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks", sa_relationship_kwargs={"primaryjoin": "Task.user_id==User.id"})

    # AI and performance-related fields
    ai_suggestion_source: Optional[str] = Field(default=None, description="Indicates if created from AI suggestion")
    estimated_duration_minutes: Optional[int] = Field(default=None, description="Estimated time to complete in minutes")
    actual_duration_minutes: Optional[int] = Field(default=None, description="Actual time taken to complete in minutes")
    category: Optional[str] = Field(default=None, max_length=100, description="Category of the task")
    ai_confidence_score: Optional[float] = Field(default=None, description="AI confidence score for this task (0-1)")
    ai_reasoning: Optional[str] = Field(default=None, description="AI reasoning behind task creation or suggestion")


class TaskCreate(TaskBase):
    """
    Model for creating new tasks.
    """
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None
    ai_suggestion_source: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    category: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    ai_reasoning: Optional[str] = None


class TaskRead(TaskBase):
    """
    Model for reading task data.
    """
    id: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    ai_suggestion_source: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    category: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    ai_reasoning: Optional[str] = None