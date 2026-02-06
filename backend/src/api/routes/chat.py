import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ...models.conversation import Message, MessageCreate, Conversation
from ...services.conversation_service import ConversationService
from ...agents.chat_agent import process_chat_request, ChatRequest as AgentChatRequest
from ...middleware.auth import get_current_user, TokenData
from ...database import sync_engine
from sqlmodel import Session
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

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
    current_user: TokenData = Depends(get_current_user)
):
    """
    Process a user message and return AI response with tool call results

    Args:
        user_id: The ID of the user sending the message
        request: Chat request containing the message and optional conversation_id
        current_user: Current authenticated user

    Returns:
        ChatResponse containing conversation ID, AI response, and tool call results
    """
    # Verify that the authenticated user matches the requested user ID
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own chat"
        )

    # Create session manually since we're using sync_engine
    with Session(sync_engine) as session:
        try:
            # Build conversation history for the chat agent
            conversation_history_formatted = []
            conversation_service = ConversationService(session)

            if request.conversation_id:
                # If we have a conversation ID, get history
                conversation = conversation_service.get_conversation(request.conversation_id, user_id)
                if not conversation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found"
                    )
            else:
                # Create new conversation if none exists
                conversation = conversation_service.create_conversation(user_id)

            # Create user message in the conversation first
            user_message_data = MessageCreate(
                user_id=user_id,
                conversation_id=conversation.id,
                role="user",
                content=request.message
            )
            user_message = conversation_service.create_message(user_message_data)

            # Get conversation messages and format them for the chat agent
            # We need to get messages after creating the user message to include it
            db_messages = conversation_service.get_conversation_messages(conversation.id)
            for msg in db_messages:
                conversation_history_formatted.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Format the request for the chat agent
            chat_req = AgentChatRequest(
                user_id=user_id,
                message=request.message,
                conversation_history=conversation_history_formatted
            )

            # Process the message with the chat agent - with fallback for AI provider issues
            try:
                chat_response = process_chat_request(chat_req)
                ai_response = chat_response.response
                tool_usage = chat_response.tool_usage or {}
            except Exception as e:
                # If the main chat agent fails (likely due to AI provider issues), use fallback
                logger.error(f"Main chat agent failed: {str(e)}, using fallback")
                from ...agents.chat_agent_mock_fallback import process_chat_request_with_fallback
                chat_response = process_chat_request_with_fallback(chat_req)
                ai_response = chat_response.response
                tool_usage = chat_response.tool_usage or {}

            # Format tool call results for response
            tool_call_results = []
            if isinstance(tool_usage, dict) and "tools_called" in tool_usage:
                # Convert tool usage to the expected format
                for tool_name in tool_usage.get("tools_called", []):
                    tool_call_results.append({
                        "tool": tool_name,
                        "status": "success",
                        "result": {},
                        "arguments": {}
                    })

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
            if isinstance(tool_usage, dict):
                for tool_name in tool_usage.get("tools_called", []):
                    formatted_tool_calls.append(
                        ToolCallResult(
                            tool=tool_name,
                            status="success",
                            result={},
                            error=tool_usage.get("error"),
                            execution_time_ms=None
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
    current_user: TokenData = Depends(get_current_user)
):
    """
    Retrieve all messages in a specific conversation

    Args:
        user_id: The ID of the user requesting the conversation
        conversation_id: The ID of the conversation to retrieve
        current_user: Current authenticated user

    Returns:
        List of messages in the conversation
    """
    # Verify that the authenticated user matches the requested user ID
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own conversations"
        )

    # Create session manually since we're using sync_engine
    with Session(sync_engine) as session:
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