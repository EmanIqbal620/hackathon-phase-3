"""
Reminder Service
This module provides business logic for managing smart reminders for tasks.
"""
from typing import Dict, List, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models import Task
from ..models.reminder import Reminder, ReminderCreate, ReminderUpdate
from ..database import sync_engine
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderService:
    """Service class for handling reminder scheduling and management."""

    @staticmethod
    def create_reminder(user_id: str, task_id: str, scheduled_time: datetime,
                       delivery_method: str = "notification",
                       reminder_type: str = "deadline",
                       custom_message: Optional[str] = None) -> Reminder:
        """
        Create a new reminder for a task.

        Args:
            user_id: ID of the user creating the reminder
            task_id: ID of the task to create reminder for
            scheduled_time: When to schedule the reminder
            delivery_method: Method to deliver the reminder
            reminder_type: Type of reminder
            custom_message: Custom message for the reminder

        Returns:
            Created Reminder object
        """
        with Session(sync_engine) as session:
            # Verify the task exists and belongs to the user
            task = session.exec(
                select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
            ).first()

            if not task:
                raise ValueError(f"Task {task_id} not found or does not belong to user {user_id}")

            # Create reminder object
            reminder_create = ReminderCreate(
                user_id=user_id,
                task_id=task_id,
                scheduled_time=scheduled_time,
                delivery_method=delivery_method,
                reminder_type=reminder_type,
                custom_message=custom_message
            )

            # Create the reminder instance
            reminder_record = Reminder.model_validate(reminder_create)

            # Add to the session and commit
            session.add(reminder_record)
            session.commit()
            session.refresh(reminder_record)

            logger.info(f"Reminder created for user {user_id}, task {task_id}, scheduled for {scheduled_time}")
            return reminder_record

    @staticmethod
    def get_reminders(user_id: str, status: str = "pending", time_range: str = "week") -> List[Reminder]:
        """
        Get reminders for a user with optional filtering.

        Args:
            user_id: ID of the user to get reminders for
            status: Filter by status ('pending', 'sent', 'all')
            time_range: Time range for upcoming reminders ('today', 'week', 'month')

        Returns:
            List of Reminder objects
        """
        with Session(sync_engine) as session:
            # Base query for user's reminders
            query = select(Reminder).where(Reminder.user_id == user_id)

            # Apply status filter
            if status == "pending":
                query = query.where(Reminder.sent == False)
            elif status == "sent":
                query = query.where(Reminder.sent == True)

            # Apply time range filter
            now = datetime.utcnow()
            if time_range == "today":
                end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.where(Reminder.scheduled_time <= end_time)
            elif time_range == "week":
                end_time = now + timedelta(weeks=1)
                query = query.where(Reminder.scheduled_time <= end_time)
            elif time_range == "month":
                end_time = now + timedelta(days=30)
                query = query.where(Reminder.scheduled_time <= end_time)

            # Execute query and return results
            reminders = session.exec(query.order_by(Reminder.scheduled_time.asc())).all()
            return reminders

    @staticmethod
    def get_upcoming_reminders(user_id: str, within_hours: int = 24) -> List[Reminder]:
        """
        Get reminders that are scheduled to be sent within a certain time period.

        Args:
            user_id: ID of the user to get reminders for
            within_hours: Number of hours to look ahead

        Returns:
            List of Reminder objects
        """
        with Session(sync_engine) as session:
            # Get reminders that are scheduled within the specified time window and haven't been sent yet
            now = datetime.utcnow()
            future_time = now + timedelta(hours=within_hours)

            query = select(Reminder).where(
                Reminder.user_id == user_id,
                Reminder.scheduled_time >= now,
                Reminder.scheduled_time <= future_time,
                Reminder.sent == False
            ).order_by(Reminder.scheduled_time.asc())

            reminders = session.exec(query).all()
            return reminders

    @staticmethod
    def mark_reminder_as_sent(reminder_id: str) -> Reminder:
        """
        Mark a reminder as sent.

        Args:
            reminder_id: ID of the reminder to mark as sent

        Returns:
            Updated Reminder object
        """
        with Session(sync_engine) as session:
            # Get the reminder
            reminder = session.exec(
                select(Reminder).where(Reminder.id == reminder_id)
            ).first()

            if not reminder:
                raise ValueError(f"Reminder with ID {reminder_id} not found")

            # Update the reminder
            reminder.sent = True
            reminder.sent_at = datetime.utcnow()

            # Commit the changes
            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            logger.info(f"Reminder {reminder_id} marked as sent")
            return reminder

    @staticmethod
    def acknowledge_reminder(reminder_id: str) -> Reminder:
        """
        Mark a reminder as acknowledged by the user.

        Args:
            reminder_id: ID of the reminder to acknowledge

        Returns:
            Updated Reminder object
        """
        with Session(sync_engine) as session:
            # Get the reminder
            reminder = session.exec(
                select(Reminder).where(Reminder.id == reminder_id)
            ).first()

            if not reminder:
                raise ValueError(f"Reminder with ID {reminder_id} not found")

            # Update the reminder
            reminder.acknowledged_at = datetime.utcnow()

            # Commit the changes
            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            logger.info(f"Reminder {reminder_id} acknowledged by user")
            return reminder

    @staticmethod
    def cancel_reminder(reminder_id: str, user_id: str) -> bool:
        """
        Cancel a reminder (delete it if it hasn't been sent yet).

        Args:
            reminder_id: ID of the reminder to cancel
            user_id: ID of the user who owns the reminder

        Returns:
            True if successfully canceled, False otherwise
        """
        with Session(sync_engine) as session:
            # Get the reminder
            reminder = session.exec(
                select(Reminder).where(Reminder.id == reminder_id).where(Reminder.user_id == user_id)
            ).first()

            if not reminder:
                raise ValueError(f"Reminder with ID {reminder_id} not found or does not belong to user {user_id}")

            if reminder.sent:
                raise ValueError(f"Cannot cancel reminder {reminder_id} as it has already been sent")

            # Delete the reminder
            session.delete(reminder)
            session.commit()

            logger.info(f"Reminder {reminder_id} canceled")
            return True

    @staticmethod
    def update_reminder(reminder_id: str, user_id: str, update_data: ReminderUpdate) -> Reminder:
        """
        Update an existing reminder.

        Args:
            reminder_id: ID of the reminder to update
            user_id: ID of the user who owns the reminder
            update_data: Data to update the reminder with

        Returns:
            Updated Reminder object
        """
        with Session(sync_engine) as session:
            # Get the reminder
            reminder = session.exec(
                select(Reminder).where(Reminder.id == reminder_id).where(Reminder.user_id == user_id)
            ).first()

            if not reminder:
                raise ValueError(f"Reminder with ID {reminder_id} not found or does not belong to user {user_id}")

            # Update the reminder with provided fields
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(reminder, field):
                    setattr(reminder, field, value)

            # Commit the changes
            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            logger.info(f"Reminder {reminder_id} updated")
            return reminder

    @staticmethod
    def get_reminder_stats(user_id: str) -> Dict:
        """
        Get statistics about reminders for a user.

        Args:
            user_id: ID of the user to get stats for

        Returns:
            Dictionary with reminder statistics
        """
        with Session(sync_engine) as session:
            # Get all reminders for the user
            all_reminders = session.exec(
                select(Reminder).where(Reminder.user_id == user_id)
            ).all()

            # Count by status
            total = len(all_reminders)
            sent = len([r for r in all_reminders if r.sent])
            pending = len([r for r in all_reminders if not r.sent])
            acknowledged = len([r for r in all_reminders if r.acknowledged_at])

            # Calculate response rate
            response_rate = (acknowledged / sent * 100) if sent > 0 else 0

            # Get most common reminder types
            type_counts = {}
            for r in all_reminders:
                if r.reminder_type in type_counts:
                    type_counts[r.reminder_type] += 1
                else:
                    type_counts[r.reminder_type] = 1

            # Get most common delivery methods
            method_counts = {}
            for r in all_reminders:
                if r.delivery_method in method_counts:
                    method_counts[r.delivery_method] += 1
                else:
                    method_counts[r.delivery_method] = 1

            stats = {
                "user_id": user_id,
                "total_reminders": total,
                "sent_reminders": sent,
                "pending_reminders": pending,
                "acknowledged_reminders": acknowledged,
                "response_rate_percent": round(response_rate, 2),
                "most_common_type": max(type_counts, key=type_counts.get) if type_counts else None,
                "most_common_delivery_method": max(method_counts, key=method_counts.get) if method_counts else None,
                "type_distribution": type_counts,
                "delivery_method_distribution": method_counts
            }

            return stats

    @staticmethod
    def schedule_smart_reminders_for_task(task_id: str, user_id: str) -> List[Reminder]:
        """
        Automatically schedule smart reminders for a task based on its properties.

        Args:
            task_id: ID of the task to schedule reminders for
            user_id: ID of the user who owns the task

        Returns:
            List of created Reminder objects
        """
        with Session(sync_engine) as session:
            # Get the task
            task = session.exec(
                select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
            ).first()

            if not task:
                raise ValueError(f"Task {task_id} not found or does not belong to user {user_id}")

            created_reminders = []

            # Schedule a reminder based on priority and due date
            if task.due_date:
                # Schedule a reminder 24 hours before the due date for high priority tasks
                if task.priority == "high":
                    reminder_time = task.due_date - timedelta(hours=24)
                    if reminder_time > datetime.utcnow():  # Only schedule if the time is in the future
                        reminder = ReminderService.create_reminder(
                            user_id=user_id,
                            task_id=task_id,
                            scheduled_time=reminder_time,
                            delivery_method="notification",
                            reminder_type="deadline",
                            custom_message=f"This is a high-priority task due tomorrow: {task.title}"
                        )
                        created_reminders.append(reminder)

                # Schedule a reminder 1 hour before the due date for any priority level
                reminder_time = task.due_date - timedelta(hours=1)
                if reminder_time > datetime.utcnow():  # Only schedule if the time is in the future
                    reminder = ReminderService.create_reminder(
                        user_id=user_id,
                        task_id=task_id,
                        scheduled_time=reminder_time,
                        delivery_method="notification",
                        reminder_type="deadline",
                        custom_message=f"Reminder: Task '{task.title}' is due soon!"
                    )
                    created_reminders.append(reminder)

            # For tasks without due dates, schedule a follow-up reminder after a few days
            else:
                if task.priority == "high":
                    # For high priority tasks without due dates, schedule a reminder in 2 days
                    reminder_time = datetime.utcnow() + timedelta(days=2)
                    reminder = ReminderService.create_reminder(
                        user_id=user_id,
                        task_id=task_id,
                        scheduled_time=reminder_time,
                        delivery_method="notification",
                        reminder_type="follow_up",
                        custom_message=f"Follow-up: Don't forget about task '{task.title}'"
                    )
                    created_reminders.append(reminder)

            logger.info(f"Created {len(created_reminders)} smart reminders for task {task_id}")
            return created_reminders