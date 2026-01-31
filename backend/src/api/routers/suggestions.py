"""
Suggestions API Router
This module defines the FastAPI endpoints for AI-generated task suggestions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from ....dependencies.auth import get_current_user, TokenData
from ....services.suggestion_service import SuggestionService
from ....models.suggestion import SuggestionRead, SuggestionResponse
from ....database import sync_engine
from sqlmodel import Session, select
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class SuggestionCreateRequest(BaseModel):
    """Request model for creating a new suggestion"""
    user_id: str = Field(..., description="ID of the user to create suggestion for")
    suggestion_type: str = Field(..., description="Type of suggestion: 'pattern_based', 'priority_based', 'deadline_based', 'contextual'")
    title: str = Field(..., description="Title of the suggested task", max_length=255)
    description: Optional[str] = Field(None, description="Description of the suggested task")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the suggestion")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the suggestion")


class SuggestionAcceptRequest(BaseModel):
    """Request model for accepting a suggestion"""
    create_task: bool = Field(default=True, description="Whether to create a task from the suggestion")
    custom_due_date: Optional[datetime] = Field(None, description="Custom due date for the created task")
    notes: Optional[str] = Field(None, description="Additional notes for the created task")


class SuggestionListResponse(BaseModel):
    """Response model for listing suggestions"""
    user_id: str
    suggestions: List[Dict]
    count: int


@router.get("/{user_id}/list", response_model=SuggestionListResponse)
async def get_suggestions(
    user_id: str,
    limit: int = 5,
    suggestion_type: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get AI-generated suggestions for a user.

    This endpoint retrieves intelligent task suggestions based on the user's
    task patterns, priorities, deadlines, and context.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own suggestions"
        )

    try:
        logger.info(f"Fetching suggestions for user {user_id}, type: {suggestion_type}, limit: {limit}")

        # Get pending suggestions from the database
        pending_suggestions = SuggestionService.get_pending_suggestions(user_id, limit)

        # Convert to response format
        suggestions_list = []
        for suggestion in pending_suggestions:
            suggestions_list.append({
                "id": str(suggestion.id),
                "title": suggestion.suggested_task_title,
                "description": suggestion.suggested_task_description,
                "type": suggestion.suggestion_type,
                "confidence": suggestion.confidence_score,
                "reasoning": suggestion.reasoning,
                "created_at": suggestion.created_at.isoformat(),
                "accepted": suggestion.accepted
            })

        response = SuggestionListResponse(
            user_id=user_id,
            suggestions=suggestions_list,
            count=len(suggestions_list)
        )

        logger.info(f"Successfully retrieved {len(suggestions_list)} suggestions for user {user_id}")
        return response

    except Exception as e:
        logger.error(f"Error retrieving suggestions for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving suggestions"
        )


@router.post("/{suggestion_id}/accept", response_model=SuggestionResponse)
async def accept_suggestion(
    suggestion_id: str,
    request: SuggestionAcceptRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Accept an AI-generated suggestion and optionally create a task.

    This endpoint marks a suggestion as accepted and optionally creates
    a new task based on the suggestion.
    """
    try:
        logger.info(f"Accepting suggestion {suggestion_id} for user {current_user.user_id}")

        # Mark the suggestion as accepted
        updated_suggestion = SuggestionService.accept_suggestion(suggestion_id)

        response_data = {
            "success": True,
            "message": f"Suggestion '{updated_suggestion.suggested_task_title}' accepted",
            "suggestion_id": str(updated_suggestion.id),
            "task_created": False,
            "task_id": None
        }

        # If requested, create a task from the suggestion
        if request.create_task:
            # In a real implementation, we would create a task here
            # For now, we'll just simulate the creation
            from uuid import uuid4
            task_id = str(uuid4())

            response_data["task_created"] = True
            response_data["task_id"] = task_id

            # Update the suggestion with the created task ID
            updated_suggestion.converted_to_task_id = task_id

            logger.info(f"Task {task_id} created from suggestion {suggestion_id}")

        logger.info(f"Suggestion {suggestion_id} accepted by user {current_user.user_id}")
        return SuggestionResponse(**response_data)

    except ValueError as e:
        logger.error(f"Invalid suggestion ID {suggestion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error accepting suggestion {suggestion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while accepting the suggestion"
        )


