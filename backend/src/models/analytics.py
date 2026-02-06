"""
Analytics Data Model
This module defines the SQLModel for storing aggregated analytics metrics for users.
"""
from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
import uuid


class AnalyticsDataBase(SQLModel):
    """Base class for AnalyticsData model"""
    user_id: int = Field(..., description="ID of the user this analytics data belongs to")
    metric_type: str = Field(..., description="Type of metric: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'")
    date_range_start: datetime = Field(..., description="Start date for the analytics period")
    date_range_end: datetime = Field(..., description="End date for the analytics period")
    tasks_created: int = Field(default=0, description="Number of tasks created in this period")
    tasks_completed: int = Field(default=0, description="Number of tasks completed in this period")
    tasks_pending: int = Field(default=0, description="Number of tasks pending in this period")
    tasks_missed: int = Field(default=0, description="Number of tasks missed in this period")
    average_completion_time_days: Optional[float] = Field(default=None, description="Average time to complete tasks in days")
    completion_rate_percent: Optional[float] = Field(default=None, description="Percentage of tasks completed vs created")


class AnalyticsData(AnalyticsDataBase, table=True):
    """AnalyticsData model for database table"""
    __tablename__ = "analytics_data"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this analytics record"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this record was last updated"
    )


class AnalyticsDataCreate(AnalyticsDataBase):
    """Schema for creating new analytics data records"""
    pass


class AnalyticsDataRead(AnalyticsDataBase):
    """Schema for reading analytics data records"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AnalyticsDataUpdate(SQLModel):
    """Schema for updating analytics data records"""
    tasks_created: Optional[int] = None
    tasks_completed: Optional[int] = None
    tasks_pending: Optional[int] = None
    tasks_missed: Optional[int] = None
    average_completion_time_days: Optional[float] = None
    completion_rate_percent: Optional[float] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None