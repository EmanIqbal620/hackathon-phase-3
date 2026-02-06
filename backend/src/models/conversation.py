from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy import JSON
from typing import Dict, Any, Union, List

# Conversation Model
class ConversationBase(SQLModel):
    user_id: str = Field(foreign_key="user.id", index=True)  # Foreign Key to User, required for isolation
    title: Optional[str] = Field(max_length=200, default=None)  # Optional, auto-generated from first message or user-edited


class Conversation(ConversationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="conversations", sa_relationship_kwargs={"primaryjoin": "Conversation.user_id==User.id"})


    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"primaryjoin": "Conversation.id==Message.conversation_id"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure updated_at is set to current time when initialized
        if not hasattr(self, 'updated_at') or not self.updated_at:
            self.updated_at = datetime.utcnow()


class ConversationCreate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime


# Message Model
class MessageBase(SQLModel):
    user_id: str = Field(foreign_key="user.id", index=True)  # Foreign Key to User, required for isolation
    conversation_id: int = Field(foreign_key="conversation.id", index=True)  # Foreign Key to Conversation, required
    role: str = Field(max_length=20)  # "user" or "assistant", required
    content: str = Field(max_length=10000)  # Message content, required
    tool_call_results: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(default=None, sa_type=JSON)  # Optional, stores results from tool calls


class Message(MessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)  # When message was sent/received, required

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages", sa_relationship_kwargs={"primaryjoin": "Message.conversation_id==Conversation.id"})


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure timestamp is set to current time when initialized
        if not hasattr(self, 'timestamp') or not self.timestamp:
            self.timestamp = datetime.utcnow()


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    timestamp: datetime