"""
Pattern Recognition Algorithm for MCP Tools
This module implements the pattern recognition algorithm used by the MCP tools for AI suggestions.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select
from mcp.types import TextContent
from ..models import Task
from ..database import sync_engine
from collections import Counter, defaultdict
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternRecognitionAlgorithm:
    """Algorithm class for recognizing patterns in user task data for MCP tools."""

    @staticmethod
    def analyze_user_patterns(user_id: str) -> List[TextContent]:
        """
        Analyze user's task patterns and return structured data for MCP tools.

        Args:
            user_id: ID of the user to analyze patterns for

        Returns:
            List of TextContent with pattern analysis results
        """
        try:
            with Session(sync_engine) as session:
                # Get user's tasks
                all_tasks = session.exec(
                    select(Task).where(Task.user_id == user_id)
                ).all()

                if not all_tasks:
                    result = {
                        "user_id": user_id,
                        "patterns_found": False,
                        "message": "No tasks found for pattern analysis",
                        "recommendation": "Start by adding some tasks to establish patterns"
                    }
                    return [TextContent(type="text", text=str(result))]

                # Analyze patterns
                pattern_analysis = {
                    "user_id": user_id,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "patterns_found": True,
                    "total_tasks": len(all_tasks),
                    "patterns": {
                        "recurring_patterns": PatternRecognitionAlgorithm._analyze_recurring_patterns(all_tasks),
                        "priority_patterns": PatternRecognitionAlgorithm._analyze_priority_patterns(all_tasks),
                        "timing_patterns": PatternRecognitionAlgorithm._analyze_timing_patterns(all_tasks),
                        "category_patterns": PatternRecognitionAlgorithm._analyze_category_patterns(all_tasks),
                        "completion_patterns": PatternRecognitionAlgorithm._analyze_completion_patterns(all_tasks)
                    }
                }

                logger.info(f"Pattern analysis completed for user {user_id}")
                return [TextContent(type="text", text=str(pattern_analysis))]

        except Exception as e:
            logger.error(f"Error in pattern analysis for user {user_id}: {str(e)}")
            error_result = {
                "user_id": user_id,
                "patterns_found": False,
                "error": str(e),
                "message": "Pattern analysis failed"
            }
            return [TextContent(type="text", text=str(error_result))]

    @staticmethod
    def _analyze_recurring_patterns(tasks: List[Task]) -> Dict:
        """
        Analyze recurring patterns in task titles.

        Args:
            tasks: List of user's tasks

        Returns:
            Dictionary with recurring pattern analysis
        """
        # Count occurrences of similar task titles
        title_variations = defaultdict(list)
        for task in tasks:
            # Normalize title for comparison (remove common words, convert to lowercase)
            normalized_title = " ".join(task.title.lower().split())
            title_variations[normalized_title].append(task)

        # Find recurring patterns
        recurring_patterns = []
        for title, task_list in title_variations.items():
            if len(task_list) >= 2:  # At least 2 occurrences
                # Calculate average interval between occurrences
                sorted_tasks = sorted(task_list, key=lambda t: t.created_at)
                intervals = []
                for i in range(1, len(sorted_tasks)):
                    interval = (sorted_tasks[i].created_at - sorted_tasks[i-1].created_at).days
                    if interval > 0:
                        intervals.append(interval)

                avg_interval = sum(intervals) / len(intervals) if intervals else 0

                recurring_patterns.append({
                    "title": title,
                    "frequency": len(task_list),
                    "average_interval_days": round(avg_interval, 2),
                    "last_occurrence": max(t.created_at for t in task_list).isoformat(),
                    "confidence": min(0.95, 0.5 + (len(task_list) * 0.1))
                })

        return {
            "count": len(recurring_patterns),
            "patterns": recurring_patterns
        }

    @staticmethod
    def _analyze_priority_patterns(tasks: List[Task]) -> Dict:
        """
        Analyze priority setting patterns.

        Args:
            tasks: List of user's tasks

        Returns:
            Dictionary with priority pattern analysis
        """
        priority_counts = Counter([task.priority for task in tasks])

        # Identify high-priority patterns
        high_priority_tasks = [task for task in tasks if task.priority == "high"]
        high_priority_titles = Counter([task.title for task in high_priority_tasks])

        # Calculate completion rates by priority
        completion_rates = {}
        for priority in ["low", "medium", "high"]:
            priority_tasks = [t for t in tasks if t.priority == priority]
            if priority_tasks:
                completed = [t for t in priority_tasks if t.is_completed]
                completion_rates[priority] = len(completed) / len(priority_tasks) if priority_tasks else 0
            else:
                completion_rates[priority] = 0

        return {
            "priority_distribution": dict(priority_counts),
            "high_priority_titles": dict(high_priority_titles.most_common(5)),
            "completion_rates_by_priority": completion_rates,
            "total_tasks": len(tasks)
        }

    @staticmethod
    def _analyze_timing_patterns(tasks: List[Task]) -> Dict:
        """
        Analyze timing patterns (day of week, time of day).

        Args:
            tasks: List of user's tasks

        Returns:
            Dictionary with timing pattern analysis
        """
        # Analyze by day of week
        day_of_week_counts = defaultdict(int)
        for task in tasks:
            day = task.created_at.strftime('%A')
            day_of_week_counts[day] += 1

        # Analyze by time of day
        time_of_day_counts = defaultdict(int)
        for task in tasks:
            hour = task.created_at.hour
            if 5 <= hour < 12:
                period = "morning"
            elif 12 <= hour < 17:
                period = "afternoon"
            elif 17 <= hour < 22:
                period = "evening"
            else:
                period = "night"
            time_of_day_counts[period] += 1

        return {
            "by_day_of_week": dict(day_of_week_counts),
            "by_time_of_day": dict(time_of_day_counts),
            "most_active_day": max(day_of_week_counts, key=day_of_week_counts.get) if day_of_week_counts else None,
            "most_active_time": max(time_of_day_counts, key=time_of_day_counts.get) if time_of_day_counts else None
        }

    @staticmethod
    def _analyze_category_patterns(tasks: List[Task]) -> Dict:
        """
        Analyze category patterns in tasks.

        Args:
            tasks: List of user's tasks

        Returns:
            Dictionary with category pattern analysis
        """
        category_counts = defaultdict(int)
        for task in tasks:
            category = task.category or "uncategorized"
            category_counts[category] += 1

        # Find most common categories
        most_common_categories = Counter(category_counts).most_common(10)

        return {
            "category_distribution": dict(category_counts),
            "most_common_categories": [{"category": cat, "count": count} for cat, count in most_common_categories]
        }

    @staticmethod
    def _analyze_completion_patterns(tasks: List[Task]) -> Dict:
        """
        Analyze task completion patterns.

        Args:
            tasks: List of user's tasks

        Returns:
            Dictionary with completion pattern analysis
        """
        completed_tasks = [t for t in tasks if t.is_completed]
        incomplete_tasks = [t for t in tasks if not t.is_completed]

        # Calculate average completion time
        total_completion_time = 0
        completion_count = 0
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                time_diff = (task.completed_at - task.created_at).total_seconds()
                total_completion_time += time_diff
                completion_count += 1

        avg_completion_time = (total_completion_time / completion_count / (24 * 3600)) if completion_count > 0 else 0  # in days

        # Analyze completion by priority
        completion_by_priority = defaultdict(lambda: {"completed": 0, "total": 0})
        for task in tasks:
            completion_by_priority[task.priority]["total"] += 1
            if task.is_completed:
                completion_by_priority[task.priority]["completed"] += 1

        completion_rates_by_priority = {}
        for priority, counts in completion_by_priority.items():
            completion_rates_by_priority[priority] = (
                counts["completed"] / counts["total"] if counts["total"] > 0 else 0
            )

        return {
            "total_completed": len(completed_tasks),
            "total_incomplete": len(incomplete_tasks),
            "completion_rate": len(completed_tasks) / len(tasks) if tasks else 0,
            "average_completion_time_days": round(avg_completion_time, 2),
            "completion_rates_by_priority": completion_rates_by_priority
        }

    @staticmethod
    def generate_suggestions_from_patterns(user_id: str) -> List[TextContent]:
        """
        Generate AI suggestions based on identified patterns.

        Args:
            user_id: ID of the user to generate suggestions for

        Returns:
            List of TextContent with AI-generated suggestions
        """
        try:
            pattern_analysis = PatternRecognitionAlgorithm.analyze_user_patterns(user_id)[0].text
            # Convert string representation back to dictionary
            import ast
            analysis_dict = ast.literal_eval(pattern_analysis)

            if not analysis_dict.get("patterns_found"):
                return [TextContent(type="text", text=str({"suggestions": [], "message": "No patterns found to generate suggestions"}))]

            patterns = analysis_dict["patterns"]
            suggestions = []

            # Generate suggestions based on recurring patterns
            recurring_patterns = patterns["recurring_patterns"]["patterns"]
            for pattern in recurring_patterns:
                if pattern["average_interval_days"] > 0:
                    # Calculate if it's time to repeat this task
                    last_occurrence = datetime.fromisoformat(pattern["last_occurrence"].replace('Z', '+00:00'))
                    next_expected = last_occurrence + timedelta(days=pattern["average_interval_days"])

                    if datetime.utcnow() >= next_expected:
                        suggestions.append({
                            "type": "recurring_task_suggestion",
                            "title": f"Add task: {pattern['title']}",
                            "description": f"Based on your pattern, it's time to add '{pattern['title']}' again (typically done every {pattern['average_interval_days']:.0f} days)",
                            "confidence": pattern["confidence"],
                            "priority": "medium"
                        })

            # Generate suggestions based on completion patterns
            completion_data = patterns["completion_patterns"]
            if completion_data["completion_rate"] < 0.7:
                suggestions.append({
                    "type": "productivity_suggestion",
                    "title": "Improve task completion rate",
                    "description": f"Your task completion rate is {completion_data['completion_rate']*100:.0f}%. Consider breaking large tasks into smaller, manageable parts.",
                    "confidence": 0.8,
                    "priority": "high"
                })

            # Generate suggestions based on timing patterns
            timing_data = patterns["timing_patterns"]
            most_active_day = timing_data.get("most_active_day")
            if most_active_day:
                suggestions.append({
                    "type": "scheduling_suggestion",
                    "title": f"Schedule tasks for {most_active_day}s",
                    "description": f"You're most active on {most_active_day}s. Consider scheduling important tasks on {most_active_day}s for better productivity.",
                    "confidence": 0.7,
                    "priority": "medium"
                })

            result = {
                "user_id": user_id,
                "suggestions_generated": len(suggestions),
                "suggestions": suggestions,
                "message": f"Generated {len(suggestions)} suggestions based on pattern analysis"
            }

            logger.info(f"Generated {len(suggestions)} suggestions for user {user_id}")
            return [TextContent(type="text", text=str(result))]

        except Exception as e:
            logger.error(f"Error generating suggestions from patterns for user {user_id}: {str(e)}")
            error_result = {
                "user_id": user_id,
                "suggestions_generated": 0,
                "suggestions": [],
                "error": str(e),
                "message": "Failed to generate suggestions from patterns"
            }
            return [TextContent(type="text", text=str(error_result))]