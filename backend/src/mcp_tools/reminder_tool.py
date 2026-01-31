"""
MCP Tool for managing smart reminders
This tool allows the AI agent to schedule and manage intelligent reminders for tasks.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from ..models import Task
from ...database import sync_engine
from datetime import datetime, timedelta


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderParams(BaseModel):
    """Parameters for the reminder MCP tool"""
    user_id: str = Field(..., description="ID of the user to manage reminders for")
    task_id: str = Field(..., description="ID of the task to set reminder for")
    scheduled_time: str = Field(..., description="ISO formatted datetime string for when to schedule the reminder")
    delivery_method: Optional[str] = Field("notification", description="Method to deliver the reminder: 'notification', 'email', 'sms'")
    reminder_type: Optional[str] = Field("deadline", description="Type of reminder: 'deadline', 'follow_up', 'recurring', 'custom'")


def reminder_tool(params: ReminderParams) -> List[TextContent]:
    """MCP tool to schedule and manage smart reminders for tasks"""
    logger.info(f"Scheduling reminder for user {params.user_id}, task {params.task_id}")

    try:
        with Session(sync_engine) as session:
            # Verify the task exists and belongs to the user
            task = session.exec(
                select(Task).where(Task.id == params.task_id).where(Task.user_id == params.user_id)
            ).first()

            if not task:
                error_response = {
                    "success": False,
                    "message": f"Task {params.task_id} not found or does not belong to user {params.user_id}"
                }
                return [TextContent(type="text", text=str(error_response))]

            # In a real implementation, this would create a reminder record in the database
            # For now, we'll just simulate the reminder scheduling
            scheduled_datetime = datetime.fromisoformat(params.scheduled_time.replace('Z', '+00:00'))

            # Prepare reminder response
            reminder_data = {
                "success": True,
                "task_id": params.task_id,
                "task_title": task.title,
                "scheduled_time": params.scheduled_time,
                "delivery_method": params.delivery_method,
                "reminder_type": params.reminder_type,
                "message": f"Reminder scheduled for '{task.title}' on {scheduled_datetime.strftime('%Y-%m-%d at %H:%M')}",
                "status": "pending"
            }

            logger.info(f"Reminder scheduled for user {params.user_id}, task {params.task_id}")
            return [TextContent(type="text", text=str(reminder_data))]

    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to schedule reminder: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


class CreateReminderParams(BaseModel):
    """Parameters for creating a new reminder"""
    user_id: str = Field(..., description="ID of the user creating the reminder")
    task_id: str = Field(..., description="ID of the task to create reminder for")
    scheduled_time: str = Field(..., description="ISO formatted datetime string for when to schedule the reminder")
    delivery_method: Optional[str] = Field("notification", description="Method to deliver the reminder: 'notification', 'email', 'sms'")
    reminder_type: Optional[str] = Field("deadline", description="Type of reminder: 'deadline', 'follow_up', 'recurring', 'custom'")
    custom_message: Optional[str] = Field(None, description="Custom message for the reminder")


def create_reminder(params: CreateReminderParams) -> List[TextContent]:
    """MCP tool to create a new reminder for a task"""
    logger.info(f"Creating reminder for user {params.user_id}, task {params.task_id}")

    try:
        with Session(sync_engine) as session:
            # Verify the task exists and belongs to the user
            task = session.exec(
                select(Task).where(Task.id == params.task_id).where(Task.user_id == params.user_id)
            ).first()

            if not task:
                error_response = {
                    "success": False,
                    "message": f"Task {params.task_id} not found or does not belong to user {params.user_id}"
                }
                return [TextContent(type="text", text=str(error_response))]

            # In a real implementation, this would create a reminder record in the database
            # For now, we'll just simulate the reminder creation
            scheduled_datetime = datetime.fromisoformat(params.scheduled_time.replace('Z', '+00:00'))

            # Prepare reminder response
            reminder_data = {
                "success": True,
                "id": f"reminder-{params.task_id}-{int(scheduled_datetime.timestamp())}",
                "task_id": params.task_id,
                "task_title": task.title,
                "scheduled_time": params.scheduled_time,
                "delivery_method": params.delivery_method,
                "reminder_type": params.reminder_type,
                "custom_message": params.custom_message,
                "created_at": datetime.utcnow().isoformat(),
                "message": f"Reminder created for '{task.title}' on {scheduled_datetime.strftime('%Y-%m-%d at %H:%M')}",
                "status": "pending"
            }

            logger.info(f"Reminder created for user {params.user_id}, task {params.task_id}")
            return [TextContent(type="text", text=str(reminder_data))]

    except Exception as e:
        logger.error(f"Error creating reminder: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to create reminder: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


class GetRemindersParams(BaseModel):
    """Parameters for getting reminders"""
    user_id: str = Field(..., description="ID of the user to get reminders for")
    status: Optional[str] = Field("pending", description="Filter by status: 'pending', 'sent', 'all'")
    time_range: Optional[str] = Field("week", description="Time range for upcoming reminders: 'today', 'week', 'month'")


def get_reminders(params: GetRemindersParams) -> List[TextContent]:
    """MCP tool to retrieve scheduled reminders for a user"""
    logger.info(f"Getting reminders for user {params.user_id}, status: {params.status}")

    try:
        # In a real implementation, this would query the database for reminders
        # For now, we'll simulate with mock data
        mock_reminders = [
            {
                "id": "reminder-1",
                "task_id": "task-1",
                "task_title": "Submit quarterly report",
                "scheduled_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                "delivery_method": "notification",
                "type": "deadline",
                "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "sent": False,
                "acknowledged": False
            },
            {
                "id": "reminder-2",
                "task_id": "task-2",
                "task_title": "Team meeting preparation",
                "scheduled_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "delivery_method": "email",
                "type": "follow_up",
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "sent": False,
                "acknowledged": False
            }
        ]

        # Filter based on status
        if params.status == "pending":
            filtered_reminders = [r for r in mock_reminders if not r["sent"]]
        elif params.status == "sent":
            filtered_reminders = [r for r in mock_reminders if r["sent"]]
        else:
            filtered_reminders = mock_reminders

        # Filter based on time range
        now = datetime.utcnow()
        if params.time_range == "today":
            filtered_reminders = [
                r for r in filtered_reminders
                if datetime.fromisoformat(r["scheduled_time"].replace('Z', '+00:00')) <= now + timedelta(days=1)
            ]
        elif params.time_range == "week":
            filtered_reminders = [
                r for r in filtered_reminders
                if datetime.fromisoformat(r["scheduled_time"].replace('Z', '+00:00')) <= now + timedelta(weeks=1)
            ]

        # Prepare response
        reminders_data = {
            "success": True,
            "user_id": params.user_id,
            "status_filter": params.status,
            "time_range": params.time_range,
            "reminders": filtered_reminders,
            "count": len(filtered_reminders)
        }

        logger.info(f"Retrieved {len(filtered_reminders)} reminders for user {params.user_id}")
        return [TextContent(type="text", text=str(reminders_data))]

    except Exception as e:
        logger.error(f"Error retrieving reminders: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to retrieve reminders: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


# Mock function for testing purposes
def mock_reminder_tool(params: ReminderParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Scheduling reminder for user {params.user_id}, task {params.task_id}")

    # In a real implementation, this would schedule a reminder in the database
    # For now, we return mock reminder data
    mock_reminder = {
        "success": True,
        "task_id": params.task_id,
        "task_title": "Mock Task Title",
        "scheduled_time": params.scheduled_time,
        "delivery_method": params.delivery_method,
        "reminder_type": params.reminder_type,
        "message": f"Mock reminder scheduled for 'Mock Task Title' on {datetime.fromisoformat(params.scheduled_time.replace('Z', '+00:00')).strftime('%Y-%m-%d at %H:%M')}",
        "status": "pending"
    }

    return [TextContent(type="text", text=str(mock_reminder))]