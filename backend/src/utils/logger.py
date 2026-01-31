import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import traceback
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AIInteractionLogger:
    """
    Specialized logger for AI interactions with structured logging
    """

    def __init__(self, name: str = "ai_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_interaction_start(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        session_id: Optional[str] = None
    ):
        """
        Log the start of an AI interaction

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation
            message: The user's message
            session_id: Optional session ID
        """
        log_data = {
            "event": "interaction_start",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message": message,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(f"AI_INTERACTION_START: {json.dumps(log_data)}")

    def log_interaction_end(
        self,
        user_id: str,
        conversation_id: str,
        response: str,
        tools_used: list,
        execution_time_ms: float,
        session_id: Optional[str] = None
    ):
        """
        Log the end of an AI interaction

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation
            response: The AI's response
            tools_used: List of tools used in the interaction
            execution_time_ms: Execution time in milliseconds
            session_id: Optional session ID
        """
        log_data = {
            "event": "interaction_end",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "response_length": len(response),
            "tools_used": tools_used,
            "execution_time_ms": execution_time_ms,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(f"AI_INTERACTION_END: {json.dumps(log_data)}")

    def log_tool_execution(
        self,
        user_id: str,
        conversation_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        execution_time_ms: float,
        success: bool,
        session_id: Optional[str] = None
    ):
        """
        Log the execution of an AI tool

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation
            tool_name: The name of the tool
            parameters: Parameters passed to the tool
            result: Result of the tool execution
            execution_time_ms: Execution time in milliseconds
            success: Whether the tool execution was successful
            session_id: Optional session ID
        """
        log_data = {
            "event": "tool_execution",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result_summary": self._summarize_result(result),
            "execution_time_ms": execution_time_ms,
            "success": success,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(f"TOOL_EXECUTION: {json.dumps(log_data)}")

    def log_error(
        self,
        user_id: str,
        conversation_id: str,
        error: Exception,
        context: str = "",
        session_id: Optional[str] = None
    ):
        """
        Log an error in AI interaction

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation
            error: The exception that occurred
            context: Additional context about the error
            session_id: Optional session ID
        """
        log_data = {
            "event": "error",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.error(f"AI_ERROR: {json.dumps(log_data)}")

    def log_performance_metrics(
        self,
        user_id: str,
        conversation_id: str,
        avg_response_time: float,
        avg_tokens_per_second: float,
        session_id: Optional[str] = None
    ):
        """
        Log performance metrics for AI interaction

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation
            avg_response_time: Average response time in milliseconds
            avg_tokens_per_second: Average tokens per second
            session_id: Optional session ID
        """
        log_data = {
            "event": "performance_metrics",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "avg_response_time_ms": avg_response_time,
            "avg_tokens_per_second": avg_tokens_per_second,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(f"PERFORMANCE_METRICS: {json.dumps(log_data)}")

    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the result for logging

        Args:
            result: The result to summarize

        Returns:
            A summary of the result
        """
        if isinstance(result, dict):
            # Limit the size of result for logging
            summary = {}
            for key, value in result.items():
                if isinstance(value, (str, int, float, bool)):
                    summary[key] = value
                elif isinstance(value, (list, tuple)):
                    summary[key] = f"<{len(value)} items>"
                else:
                    summary[key] = str(type(value))
            return summary
        else:
            return {"type": type(result).__name__, "summary": str(result)[:100]}


# Global AI interaction logger instance
ai_logger = AIInteractionLogger()