from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class ToolCallLog(SQLModel, table=True):
    """
    Record of AI agent's tool invocations with status and results for transparency
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign Key to User, required for isolation
    conversation_id: int = Field(index=True)  # Foreign Key to Conversation, required
    message_id: Optional[int] = Field(default=None, index=True)  # Foreign Key to Message that triggered the tool call
    tool_name: str = Field(max_length=100)  # Name of the tool called, required
    parameters: Dict[str, Any] = Field(default={})  # Parameters passed to the tool, required
    result: Optional[Dict[str, Any]] = Field(default=None)  # Result from the tool call, optional
    status: str = Field(sa_column_kwargs={"default": "pending"})  # Enum: "success"|"error"|"pending", required
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # When tool was called, required

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate status field
        if hasattr(self, 'status') and self.status not in ['success', 'error', 'pending']:
            raise ValueError("Status must be one of: 'success', 'error', 'pending'")