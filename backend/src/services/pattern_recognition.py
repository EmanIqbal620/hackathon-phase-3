"""
Pattern Recognition Service
This module provides business logic for identifying patterns in user task data to generate intelligent suggestions.
"""
from typing import Dict, List, Tuple, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from ..models import Task
from ..database import sync_engine
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternRecognitionService:
    """Service class for identifying patterns in user task data."""

    @staticmethod
    def identify_recurring_patterns(user_id: str) -> List[Dict]:
        """
        Identify recurring patterns in user's task behavior.

        Args:
            user_id: ID of the user to analyze patterns for

        Returns:
            List of dictionaries describing identified patterns
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            patterns = []

            # Identify patterns by title frequency
            title_frequency = Counter([task.title.lower() for task in all_tasks])
            frequent_titles = [title for title, count in title_frequency.items() if count >= 2]

            for title in frequent_titles:
                occurrences = [task for task in all_tasks if task.title.lower() == title]

                # Calculate average frequency
                if len(occurrences) > 1:
                    # Calculate average interval between occurrences
                    sorted_tasks = sorted(occurrences, key=lambda t: t.created_at)
                    intervals = []
                    for i in range(1, len(sorted_tasks)):
                        interval = (sorted_tasks[i].created_at - sorted_tasks[i-1].created_at).days
                        if interval > 0:  # Only count positive intervals
                            intervals.append(interval)

                    avg_interval = sum(intervals) / len(intervals) if intervals else 0

                    patterns.append({
                        "pattern_type": "frequency",
                        "title": title,
                        "frequency_count": len(occurrences),
                        "average_interval_days": round(avg_interval, 2),
                        "last_occurrence": max(task.created_at for task in occurrences).isoformat(),
                        "confidence": min(0.95, 0.5 + (len(occurrences) * 0.1))  # Higher confidence for more occurrences
                    })

            # Identify patterns by day of week
            day_patterns = defaultdict(list)
            for task in all_tasks:
                day_of_week = task.created_at.strftime('%A')
                day_patterns[day_of_week].append(task.title.lower())

            for day, titles in day_patterns.items():
                if len(titles) >= 2:  # At least 2 tasks on this day
                    title_counts = Counter(titles)
                    most_common_title = title_counts.most_common(1)[0]

                    patterns.append({
                        "pattern_type": "day_of_week",
                        "day_of_week": day,
                        "common_task": most_common_title[0],
                        "task_count_on_day": len(titles),
                        "confidence": min(0.9, 0.4 + (len(titles) * 0.1))
                    })

            # Identify patterns by time of day
            time_patterns = defaultdict(list)
            for task in all_tasks:
                hour = task.created_at.hour
                # Group hours into time periods
                if 5 <= hour < 12:
                    period = "morning"
                elif 12 <= hour < 17:
                    period = "afternoon"
                elif 17 <= hour < 22:
                    period = "evening"
                else:
                    period = "night"

                time_patterns[period].append(task.title.lower())

            for period, titles in time_patterns.items():
                if len(titles) >= 2:  # At least 2 tasks in this time period
                    title_counts = Counter(titles)
                    most_common_title = title_counts.most_common(1)[0]

                    patterns.append({
                        "pattern_type": "time_of_day",
                        "time_period": period,
                        "common_task": most_common_title[0],
                        "task_count_in_period": len(titles),
                        "confidence": min(0.85, 0.3 + (len(titles) * 0.08))
                    })

            return patterns

    @staticmethod
    def identify_priority_patterns(user_id: str) -> List[Dict]:
        """
        Identify patterns in user's priority-setting behavior.

        Args:
            user_id: ID of the user to analyze priority patterns for

        Returns:
            List of dictionaries describing priority patterns
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            if not all_tasks:
                return []

            # Count tasks by priority
            priority_counts = Counter([task.priority for task in all_tasks if task.priority])

            # Identify patterns where user tends to set high priority
            high_priority_tasks = [task for task in all_tasks if task.priority == "high"]

            patterns = [{
                "pattern_type": "priority_distribution",
                "distribution": dict(priority_counts),
                "total_tasks": len(all_tasks),
                "percentage_high": round((priority_counts.get("high", 0) / len(all_tasks)) * 100, 2),
                "percentage_medium": round((priority_counts.get("medium", 0) / len(all_tasks)) * 100, 2),
                "percentage_low": round((priority_counts.get("low", 0) / len(all_tasks)) * 100, 2)
            }]

            # Look for titles that are frequently set as high priority
            high_priority_titles = Counter([task.title.lower() for task in high_priority_tasks])
            frequent_high_priority = [title for title, count in high_priority_titles.items() if count >= 2]

            for title in frequent_high_priority:
                patterns.append({
                    "pattern_type": "frequently_high_priority",
                    "title": title,
                    "high_priority_count": high_priority_titles[title],
                    "confidence": min(0.95, 0.6 + (high_priority_titles[title] * 0.1))
                })

            return patterns

    @staticmethod
    def identify_deadline_patterns(user_id: str) -> List[Dict]:
        """
        Identify patterns in user's deadline-setting and completion behavior.

        Args:
            user_id: ID of the user to analyze deadline patterns for

        Returns:
            List of dictionaries describing deadline patterns
        """
        with Session(sync_engine) as session:
            # Get user's tasks with due dates
            tasks_with_deadlines = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.due_date.is_not(None)
                )
            ).all()

            patterns = []

            if not tasks_with_deadlines:
                return patterns

            # Analyze completion relative to deadlines
            completed_on_time = 0
            completed_late = 0
            missed = 0

            for task in tasks_with_deadlines:
                if task.is_completed and task.completed_at:
                    if task.completed_at <= task.due_date:
                        completed_on_time += 1
                    else:
                        completed_late += 1
                elif not task.is_completed and task.due_date < datetime.utcnow():
                    missed += 1

            total_deadline_tasks = len(tasks_with_deadlines)
            if total_deadline_tasks > 0:
                patterns.append({
                    "pattern_type": "deadline_performance",
                    "total_tasks_with_deadlines": total_deadline_tasks,
                    "completed_on_time": completed_on_time,
                    "completed_late": completed_late,
                    "missed_after_deadline": missed,
                    "on_time_rate": round((completed_on_time / total_deadline_tasks) * 100, 2),
                    "late_rate": round((completed_late / total_deadline_tasks) * 100, 2)
                })

            # Identify tasks that are frequently set with short deadlines
            short_deadline_tasks = []
            for task in tasks_with_deadlines:
                if task.created_at and task.due_date:
                    lead_time = (task.due_date - task.created_at).days
                    if 0 < lead_time <= 2:  # Set with 2 days or less notice
                        short_deadline_tasks.append(task.title.lower())

            if short_deadline_tasks:
                frequent_short_deadline = Counter(short_deadline_tasks).most_common(3)
                for title, count in frequent_short_deadline:
                    patterns.append({
                        "pattern_type": "frequently_short_deadline",
                        "title": title,
                        "short_deadline_count": count,
                        "confidence": min(0.9, 0.5 + (count * 0.15))
                    })

            return patterns

    @staticmethod
    def identify_contextual_patterns(user_id: str) -> List[Dict]:
        """
        Identify contextual patterns in user's task behavior.

        Args:
            user_id: ID of the user to analyze contextual patterns for

        Returns:
            List of dictionaries describing contextual patterns
        """
        with Session(sync_engine) as session:
            # Get user's tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            patterns = []

            # Identify task sequences (what tasks tend to follow others)
            task_sequences = []
            sorted_tasks = sorted(all_tasks, key=lambda t: t.created_at)

            for i in range(len(sorted_tasks) - 1):
                current_task = sorted_tasks[i]
                next_task = sorted_tasks[i + 1]

                # Check if there's a temporal relationship (within a few days)
                time_diff = (next_task.created_at - current_task.created_at).days
                if 0 < time_diff <= 3:  # Within 3 days
                    task_sequences.append((current_task.title.lower(), next_task.title.lower()))

            # Count common sequences
            sequence_counter = Counter(task_sequences)
            common_sequences = sequence_counter.most_common(5)

            for (prev_task, next_task), count in common_sequences:
                if count >= 2:  # At least 2 occurrences
                    patterns.append({
                        "pattern_type": "task_sequence",
                        "previous_task": prev_task,
                        "following_task": next_task,
                        "sequence_count": count,
                        "confidence": min(0.95, 0.6 + (count * 0.1))
                    })

            # Identify seasonal patterns (if enough historical data)
            monthly_counts = defaultdict(int)
            for task in all_tasks:
                month = task.created_at.month
                monthly_counts[month] += 1

            # Find months with unusually high task creation
            avg_monthly_count = sum(monthly_counts.values()) / len(monthly_counts) if monthly_counts else 0
            seasonal_peaks = {month: count for month, count in monthly_counts.items()
                              if count > avg_monthly_count * 1.5}  # 50% above average

            for month, count in seasonal_peaks.items():
                month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                patterns.append({
                    "pattern_type": "seasonal_peak",
                    "month": month_names[month - 1],
                    "task_count": count,
                    "confidence": 0.7
                })

            return patterns

    @staticmethod
    def generate_prediction_insights(user_id: str) -> List[Dict]:
        """
        Generate prediction insights based on identified patterns.

        Args:
            user_id: ID of the user to generate predictions for

        Returns:
            List of dictionaries with predictive insights
        """
        # Get all patterns
        recurring_patterns = PatternRecognitionService.identify_recurring_patterns(user_id)
        priority_patterns = PatternRecognitionService.identify_priority_patterns(user_id)
        deadline_patterns = PatternRecognitionService.identify_deadline_patterns(user_id)
        contextual_patterns = PatternRecognitionService.identify_contextual_patterns(user_id)

        insights = []

        # Generate insights from recurring patterns
        for pattern in recurring_patterns:
            if pattern["pattern_type"] == "frequency" and pattern["average_interval_days"] > 0:
                next_expected = datetime.utcnow() + timedelta(days=round(pattern["average_interval_days"]))
                insights.append({
                    "type": "prediction",
                    "category": "recurring_task",
                    "title": f"Consider adding '{pattern['title']}' task",
                    "description": f"Based on your pattern, you typically add this task every {pattern['average_interval_days']} days. It's been {pattern['average_interval_days']} days since the last occurrence.",
                    "predicted_date": next_expected.isoformat(),
                    "confidence": pattern["confidence"]
                })

        # Generate insights from deadline patterns
        for pattern in deadline_patterns:
            if pattern["pattern_type"] == "deadline_performance":
                if pattern["late_rate"] > 30:  # More than 30% late
                    insights.append({
                        "type": "recommendation",
                        "category": "deadline_management",
                        "title": "Improve deadline management",
                        "description": f"You complete {pattern['late_rate']}% of tasks after their deadline. Consider setting earlier deadlines or breaking tasks into smaller parts.",
                        "confidence": 0.8
                    })

        # Generate insights from priority patterns
        for pattern in priority_patterns:
            if pattern["pattern_type"] == "priority_distribution" and pattern["percentage_high"] > 60:
                insights.append({
                    "type": "recommendation",
                    "category": "priority_setting",
                    "title": "Review priority settings",
                    "description": f"You set {pattern['percentage_high']}% of tasks as high priority. Consider reserving high priority for truly critical tasks.",
                    "confidence": 0.75
                })

        return insights

    @staticmethod
    def get_user_behavior_profile(user_id: str) -> Dict:
        """
        Get a comprehensive profile of the user's task behavior patterns.

        Args:
            user_id: ID of the user to analyze

        Returns:
            Dictionary containing the user's behavior profile
        """
        recurring_patterns = PatternRecognitionService.identify_recurring_patterns(user_id)
        priority_patterns = PatternRecognitionService.identify_priority_patterns(user_id)
        deadline_patterns = PatternRecognitionService.identify_deadline_patterns(user_id)
        contextual_patterns = PatternRecognitionService.identify_contextual_patterns(user_id)
        predictions = PatternRecognitionService.generate_prediction_insights(user_id)

        profile = {
            "user_id": user_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "patterns_summary": {
                "recurring_patterns_count": len(recurring_patterns),
                "priority_patterns_count": len(priority_patterns),
                "deadline_patterns_count": len(deadline_patterns),
                "contextual_patterns_count": len(contextual_patterns)
            },
            "recurring_patterns": recurring_patterns,
            "priority_patterns": priority_patterns,
            "deadline_patterns": deadline_patterns,
            "contextual_patterns": contextual_patterns,
            "predictions": predictions,
            "overall_insights_count": len(predictions)
        }

        return profile