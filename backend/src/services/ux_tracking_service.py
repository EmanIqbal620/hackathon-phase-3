"""
UX Tracking Service
This module provides business logic for tracking and analyzing user experience interactions.
"""
from typing import Dict, List, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models import Task
from ..models.ux_enhancement import UXEnhancement, UXEnhancementCreate
from ..database import sync_engine
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UXTrackingService:
    """Service class for tracking and analyzing user experience interactions."""

    @staticmethod
    def track_user_interaction(
        user_id: str,
        interaction_type: str,
        task_id: Optional[str] = None,
        enhancement_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> UXEnhancement:
        """
        Track a user interaction with the system.

        Args:
            user_id: ID of the user interacting
            interaction_type: Type of interaction ('click', 'hover', 'scroll', 'task_action', 'theme_toggle', etc.)
            task_id: Optional ID of the task involved in the interaction
            enhancement_type: Optional type of UX enhancement ('animation', 'micro_interaction', 'theme_transition', etc.)
            metadata: Optional additional metadata about the interaction

        Returns:
            Created UXEnhancement record
        """
        with Session(sync_engine) as session:
            # Create UX enhancement tracking record
            ux_enhancement_data = UXEnhancementCreate(
                user_id=user_id,
                enhancement_type=enhancement_type or interaction_type,
                feature_name=interaction_type,
                usage_count=1,
                effectiveness_rating=None,  # To be set later based on outcome
                feedback=None,  # To be set later by user
                metadata=metadata
            )

            # Create the UX enhancement instance
            ux_enhancement = UXEnhancement.model_validate(ux_enhancement_data)

            # Add to session and commit
            session.add(ux_enhancement)
            session.commit()
            session.refresh(ux_enhancement)

            logger.info(f"Tracked UX interaction: {interaction_type} for user {user_id}")
            return ux_enhancement

    @staticmethod
    def update_interaction_effectiveness(
        ux_enhancement_id: str,
        effectiveness_rating: float,
        feedback: Optional[str] = None
    ) -> UXEnhancement:
        """
        Update the effectiveness rating of a UX enhancement based on user outcome.

        Args:
            ux_enhancement_id: ID of the UX enhancement to update
            effectiveness_rating: Rating from 0 to 1 indicating effectiveness
            feedback: Optional user feedback

        Returns:
            Updated UXEnhancement record
        """
        with Session(sync_engine) as session:
            # Get the UX enhancement
            ux_enhancement = session.exec(
                select(UXEnhancement).where(UXEnhancement.id == ux_enhancement_id)
            ).first()

            if not ux_enhancement:
                raise ValueError(f"UX Enhancement with ID {ux_enhancement_id} not found")

            # Update the effectiveness rating and feedback
            ux_enhancement.effectiveness_rating = effectiveness_rating
            if feedback:
                ux_enhancement.feedback = feedback
            ux_enhancement.updated_at = datetime.utcnow()

            # Commit the changes
            session.add(ux_enhancement)
            session.commit()
            session.refresh(ux_enhancement)

            logger.info(f"Updated effectiveness rating for UX enhancement {ux_enhancement_id}: {effectiveness_rating}")
            return ux_enhancement

    @staticmethod
    def get_user_interaction_analytics(user_id: str, time_range: str = "week") -> Dict:
        """
        Get analytics about user interactions with UX enhancements.

        Args:
            user_id: ID of the user to get analytics for
            time_range: Time range for analytics ('day', 'week', 'month', 'quarter')

        Returns:
            Dictionary with interaction analytics
        """
        with Session(sync_engine) as session:
            # Calculate date range based on time_range
            now = datetime.utcnow()
            if time_range == "day":
                start_date = now - timedelta(days=1)
            elif time_range == "week":
                start_date = now - timedelta(weeks=1)
            elif time_range == "month":
                start_date = now - timedelta(days=30)
            elif time_range == "quarter":
                start_date = now - timedelta(days=90)
            else:  # default to week
                start_date = now - timedelta(weeks=1)

            # Get all UX enhancements for the user in the time range
            query = select(UXEnhancement).where(
                UXEnhancement.user_id == user_id,
                UXEnhancement.created_at >= start_date
            )
            all_enhancements = session.exec(query).all()

            if not all_enhancements:
                return {
                    "user_id": user_id,
                    "time_range": time_range,
                    "analytics": {
                        "total_interactions": 0,
                        "unique_features_used": 0,
                        "average_effectiveness": 0,
                        "most_used_feature": None,
                        "engagement_score": 0
                    }
                }

            # Calculate analytics
            total_interactions = len(all_enhancements)

            # Count unique features used
            unique_features = set(enh.feature_name for enh in all_enhancements)

            # Calculate average effectiveness (only for enhancements that have ratings)
            rated_enhancements = [enh for enh in all_enhancements if enh.effectiveness_rating is not None]
            average_effectiveness = (
                sum(enh.effectiveness_rating for enh in rated_enhancements) / len(rated_enhancements)
                if rated_enhancements else 0
            )

            # Find most used feature
            feature_counts = {}
            for enh in all_enhancements:
                feature_name = enh.feature_name
                if feature_name in feature_counts:
                    feature_counts[feature_name] += 1
                else:
                    feature_counts[feature_name] = 1

            most_used_feature = max(feature_counts, key=feature_counts.get) if feature_counts else None

            # Calculate engagement score based on interaction variety and frequency
            engagement_score = min(100, (total_interactions * len(unique_features) * 2))

            # Break down by enhancement type
            type_breakdown = {}
            for enh in all_enhancements:
                enh_type = enh.enhancement_type
                if enh_type in type_breakdown:
                    type_breakdown[enh_type]["count"] += 1
                    if enh.effectiveness_rating is not None:
                        type_breakdown[enh_type]["total_rating"] += enh.effectiveness_rating
                        type_breakdown[enh_type]["rated_count"] += 1
                else:
                    type_breakdown[enh_type] = {
                        "count": 1,
                        "total_rating": enh.effectiveness_rating or 0,
                        "rated_count": 1 if enh.effectiveness_rating is not None else 0
                    }

            # Calculate average ratings by type
            for enh_type, data in type_breakdown.items():
                if data["rated_count"] > 0:
                    data["avg_rating"] = data["total_rating"] / data["rated_count"]
                else:
                    data["avg_rating"] = 0
                # Remove helper fields
                del data["total_rating"]
                del data["rated_count"]

            analytics = {
                "user_id": user_id,
                "time_range": time_range,
                "period_start": start_date.isoformat(),
                "period_end": now.isoformat(),
                "analytics": {
                    "total_interactions": total_interactions,
                    "unique_features_used": len(unique_features),
                    "average_effectiveness": round(average_effectiveness, 2),
                    "most_used_feature": most_used_feature,
                    "engagement_score": round(engagement_score, 2),
                    "type_breakdown": type_breakdown
                }
            }

            logger.info(f"Generated UX interaction analytics for user {user_id}")
            return analytics

    @staticmethod
    def get_feature_effectiveness_report(user_id: str, feature_name: str) -> Dict:
        """
        Get effectiveness report for a specific feature.

        Args:
            user_id: ID of the user to get report for
            feature_name: Name of the feature to analyze

        Returns:
            Dictionary with feature effectiveness report
        """
        with Session(sync_engine) as session:
            # Get UX enhancements for this specific feature
            query = select(UXEnhancement).where(
                UXEnhancement.user_id == user_id,
                UXEnhancement.feature_name == feature_name
            )
            feature_enhancements = session.exec(query).all()

            if not feature_enhancements:
                return {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "report": {
                        "usage_count": 0,
                        "average_effectiveness": 0,
                        "user_feedback_count": 0,
                        "recommendation": "Feature not used recently"
                    }
                }

            # Calculate effectiveness metrics
            usage_count = len(feature_enhancements)
            rated_enhancements = [enh for enh in feature_enhancements if enh.effectiveness_rating is not None]

            avg_effectiveness = (
                sum(enh.effectiveness_rating for enh in rated_enhancements) / len(rated_enhancements)
                if rated_enhancements else 0
            )

            feedback_count = len([enh for enh in feature_enhancements if enh.feedback])

            # Generate recommendation based on effectiveness
            if avg_effectiveness >= 0.8:
                recommendation = "Highly effective - continue using this feature"
            elif avg_effectiveness >= 0.6:
                recommendation = "Moderately effective - consider improvements"
            elif avg_effectiveness >= 0.4:
                recommendation = "Somewhat effective - review user experience"
            else:
                recommendation = "Low effectiveness - consider redesign or removal"

            report = {
                "user_id": user_id,
                "feature_name": feature_name,
                "report": {
                    "usage_count": usage_count,
                    "average_effectiveness": round(avg_effectiveness, 2),
                    "user_feedback_count": feedback_count,
                    "recommendation": recommendation
                }
            }

            logger.info(f"Generated feature effectiveness report for {feature_name} and user {user_id}")
            return report

    @staticmethod
    def identify_ux_improvement_opportunities(user_id: str) -> List[Dict]:
        """
        Identify opportunities for UX improvements based on user interaction patterns.

        Args:
            user_id: ID of the user to analyze for improvement opportunities

        Returns:
            List of improvement opportunities
        """
        with Session(sync_engine) as session:
            # Get user's recent interactions
            query = select(UXEnhancement).where(UXEnhancement.user_id == user_id)
            all_interactions = session.exec(query).all()

            opportunities = []

            # Find features with low effectiveness ratings
            low_effectiveness_features = [
                enh for enh in all_interactions
                if enh.effectiveness_rating and enh.effectiveness_rating < 0.5
            ]

            if low_effectiveness_features:
                # Group by feature name
                feature_ratings = {}
                for enh in low_effectiveness_features:
                    if enh.feature_name in feature_ratings:
                        feature_ratings[enh.feature_name].append(enh.effectiveness_rating)
                    else:
                        feature_ratings[enh.feature_name] = [enh.effectiveness_rating]

                for feature, ratings in feature_ratings.items():
                    avg_rating = sum(ratings) / len(ratings)
                    opportunities.append({
                        "opportunity_type": "feature_improvement",
                        "feature_name": feature,
                        "current_avg_effectiveness": round(avg_rating, 2),
                        "suggestion": f"Improve '{feature}' feature - currently has low effectiveness rating ({avg_rating})"
                    })

            # Find underused features that might need better discovery
            all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
            task_count = len(all_tasks)

            # If user has many tasks but low interaction count with UX features, suggest more engagement
            if task_count > 10 and len(all_interactions) < task_count * 0.2:  # Less than 20% of tasks have UX interactions
                opportunities.append({
                    "opportunity_type": "feature_discovery",
                    "feature_name": "general_ux_features",
                    "current_avg_effectiveness": "N/A",
                    "suggestion": "User might benefit from discovering more UX features - low interaction rate relative to task count"
                })

            # Find features that are used frequently but could be improved
            feature_counts = {}
            for enh in all_interactions:
                if enh.feature_name in feature_counts:
                    feature_counts[enh.feature_name] += 1
                else:
                    feature_counts[enh.feature_name] = 1

            frequently_used_low_rated = [
                feature for feature, count in feature_counts.items()
                if count >= 5 and feature in [enh.feature_name for enh in low_effectiveness_features]
            ]

            for feature in frequently_used_low_rated:
                opportunities.append({
                    "opportunity_type": "high_usage_low_satisfaction",
                    "feature_name": feature,
                    "current_avg_effectiveness": "low",
                    "suggestion": f"Improve '{feature}' feature - used frequently but has low effectiveness ratings"
                })

            return opportunities

    @staticmethod
    def generate_ux_insights(user_id: str) -> Dict:
        """
        Generate insights about user's UX preferences and behavior.

        Args:
            user_id: ID of the user to generate insights for

        Returns:
            Dictionary with UX insights
        """
        with Session(sync_engine) as session:
            # Get all UX enhancements for the user
            all_enhancements = session.exec(
                select(UXEnhancement).where(UXEnhancement.user_id == user_id)
            ).all()

            insights = {
                "user_id": user_id,
                "insights": {
                    "preferred_interaction_styles": [],
                    "feature_engagement_pattern": "moderate",
                    "accessibility_preferences": [],
                    "suggested_improvements": []
                }
            }

            if not all_enhancements:
                insights["insights"]["suggested_improvements"].append(
                    "More UX interactions needed to generate personalized insights"
                )
                return insights

            # Analyze interaction patterns
            total_interactions = len(all_enhancements)

            # Find most effective features
            rated_enhancements = [enh for enh in all_enhancements if enh.effectiveness_rating is not None]
            if rated_enhancements:
                # Group by feature name and calculate average effectiveness
                feature_effectiveness = {}
                for enh in rated_enhancements:
                    if enh.feature_name in feature_effectiveness:
                        feature_effectiveness[enh.feature_name].append(enh.effectiveness_rating)
                    else:
                        feature_effectiveness[enh.feature_name] = [enh.effectiveness_rating]

                # Calculate average for each feature
                feature_avg_effectiveness = {
                    feature: sum(ratings) / len(ratings)
                    for feature, ratings in feature_effectiveness.items()
                }

                # Find most effective features
                if feature_avg_effectiveness:
                    most_effective = max(feature_avg_effectiveness, key=feature_avg_effectiveness.get)
                    if feature_avg_effectiveness[most_effective] >= 0.8:
                        insights["insights"]["preferred_interaction_styles"].append(most_effective)

            # Determine engagement pattern
            if total_interactions < 5:
                insights["insights"]["feature_engagement_pattern"] = "low"
            elif total_interactions < 20:
                insights["insights"]["feature_engagement_pattern"] = "moderate"
            else:
                insights["insights"]["feature_engagement_pattern"] = "high"

            # Identify accessibility preferences based on settings
            # This would be enhanced with actual accessibility settings in a real implementation
            from .accessibility_service import AccessibilityService
            accessibility_settings = AccessibilityService.get_accessibility_settings(user_id)
            if accessibility_settings:
                if accessibility_settings.high_contrast_enabled:
                    insights["insights"]["accessibility_preferences"].append("high_contrast")
                if accessibility_settings.reduced_motion_enabled:
                    insights["insights"]["accessibility_preferences"].append("reduced_motion")
                if accessibility_settings.font_size_preference in ["large", "extra_large"]:
                    insights["insights"]["accessibility_preferences"].append("larger_text")

            # Get improvement opportunities
            improvement_opportunities = UXTrackingService.identify_ux_improvement_opportunities(user_id)
            insights["insights"]["suggested_improvements"] = [opp["suggestion"] for opp in improvement_opportunities]

            return insights

    @staticmethod
    def calculate_engagement_metrics(user_id: str, time_range: str = "week") -> Dict:
        """
        Calculate engagement metrics for UX features.

        Args:
            user_id: ID of the user to calculate metrics for
            time_range: Time range for metrics ('day', 'week', 'month', 'quarter')

        Returns:
            Dictionary with engagement metrics
        """
        with Session(sync_engine) as session:
            # Calculate date range
            now = datetime.utcnow()
            if time_range == "day":
                start_date = now - timedelta(days=1)
            elif time_range == "week":
                start_date = now - timedelta(weeks=1)
            elif time_range == "month":
                start_date = now - timedelta(days=30)
            elif time_range == "quarter":
                start_date = now - timedelta(days=90)
            else:
                start_date = now - timedelta(weeks=1)

            # Get recent interactions
            query = select(UXEnhancement).where(
                UXEnhancement.user_id == user_id,
                UXEnhancement.created_at >= start_date
            )
            recent_interactions = session.exec(query).all()

            # Calculate metrics
            total_interactions = len(recent_interactions)

            # Count by enhancement type
            type_counts = {}
            for interaction in recent_interactions:
                enh_type = interaction.enhancement_type
                if enh_type in type_counts:
                    type_counts[enh_type] += 1
                else:
                    type_counts[enh_type] = 1

            # Calculate effectiveness metrics
            rated_interactions = [i for i in recent_interactions if i.effectiveness_rating is not None]
            avg_effectiveness = (
                sum(i.effectiveness_rating for i in rated_interactions) / len(rated_interactions)
                if rated_interactions else 0
            )

            # Calculate daily average if looking at weekly data
            days_in_range = (now - start_date).days or 1
            daily_avg_interactions = total_interactions / days_in_range

            metrics = {
                "user_id": user_id,
                "time_range": time_range,
                "metrics": {
                    "total_interactions": total_interactions,
                    "daily_average_interactions": round(daily_avg_interactions, 2),
                    "average_effectiveness": round(avg_effectiveness, 2),
                    "interaction_types": type_counts,
                    "engagement_trend": "increasing" if daily_avg_interactions > 1 else "stable"  # Simplified
                }
            }

            logger.info(f"Calculated engagement metrics for user {user_id}")
            return metrics