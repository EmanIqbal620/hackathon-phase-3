"""
MCP Tool for Analytics
This module provides an MCP tool for retrieving and analyzing user task data.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from mcp.types import TextContent
import logging
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from ..models.task import Task
from ..database import sync_engine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsParams(BaseModel):
    """Parameters for the analytics MCP tool"""
    user_id: str = Field(..., description="ID of the user to get analytics for")
    time_range: Optional[str] = Field("week", description="Time range for analytics: 'day', 'week', 'month', 'quarter', 'year'")


def analytics_tool(params: AnalyticsParams) -> List[TextContent]:
    """MCP tool to provide task analytics and insights for a user"""
    logger.info(f"Generating analytics for user {params.user_id}, time range: {params.time_range}")

    try:
        with Session(sync_engine) as session:
            # Base query for user's tasks
            base_query = select(Task).where(Task.user_id == params.user_id)

            # Apply time filter based on time_range
            if params.time_range == "day":
                start_date = datetime.utcnow() - timedelta(days=1)
                base_query = base_query.where(Task.created_at >= start_date)
            elif params.time_range == "week":
                start_date = datetime.utcnow() - timedelta(weeks=1)
                base_query = base_query.where(Task.created_at >= start_date)
            elif params.time_range == "month":
                start_date = datetime.utcnow() - timedelta(days=30)
                base_query = base_query.where(Task.created_at >= start_date)
            elif params.time_range == "quarter":
                start_date = datetime.utcnow() - timedelta(days=90)
                base_query = base_query.where(Task.created_at >= start_date)
            elif params.time_range == "year":
                start_date = datetime.utcnow() - timedelta(days=365)
                base_query = base_query.where(Task.created_at >= start_date)

            # Get all tasks for the user/time range
            all_tasks = session.exec(base_query).all()

            # Get completed tasks
            completed_query = base_query.where(Task.is_completed == True)
            completed_tasks = session.exec(completed_query).all()

            # Get pending tasks
            pending_tasks = [task for task in all_tasks if not task.is_completed]

            # Calculate metrics
            total_count = len(all_tasks)
            completed_count = len(completed_tasks)
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

            # Calculate average completion time
            total_completion_time = 0
            completion_count = 0
            for task in completed_tasks:
                if task.created_at and task.completed_at:
                    time_diff = (task.completed_at - task.created_at).total_seconds()
                    total_completion_time += time_diff
                    completion_count += 1

            avg_completion_time = (total_completion_time / completion_count / (24 * 3600)) if completion_count > 0 else 0  # in days

            # Count tasks by priority
            priority_counts = {"high": 0, "medium": 0, "low": 0}
            for task in all_tasks:
                if task.priority in priority_counts:
                    priority_counts[task.priority] += 1

            # Find most productive day of the week
            day_counts = {}
            for task in all_tasks:
                if task.created_at:
                    day_of_week = task.created_at.strftime('%A')
                    day_counts[day_of_week] = day_counts.get(day_of_week, 0) + 1

            most_productive_day = max(day_counts, key=day_counts.get) if day_counts else "N/A"

            # Prepare analytics response
            analytics_data = {
                "success": True,
                "user_id": params.user_id,
                "time_range": params.time_range,
                "metrics": {
                    "total_tasks": total_count,
                    "tasks_created": total_count,
                    "tasks_completed": completed_count,
                    "tasks_pending": len(pending_tasks),
                    "tasks_missed": 0,  # This would require more complex logic to determine
                    "completion_rate_percent": round(completion_rate, 2),
                    "average_completion_time_days": round(avg_completion_time, 2),
                    "most_productive_day": most_productive_day
                },
                "breakdown": {
                    "by_priority": priority_counts,
                    "by_status": {
                        "completed": completed_count,
                        "pending": len(pending_tasks)
                    }
                },
                "insights": generate_insights(total_count, completion_rate, avg_completion_time, priority_counts)
            }

            logger.info(f"Generated analytics for user {params.user_id}")
            return [TextContent(type="text", text=str(analytics_data))]

    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Failed to generate analytics: {str(e)}"
        }
        return [TextContent(type="text", text=str(error_response))]


def generate_insights(total_tasks: int, completion_rate: float, avg_completion_time: float, priority_counts: Dict) -> List[str]:
    """Generate insights based on the analytics data"""
    insights = []

    if total_tasks > 0:
        insights.append(f"You've created {total_tasks} tasks in this period.")

    if completion_rate >= 80:
        insights.append("Excellent! Your task completion rate is very high.")
    elif completion_rate >= 60:
        insights.append("Good job! You're completing a solid portion of your tasks.")
    else:
        insights.append("Consider focusing on completing more of your started tasks.")

    if avg_completion_time > 0:
        insights.append(f"On average, you complete tasks in {avg_completion_time:.1f} days.")

    if priority_counts['high'] > priority_counts['medium'] and priority_counts['high'] > priority_counts['low']:
        insights.append("You tend to create many high-priority tasks.")

    return insights