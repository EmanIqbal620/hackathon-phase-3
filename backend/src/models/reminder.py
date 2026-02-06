"""
Reminder Model
This module defines the SQLModel for storing scheduled reminders for tasks.
"""
from sqlmodel import SQLModel, Field, Column, DateTime, Boolean, String
from datetime import datetime
from typing import Optional
import uuid


class ReminderBase(SQLModel):
    """Base class for Reminder model"""
    user_id: int = Field(..., description="ID of the user this reminder is for")
    task_id: str = Field(..., description="ID of the task this reminder is for")
    scheduled_time: datetime = Field(..., sa_column=Column(DateTime(timezone=True)), description="When to send the reminder")
    delivery_method: str = Field(default="notification", description="Method to deliver: 'notification', 'email', 'sms'")
    reminder_type: str = Field(default="deadline", description="Type of reminder: 'deadline', 'follow_up', 'recurring', 'custom'")


class Reminder(ReminderBase, table=True):
    """Reminder model for database table"""
    __tablename__ = "reminders"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this reminder"
    )
    custom_message: Optional[str] = Field(None, description="Custom message for the reminder")
    sent: bool = Field(default=False, description="Whether the reminder has been sent")
    sent_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp when the reminder was sent"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp when this reminder was created"
    )
    acknowledged_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Timestamp when the reminder was acknowledged by the user"
    )


class ReminderCreate(ReminderBase):
    """Schema for creating new reminder records"""
    custom_message: Optional[str] = None


class ReminderRead(ReminderBase):
    """Schema for reading reminder records"""
    id: uuid.UUID
    custom_message: Optional[str]
    sent: bool
    sent_at: Optional[datetime]
    created_at: datetime
    acknowledged_at: Optional[datetime]


class ReminderUpdate(SQLModel):
    """Schema for updating reminder records"""
    scheduled_time: Optional[datetime] = None
    delivery_method: Optional[str] = None
    reminder_type: Optional[str] = None
    custom_message: Optional[str] = None
    sent: Optional[bool] = None
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None


class ReminderResponse(SQLModel):
    """Response schema for reminder operations"""
    success: bool
    message: str
    reminder_id: Optional[uuid.UUID] = None
    scheduled_time: Optional[datetime]
    status: str