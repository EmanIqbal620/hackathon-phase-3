"""
Chat API Router
This module defines the API endpoints for the chatbot functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from ...dependencies.auth import get_current_user, TokenData
from ...agents.chat_agent import ChatRequest, process_chat_request
from ...models import Message, MessageCreate, Conversation, ConversationCreate
from ...database import sync_engine
from sqlmodel import Session, select
from datetime import datetime
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])

class ChatInput(BaseModel):
    """Input model for chat requests"""
    message: str = Field(
        ...,
        description="The user's message to the chatbot",
        min_length=1,
        max_length=2000,  # Limit message length to prevent abuse
    )
    conversation_id: Optional[str] = Field(
        None,
        description="The ID of the conversation (omit for new conversation)",
        pattern=r'^[a-zA-Z0-9_-]*$',  # Basic pattern to prevent injection
        min_length=1,
        max_length=100
    )


class ChatOutput(BaseModel):
    """Output model for chat responses"""
    response: str = Field(..., description="The AI's response to the user")
    conversation_id: str = Field(..., description="The ID of the conversation")
    tool_usage: Dict[str, any] = Field(..., description="Information about MCP tools used by the agent")


@router.post("/{user_id}", response_model=ChatOutput)
async def chat_endpoint(
    user_id: str,
    chat_input: ChatInput,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Main chat endpoint that processes user messages and returns AI responses.

    This endpoint:
    1. Authenticates the user via JWT
    2. Validates that the user_id in the path matches the authenticated user
    3. Loads conversation history from the database
    4. Processes the message with the AI agent
    5. Saves the user message and AI response to the database
    6. Returns the AI response
    """
    start_time = time.time()

    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own chat conversations"
        )

    logger.info(f"Processing chat request for user {user_id}")

    try:
        # Load conversation history from database
        conversation_history = []
        conversation_id = chat_input.conversation_id

        with Session(sync_engine) as session:
            # If no conversation_id provided, create a new conversation
            if not conversation_id:
                conversation_data = ConversationCreate(user_id=user_id)
                conversation = Conversation.model_validate(conversation_data)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                conversation_id = conversation.id
                logger.info(f"Created new conversation {conversation_id} for user {user_id}")
            else:
                # Verify that the conversation belongs to the user
                statement = select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
                conversation = session.exec(statement).first()
                if not conversation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found or does not belong to user"
                    )

                # Update the conversation's last activity time
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)

            # Load message history for this conversation
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            messages = session.exec(statement).all()

            # Convert messages to the format expected by the agent
            for msg in messages:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Create the chat request for the agent
        agent_request = ChatRequest(
            user_id=user_id,
            message=chat_input.message,
            conversation_history=conversation_history
        )

        # Process the request with the AI agent
        agent_response = process_chat_request(agent_request)

        # Save the user's message to the database
        with Session(sync_engine) as session:
            user_message_data = MessageCreate(
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content=chat_input.message
            )
            user_message = Message.model_validate(user_message_data)
            session.add(user_message)

            # Save the assistant's response to the database
            assistant_message_data = MessageCreate(
                conversation_id=conversation_id,
                user_id=user_id,  # The assistant acts on behalf of the user
                role="assistant",
                content=agent_response.response
            )
            assistant_message = Message.model_validate(assistant_message_data)
            session.add(assistant_message)

            session.commit()

        # Calculate response time for performance monitoring
        response_time = time.time() - start_time

        # Log performance metrics
        logger.info(f"Chat request completed for user {user_id}, response_time: {response_time:.2f}s")

        # Return the response
        return ChatOutput(
            response=agent_response.response,
            conversation_id=conversation_id,
            tool_usage=agent_response.tool_usage
        )

    except HTTPException:
        # Calculate response time even for errors
        response_time = time.time() - start_time
        logger.warning(f"Chat request failed for user {user_id}, response_time: {response_time:.2f}s")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Calculate response time for other errors
        response_time = time.time() - start_time
        logger.error(f"Error in chat endpoint for user {user_id}, response_time: {response_time:.2f}s, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


class ConversationListResponse(BaseModel):
    """Response model for listing conversations"""
    conversations: List[Dict]
    total: int


@router.get("/conversations/{user_id}", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    List all conversations for a user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own conversations"
        )

    try:
        with Session(sync_engine) as session:
            statement = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.created_at.desc())
            conversations = session.exec(statement).all()

            conversation_list = []
            for conv in conversations:
                conversation_list.append({
                    "id": conv.id,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                })

        return ConversationListResponse(
            conversations=conversation_list,
            total=len(conversation_list)
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving conversations"
        )


class MessageHistoryResponse(BaseModel):
    """Response model for conversation message history"""
    messages: List[Dict]


@router.get("/conversations/{user_id}/{conversation_id}", response_model=MessageHistoryResponse)
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get the message history for a specific conversation.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own conversations"
        )

    try:
        with Session(sync_engine) as session:
            # Verify that the conversation belongs to the user
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = session.exec(statement).first()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or does not belong to user"
                )

            # Get messages for this conversation
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            messages = session.exec(statement).all()

            message_list = []
            for msg in messages:
                message_list.append({
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                })

        return MessageHistoryResponse(messages=message_list)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving conversation history"
        )