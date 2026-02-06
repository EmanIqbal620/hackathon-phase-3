"""
Accessibility Settings Model
This module defines the SQLModel for storing user accessibility preferences.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class AccessibilitySettingsBase(SQLModel):
    """Base class for AccessibilitySettings model"""
    user_id: str = Field(..., description="ID of the user this accessibility settings belongs to")
    high_contrast_enabled: bool = Field(default=False, description="Whether high contrast mode is enabled")
    reduced_motion_enabled: bool = Field(default=False, description="Whether reduced motion is enabled")
    screen_reader_optimized: bool = Field(default=True, description="Whether UI is optimized for screen readers")
    keyboard_navigation_only: bool = Field(default=False, description="Whether to enable keyboard-only navigation")
    font_size_preference: str = Field(default="normal", description="Font size preference: 'small', 'normal', 'large', 'extra_large'")


class AccessibilitySettings(AccessibilitySettingsBase, table=True):
    """AccessibilitySettings model for database table"""
    __tablename__ = "accessibility_settings"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this accessibility settings record"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when these settings were created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when these settings were last updated"
    )


class AccessibilitySettingsCreate(AccessibilitySettingsBase):
    """Schema for creating new accessibility settings records"""
    pass


class AccessibilitySettingsRead(AccessibilitySettingsBase):
    """Schema for reading accessibility settings records"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AccessibilitySettingsUpdate(SQLModel):
    """Schema for updating accessibility settings records"""
    high_contrast_enabled: Optional[bool] = None
    reduced_motion_enabled: Optional[bool] = None
    screen_reader_optimized: Optional[bool] = None
    keyboard_navigation_only: Optional[bool] = None
    font_size_preference: Optional[str] = None