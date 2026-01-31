from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ToolCallRequest(BaseModel):
    """Standard request format for MCP tool calls"""
    user_id: str
    tool_name: str
    parameters: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """Standard response format for MCP tool calls"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: str = "success"  # "success", "error", "pending"


class BaseMCPTaskTool(ABC):
    """
    Abstract base class for all MCP task management tools
    """

    @abstractmethod
    async def execute(self, user_id: str, **kwargs) -> ToolCallResponse:
        """
        Execute the MCP tool with the given parameters

        Args:
            user_id: The ID of the user making the request
            **kwargs: Tool-specific parameters

        Returns:
            ToolCallResponse containing the result of the operation
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool as it should appear in the MCP manifest"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A human-readable description of what the tool does"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for the tool's input parameters"""
        pass