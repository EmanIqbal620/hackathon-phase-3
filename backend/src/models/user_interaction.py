"""
User Interaction Model
This module defines the SQLModel for storing user interactions with the AI system.
"""
from sqlmodel import SQLModel, Field, Column, DateTime, String, JSON
from datetime import datetime
from typing import Optional
import uuid


class UserInteractionBase(SQLModel):
    """Base class for UserInteraction model"""
    user_id: int = Field(..., description="ID of the user performing the interaction")
    interaction_type: str = Field(..., description="Type of interaction: 'chat_message', 'suggestion_response', 'analytics_view', 'task_action'")
    input_content: str = Field(..., description="Content of the user's input")
    output_content: str = Field(..., description="Content of the system's output")
    intent_classification: Optional[str] = Field(None, description="Classified intent of the user's input")
    conversation_context: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="JSON context for the conversation")


class UserInteraction(UserInteractionBase, table=True):
    """UserInteraction model for database table"""
    __tablename__ = "user_interactions"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this user interaction"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp when this interaction occurred"
    )
    ai_processing_time_ms: Optional[int] = Field(
        default=None,
        description="Time in milliseconds it took the AI to process this interaction"
    )


class UserInteractionCreate(UserInteractionBase):
    """Schema for creating new user interaction records"""
    pass


class UserInteractionRead(UserInteractionBase):
    """Schema for reading user interaction records"""
    id: uuid.UUID
    created_at: datetime
    ai_processing_time_ms: Optional[int]


class UserInteractionUpdate(SQLModel):
    """Schema for updating user interaction records"""
    input_content: Optional[str] = None
    output_content: Optional[str] = None
    intent_classification: Optional[str] = None
    conversation_context: Optional[dict] = None
    ai_processing_time_ms: Optional[int] = None


class UserInteractionStats(SQLModel):
    """Schema for user interaction statistics"""
    total_interactions: int
    avg_ai_processing_time_ms: Optional[float]
    most_common_intent: Optional[str]
    last_interaction_at: Optional[datetime]