"""
Suggestion Model
This module defines the SQLModel for storing AI-generated task suggestions for users.
"""
from sqlmodel import SQLModel, Field, Column, DateTime, Boolean, String
from datetime import datetime
from typing import Optional
import uuid


class SuggestionBase(SQLModel):
    """Base class for Suggestion model"""
    user_id: str = Field(..., description="ID of the user this suggestion is for")
    suggested_task_title: str = Field(..., description="Title of the suggested task", max_length=255)
    suggested_task_description: Optional[str] = Field(None, description="Description of the suggested task")
    suggestion_type: str = Field(..., description="Type of suggestion: 'pattern_based', 'priority_based', 'deadline_based', 'contextual'")
    confidence_score: float = Field(..., description="Confidence score between 0 and 1")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the suggestion")


class Suggestion(SuggestionBase, table=True):
    """Suggestion model for database table"""
    __tablename__ = "suggestions"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this suggestion"
    )
    accepted: Optional[bool] = Field(default=None, description="Whether the user accepted this suggestion")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp when this suggestion was created"
    )
    dismissed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp when this suggestion was dismissed"
    )
    converted_to_task_id: Optional[uuid.UUID] = Field(
        default=None,
        description="ID of the task created from this suggestion (if any)"
    )


class SuggestionCreate(SuggestionBase):
    """Schema for creating new suggestion records"""
    pass


class SuggestionRead(SuggestionBase):
    """Schema for reading suggestion records"""
    id: uuid.UUID
    accepted: Optional[bool]
    created_at: datetime
    dismissed_at: Optional[datetime]
    converted_to_task_id: Optional[uuid.UUID]


class SuggestionUpdate(SQLModel):
    """Schema for updating suggestion records"""
    accepted: Optional[bool] = None
    dismissed_at: Optional[datetime] = None
    converted_to_task_id: Optional[uuid.UUID] = None


class SuggestionResponse(SQLModel):
    """Response schema for suggestion operations"""
    success: bool
    message: str
    suggestion_id: Optional[uuid.UUID] = None
    task_created: bool = False
    task_id: Optional[uuid.UUID] = None