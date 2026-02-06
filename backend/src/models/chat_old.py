from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid


class ConversationBase(SQLModel):
    """Base class for conversation models."""
    user_id: int = Field(index=True)


class Conversation(ConversationBase, table=True):
    """Conversation model to track chat conversations."""
    __tablename__ = "conversations"

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class MessageBase(SQLModel):
    """Base class for message models."""
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str


class Message(MessageBase, table=True):
    """Message model to store chat messages."""
    __tablename__ = "messages"

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")


# Create indexes for performance
class Indexes:
    """Indexes for chat models."""
    # These are automatically created by SQLModel based on Field(index=True)
    pass