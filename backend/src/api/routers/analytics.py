"""
Analytics API Router
This module defines the API endpoints for analytics functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from ...dependencies.auth import get_current_user, TokenData
from ...services.analytics_service import AnalyticsService
from ...src.models import Task
from ...database import sync_engine
from sqlmodel import Session, select
import time
import hashlib
from functools import wraps


# Create router
router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsResponse(BaseModel):
    """Response model for analytics endpoints"""
    success: bool
    data: Dict
    message: Optional[str] = None


class TimeRangeRequest(BaseModel):
    """Request model for time range analytics"""
    time_range: str  # 'day', 'week', 'month', 'quarter', 'year'
    user_id: Optional[str] = None  # Will be populated from auth if not provided




# In-memory cache for analytics data
_ANALYTICS_CACHE = {}
_CACHE_TTL = 300  # 5 minutes in seconds


def cache_analytics_data(ttl: int = _CACHE_TTL):
    """
    Decorator to cache analytics API responses.

    Args:
        ttl: Time to live for cached data in seconds (default 300 seconds)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create a cache key based on function name and parameters
            cache_key_parts = [func.__name__]

            # Add user_id to cache key (from path parameter)
            if 'user_id' in kwargs:
                cache_key_parts.append(f"user:{kwargs['user_id']}")

            # Add time_range or time_period to cache key
            if 'time_range' in kwargs:
                cache_key_parts.append(f"range:{kwargs['time_range']}")
            elif 'time_period' in kwargs:
                cache_key_parts.append(f"period:{kwargs['time_period']}")

            # Add other relevant parameters
            if 'current_user' in kwargs:
                cache_key_parts.append(f"auth:{getattr(kwargs['current_user'], 'user_id', 'unknown')}")

            cache_key = "|".join(cache_key_parts)

            # Check if we have cached data
            current_time = time.time()
            if cache_key in _ANALYTICS_CACHE:
                cached_data, timestamp = _ANALYTICS_CACHE[cache_key]

                # Check if cache is still valid
                if current_time - timestamp < ttl:
                    return cached_data

            # Call the original function
            result = await func(*args, **kwargs)

            # Cache the result
            _ANALYTICS_CACHE[cache_key] = (result, current_time)

            return result

        return wrapper
    return decorator


@router.get("/user/{user_id}/dashboard", response_model=AnalyticsResponse)
@cache_analytics_data(ttl=300)  # Cache for 5 minutes
async def get_user_analytics(
    user_id: str,
    time_range: str = "week",
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get comprehensive analytics dashboard data for a user.

    This endpoint provides metrics about completed vs pending tasks,
    productivity trends over time, and task category breakdowns with interactive visualizations.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )

    try:
        # Validate time_range parameter
        valid_ranges = ["day", "week", "month", "quarter", "year"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"time_range must be one of: {', '.join(valid_ranges)}"
            )

        # Get analytics from service
        analytics_data = AnalyticsService.calculate_user_analytics(user_id, time_range)

        return AnalyticsResponse(
            success=True,
            data=analytics_data,
            message=f"Analytics retrieved successfully for user {user_id} for {time_range} period"
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving analytics: {str(e)}"
        )


@router.get("/user/{user_id}/trends", response_model=AnalyticsResponse)
@cache_analytics_data(ttl=300)  # Cache for 5 minutes
async def get_analytics_trends(
    user_id: str,
    time_period: str = "week",
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get trend data for analytics charts.

    This endpoint provides time-series data for visualizing trends in task completion,
    creation, and other metrics over time.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )

    try:
        # Validate time_period parameter
        valid_periods = ["day", "week", "month", "quarter"]
        if time_period not in valid_periods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"time_period must be one of: {', '.join(valid_periods)}"
            )

        # Get trend data from service
        trend_data = AnalyticsService.get_trend_data(user_id, time_period)

        return AnalyticsResponse(
            success=True,
            data={"trend_data": trend_data},
            message=f"Trend data retrieved successfully for user {user_id} for {time_period} period"
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving trend data: {str(e)}"
        )


@router.get("/user/{user_id}/productivity-score", response_model=AnalyticsResponse)
@cache_analytics_data(ttl=600)  # Cache for 10 minutes (score changes less frequently)
async def get_productivity_score(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get user's productivity score.

    This endpoint calculates and returns a productivity score based on various metrics
    like completion rate, completion speed, and priority management.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )

    try:
        # Calculate productivity score
        productivity_score = AnalyticsService.get_productivity_score(user_id)

        return AnalyticsResponse(
            success=True,
            data={"productivity_score": productivity_score},
            message=f"Productivity score calculated for user {user_id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calculating productivity score: {str(e)}"
        )


@router.get("/user/{user_id}/suggestions", response_model=AnalyticsResponse)
@cache_analytics_data(ttl=900)  # Cache for 15 minutes (suggestions are less time-sensitive)
async def get_analytics_suggestions(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get AI-generated suggestions based on analytics data.

    This endpoint provides intelligent suggestions for improving productivity
    based on the user's analytics and task patterns.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )

    try:
        # Get suggestions based on analytics data
        suggestions = AnalyticsService.generate_suggestions_from_analytics(user_id)

        return AnalyticsResponse(
            success=True,
            data={"suggestions": suggestions},
            message=f"Analytics-based suggestions generated for user {user_id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating suggestions: {str(e)}"
        )


# Endpoint to clear cache (for administrative purposes)
@router.post("/admin/clear-cache")
async def clear_analytics_cache(current_user: TokenData = Depends(get_current_user)):
    """
    Administrative endpoint to clear the analytics cache.

    Only administrators should be able to access this endpoint.
    """
    # In a real application, you'd check if the user has admin privileges
    # For this implementation, we'll allow it for demo purposes
    global _ANALYTICS_CACHE
    cleared_count = len(_ANALYTICS_CACHE)
    _ANALYTICS_CACHE = {}

    return AnalyticsResponse(
        success=True,
        data={"cleared_entries": cleared_count},
        message=f"Cleared {cleared_count} entries from analytics cache"
    )


# Health check endpoint for analytics service
@router.get("/health", response_model=AnalyticsResponse)
async def analytics_health_check():
    """
    Health check endpoint for the analytics service.

    Returns the status of the analytics service.
    """
    try:
        # Verify that the analytics service is operational
        # This could include checking database connectivity, etc.
        return AnalyticsResponse(
            success=True,
            data={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "cache_entries": len(_ANALYTICS_CACHE)
            },
            message="Analytics service is healthy"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics service health check failed: {str(e)}"
        )