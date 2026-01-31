from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ...models.conversation import Message, MessageCreate, Conversation
from ...models.tool_call_log import ToolCallLog
from ...services.conversation_service import ConversationService
from ...services.ai_agent_service import AIAgentService
from ...middleware.auth import get_current_user, TokenData
from ...middleware.rate_limit import check_rate_limit
from ...database import get_session
from sqlmodel import Session
import uuid
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ToolCallResult(BaseModel):
    tool: str
    status: str
    result: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[ToolCallResult]


@router.post("/{user_id}", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check rate limit for the user
    await check_rate_limit(user_id)
    """
    Process a user message and return AI response with tool call results

    Args:
        user_id: The ID of the user sending the message
        request: Chat request containing the message and optional conversation_id
        current_user: Current authenticated user
        session: Database session

    Returns:
        ChatResponse containing conversation ID, AI response, and tool call results
    """
    # Verify that the authenticated user matches the requested user ID
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own chat"
        )

    try:
        # Initialize services
        conversation_service = ConversationService(session)
        ai_agent_service = AIAgentService(session)

        # Create or retrieve conversation
        if request.conversation_id:
            conversation = conversation_service.get_conversation(request.conversation_id, user_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            conversation = conversation_service.create_conversation(user_id)

        # Create user message in the conversation
        user_message_data = MessageCreate(
            user_id=user_id,
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        user_message = conversation_service.create_message(user_message_data)

        # Get conversation history for context
        conversation_history = conversation_service.get_conversation_messages(conversation.id)

        # Process the message with AI agent
        ai_response, tool_call_results = await ai_agent_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )

        # Create assistant message with tool call results
        assistant_message_data = MessageCreate(
            user_id=user_id,  # AI acts on behalf of user
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            tool_call_results=tool_call_results
        )
        assistant_message = conversation_service.create_message(assistant_message_data)

        # Format tool call results for response with more detailed information
        formatted_tool_calls = []
        for tool_result in tool_call_results or []:
            formatted_tool_calls.append(
                ToolCallResult(
                    tool=tool_result.get("tool", "unknown"),
                    status=tool_result.get("status", "unknown"),
                    result=tool_result.get("result", {}),
                    error=tool_result.get("error"),
                    execution_time_ms=tool_result.get("execution_time_ms")
                )
            )

        return ChatResponse(
            conversation_id=conversation.id,
            response=ai_response,
            tool_calls=formatted_tool_calls
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your message: {str(e)}"
        )


@router.get("/{user_id}/{conversation_id}", response_model=List[Dict[str, Any]])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve all messages in a specific conversation

    Args:
        user_id: The ID of the user requesting the conversation
        conversation_id: The ID of the conversation to retrieve
        current_user: Current authenticated user
        session: Database session

    Returns:
        List of messages in the conversation
    """
    # Verify that the authenticated user matches the requested user ID
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own conversations"
        )

    try:
        conversation_service = ConversationService(session)
        messages = conversation_service.get_conversation_messages(conversation_id)

        # Verify that the conversation belongs to the user
        if messages and messages[0].user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own conversations"
            )

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.id,
                "user_id": msg.user_id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "tool_call_results": msg.tool_call_results
            })

        return formatted_messages

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving conversation: {str(e)}"
        )