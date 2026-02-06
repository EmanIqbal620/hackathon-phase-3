"""
UX Enhancement Model
This module defines the SQLModel for tracking UX enhancements and user interactions with them.
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class UXEnhancementBase(SQLModel):
    """Base class for UXEnhancement model"""
    user_id: str = Field(..., description="ID of the user this UX enhancement tracking belongs to")
    enhancement_type: str = Field(..., description="Type of UX enhancement: 'animation', 'micro_interaction', 'theme_transition', 'suggestion_interaction', 'feature_discovery'")
    feature_name: str = Field(..., description="Name of the feature/enhancement", max_length=100)
    usage_count: int = Field(default=0, description="Number of times the user interacted with this enhancement")
    effectiveness_rating: Optional[float] = Field(default=None, description="Effectiveness rating (0-1 scale)")
    feedback: Optional[str] = Field(default=None, description="User feedback about the enhancement")
    enhancement_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON, description="Additional metadata about the interaction")


class UXEnhancement(UXEnhancementBase, table=True):
    """UXEnhancement model for database table"""
    __tablename__ = "ux_enhancements"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this UX enhancement tracking record"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this record was last updated"
    )


class UXEnhancementCreate(UXEnhancementBase):
    """Schema for creating new UX enhancement tracking records"""
    pass


class UXEnhancementRead(UXEnhancementBase):
    """Schema for reading UX enhancement tracking records"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UXEnhancementUpdate(SQLModel):
    """Schema for updating UX enhancement tracking records"""
    usage_count: Optional[int] = None
    effectiveness_rating: Optional[float] = None
    feedback: Optional[str] = None
    enhancement_metadata: Optional[Dict[str, Any]] = None