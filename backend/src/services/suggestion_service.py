"""
Suggestion Service
This module provides business logic for generating and managing AI task suggestions.
"""
from typing import Dict, List, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models import Task
from ..models.suggestion import Suggestion, SuggestionCreate, SuggestionUpdate
from ..database import sync_engine
from collections import Counter
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuggestionService:
    """Service class for handling AI-generated task suggestions."""

    @staticmethod
    def generate_pattern_based_suggestions(user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate suggestions based on user's historical task patterns.

        Args:
            user_id: ID of the user to generate suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            suggestions = []

            # Find recurring patterns in task titles
            title_patterns = Counter([task.title.lower() for task in all_tasks if task.title])

            # Look for tasks that appear frequently
            frequent_tasks = [(title, count) for title, count in title_patterns.items() if count >= 2]

            for title, count in frequent_tasks[:limit]:  # Limit to top N
                # Check if the user has done this task recently
                recent_similar_tasks = [
                    task for task in all_tasks
                    if task.title.lower() == title and
                    task.created_at and
                    task.created_at >= datetime.utcnow() - timedelta(days=7)
                ]

                # If they haven't done it recently, suggest it
                if not recent_similar_tasks:
                    day_of_week = datetime.now().strftime("%A")
                    suggestions.append({
                        "title": title,
                        "description": f"Based on your pattern of adding this task regularly",
                        "type": "pattern_based",
                        "confidence": min(0.9, 0.5 + (count * 0.1)),  # Higher confidence for more frequent patterns
                        "reasoning": f"You usually add '{title}' tasks regularly (appears {count} times in your history)",
                        "category": SuggestionService._infer_category_from_title(title)
                    })

            return suggestions

    @staticmethod
    def generate_priority_based_suggestions(user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate suggestions for high-priority tasks or tasks that should be prioritized.

        Args:
            user_id: ID of the user to generate suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            suggestions = []

            # Find incomplete high-priority tasks
            high_priority_tasks = [task for task in all_tasks if task.priority == "high" and not task.is_completed]

            # Find tasks that have been pending for a long time
            long_pending_tasks = [
                task for task in all_tasks
                if not task.is_completed and
                task.created_at and
                (datetime.utcnow() - task.created_at).days > 7
            ]

            # Suggest completing high priority tasks
            for task in high_priority_tasks[:min(limit, 2)]:  # Limit to top 2
                suggestions.append({
                    "title": f"Complete: {task.title}",
                    "description": f"This is a high-priority task that requires your attention",
                    "type": "priority_based",
                    "confidence": 0.85,
                    "reasoning": f"'{task.title}' is marked as high priority and should be completed soon",
                    "category": task.category or SuggestionService._infer_category_from_title(task.title)
                })

            # Suggest reviewing long-pending tasks
            for task in long_pending_tasks[:min(limit - len(suggestions), 2)]:  # Limit to top 2
                suggestions.append({
                    "title": f"Review: {task.title}",
                    "description": f"This task has been pending for {(datetime.utcnow() - task.created_at).days} days",
                    "type": "priority_based",
                    "confidence": 0.75,
                    "reasoning": f"'{task.title}' has been pending for {(datetime.utcnow() - task.created_at).days} days - consider completing or re-evaluating",
                    "category": task.category or SuggestionService._infer_category_from_title(task.title)
                })

            return suggestions

    @staticmethod
    def generate_deadline_based_suggestions(user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate suggestions for tasks with approaching deadlines.

        Args:
            user_id: ID of the user to generate suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            suggestions = []

            # Find tasks with due dates in the near future
            now = datetime.utcnow()
            upcoming_deadlines = [
                task for task in all_tasks
                if task.due_date and
                not task.is_completed and
                task.due_date <= now + timedelta(days=3) and  # Due within 3 days
                task.due_date >= now  # Not overdue
            ]

            # Find overdue tasks
            overdue_tasks = [
                task for task in all_tasks
                if task.due_date and
                not task.is_completed and
                task.due_date < now
            ]

            # Suggest completing upcoming deadlines
            for task in upcoming_deadlines[:limit]:
                days_until_due = (task.due_date - now).days
                suggestions.append({
                    "title": f"Complete by {task.due_date.strftime('%m/%d')}: {task.title}",
                    "description": f"This task is due in {days_until_due} day{'s' if days_until_due != 1 else ''}",
                    "type": "deadline_based",
                    "confidence": 0.9 if days_until_due == 0 else 0.8,  # Higher confidence if due today
                    "reasoning": f"'{task.title}' is due on {task.due_date.strftime('%A, %B %d')} ({days_until_due} day{'s' if days_until_due != 1 else ''} from now)",
                    "category": task.category or SuggestionService._infer_category_from_title(task.title)
                })

            # Suggest addressing overdue tasks
            for task in overdue_tasks[:min(limit - len(suggestions), limit)]:
                days_overdue = (now - task.due_date).days
                suggestions.append({
                    "title": f"Overdue: {task.title}",
                    "description": f"This task was due {days_overdue} day{'s' if days_overdue != 1 else ''} ago",
                    "type": "deadline_based",
                    "confidence": 0.85,
                    "reasoning": f"'{task.title}' was due on {task.due_date.strftime('%A, %B %d')} ({days_overdue} day{'s' if days_overdue != 1 else ''} ago)",
                    "category": task.category or SuggestionService._infer_category_from_title(task.title)
                })

            return suggestions

    @staticmethod
    def generate_contextual_suggestions(user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate contextual suggestions based on task relationships and patterns.

        Args:
            user_id: ID of the user to generate suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            suggestions = []

            # Find tasks that might be related to recent completions
            recently_completed = [
                task for task in all_tasks
                if task.is_completed and
                task.completed_at and
                (datetime.utcnow() - task.completed_at).days <= 2
            ]

            # Suggest follow-up tasks based on completed tasks
            for task in recently_completed[:min(limit, 2)]:
                # Create a follow-up suggestion based on the completed task
                follow_up_title = f"Follow-up: {task.title}"
                suggestions.append({
                    "title": follow_up_title,
                    "description": f"Consider follow-up actions for '{task.title}'",
                    "type": "contextual",
                    "confidence": 0.7,
                    "reasoning": f"Since you recently completed '{task.title}', you might want to do follow-up actions",
                    "category": task.category or SuggestionService._infer_category_from_title(task.title)
                })

            # Suggest tasks based on common sequences
            # For example, if a user often does certain tasks after others
            if len(all_tasks) >= 2 and len(suggestions) < limit:
                # This is a simplified version - in reality, you'd want more sophisticated pattern analysis
                last_task = max(all_tasks, key=lambda t: t.created_at if t.created_at else datetime.min)
                if last_task.title.lower().startswith("buy"):
                    # Suggest related tasks after buying something
                    suggestions.append({
                        "title": "Organize purchases",
                        "description": "Consider organizing or putting away your recent purchases",
                        "type": "contextual",
                        "confidence": 0.6,
                        "reasoning": "You recently added a purchase-related task, so organizing might be relevant",
                        "category": "shopping"
                    })

            return suggestions

    @staticmethod
    def create_suggestion_in_db(suggestion_data: Dict, user_id: str) -> Suggestion:
        """
        Save a suggestion to the database.

        Args:
            suggestion_data: Dictionary containing suggestion data
            user_id: ID of the user the suggestion is for

        Returns:
            Saved Suggestion object
        """
        with Session(sync_engine) as session:
            # Create suggestion object
            suggestion_create = SuggestionCreate(
                user_id=user_id,
                suggested_task_title=suggestion_data["title"],
                suggested_task_description=suggestion_data.get("description"),
                suggestion_type=suggestion_data["type"],
                confidence_score=suggestion_data["confidence"],
                reasoning=suggestion_data["reasoning"]
            )

            # Create the suggestion instance
            suggestion_record = Suggestion.model_validate(suggestion_create)

            # Add to the session and commit
            session.add(suggestion_record)
            session.commit()
            session.refresh(suggestion_record)

            logger.info(f"Suggestion saved to database with ID: {suggestion_record.id}")
            return suggestion_record

    @staticmethod
    def get_pending_suggestions(user_id: str, limit: int = 10) -> List[Suggestion]:
        """
        Get pending (not accepted or dismissed) suggestions for a user.

        Args:
            user_id: ID of the user to get suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of Suggestion objects
        """
        with Session(sync_engine) as session:
            # Query for suggestions that are neither accepted nor dismissed
            query = select(Suggestion).where(
                Suggestion.user_id == user_id
            ).where(
                Suggestion.accepted.is_(None)  # Not yet accepted/dismissed
            ).order_by(Suggestion.created_at.desc()).limit(limit)

            suggestions = session.exec(query).all()
            return suggestions

    @staticmethod
    def accept_suggestion(suggestion_id: str, task_id: Optional[str] = None) -> Suggestion:
        """
        Mark a suggestion as accepted.

        Args:
            suggestion_id: ID of the suggestion to accept
            task_id: Optional ID of the task created from this suggestion

        Returns:
            Updated Suggestion object
        """
        with Session(sync_engine) as session:
            # Get the suggestion
            suggestion = session.exec(
                select(Suggestion).where(Suggestion.id == suggestion_id)
            ).first()

            if not suggestion:
                raise ValueError(f"Suggestion with ID {suggestion_id} not found")

            # Update the suggestion
            suggestion.accepted = True
            if task_id:
                suggestion.converted_to_task_id = task_id

            # Commit the changes
            session.add(suggestion)
            session.commit()
            session.refresh(suggestion)

            logger.info(f"Suggestion {suggestion_id} marked as accepted")
            return suggestion

    @staticmethod
    def dismiss_suggestion(suggestion_id: str) -> Suggestion:
        """
        Mark a suggestion as dismissed.

        Args:
            suggestion_id: ID of the suggestion to dismiss

        Returns:
            Updated Suggestion object
        """
        with Session(sync_engine) as session:
            # Get the suggestion
            suggestion = session.exec(
                select(Suggestion).where(Suggestion.id == suggestion_id)
            ).first()

            if not suggestion:
                raise ValueError(f"Suggestion with ID {suggestion_id} not found")

            # Update the suggestion
            suggestion.accepted = False
            suggestion.dismissed_at = datetime.utcnow()

            # Commit the changes
            session.add(suggestion)
            session.commit()
            session.refresh(suggestion)

            logger.info(f"Suggestion {suggestion_id} marked as dismissed")
            return suggestion

    @staticmethod
    def get_pending_suggestions(user_id: str, limit: int = 10) -> List[Suggestion]:
        """
        Get pending (not accepted or dismissed) suggestions for a user.

        Args:
            user_id: ID of the user to get suggestions for
            limit: Maximum number of suggestions to return

        Returns:
            List of Suggestion objects
        """
        with Session(sync_engine) as session:
            # Query for suggestions that are neither accepted nor dismissed
            query = select(Suggestion).where(
                Suggestion.user_id == user_id
            ).where(
                Suggestion.accepted.is_(None)  # Not yet accepted/dismissed
            ).order_by(Suggestion.created_at.desc()).limit(limit)

            suggestions = session.exec(query).all()
            return suggestions

    @staticmethod
    def _infer_category_from_title(title: str) -> str:
        """
        Infer a category from a task title.

        Args:
            title: Title of the task

        Returns:
            Inferred category
        """
        title_lower = title.lower()

        # Common categories based on keywords
        if any(keyword in title_lower for keyword in ["buy", "shop", "grocery", "purchase", "market"]):
            return "shopping"
        elif any(keyword in title_lower for keyword in ["call", "phone", "contact", "meeting", "zoom"]):
            return "communication"
        elif any(keyword in title_lower for keyword in ["clean", "organize", "tidy", "wash", "laundry"]):
            return "household"
        elif any(keyword in title_lower for keyword in ["exercise", "workout", "run", "gym", "fitness"]):
            return "health"
        elif any(keyword in title_lower for keyword in ["learn", "study", "read", "book", "course"]):
            return "education"
        elif any(keyword in title_lower for keyword in ["work", "project", "report", "meeting", "presentation"]):
            return "work"
        elif any(keyword in title_lower for keyword in ["doctor", "appointment", "medical", "health"]):
            return "health"
        else:
            return "general"