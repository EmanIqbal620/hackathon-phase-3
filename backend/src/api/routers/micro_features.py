"""
Micro Features API Router
This module defines the API endpoints for managing optional micro-features in the todo application.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from ....dependencies.auth import get_current_user, TokenData
from ....models.micro_feature import (
    MicroFeature, MicroFeatureCreate, MicroFeatureRead,
    UserMicroFeaturePreference, UserMicroFeaturePreferenceCreate,
    UserMicroFeaturePreferenceRead
)
from ....services.micro_feature_service import MicroFeatureService
from ....database import sync_engine
from sqlmodel import Session, select
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/micro-features", tags=["micro-features"])


class MicroFeatureRequest(BaseModel):
    """Request model for creating a micro feature"""
    name: str = Field(..., description="Unique name of the feature", max_length=100)
    description: str = Field(..., description="Description of what the feature does")
    is_enabled_by_default: bool = Field(default=False, description="Whether this feature is enabled by default")
    category: str = Field(..., description="Category of the feature: 'navigation', 'productivity', 'accessibility', 'appearance', 'interaction'")
    keyboard_shortcut: Optional[str] = Field(default=None, description="Default keyboard shortcut if applicable")


class MicroFeaturePreferenceRequest(BaseModel):
    """Request model for updating micro feature preferences"""
    is_enabled: bool = Field(..., description="Whether to enable the feature")
    custom_settings: Optional[dict] = Field(default=None, description="Custom settings for the feature")


class MicroFeatureListResponse(BaseModel):
    """Response model for listing micro features"""
    features: List[MicroFeatureRead]
    user_preferences: List[UserMicroFeaturePreferenceRead]
    total_count: int


class MicroFeaturePreferenceResponse(BaseModel):
    """Response model for micro feature preference operations"""
    success: bool
    message: str
    feature_id: str
    is_enabled: bool
    updated_at: str


@router.get("/list", response_model=MicroFeatureListResponse)
async def get_micro_features(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get available micro features and user preferences.

    This endpoint returns all available micro features along with the user's preferences for each.
    """
    try:
        logger.info(f"Fetching micro features for user {current_user.user_id}")

        # Get all micro features
        with Session(sync_engine) as session:
            all_features = session.exec(select(MicroFeature)).all()

        # Get user's preferences for micro features
        user_preferences = MicroFeatureService.get_user_preferences(current_user.user_id)

        response = MicroFeatureListResponse(
            features=[MicroFeatureRead.from_orm(f) if hasattr(MicroFeatureRead, 'from_orm') else f for f in all_features],
            user_preferences=user_preferences,
            total_count=len(all_features)
        )

        logger.info(f"Retrieved {len(all_features)} micro features for user {current_user.user_id}")
        return response

    except Exception as e:
        logger.error(f"Error fetching micro features: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving micro features"
        )


@router.get("/user/{user_id}/preferences", response_model=List[UserMicroFeaturePreferenceRead])
async def get_user_micro_feature_preferences(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get user's micro feature preferences.

    This endpoint returns the user's preferences for all micro features.
    """
    # Verify that the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own micro feature preferences"
        )

    try:
        logger.info(f"Fetching micro feature preferences for user {user_id}")

        preferences = MicroFeatureService.get_user_preferences(user_id)

        logger.info(f"Retrieved {len(preferences)} micro feature preferences for user {user_id}")
        return preferences

    except Exception as e:
        logger.error(f"Error fetching micro feature preferences for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving micro feature preferences"
        )


@router.post("/user/{user_id}/preferences/{feature_id}")
async def update_micro_feature_preference(
    user_id: str,
    feature_id: str,
    request: MicroFeaturePreferenceRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update a user's preference for a specific micro feature.

    This endpoint allows users to enable or disable specific micro features and customize their settings.
    """
    # Verify that the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own micro feature preferences"
        )

    try:
        logger.info(f"Updating micro feature preference for user {user_id}, feature {feature_id}")

        # Update the preference
        updated_preference = MicroFeatureService.update_user_preference(
            user_id=user_id,
            feature_id=feature_id,
            is_enabled=request.is_enabled,
            custom_settings=request.custom_settings
        )

        response = MicroFeaturePreferenceResponse(
            success=True,
            message=f"Micro feature preference updated for feature {feature_id}",
            feature_id=feature_id,
            is_enabled=request.is_enabled,
            updated_at=datetime.utcnow().isoformat()
        )

        logger.info(f"Updated micro feature preference for user {user_id}, feature {feature_id}")
        return response

    except ValueError as e:
        logger.warning(f"Invalid micro feature preference update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating micro feature preference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating micro feature preference"
        )


@router.get("/user/{user_id}/enabled", response_model=List[MicroFeatureRead])
async def get_enabled_micro_features(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get only the micro features that are enabled by the user.

    This endpoint returns only the micro features that the user has enabled.
    """
    # Verify that the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own enabled micro features"
        )

    try:
        logger.info(f"Fetching enabled micro features for user {user_id}")

        # Get enabled micro features
        enabled_features = MicroFeatureService.get_enabled_features(user_id)

        logger.info(f"Retrieved {len(enabled_features)} enabled micro features for user {user_id}")
        return enabled_features

    except Exception as e:
        logger.error(f"Error fetching enabled micro features for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving enabled micro features"
        )


@router.post("/register", response_model=MicroFeatureRead)
async def register_micro_feature(
    feature_request: MicroFeatureRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Register a new micro feature in the system.

    This endpoint allows registering new micro features that users can enable/disable.
    Only administrators should be able to call this endpoint in a production system.
    """
    # In a real system, you'd check admin privileges here
    # For this implementation, we'll allow it for demo purposes
    logger.warning(f"Registering new micro feature by user {current_user.user_id} (in production, this would require admin privileges)")

    try:
        # Create the new micro feature
        new_feature = MicroFeatureService.register_feature(
            name=feature_request.name,
            description=feature_request.description,
            is_enabled_by_default=feature_request.is_enabled_by_default,
            category=feature_request.category,
            keyboard_shortcut=feature_request.keyboard_shortcut
        )

        logger.info(f"Registered new micro feature: {feature_request.name}")
        return new_feature

    except ValueError as e:
        logger.warning(f"Invalid micro feature registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering micro feature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the micro feature"
        )


@router.get("/analytics/{user_id}", response_model=Dict)
async def get_micro_feature_analytics(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get analytics about user's micro feature usage.

    This endpoint provides metrics about how the user engages with different micro features.
    """
    # Verify that the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own micro feature analytics"
        )

    try:
        logger.info(f"Fetching micro feature analytics for user {user_id}")

        # Get analytics
        analytics = MicroFeatureService.get_user_analytics(user_id)

        logger.info(f"Retrieved micro feature analytics for user {user_id}")
        return analytics

    except Exception as e:
        logger.error(f"Error fetching micro feature analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving micro feature analytics"
        )


@router.get("/health")
async def micro_features_health_check():
    """
    Health check endpoint for the micro features service.

    This endpoint confirms the micro features service is operational.
    """
    try:
        # Verify that the micro features service is working
        # In a real implementation, this might check database connectivity, etc.
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "micro_features"
        }
    except Exception as e:
        logger.error(f"Micro features health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Micro features service health check failed"
        )


# Include this router in the main application
def include_router(app):
    """
    Helper function to include this router in the main application.

    Args:
        app: FastAPI application instance
    """
    app.include_router(router)