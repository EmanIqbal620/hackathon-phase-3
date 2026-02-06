from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from ...middleware.auth import get_current_user
from ...src.models.user import User
from ...services.ai_agent_service import AIAgentService
from ...database import sync_engine
from sqlmodel import Session
import logging

router = APIRouter(prefix="/ai-agent", tags=["AI-Agent"])

# Define request/response models
class AIRequest(BaseModel):
    user_id: str
    conversation_id: Optional[str] = None
    message: str

class AIResponse(BaseModel):
    response: str
    conversation_id: str

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/message", response_model=AIResponse)
async def handle_ai_message(
    request: AIRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Main AI-Agent endpoint that:
    1. Receives user message, user_id, and conversation_id
    2. Detects intent (add, delete, update, list tasks)
    3. Calls the appropriate MCP tool with direct database access
    4. Returns JSON response with AI message
    """
    try:
        # Use the proper MCP tools with direct database access
        with Session(sync_engine) as session:
            ai_agent_service = AIAgentService(session)

            # Process the message using the AI agent service
            ai_response, tool_call_results = await ai_agent_service.process_message(
                user_id=current_user.id,
                message=request.message,
                conversation_history=[]
            )

            # Generate a conversation ID if not provided
            conversation_id = request.conversation_id or f"conv_{current_user.id}_{hash(request.message)}"

            return AIResponse(
                response=ai_response,
                conversation_id=str(conversation_id)
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing AI message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )