"""
Suggestion Ranking Algorithm
This module provides business logic for ranking AI-generated task suggestions based on priority, frequency, and user behavior.
"""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from ..models.suggestion import Suggestion
from ..models.task import Task
from ..database import sync_engine
from sqlmodel import Session, select
from collections import Counter
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuggestionRankingService:
    """Service class for ranking AI-generated task suggestions."""

    @staticmethod
    def rank_suggestions_by_priority(suggestions: List[Dict], user_id: str) -> List[Dict]:
        """
        Rank suggestions based on priority factors.

        Args:
            suggestions: List of suggestion dictionaries to rank
            user_id: ID of the user the suggestions are for

        Returns:
            List of suggestions ranked by priority
        """
        ranked_suggestions = []

        for suggestion in suggestions:
            # Calculate priority score
            priority_score = SuggestionRankingService._calculate_priority_score(suggestion, user_id)
            suggestion["priority_score"] = priority_score
            ranked_suggestions.append(suggestion)

        # Sort by priority score (highest first)
        ranked_suggestions.sort(key=lambda x: x["priority_score"], reverse=True)

        return ranked_suggestions

    @staticmethod
    def _calculate_priority_score(suggestion: Dict, user_id: str) -> float:
        """
        Calculate a priority score for a suggestion based on multiple factors.

        Args:
            suggestion: Suggestion dictionary to score
            user_id: ID of the user the suggestion is for

        Returns:
            Priority score between 0 and 1
        """
        base_score = suggestion.get("confidence", 0.5)  # Start with confidence score

        # Factor 1: Suggestion type weighting
        type_weights = {
            "deadline_based": 0.9,  # Deadlines are important
            "priority_based": 0.8,  # High priority tasks are important
            "pattern_based": 0.7,   # Pattern-based suggestions are moderately important
            "contextual": 0.6       # Contextual suggestions are somewhat important
        }
        type_weight = type_weights.get(suggestion.get("type", "pattern_based"), 0.5)
        base_score *= type_weight

        # Factor 2: Urgency based on user's historical patterns
        with Session(sync_engine) as session:
            # Get user's tasks to understand their patterns
            user_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            # Calculate urgency based on user's typical behavior
            urgency_factor = SuggestionRankingService._calculate_urgency_factor(
                suggestion, user_tasks
            )
            base_score *= (0.5 + urgency_factor * 0.5)  # Weight urgency factor

        # Factor 3: Recency of similar tasks
        recency_factor = SuggestionRankingService._calculate_recency_factor(
            suggestion, user_id
        )
        base_score *= (0.5 + recency_factor * 0.5)

        # Factor 4: Frequency of similar tasks
        frequency_factor = SuggestionRankingService._calculate_frequency_factor(
            suggestion, user_id
        )
        base_score *= (0.5 + frequency_factor * 0.5)

        # Ensure the score is between 0 and 1
        return min(1.0, max(0.0, base_score))

    @staticmethod
    def _calculate_urgency_factor(suggestion: Dict, user_tasks: List[Task]) -> float:
        """
        Calculate urgency factor based on user's historical task patterns.

        Args:
            suggestion: Suggestion dictionary
            user_tasks: List of user's tasks

        Returns:
            Urgency factor between 0 and 1
        """
        title = suggestion.get("title", "").lower()

        # Check if this is a task the user typically handles urgently
        urgent_task_indicators = [
            "urgent", "asap", "important", "critical", "emergency", "deadline"
        ]

        if any(indicator in title for indicator in urgent_task_indicators):
            return 0.9

        # Check if this is related to a task type the user historically handles quickly
        quick_completion_tasks = []
        for task in user_tasks:
            if task.is_completed and task.created_at and task.completed_at:
                completion_time = (task.completed_at - task.created_at).days
                if completion_time <= 1:  # Completed within 1 day
                    quick_completion_tasks.append(task.title.lower())

        if title in quick_completion_tasks:
            return 0.8

        return 0.3  # Default low urgency

    @staticmethod
    def _calculate_recency_factor(suggestion: Dict, user_id: str) -> float:
        """
        Calculate recency factor based on when user last performed a similar task.

        Args:
            suggestion: Suggestion dictionary
            user_id: ID of the user the suggestion is for

        Returns:
            Recency factor between 0 and 1
        """
        with Session(sync_engine) as session:
            title = suggestion.get("title", "").lower()

            # Get tasks with similar titles
            similar_tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(f"%{title.split()[0] if title.split() else ''}%")  # Match first word
                )
            ).all()

            if not similar_tasks:
                return 0.5  # Neutral if no similar tasks found

            # Find the most recent occurrence
            recent_tasks = [task for task in similar_tasks if task.created_at]
            if not recent_tasks:
                return 0.5

            most_recent = max(recent_tasks, key=lambda t: t.created_at)
            days_since = (datetime.utcnow() - most_recent.created_at).days

            # The longer it's been since a similar task, the higher the recency factor
            # (meaning it's time to do it again)
            if days_since > 30:
                return 0.9  # Long time since last occurrence
            elif days_since > 14:
                return 0.7
            elif days_since > 7:
                return 0.5
            elif days_since > 3:
                return 0.3
            else:
                return 0.1  # Recently done

    @staticmethod
    def _calculate_frequency_factor(suggestion: Dict, user_id: str) -> float:
        """
        Calculate frequency factor based on how often user performs similar tasks.

        Args:
            suggestion: Suggestion dictionary
            user_id: ID of the user the suggestion is for

        Returns:
            Frequency factor between 0 and 1
        """
        with Session(sync_engine) as session:
            title = suggestion.get("title", "").lower()

            # Count similar tasks in user's history
            similar_tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(f"%{title.split()[0] if title.split() else ''}%")  # Match first word
                )
            ).all()

            # Calculate frequency score based on occurrence count
            count = len(similar_tasks)
            if count >= 5:
                return 0.9  # Very frequent
            elif count >= 3:
                return 0.7  # Moderately frequent
            elif count >= 1:
                return 0.5  # Somewhat frequent
            else:
                return 0.2  # Rare

    @staticmethod
    def rank_suggestions_by_user_preferences(suggestions: List[Dict], user_id: str) -> List[Dict]:
        """
        Rank suggestions based on the user's historical preferences and behavior.

        Args:
            suggestions: List of suggestion dictionaries to rank
            user_id: ID of the user the suggestions are for

        Returns:
            List of suggestions ranked by user preferences
        """
        with Session(sync_engine) as session:
            # Get user's task history to understand preferences
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            # Calculate user preference scores for different categories
            category_preferences = SuggestionRankingService._calculate_category_preferences(all_tasks)

            ranked_suggestions = []
            for suggestion in suggestions:
                # Calculate preference score based on user's historical preferences
                category = suggestion.get("category", "general")
                preference_score = category_preferences.get(category, 0.5)

                # Adjust the base score based on user preferences
                adjusted_score = (suggestion.get("priority_score", 0.5) * 0.7) + (preference_score * 0.3)
                suggestion["preference_adjusted_score"] = adjusted_score
                ranked_suggestions.append(suggestion)

            # Sort by adjusted score (highest first)
            ranked_suggestions.sort(key=lambda x: x["preference_adjusted_score"], reverse=True)

            return ranked_suggestions

    @staticmethod
    def _calculate_category_preferences(tasks: List[Task]) -> Dict[str, float]:
        """
        Calculate user's category preferences based on historical task data.

        Args:
            tasks: List of user's tasks

        Returns:
            Dictionary mapping categories to preference scores
        """
        category_counts = Counter()
        completed_counts = Counter()

        for task in tasks:
            category = task.category or "general"
            category_counts[category] += 1

            if task.is_completed:
                completed_counts[category] += 1

        # Calculate completion rates for each category
        category_preferences = {}
        for category, total_count in category_counts.items():
            completed_count = completed_counts[category]
            completion_rate = completed_count / total_count if total_count > 0 else 0

            # Preference score is based on both frequency and completion rate
            frequency_score = min(1.0, total_count / 10)  # Cap frequency at 10 tasks
            preference_score = (frequency_score * 0.6) + (completion_rate * 0.4)
            category_preferences[category] = preference_score

        return category_preferences

    @staticmethod
    def rank_suggestions_by_behavioral_patterns(suggestions: List[Dict], user_id: str) -> List[Dict]:
        """
        Rank suggestions based on behavioral patterns identified in user's task history.

        Args:
            suggestions: List of suggestion dictionaries to rank
            user_id: ID of the user the suggestions are for

        Returns:
            List of suggestions ranked by behavioral patterns
        """
        from .pattern_recognition import PatternRecognitionService

        # Get user's behavioral patterns
        behavior_profile = PatternRecognitionService.get_user_behavior_profile(user_id)

        ranked_suggestions = []
        for suggestion in suggestions:
            # Calculate behavioral pattern score
            pattern_score = SuggestionRankingService._calculate_behavioral_pattern_score(
                suggestion, behavior_profile
            )

            # Adjust the base score based on behavioral patterns
            adjusted_score = (suggestion.get("preference_adjusted_score", 0.5) * 0.6) + (pattern_score * 0.4)
            suggestion["behavioral_adjusted_score"] = adjusted_score
            ranked_suggestions.append(suggestion)

        # Sort by behavioral adjusted score (highest first)
        ranked_suggestions.sort(key=lambda x: x["behavioral_adjusted_score"], reverse=True)

        return ranked_suggestions

    @staticmethod
    def _calculate_behavioral_pattern_score(suggestion: Dict, behavior_profile: Dict) -> float:
        """
        Calculate score based on how well the suggestion aligns with user's behavioral patterns.

        Args:
            suggestion: Suggestion dictionary
            behavior_profile: User's behavioral pattern profile

        Returns:
            Behavioral pattern score between 0 and 1
        """
        score = 0.5  # Base score

        # Check if the suggestion aligns with recurring patterns
        for pattern in behavior_profile.get("recurring_patterns", []):
            if pattern["pattern_type"] == "frequency":
                if pattern["title"] in suggestion.get("title", "").lower():
                    # This matches a recurring pattern, increase score
                    score += pattern["confidence"] * 0.3
                    break

        # Check if the suggestion aligns with priority patterns
        for pattern in behavior_profile.get("priority_patterns", []):
            if pattern["pattern_type"] == "frequently_high_priority":
                if pattern["title"] in suggestion.get("title", "").lower():
                    # This matches a frequently high priority task, increase score
                    score += 0.2
                    break

        # Check if the suggestion aligns with deadline patterns
        for pattern in behavior_profile.get("deadline_patterns", []):
            if pattern["pattern_type"] == "frequently_short_deadline":
                if pattern["title"] in suggestion.get("title", "").lower():
                    # This matches a frequently short deadline task, increase score
                    score += 0.15
                    break

        # Ensure score stays between 0 and 1
        return min(1.0, max(0.0, score))

    @staticmethod
    def get_top_ranked_suggestions(suggestions: List[Dict], user_id: str, limit: int = 5) -> List[Dict]:
        """
        Get the top-ranked suggestions after applying all ranking algorithms.

        Args:
            suggestions: List of suggestion dictionaries to rank
            user_id: ID of the user the suggestions are for
            limit: Maximum number of suggestions to return

        Returns:
            List of top-ranked suggestions
        """
        # Apply priority ranking
        priority_ranked = SuggestionRankingService.rank_suggestions_by_priority(
            suggestions, user_id
        )

        # Apply user preference ranking
        preference_ranked = SuggestionRankingService.rank_suggestions_by_user_preferences(
            priority_ranked, user_id
        )

        # Apply behavioral pattern ranking
        behavioral_ranked = SuggestionRankingService.rank_suggestions_by_behavioral_patterns(
            preference_ranked, user_id
        )

        # Return top suggestions
        return behavioral_ranked[:limit]

    @staticmethod
    def calculate_comprehensive_ranking(suggestion_data: Dict, user_id: str) -> float:
        """
        Calculate a comprehensive ranking score for a single suggestion.

        Args:
            suggestion_data: Suggestion dictionary to score
            user_id: ID of the user the suggestion is for

        Returns:
            Comprehensive ranking score between 0 and 1
        """
        # Calculate all component scores
        priority_score = SuggestionRankingService._calculate_priority_score(
            suggestion_data, user_id
        )

        # Get user preferences
        with Session(sync_engine) as session:
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()
            category_preferences = SuggestionRankingService._calculate_category_preferences(all_tasks)

        # Apply preference adjustment
        category = suggestion_data.get("category", "general")
        preference_score = category_preferences.get(category, 0.5)
        preference_adjusted = (priority_score * 0.7) + (preference_score * 0.3)

        # Get behavioral pattern score
        from .pattern_recognition import PatternRecognitionService
        behavior_profile = PatternRecognitionService.get_user_behavior_profile(user_id)
        pattern_score = SuggestionRankingService._calculate_behavioral_pattern_score(
            suggestion_data, behavior_profile
        )

        # Final comprehensive score
        comprehensive_score = (preference_adjusted * 0.6) + (pattern_score * 0.4)

        return comprehensive_score