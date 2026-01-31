from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Union
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBotError(Exception):
    """Base exception class for chatbot-related errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(ChatBotError):
    """Raised when input validation fails"""
    pass

class AuthenticationError(ChatBotError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(ChatBotError):
    """Raised when authorization fails"""
    pass

class DatabaseError(ChatBotError):
    """Raised when database operations fail"""
    pass

class AIServiceError(ChatBotError):
    """Raised when AI service operations fail"""
    pass

def setup_error_handlers(app):
    """Set up global error handlers for the FastAPI application"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.message,
                "error_code": exc.error_code or "VALIDATION_ERROR"
            }
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": exc.message,
                "error_code": exc.error_code or "AUTHENTICATION_ERROR"
            }
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(request: Request, exc: AuthorizationError):
        logger.warning(f"Authorization Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": exc.message,
                "error_code": exc.error_code or "AUTHORIZATION_ERROR"
            }
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"Database Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "A database error occurred",
                "error_code": exc.error_code or "DATABASE_ERROR",
                "detail": exc.message if app.debug else None
            }
        )

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        logger.error(f"AI Service Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "An error occurred with the AI service",
                "error_code": exc.error_code or "AI_SERVICE_ERROR",
                "detail": exc.message if app.debug else None
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "An unexpected error occurred",
                "error_code": "UNEXPECTED_ERROR"
            }
        )

def log_api_call(endpoint: str, user_id: str = None, success: bool = True):
    """Log API calls for monitoring and debugging"""
    status = "SUCCESS" if success else "FAILED"
    user_info = f"User: {user_id}" if user_id else "Anonymous"
    logger.info(f"API Call: {endpoint} - {user_info} - {status}")

def log_chat_interaction(user_message: str, assistant_response: str = None, user_id: str = None):
    """Log chat interactions for analysis and debugging"""
    user_info = f"User: {user_id}" if user_id else "Anonymous"
    logger.info(f"Chat Interaction - {user_info}: User said '{user_message[:50]}...' | Assistant replied '{assistant_response[:50]}...'")
