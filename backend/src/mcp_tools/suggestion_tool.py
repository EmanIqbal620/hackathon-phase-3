"""
MCP Tool for providing task suggestions
This tool allows the AI agent to generate context-aware task suggestions based on user's task patterns.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from mcp.types import TextContent
import logging
from sqlmodel import Session, select
from ..models import Task
from ...database import sync_engine
from datetime import datetime, timedelta
from collections import Counter


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuggestionParams(BaseModel):
    """Parameters for the suggestion MCP tool"""
    user_id: str = Field(..., description="ID of the user to get suggestions for")
    suggestion_type: Optional[str] = Field("pattern_based", description="Type of suggestion: 'pattern_based', 'priority_based', 'deadline_based', 'contextual'")


def suggestion_tool(params: SuggestionParams) -> List[TextContent]:
    """MCP tool to provide task suggestions for a user based on patterns and context"""
    logger.info(f"Generating suggestions for user {params.user_id}, type: {params.suggestion_type}")

    try:
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == params.user_id)
            ).all()

            # Generate suggestions based on the type
            if params.suggestion_type == "pattern_based":
                suggestions = generate_pattern_based_suggestions(all_tasks, params.user_id)
            elif params.suggestion_type == "priority_based":
                suggestions = generate_priority_based_suggestions(all_tasks, params.user_id)
            elif params.suggestion_type == "deadline_based":
                suggestions = generate_deadline_based_suggestions(all_tasks, params.user_id)
            elif params.suggestion_type == "contextual":
                suggestions = generate_contextual_suggestions(all_tasks, params.user_id)
            else:
                suggestions = generate_pattern_based_suggestions(all_tasks, params.user_id)

            # Prepare suggestions response
            suggestions_data = {
                "success": True,
                "suggestion_type": params.suggestion_type,
                "suggestions": suggestions,
                "count": len(suggestions)
            }

            logger.info(f"Generated {len(suggestions)} suggestions for user {params.user_id}")
            return [TextContent(type="text", text=str(suggestions_data))]

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to generate suggestions: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


def generate_pattern_based_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate suggestions based on user's historical task patterns"""
    suggestions = []

    # Find recurring patterns in task titles
    title_patterns = Counter([task.title.lower() for task in tasks])

    # Look for tasks that appear frequently
    frequent_tasks = [(title, count) for title, count in title_patterns.items() if count >= 2]

    for title, count in frequent_tasks[:3]:  # Limit to top 3
        # Check if the user has done this task recently
        recent_similar_tasks = [
            task for task in tasks
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
                "reasoning": f"You usually add '{title}' tasks regularly (appears {count} times in your history)"
            })

    return suggestions


def generate_priority_based_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate suggestions for high-priority tasks or tasks that should be prioritized"""
    suggestions = []

    # Find incomplete high-priority tasks
    high_priority_tasks = [task for task in tasks if task.priority == "high" and not task.completed]

    # Find tasks that have been pending for a long time
    long_pending_tasks = [
        task for task in tasks
        if not task.completed and
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


def generate_deadline_based_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate suggestions for tasks with approaching deadlines"""
    suggestions = []

    # Find tasks with due dates in the near future
    now = datetime.utcnow()
    upcoming_deadlines = [
        task for task in tasks
        if task.due_date and
        not task.completed and
        task.due_date <= now + timedelta(days=3) and  # Due within 3 days
        task.due_date >= now  # Not overdue
    ]

    # Find overdue tasks
    overdue_tasks = [
        task for task in tasks
        if task.due_date and
        not task.completed and
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


def generate_contextual_suggestions(tasks: List[Task], user_id: str) -> List[Dict]:
    """Generate contextual suggestions based on task relationships and patterns"""
    suggestions = []

    # Find tasks that might be related to recent completions
    recently_completed = [
        task for task in tasks
        if task.completed and
        task.completed_at and
        (datetime.utcnow() - task.completed_at).days <= 2
    ]

    # Suggest follow-up tasks based on completed tasks
    for task in recently_completed[:2]:
        # Create a follow-up suggestion based on the completed task
        follow_up_title = f"Follow-up: {task.title}"
        suggestions.append({
            "title": follow_up_title,
            "description": f"Consider follow-up actions for '{task.title}'",
            "type": "contextual",
            "confidence": 0.7,
            "reasoning": f"Since you recently completed '{task.title}', you might want to do follow-up actions"
        })

    # Suggest tasks based on common sequences
    # For example, if a user often does certain tasks after others
    if len(tasks) >= 2:
        # This is a simplified version - in reality, you'd want more sophisticated pattern analysis
        last_task = max(tasks, key=lambda t: t.created_at if t.created_at else datetime.min)
        if last_task.title.lower().startswith("buy"):
            # Suggest related tasks after buying something
            suggestions.append({
                "title": "Organize purchases",
                "description": "Consider organizing or putting away your recent purchases",
                "type": "contextual",
                "confidence": 0.6,
                "reasoning": "You recently added a purchase-related task, so organizing might be relevant"
            })

    return suggestions


# Mock function for testing purposes
def mock_suggestion_tool(params: SuggestionParams) -> List[TextContent]:
    """Mock implementation for testing"""
    logger.info(f"(MOCK) Generating suggestions for user {params.user_id}, type: {params.suggestion_type}")

    # In a real implementation, this would analyze user's task patterns
    # For now, we return mock suggestions
    mock_suggestions = {
        "success": True,
        "suggestion_type": params.suggestion_type,
        "suggestions": [
            {
                "title": "Buy groceries",
                "description": "Weekly grocery shopping based on your pattern",
                "type": "pattern_based",
                "confidence": 0.85,
                "reasoning": "You usually add grocery shopping tasks on Sundays"
            },
            {
                "title": "Complete project proposal",
                "description": "High-priority task that requires immediate attention",
                "type": "priority_based",
                "confidence": 0.9,
                "reasoning": "This is marked as high priority and should be completed soon"
            }
        ],
        "count": 2
    }

    return [TextContent(type="text", text=str(mock_suggestions))]