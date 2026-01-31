"""
Micro Feature Service
This module provides business logic for managing optional micro-features and user preferences.
"""
from typing import List, Dict, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models.micro_feature import MicroFeature, MicroFeatureCreate, UserMicroFeaturePreference, UserMicroFeaturePreferenceCreate
from ..database import sync_engine
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MicroFeatureService:
    """Service class for managing micro features and user preferences."""

    @staticmethod
    def get_available_features() -> List[MicroFeature]:
        """
        Get all available micro features.

        Returns:
            List of all available micro features
        """
        with Session(sync_engine) as session:
            features = session.exec(select(MicroFeature)).all()
            return features

    @staticmethod
    def get_user_preferences(user_id: str) -> List[UserMicroFeaturePreference]:
        """
        Get all micro feature preferences for a user.

        Args:
            user_id: ID of the user to get preferences for

        Returns:
            List of user's micro feature preferences
        """
        with Session(sync_engine) as session:
            preferences = session.exec(
                select(UserMicroFeaturePreference).where(UserMicroFeaturePreference.user_id == user_id)
            ).all()
            return preferences

    @staticmethod
    def get_enabled_features(user_id: str) -> List[MicroFeature]:
        """
        Get only the micro features that are enabled by the user.

        Args:
            user_id: ID of the user to get enabled features for

        Returns:
            List of enabled micro features
        """
        with Session(sync_engine) as session:
            # Get user's preferences for enabled features
            enabled_prefs = session.exec(
                select(UserMicroFeaturePreference)
                .where(UserMicroFeaturePreference.user_id == user_id)
                .where(UserMicroFeaturePreference.is_enabled == True)
            ).all()

            # Get the actual features for these preferences
            enabled_feature_ids = [pref.micro_feature_id for pref in enabled_prefs]
            enabled_features = []

            for feature_id in enabled_feature_ids:
                feature = session.exec(
                    select(MicroFeature).where(MicroFeature.id == feature_id)
                ).first()
                if feature:
                    enabled_features.append(feature)

            return enabled_features

    @staticmethod
    def update_user_preference(
        user_id: str,
        feature_id: str,
        is_enabled: bool,
        custom_settings: Optional[dict] = None
    ) -> UserMicroFeaturePreference:
        """
        Update a user's preference for a specific micro feature.

        Args:
            user_id: ID of the user updating preference
            feature_id: ID of the feature to update preference for
            is_enabled: Whether the feature should be enabled
            custom_settings: Optional custom settings for the feature

        Returns:
            Updated UserMicroFeaturePreference object
        """
        with Session(sync_engine) as session:
            # Check if preference already exists
            existing_preference = session.exec(
                select(UserMicroFeaturePreference)
                .where(UserMicroFeaturePreference.user_id == user_id)
                .where(UserMicroFeaturePreference.micro_feature_id == feature_id)
            ).first()

            if existing_preference:
                # Update existing preference
                existing_preference.is_enabled = is_enabled
                if custom_settings:
                    existing_preference.custom_settings = custom_settings
                existing_preference.updated_at = datetime.utcnow()

                session.add(existing_preference)
            else:
                # Create new preference
                preference_data = UserMicroFeaturePreferenceCreate(
                    user_id=user_id,
                    micro_feature_id=feature_id,
                    is_enabled=is_enabled,
                    custom_settings=custom_settings or {}
                )
                new_preference = UserMicroFeaturePreference.model_validate(preference_data)
                session.add(new_preference)
                existing_preference = new_preference

            session.commit()
            session.refresh(existing_preference)

            logger.info(f"Updated micro feature preference for user {user_id}, feature {feature_id}: {'enabled' if is_enabled else 'disabled'}")
            return existing_preference

    @staticmethod
    def register_feature(
        name: str,
        description: str,
        is_enabled_by_default: bool = False,
        category: str = "general",
        keyboard_shortcut: Optional[str] = None
    ) -> MicroFeature:
        """
        Register a new micro feature in the system.

        Args:
            name: Unique name of the feature
            description: Description of what the feature does
            is_enabled_by_default: Whether this feature is enabled by default
            category: Category of the feature
            keyboard_shortcut: Default keyboard shortcut if applicable

        Returns:
            Created MicroFeature object
        """
        with Session(sync_engine) as session:
            # Check if feature with this name already exists
            existing_feature = session.exec(
                select(MicroFeature).where(MicroFeature.name == name)
            ).first()

            if existing_feature:
                raise ValueError(f"Micro feature with name '{name}' already exists")

            # Create new feature
            feature_data = MicroFeatureCreate(
                name=name,
                description=description,
                is_enabled_by_default=is_enabled_by_default,
                category=category,
                keyboard_shortcut=keyboard_shortcut
            )

            new_feature = MicroFeature.model_validate(feature_data)
            session.add(new_feature)
            session.commit()
            session.refresh(new_feature)

            logger.info(f"Registered new micro feature: {name}")
            return new_feature

    @staticmethod
    def get_feature_by_name(name: str) -> Optional[MicroFeature]:
        """
        Get a micro feature by its name.

        Args:
            name: Name of the feature to retrieve

        Returns:
            MicroFeature object if found, None otherwise
        """
        with Session(sync_engine) as session:
            feature = session.exec(
                select(MicroFeature).where(MicroFeature.name == name)
            ).first()
            return feature

    @staticmethod
    def get_feature_by_id(feature_id: str) -> Optional[MicroFeature]:
        """
        Get a micro feature by its ID.

        Args:
            feature_id: ID of the feature to retrieve

        Returns:
            MicroFeature object if found, None otherwise
        """
        with Session(sync_engine) as session:
            feature = session.exec(
                select(MicroFeature).where(MicroFeature.id == feature_id)
            ).first()
            return feature

    @staticmethod
    def get_user_analytics(user_id: str) -> Dict:
        """
        Get analytics about user's micro feature usage.

        Args:
            user_id: ID of the user to get analytics for

        Returns:
            Dictionary with micro feature usage analytics
        """
        with Session(sync_engine) as session:
            # Get all preferences for the user
            all_preferences = MicroFeatureService.get_user_preferences(user_id)

            # Get all available features
            all_features = MicroFeatureService.get_available_features()

            # Calculate analytics
            total_features = len(all_features)
            enabled_features = len([pref for pref in all_preferences if pref.is_enabled])
            disabled_features = len([pref for pref in all_preferences if not pref.is_enabled])

            # Count by category
            category_counts = {}
            for feature in all_features:
                if feature.category in category_counts:
                    category_counts[feature.category] += 1
                else:
                    category_counts[feature.category] = 1

            # Get most popular features (those that are enabled by most users)
            # This would require a broader query across all users in a real implementation
            # For now, we'll just return user-specific data

            analytics = {
                "user_id": user_id,
                "features_overview": {
                    "total_features_available": total_features,
                    "enabled_features": enabled_features,
                    "disabled_features": disabled_features,
                    "enabled_percentage": round((enabled_features / total_features * 100) if total_features > 0 else 0, 2)
                },
                "features_by_category": category_counts,
                "custom_settings_summary": {
                    "has_custom_settings": len([pref for pref in all_preferences if pref.custom_settings]) > 0,
                    "custom_settings_count": len([pref for pref in all_preferences if pref.custom_settings])
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Generated micro feature analytics for user {user_id}")
            return analytics

    @staticmethod
    def initialize_default_preferences(user_id: str) -> List[UserMicroFeaturePreference]:
        """
        Initialize default preferences for a new user based on feature defaults.

        Args:
            user_id: ID of the new user to initialize preferences for

        Returns:
            List of created UserMicroFeaturePreference objects
        """
        with Session(sync_engine) as session:
            # Get all features that are enabled by default
            default_enabled_features = session.exec(
                select(MicroFeature).where(MicroFeature.is_enabled_by_default == True)
            ).all()

            created_preferences = []

            for feature in default_enabled_features:
                # Check if user already has a preference for this feature
                existing_pref = session.exec(
                    select(UserMicroFeaturePreference)
                    .where(UserMicroFeaturePreference.user_id == user_id)
                    .where(UserMicroFeaturePreference.micro_feature_id == str(feature.id))
                ).first()

                if not existing_pref:
                    # Create default preference for this user
                    preference_data = UserMicroFeaturePreferenceCreate(
                        user_id=user_id,
                        micro_feature_id=str(feature.id),
                        is_enabled=True,
                        custom_settings={}
                    )
                    new_preference = UserMicroFeaturePreference.model_validate(preference_data)
                    session.add(new_preference)
                    session.commit()
                    session.refresh(new_preference)

                    created_preferences.append(new_preference)

            # Also create preferences for features that are disabled by default
            all_features = session.exec(select(MicroFeature)).all()
            for feature in all_features:
                existing_pref = session.exec(
                    select(UserMicroFeaturePreference)
                    .where(UserMicroFeaturePreference.user_id == user_id)
                    .where(UserMicroFeaturePreference.micro_feature_id == str(feature.id))
                ).first()

                if not existing_pref:
                    # Create default preference based on feature's default setting
                    preference_data = UserMicroFeaturePreferenceCreate(
                        user_id=user_id,
                        micro_feature_id=str(feature.id),
                        is_enabled=feature.is_enabled_by_default,
                        custom_settings={}
                    )
                    new_preference = UserMicroFeaturePreference.model_validate(preference_data)
                    session.add(new_preference)
                    session.commit()
                    session.refresh(new_preference)

                    created_preferences.append(new_preference)

            logger.info(f"Initialized {len(created_preferences)} default preferences for user {user_id}")
            return created_preferences

    @staticmethod
    def get_popular_features(limit: int = 10) -> List[Dict]:
        """
        Get popular features based on usage across all users.

        Args:
            limit: Maximum number of features to return

        Returns:
            List of popular features with usage statistics
        """
        # This would require more complex queries joining preferences across users
        # For now, we'll return a mock implementation
        # In a real system, this would aggregate preference data across all users

        with Session(sync_engine) as session:
            all_features = session.exec(select(MicroFeature)).all()

            # Mock popularity data (in a real implementation, this would come from actual usage data)
            popular_features = []
            for i, feature in enumerate(all_features[:limit]):
                popular_features.append({
                    "feature": feature,
                    "popularity_score": 100 - (i * 10),  # Decreasing popularity
                    "users_enabled_count": 100 - (i * 15),  # Decreasing usage
                    "category_usage": 75 + (i % 3) * 5  # Varying by category
                })

            return popular_features

    @staticmethod
    def bulk_update_preferences(user_id: str, preferences: List[Dict]) -> Dict:
        """
        Bulk update multiple micro feature preferences at once.

        Args:
            user_id: ID of the user updating preferences
            preferences: List of preference updates in format {"feature_id": "id", "is_enabled": true/false}

        Returns:
            Dictionary with update results
        """
        updated_count = 0
        failed_updates = []

        for pref_data in preferences:
            try:
                MicroFeatureService.update_user_preference(
                    user_id=user_id,
                    feature_id=pref_data["feature_id"],
                    is_enabled=pref_data["is_enabled"],
                    custom_settings=pref_data.get("custom_settings", {})
                )
                updated_count += 1
            except Exception as e:
                failed_updates.append({
                    "feature_id": pref_data["feature_id"],
                    "error": str(e)
                })

        result = {
            "user_id": user_id,
            "updated_count": updated_count,
            "failed_count": len(failed_updates),
            "total_requested": len(preferences),
            "failed_updates": failed_updates
        }

        logger.info(f"Bulk updated {updated_count} preferences for user {user_id}")
        return result