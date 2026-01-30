from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Task(SQLModel, table=True):
    """
    Task model representing a todo item in the system.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)
    user_id: str = Field(nullable=False)  # Foreign key to User
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)  # For soft delete capability