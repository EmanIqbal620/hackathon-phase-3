"""
Reminders API Router
This module defines the API endpoints for managing smart reminders.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from ....dependencies.auth import get_current_user, TokenData
from ....services.reminder_service import ReminderService
from ....models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderResponse


# Create router
router = APIRouter(prefix="/reminders", tags=["reminders"])


class CreateReminderRequest(BaseModel):
    """Request model for creating a new reminder"""
    task_id: str = Field(..., description="ID of the task to create reminder for")
    scheduled_time: str = Field(..., description="ISO formatted datetime string for when to schedule the reminder")
    delivery_method: Optional[str] = Field("notification", description="Method to deliver: 'notification', 'email', 'sms'")
    reminder_type: Optional[str] = Field("deadline", description="Type of reminder: 'deadline', 'follow_up', 'recurring', 'custom'")
    custom_message: Optional[str] = Field(None, description="Custom message for the reminder")


class GetRemindersRequest(BaseModel):
    """Request model for getting reminders"""
    status: Optional[str] = Field("pending", description="Filter by status: 'pending', 'sent', 'all'")
    time_range: Optional[str] = Field("week", description="Time range for upcoming reminders: 'today', 'week', 'month'")


@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    request: CreateReminderRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a new reminder for a task.

    This endpoint allows users to schedule smart reminders for their tasks.
    """
    try:
        # Use the reminder service to create the reminder
        reminder = ReminderService.create_reminder(
            user_id=current_user.user_id,
            task_id=request.task_id,
            scheduled_time=datetime.fromisoformat(request.scheduled_time.replace('Z', '+00:00')),
            delivery_method=request.delivery_method,
            reminder_type=request.reminder_type,
            custom_message=request.custom_message
        )

        return ReminderResponse(
            success=True,
            message=f"Reminder created for task {request.task_id}",
            reminder_id=reminder.id,
            scheduled_time=reminder.scheduled_time,
            status="created"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reminder: {str(e)}"
        )


@router.get("/", response_model=Dict)
async def get_reminders(
    params: GetRemindersRequest = Depends(),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get reminders for the current user.

    This endpoint returns scheduled reminders for the user, with optional filtering.
    """
    try:
        # Use the reminder service to get reminders
        reminders = ReminderService.get_reminders(
            user_id=current_user.user_id,
            status=params.status,
            time_range=params.time_range
        )

        return {
            "success": True,
            "user_id": current_user.user_id,
            "status_filter": params.status,
            "time_range": params.time_range,
            "reminders": [reminder.dict() for reminder in reminders],
            "count": len(reminders)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminders: {str(e)}"
        )


@router.get("/upcoming", response_model=List[Dict])
async def get_upcoming_reminders(
    within_hours: int = 24,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get upcoming reminders within a specified time period.

    This endpoint returns reminders scheduled to be sent within the specified number of hours.
    """
    try:
        # Use the reminder service to get upcoming reminders
        reminders = ReminderService.get_upcoming_reminders(
            user_id=current_user.user_id,
            within_hours=within_hours
        )

        return [reminder.dict() for reminder in reminders]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve upcoming reminders: {str(e)}"
        )


@router.patch("/{reminder_id}/mark-sent", response_model=ReminderResponse)
async def mark_reminder_sent(
    reminder_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Mark a reminder as sent.

    This endpoint marks a reminder as sent in the system.
    """
    try:
        # Use the reminder service to mark as sent
        reminder = ReminderService.mark_reminder_as_sent(reminder_id)

        return ReminderResponse(
            success=True,
            message=f"Reminder {reminder_id} marked as sent",
            reminder_id=reminder.id,
            scheduled_time=reminder.scheduled_time,
            status="sent"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark reminder as sent: {str(e)}"
        )


@router.patch("/{reminder_id}/acknowledge", response_model=ReminderResponse)
async def acknowledge_reminder(
    reminder_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Acknowledge a reminder.

    This endpoint marks a reminder as acknowledged by the user.
    """
    try:
        # Use the reminder service to acknowledge the reminder
        reminder = ReminderService.acknowledge_reminder(reminder_id)

        return ReminderResponse(
            success=True,
            message=f"Reminder {reminder_id} acknowledged",
            reminder_id=reminder.id,
            scheduled_time=reminder.scheduled_time,
            status="acknowledged"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge reminder: {str(e)}"
        )


@router.delete("/{reminder_id}", response_model=Dict)
async def cancel_reminder(
    reminder_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Cancel a reminder.

    This endpoint cancels a scheduled reminder (deletes it if not yet sent).
    """
    try:
        # Use the reminder service to cancel the reminder
        success = ReminderService.cancel_reminder(reminder_id, current_user.user_id)

        if success:
            return {
                "success": True,
                "message": f"Reminder {reminder_id} canceled successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not cancel reminder {reminder_id}"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel reminder: {str(e)}"
        )


@router.get("/stats", response_model=Dict)
async def get_reminder_stats(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get reminder statistics for the user.

    This endpoint returns analytics about the user's reminder usage and effectiveness.
    """
    try:
        # Use the reminder service to get stats
        stats = ReminderService.get_reminder_stats(current_user.user_id)

        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminder stats: {str(e)}"
        )


# Health check endpoint
@router.get("/health", response_model=Dict)
async def reminders_health_check():
    """
    Health check for the reminders service.

    This endpoint confirms the reminders service is operational.
    """
    return {
        "success": True,
        "message": "Reminders service is operational",
        "timestamp": datetime.utcnow().isoformat()
    }


# Include the router in the application
def include_router(app):
    """
    Helper function to include this router in the main application.

    Args:
        app: FastAPI application instance
    """
    app.include_router(router)