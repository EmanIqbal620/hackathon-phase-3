"""
Analytics Service
This module provides business logic for calculating and managing analytics data.
"""
from typing import Dict, List, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from collections import Counter
import uuid
from ..models import Task
from ..models.analytics import AnalyticsData, AnalyticsDataCreate
from ..database import sync_engine
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service class for handling analytics calculations and operations."""

    @staticmethod
    def calculate_user_analytics(user_id: str, time_range: str = "week") -> Dict:
        """
        Calculate analytics for a specific user within a time range.

        Args:
            user_id: ID of the user to calculate analytics for
            time_range: Time range for calculation ('day', 'week', 'month', 'quarter', 'year')

        Returns:
            Dictionary containing calculated analytics metrics
        """
        with Session(sync_engine) as session:
            # Base query for user's tasks with proper indexing considerations
            # Using select with filters to leverage indexes on user_id, created_at, and is_completed
            base_query = select(Task).where(Task.user_id == user_id)

            # Apply time filter based on time_range
            if time_range == "day":
                start_date = datetime.utcnow() - timedelta(days=1)
                base_query = base_query.where(Task.created_at >= start_date)
            elif time_range == "week":
                start_date = datetime.utcnow() - timedelta(weeks=1)
                base_query = base_query.where(Task.created_at >= start_date)
            elif time_range == "month":
                start_date = datetime.utcnow() - timedelta(days=30)
                base_query = base_query.where(Task.created_at >= start_date)
            elif time_range == "quarter":
                start_date = datetime.utcnow() - timedelta(days=90)
                base_query = base_query.where(Task.created_at >= start_date)
            elif time_range == "year":
                start_date = datetime.utcnow() - timedelta(days=365)
                base_query = base_query.where(Task.created_at >= start_date)

            # Execute the query efficiently
            all_tasks = session.exec(base_query).all()

            # Optimized query for completed tasks using a separate query to leverage indexes
            completed_query = select(Task).where(
                Task.user_id == user_id,
                Task.is_completed == True
            )

            # Apply same time filter for completed tasks
            if time_range == "day":
                completed_query = completed_query.where(Task.created_at >= start_date)
            elif time_range == "week":
                completed_query = completed_query.where(Task.created_at >= start_date)
            elif time_range == "month":
                completed_query = completed_query.where(Task.created_at >= start_date)
            elif time_range == "quarter":
                completed_query = completed_query.where(Task.created_at >= start_date)
            elif time_range == "year":
                completed_query = completed_query.where(Task.created_at >= start_date)

            completed_tasks = session.exec(completed_query).all()

            # Calculate metrics using efficient iteration
            total_count = len(all_tasks)
            completed_count = len(completed_tasks)
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

            # Calculate average completion time efficiently
            total_completion_time = 0
            completion_count = 0
            for task in completed_tasks:
                if task.created_at and task.completed_at:
                    time_diff = task.completed_at - task.created_at
                    total_completion_time += time_diff.total_seconds()
                    completion_count += 1

            avg_completion_time = (total_completion_time / completion_count / (24 * 3600)) if completion_count > 0 else 0  # in days

            # Efficiently count tasks by priority using Counter
            from collections import Counter
            priority_counter = Counter(task.priority for task in all_tasks if task.priority)
            priority_counts = {
                "high": priority_counter.get("high", 0),
                "medium": priority_counter.get("medium", 0),
                "low": priority_counter.get("low", 0)
            }

            # Find most productive day of the week efficiently
            day_counter = Counter(
                task.created_at.strftime('%A')
                for task in all_tasks
                if task.created_at
            )
            most_productive_day = day_counter.most_common(1)[0][0] if day_counter else "N/A"

            # Prepare analytics response
            analytics_data = {
                "user_id": user_id,
                "time_range": time_range,
                "date_range_start": start_date,
                "date_range_end": datetime.utcnow(),
                "metrics": {
                    "total_tasks": total_count,
                    "tasks_created": total_count,  # All tasks in the period were created
                    "tasks_completed": completed_count,
                    "tasks_pending": total_count - completed_count,  # More efficient calculation
                    "tasks_missed": 0,  # This would need more complex logic to determine
                    "completion_rate_percent": round(completion_rate, 2),
                    "average_completion_time_days": round(avg_completion_time, 2),
                    "most_productive_day": most_productive_day
                },
                "breakdown": {
                    "by_priority": priority_counts,
                    "by_status": {
                        "completed": completed_count,
                        "pending": total_count - completed_count
                    }
                }
            }

            return analytics_data

    @staticmethod
    def get_trend_data(user_id: str, time_period: str = "week") -> List[Dict]:
        """
        Get trend data for charts and graphs with optimized queries.

        Args:
            user_id: ID of the user to get trend data for
            time_period: Period for trend data ('week', 'month', 'quarter')

        Returns:
            List of dictionaries with daily/hourly breakdown
        """
        with Session(sync_engine) as session:
            # Calculate date range based on time_period
            if time_period == "week":
                start_date = datetime.utcnow() - timedelta(weeks=1)
            elif time_period == "month":
                start_date = datetime.utcnow() - timedelta(days=30)
            else:  # quarter
                start_date = datetime.utcnow() - timedelta(days=90)

            # Optimized query to get both created and completed tasks in a single query
            # by using a union of two queries
            from sqlalchemy import union_all
            from sqlmodel import text

            # Execute both queries separately for better performance with indexes
            created_tasks = session.exec(
                select(Task)
                .where(Task.user_id == user_id, Task.created_at >= start_date)
            ).all()

            completed_tasks = session.exec(
                select(Task)
                .where(
                    Task.user_id == user_id,
                    Task.completed_at >= start_date,
                    Task.is_completed == True
                )
            ).all()

            # Group by day using Counter for efficiency
            from collections import Counter
            created_daily = Counter(task.created_at.date().isoformat() for task in created_tasks)
            completed_daily = Counter(task.completed_at.date().isoformat() for task in completed_tasks if task.completed_at)

            # Combine data
            all_dates = set(created_daily.keys()) | set(completed_daily.keys())
            trend_data = []

            for date in sorted(all_dates):
                created_count = created_daily.get(date, 0)
                completed_count = completed_daily.get(date, 0)

                trend_data.append({
                    "date": date,
                    "tasks_created": created_count,
                    "tasks_completed": completed_count,
                    "tasks_pending": max(0, created_count - completed_count)
                })

            return trend_data

    @staticmethod
    def save_analytics_to_db(analytics_data: Dict) -> AnalyticsData:
        """
        Save calculated analytics to the database.

        Args:
            analytics_data: Dictionary containing analytics data to save

        Returns:
            Saved AnalyticsData object
        """
        with Session(sync_engine) as session:
            # Create analytics data object
            analytics_create = AnalyticsDataCreate(
                user_id=analytics_data["user_id"],
                metric_type=analytics_data["time_range"],
                date_range_start=analytics_data["date_range_start"],
                date_range_end=analytics_data["date_range_end"],
                tasks_created=analytics_data["metrics"]["tasks_created"],
                tasks_completed=analytics_data["metrics"]["tasks_completed"],
                tasks_missed=analytics_data["metrics"]["tasks_missed"],
                average_completion_time=analytics_data["metrics"]["average_completion_time_days"],
                productivity_score=analytics_data["metrics"]["completion_rate_percent"]
            )

            # Create the analytics data instance
            analytics_record = AnalyticsData.model_validate(analytics_create)

            # Add to the session and commit
            session.add(analytics_record)
            session.commit()
            session.refresh(analytics_record)

            logger.info(f"Analytics saved to database with ID: {analytics_record.id}")
            return analytics_record

    @staticmethod
    def get_trend_data(user_id: str, time_period: str = "week") -> List[Dict]:
        """
        Get trend data for charts and graphs with optimized queries.

        Args:
            user_id: ID of the user to get trend data for
            time_period: Period for trend data ('week', 'month', 'quarter')

        Returns:
            List of dictionaries with daily/hourly breakdown
        """
        with Session(sync_engine) as session:
            # Calculate date range based on time_period
            if time_period == "week":
                start_date = datetime.utcnow() - timedelta(weeks=1)
            elif time_period == "month":
                start_date = datetime.utcnow() - timedelta(days=30)
            else:  # quarter
                start_date = datetime.utcnow() - timedelta(days=90)

            # Optimized query to get both created and completed tasks in a single query
            # by using a union of two queries
            from sqlalchemy import union_all
            from sqlmodel import text

            # Execute both queries separately for better performance with indexes
            created_tasks = session.exec(
                select(Task)
                .where(Task.user_id == user_id, Task.created_at >= start_date)
            ).all()

            completed_tasks = session.exec(
                select(Task)
                .where(
                    Task.user_id == user_id,
                    Task.completed_at >= start_date,
                    Task.is_completed == True
                )
            ).all()

            # Group by day using Counter for efficiency
            from collections import Counter
            created_daily = Counter(task.created_at.date().isoformat() for task in created_tasks)
            completed_daily = Counter(task.completed_at.date().isoformat() for task in completed_tasks if task.completed_at)

            # Combine data
            all_dates = set(created_daily.keys()) | set(completed_daily.keys())
            trend_data = []

            for date in sorted(all_dates):
                created_count = created_daily.get(date, 0)
                completed_count = completed_daily.get(date, 0)

                trend_data.append({
                    "date": date,
                    "tasks_created": created_count,
                    "tasks_completed": completed_count,
                    "tasks_pending": max(0, created_count - completed_count)
                })

            return trend_data

    @staticmethod
    def get_productivity_score(user_id: str) -> float:
        """
        Calculate a productivity score for the user based on various metrics.

        Args:
            user_id: ID of the user to calculate productivity score for

        Returns:
            Productivity score (0-100)
        """
        # Get user analytics
        analytics = AnalyticsService.calculate_user_analytics(user_id, "week")

        # Calculate productivity score based on multiple factors
        completion_rate = analytics["metrics"]["completion_rate_percent"]
        avg_completion_time = analytics["metrics"]["average_completion_time_days"]
        priority_balance = analytics["breakdown"]["by_priority"]["high"] / max(
            analytics["metrics"]["total_tasks"], 1
        )

        # Base score on completion rate (40%), completion speed (30%), and priority management (30%)
        score = (
            (completion_rate * 0.4) +
            (min(100, 100 / max(avg_completion_time, 1)) * 0.3) +
            (min(100, priority_balance * 100) * 0.3)
        )

        return min(100, max(0, score))  # Clamp between 0 and 100

    @staticmethod
    def generate_suggestions_from_analytics(user_id: str) -> List[Dict]:
        """
        Generate AI-powered suggestions based on user's analytics data.

        Args:
            user_id: ID of the user to generate suggestions for

        Returns:
            List of suggestion dictionaries
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

        suggestions = []

        # Get analytics to inform suggestions
        analytics = AnalyticsService.calculate_user_analytics(user_id, "week")

        # Suggest improvement if completion rate is low
        if analytics["metrics"]["completion_rate_percent"] < 70:
            suggestions.append({
                "id": f"suggestion-{uuid.uuid4()}",
                "title": "Improve Task Completion Rate",
                "description": f"Your current completion rate is {analytics['metrics']['completion_rate_percent']}%. Try breaking large tasks into smaller, manageable chunks.",
                "type": "productivity_tips",
                "confidence": 0.75,
                "reasoning": "Low completion rate suggests tasks may be too large or overwhelming"
            })

        # Suggest focusing on high-priority tasks if many are pending
        high_priority_pending = analytics["breakdown"]["by_priority"]["high"] - analytics["breakdown"]["by_priority_completed"]["high"]
        if high_priority_pending > 3:
            suggestions.append({
                "id": f"suggestion-{uuid.uuid4()}",
                "title": "Focus on High Priority Tasks",
                "description": f"You have {high_priority_pending} high priority tasks pending. Consider focusing on these first.",
                "type": "priority_management",
                "confidence": 0.8,
                "reasoning": "Multiple high priority tasks are pending which may impact important goals"
            })

        # Suggest time management if average completion time is high
        if analytics["metrics"]["average_completion_time_days"] > 7:
            suggestions.append({
                "id": f"suggestion-{uuid.uuid4()}",
                "title": "Reduce Task Completion Time",
                "description": f"Your average task completion time is {analytics['metrics']['average_completion_time_days']} days. Consider setting deadlines or breaking tasks into steps.",
                "type": "time_management",
                "confidence": 0.7,
                "reasoning": "Long average completion time may indicate tasks are too large or procrastination"
            })

        # Find patterns in task creation (e.g., recurring tasks that haven't been done recently)
        title_counts = Counter(task.title.lower() for task in all_tasks)
        recurring_tasks = [title for title, count in title_counts.items() if count >= 3]

        for title in recurring_tasks[:3]:  # Limit to top 3
            # Check if this task has been done recently
            recent_occurrences = [
                task for task in all_tasks
                if task.title.lower() == title and
                task.created_at and
                (datetime.utcnow() - task.created_at).days < 7
            ]

            if not recent_occurrences:
                # This is a recurring task that hasn't been done recently
                suggestions.append({
                    "id": f"suggestion-{uuid.uuid4()}",
                    "title": f"Add recurring task: {title}",
                    "description": f"You regularly add '{title}' tasks but haven't added one recently",
                    "type": "pattern_based",
                    "confidence": 0.85,
                    "reasoning": f"'{title}' appears {title_counts[title]} times in your history, suggesting a recurring pattern"
                })

        return suggestions