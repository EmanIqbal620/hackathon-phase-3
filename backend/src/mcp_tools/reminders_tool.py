"""
MCP Tool for Smart Reminders
This module provides an MCP tool for scheduling and managing intelligent reminders.
"""
from pydantic import BaseModel, Field
from typing import List
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models import Task
from ...database import sync_engine
from ..models.reminder import Reminder, ReminderCreate


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RemindersParams(BaseModel):
    """Parameters for the reminders MCP tool"""
    user_id: str = Field(..., description="ID of the user to manage reminders for")
    task_id: str = Field(..., description="ID of the task to set reminder for")
    reminder_time: datetime = Field(..., description="When to send the reminder")
    delivery_method: str = Field("notification", description="Method to deliver the reminder: 'notification', 'email', 'sms'")
    reminder_type: str = Field("deadline", description="Type of reminder: 'deadline', 'follow_up', 'recurring', 'custom'")


def reminders_tool(params: RemindersParams) -> List[TextContent]:
    """MCP tool to schedule and manage smart reminders for tasks"""
    logger.info(f"Scheduling reminder for user {params.user_id}, task {params.task_id}")

    try:
        with Session(sync_engine) as session:
            # Verify the task exists and belongs to the user
            task = session.exec(
                select(Task).where(
                    Task.id == params.task_id,
                    Task.user_id == params.user_id
                )
            ).first()

            if not task:
                error_response = {
                    "success": False,
                    "message": f"Task {params.task_id} not found or does not belong to user {params.user_id}"
                }
                return [TextContent(type="text", text=str(error_response))]

            # Create reminder record
            reminder_data = ReminderCreate(
                user_id=params.user_id,
                task_id=params.task_id,
                scheduled_time=params.reminder_time,
                delivery_method=params.delivery_method,
                reminder_type=params.reminder_type,
                custom_message=f"Reminder for task: {task.title}"
            )

            reminder = Reminder.model_validate(reminder_data)
            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            # Prepare success response
            reminder_info = {
                "success": True,
                "message": f"Reminder scheduled for '{task.title}' on {params.reminder_time.strftime('%Y-%m-%d at %H:%M')}",
                "reminder_id": str(reminder.id),
                "task_id": params.task_id,
                "task_title": task.title,
                "scheduled_time": params.reminder_time.isoformat(),
                "delivery_method": params.delivery_method,
                "reminder_type": params.reminder_type
            }

            logger.info(f"Reminder scheduled with ID {reminder.id} for user {params.user_id}")
            return [TextContent(type="text", text=str(reminder_info))]

    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to schedule reminder: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]