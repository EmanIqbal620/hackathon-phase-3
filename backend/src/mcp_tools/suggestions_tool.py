"""
MCP Tool for AI Suggestions
This module provides an MCP tool for generating intelligent task suggestions based on user patterns.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from datetime import datetime, timedelta
from collections import Counter
from ..models import Task
from ...database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuggestionsParams(BaseModel):
    """Parameters for the suggestions MCP tool"""
    user_id: str = Field(..., description="ID of the user to generate suggestions for")
    suggestion_type: Optional[str] = Field("smart", description="Type of suggestions: 'pattern_based', 'priority_based', 'deadline_based', 'smart'")


def suggestions_tool(params: SuggestionsParams) -> List[TextContent]:
    """MCP tool to provide intelligent task suggestions for a user"""
    logger.info(f"Generating {params.suggestion_type} suggestions for user {params.user_id}")

    try:
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == params.user_id)
            ).all()

            # Generate suggestions based on type
            if params.suggestion_type == "pattern_based":
                suggestions = _generate_pattern_based_suggestions(all_tasks, params.user_id)
            elif params.suggestion_type == "priority_based":
                suggestions = _generate_priority_based_suggestions(all_tasks, params.user_id)
            elif params.suggestion_type == "deadline_based":
                suggestions = _generate_deadline_based_suggestions(all_tasks, params.user_id)
            else:  # smart (default)
                suggestions = _generate_smart_suggestions(all_tasks, params.user_id)

            # Prepare suggestions response
            suggestions_data = {
                "success": True,
                "user_id": params.user_id,
                "suggestion_type": params.suggestion_type,
                "suggestions": suggestions,
                "count": len(suggestions)
            }

            logger.info(f"Generated {len(suggestions)} {params.suggestion_type} suggestions for user {params.user_id}")
            return [TextContent(type="text", text=str(suggestions_data))]

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to generate suggestions: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


def _generate_pattern_based_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate suggestions based on user's historical task patterns"""
    suggestions = []

    # Find recurring patterns in task titles
    title_counts = Counter([task.title.lower() for task in tasks])

    # Look for tasks that appear frequently
    frequent_tasks = [(title, count) for title, count in title_counts.items() if count >= 2]

    for title, count in frequent_tasks[:3]:  # Limit to top 3
        # Check if the user has done this task recently
        recent_similar_tasks = [
            task for task in tasks
            if task.title.lower() == title and
            task.created_at and
            (datetime.utcnow() - task.created_at).days < 7  # Within last week
        ]

        # If they haven't done it recently, suggest it
        if not recent_similar_tasks:
            suggestions.append({
                "title": title,
                "description": f"Based on your pattern of adding this task regularly",
                "type": "pattern_based",
                "confidence": min(0.9, 0.5 + (count * 0.1)),  # Higher confidence for more frequent patterns
                "reasoning": f"You usually add '{title}' tasks regularly (appears {count} times in your history)"
            })

    return suggestions


def _generate_priority_based_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate suggestions for high-priority tasks or tasks that should be prioritized"""
    suggestions = []

    # Find incomplete high-priority tasks
    high_priority_tasks = [task for task in tasks if task.priority == "high" and not task.is_completed]

    # Find tasks that have been pending for a long time
    long_pending_tasks = [
        task for task in tasks
        if not task.is_completed and
        task.created_at and
        (datetime.utcnow() - task.created_at).days > 7
    ]

    # Suggest completing high priority tasks
    for task in high_priority_tasks[:2]:  # Limit to top 2
        suggestions.append({
            "title": f"Complete: {task.title}",
            "description": f"This is a high-priority task that requires your attention",
            "type": "priority_based",
            "confidence": 0.85,
            "reasoning": f"'{task.title}' is marked as high priority and should be completed soon"
        })

    # Suggest reviewing long-pending tasks
    for task in long_pending_tasks[:2]:  # Limit to top 2
        suggestions.append({
            "title": f"Review: {task.title}",
            "description": f"This task has been pending for {(datetime.utcnow() - task.created_at).days} days",
            "type": "priority_based",
            "confidence": 0.75,
            "reasoning": f"'{task.title}' has been pending for {(datetime.utcnow() - task.created_at).days} days - consider completing or re-evaluating"
        })

    return suggestions


def _generate_deadline_based_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate suggestions for tasks with approaching deadlines"""
    suggestions = []

    now = datetime.utcnow()

    # Find tasks with due dates in the near future
    upcoming_deadlines = [
        task for task in tasks
        if task.due_date and
        not task.is_completed and
        task.due_date <= now + timedelta(days=3) and  # Due within 3 days
        task.due_date >= now  # Not overdue
    ]

    # Find overdue tasks
    overdue_tasks = [
        task for task in tasks
        if task.due_date and
        not task.is_completed and
        task.due_date < now
    ]

    # Suggest completing upcoming deadlines
    for task in upcoming_deadlines:
        days_until_due = (task.due_date - now).days
        suggestions.append({
            "title": f"Complete by {task.due_date.strftime('%m/%d')}: {task.title}",
            "description": f"This task is due in {days_until_due} day{'s' if days_until_due != 1 else ''}",
            "type": "deadline_based",
            "confidence": 0.9 if days_until_due == 0 else 0.8,  # Higher confidence if due today
            "reasoning": f"'{task.title}' is due on {task.due_date.strftime('%A, %B %d')} ({days_until_due} day{'s' if days_until_due != 1 else ''} from now)"
        })

    # Suggest addressing overdue tasks
    for task in overdue_tasks:
        days_overdue = (now - task.due_date).days
        suggestions.append({
            "title": f"Overdue: {task.title}",
            "description": f"This task was due {days_overdue} day{'s' if days_overdue != 1 else ''} ago",
            "type": "deadline_based",
            "confidence": 0.85,
            "reasoning": f"'{task.title}' was due on {task.due_date.strftime('%A, %B %d')} ({days_overdue} day{'s' if days_overdue != 1 else ''} ago)"
        })

    return suggestions


def _generate_smart_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate comprehensive smart suggestions combining multiple approaches"""
    # Combine all suggestion types
    pattern_suggestions = _generate_pattern_based_suggestions(tasks, user_id)
    priority_suggestions = _generate_priority_based_suggestions(tasks, user_id)
    deadline_suggestions = _generate_deadline_based_suggestions(tasks, user_id)

    # Combine and rank by confidence
    all_suggestions = pattern_suggestions + priority_suggestions + deadline_suggestions

    # Sort by confidence (highest first) and limit to 5
    all_suggestions.sort(key=lambda x: x["confidence"], reverse=True)

    return all_suggestions[:5]  # Return top 5 suggestions