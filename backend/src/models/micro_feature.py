"""
Micro Feature Model
This module defines the SQLModel for storing optional micro-features that users can enable/disable.
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class MicroFeatureBase(SQLModel):
    """Base class for MicroFeature model"""
    name: str = Field(..., description="Unique name of the feature", max_length=100)
    description: str = Field(..., description="Description of what the feature does")
    is_enabled_by_default: bool = Field(default=False, description="Whether this feature is enabled by default")
    category: str = Field(..., description="Category of the feature: 'navigation', 'productivity', 'accessibility', 'appearance', 'interaction'")
    keyboard_shortcut: Optional[str] = Field(default=None, description="Default keyboard shortcut if applicable")


class MicroFeature(MicroFeatureBase, table=True):
    """MicroFeature model for database table"""
    __tablename__ = "micro_features"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this micro feature"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this feature was defined"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this feature was last updated"
    )


class MicroFeatureCreate(MicroFeatureBase):
    """Schema for creating new micro feature records"""
    pass


class MicroFeatureRead(MicroFeatureBase):
    """Schema for reading micro feature records"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MicroFeatureUpdate(SQLModel):
    """Schema for updating micro feature records"""
    description: Optional[str] = None
    is_enabled_by_default: Optional[bool] = None
    category: Optional[str] = None
    keyboard_shortcut: Optional[str] = None


class UserMicroFeaturePreferenceBase(SQLModel):
    """Base class for user micro feature preferences"""
    user_id: int = Field(..., description="ID of the user")
    micro_feature_id: str = Field(..., description="ID of the micro feature")
    is_enabled: bool = Field(default=False, description="Whether the user has enabled this feature")
    custom_settings: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON, description="Custom settings for this feature")


class UserMicroFeaturePreference(UserMicroFeaturePreferenceBase, table=True):
    """UserMicroFeaturePreference model for database table"""
    __tablename__ = "user_micro_feature_preferences"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this user preference record"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this preference was set"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this preference was last updated"
    )


class UserMicroFeaturePreferenceCreate(UserMicroFeaturePreferenceBase):
    """Schema for creating new user micro feature preference records"""
    pass


class UserMicroFeaturePreferenceRead(UserMicroFeaturePreferenceBase):
    """Schema for reading user micro feature preference records"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserMicroFeaturePreferenceUpdate(SQLModel):
    """Schema for updating user micro feature preference records"""
    is_enabled: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None