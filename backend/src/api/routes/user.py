from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlmodel import Session, select

from ...dependencies.auth import get_current_user, get_current_user_identity
from ...exceptions.auth import InsufficientPermissionsException
from ...config import config
from ...database import get_session
from ...src.models.user import User

router = APIRouter(prefix="/user", tags=["User"])

# Import the TokenData and UserIdentity models
from ...dependencies.auth import TokenData, UserIdentity

@router.get(
    "/profile",
    response_model=UserIdentity,
    dependencies=[Depends(get_current_user)],
    responses={
        401: {"description": "Invalid or missing token"}
    }
)
async def get_user_profile(
    current_user: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session)
):
    """
    Get authenticated user's profile information.

    Args:
        current_user: The currently authenticated user (extracted from JWT)
        session: Database session dependency

    Returns:
        UserIdentity object with user's profile information

    Raises:
        HTTPException: If token is invalid or missing (401)
    """
    # Fetch user details from the database
    user = session.exec(select(User).where(User.id == current_user.user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserIdentity(
        user_id=user.id,
        email=user.email,
        name=user.name
    )


@router.get(
    "/{user_id}/validate",
    response_model=dict,
    dependencies=[Depends(get_current_user)],
    responses={
        401: {"description": "Invalid or missing token"},
        403: {"description": "Access denied - user mismatch"}
    }
)
async def validate_user_access(
    user_id: str,
    current_user: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session)
):
    """
    Validate JWT and return user information (used by frontend to verify session).

    Args:
        user_id: The user ID to validate against the current user's token
        current_user: The currently authenticated user (extracted from JWT)
        session: Database session dependency

    Returns:
        Dictionary with user information and validation status

    Raises:
        HTTPException: If token is invalid (401) or user ID doesn't match (403)
    """
    # Check if the user_id in the URL matches the user_id in the token
    if current_user.user_id != user_id:
        raise InsufficientPermissionsException(
            detail="Access denied - user mismatch"
        )

    # Verify the user exists in the database
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "valid": True
    }


# Additional user-related endpoints can be added here
@router.put(
    "/profile",
    response_model=UserIdentity,
    dependencies=[Depends(get_current_user)],
    responses={
        401: {"description": "Invalid or missing token"}
    }
)
async def update_user_profile(
    user_update: dict,  # In a real app, this would be a proper Pydantic model
    current_user: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session)
):
    """
    Update authenticated user's profile information.

    Args:
        user_update: Dictionary containing the fields to update
        current_user: The currently authenticated user (extracted from JWT)
        session: Database session dependency

    Returns:
        Updated UserIdentity object

    Raises:
        HTTPException: If token is invalid or missing (401)
    """
    # Fetch the user from the database
    user = session.exec(select(User).where(User.id == current_user.user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Apply updates from user_update
    if "name" in user_update:
        user.name = user_update["name"]

    if "email" in user_update:
        # Check if the new email is already taken by another user
        existing_user = session.exec(select(User).where(User.email == user_update["email"], User.id != user.id)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        user.email = user_update["email"]

    # Update the updated_at timestamp
    from datetime import datetime
    user.updated_at = datetime.utcnow()

    # Commit the changes to the database
    session.add(user)
    session.commit()
    session.refresh(user)

    # Return the updated user info
    return UserIdentity(
        user_id=user.id,
        email=user.email,
        name=user.name
    )