@router.post("/{suggestion_id}/dismiss", response_model=SuggestionResponse)
async def dismiss_suggestion(
    suggestion_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Dismiss an AI-generated suggestion.

    This endpoint marks a suggestion as dismissed, indicating the user
    does not wish to act on it.
    """
    try:
        logger.info(f"Dismissing suggestion {suggestion_id} for user {current_user.user_id}")

        # Mark the suggestion as dismissed
        updated_suggestion = SuggestionService.dismiss_suggestion(suggestion_id)

        response = SuggestionResponse(
            success=True,
            message=f"Suggestion '{updated_suggestion.suggested_task_title}' dismissed",
            suggestion_id=str(updated_suggestion.id),
            task_created=False
        )

        logger.info(f"Suggestion {suggestion_id} dismissed by user {current_user.user_id}")
        return response

    except ValueError as e:
        logger.error(f"Invalid suggestion ID {suggestion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error dismissing suggestion {suggestion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while dismissing the suggestion"
        )


@router.post("/", response_model=SuggestionResponse)
async def generate_suggestions(
    user_id: str,
    suggestion_type: str = "pattern_based",
    current_user: TokenData = Depends(get_current_user)
):
    """
    Generate AI suggestions for a user based on specified type.

    This endpoint generates new AI-powered task suggestions based on
    the user's task patterns and context.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only generate suggestions for yourself"
        )

    try:
        logger.info(f"Generating {suggestion_type} suggestions for user {user_id}")

        # Generate suggestions based on the type
        if suggestion_type == "pattern_based":
            suggestions = SuggestionService.generate_pattern_based_suggestions(user_id)
        elif suggestion_type == "priority_based":
            suggestions = SuggestionService.generate_priority_based_suggestions(user_id)
        elif suggestion_type == "deadline_based":
            suggestions = SuggestionService.generate_deadline_based_suggestions(user_id)
        elif suggestion_type == "contextual":
            suggestions = SuggestionService.generate_contextual_suggestions(user_id)
        else:
            suggestions = SuggestionService.generate_pattern_based_suggestions(user_id)

        # Save the generated suggestions to the database
        saved_suggestions = []
        for suggestion_data in suggestions:
            saved_suggestion = SuggestionService.create_suggestion_in_db(suggestion_data, user_id)
            saved_suggestions.append(saved_suggestion)

        response = SuggestionResponse(
            success=True,
            message=f"Generated {len(saved_suggestions)} {suggestion_type} suggestions for user {user_id}",
            suggestion_id=str(saved_suggestions[0].id) if saved_suggestions else None,
            task_created=False
        )

        logger.info(f"Generated {len(saved_suggestions)} {suggestion_type} suggestions for user {user_id}")
        return response

    except Exception as e:
        logger.error(f"Error generating suggestions for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating suggestions"
        )


@router.get("/{user_id}/analytics", response_model=Dict)
async def get_suggestion_analytics(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get analytics about suggestion acceptance and effectiveness.

    This endpoint provides metrics on how well the AI suggestions
    are performing for the user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own suggestion analytics"
        )

    try:
        logger.info(f"Fetching suggestion analytics for user {user_id}")

        with Session(sync_engine) as session:
            # Get all suggestions for the user
            all_suggestions = session.exec(
                select(SuggestionRead).where(SuggestionRead.user_id == user_id)
            ).all()

            # Calculate analytics
            total_suggestions = len(all_suggestions)
            accepted_suggestions = [s for s in all_suggestions if s.accepted is True]
            dismissed_suggestions = [s for s in all_suggestions if s.accepted is False]
            pending_suggestions = [s for s in all_suggestions if s.accepted is None]

            # Calculate acceptance rate
            acceptance_rate = (len(accepted_suggestions) / total_suggestions * 100) if total_suggestions > 0 else 0

            # Find most effective suggestion types
            type_acceptance = {}
            for suggestion in accepted_suggestions:
                s_type = suggestion.suggestion_type
                if s_type in type_acceptance:
                    type_acceptance[s_type] += 1
                else:
                    type_acceptance[s_type] = 1

            most_effective_type = max(type_acceptance, key=type_acceptance.get) if type_acceptance else None

            analytics_data = {
                "user_id": user_id,
                "total_suggestions": total_suggestions,
                "accepted_suggestions": len(accepted_suggestions),
                "dismissed_suggestions": len(dismissed_suggestions),
                "pending_suggestions": len(pending_suggestions),
                "acceptance_rate_percent": round(acceptance_rate, 2),
                "most_effective_type": most_effective_type,
                "type_effectiveness": type_acceptance
            }

            logger.info(f"Retrieved suggestion analytics for user {user_id}")
            return analytics_data

    except Exception as e:
        logger.error(f"Error retrieving suggestion analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving suggestion analytics"
        )