"""
Performance Metrics Model
This module defines the SQLModel for storing performance metrics data.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class PerformanceMetricsBase(SQLModel):
    """Base class for PerformanceMetrics model"""
    user_id: str = Field(..., description="ID of the user this performance metric belongs to")
    metric_type: str = Field(..., description="Type of metric: 'page_load', 'api_response', 'animation_frame', 'interaction_response'")
    value: float = Field(..., description="The measured value for this metric")
    unit: str = Field(..., description="Unit of measurement: 'milliseconds', 'seconds', 'frames_per_second', 'bytes'")
    page_route: Optional[str] = Field(default=None, description="Which page/route the metric relates to")
    api_endpoint: Optional[str] = Field(default=None, description="Which API endpoint the metric relates to")
    device_info: Optional[str] = Field(default=None, description="Client device information")
    network_condition: Optional[str] = Field(default=None, description="Network condition ('fast_3g', 'slow_4g', 'offline', etc.)")


class PerformanceMetrics(PerformanceMetricsBase, table=True):
    """PerformanceMetrics model for database table"""
    __tablename__ = "performance_metrics"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for this performance metric"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this metric was recorded"
    )


class PerformanceMetricsCreate(PerformanceMetricsBase):
    """Schema for creating new performance metrics records"""
    pass


class PerformanceMetricsRead(PerformanceMetricsBase):
    """Schema for reading performance metrics records"""
    id: uuid.UUID
    created_at: datetime


class PerformanceMetricsUpdate(SQLModel):
    """Schema for updating performance metrics records"""
    value: Optional[float] = None
    page_route: Optional[str] = None
    api_endpoint: Optional[str] = None
    device_info: Optional[str] = None
    network_condition: Optional[str] = None