"""
MCP Server Implementation for AI-Powered Todo Chatbot
Provides tools for the AI agent to interact with the task management system.
"""
import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import TextContent, ImageContent, ResourceTemplate, InitOptions
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("todo-chatbot-mcp-server")

class AddTaskRequest(BaseModel):
    """Request model for adding a task"""
    title: str = Field(..., description="Title of the task")
    description: str = Field("", description="Optional description of the task")
    user_id: str = Field(..., description="ID of the user adding the task")


class AddTaskResult(BaseModel):
    """Result model for adding a task"""
    success: bool = Field(..., description="Whether the operation was successful")
    task_id: str = Field(..., description="ID of the created task")
    message: str = Field(..., description="Confirmation message")


class ListTasksRequest(BaseModel):
    """Request model for listing tasks"""
    user_id: str = Field(..., description="ID of the user whose tasks to list")
    status_filter: str = Field("all", description="Filter for task status: 'all', 'pending', 'completed'")


class TaskItem(BaseModel):
    """Model representing a task item"""
    id: str
    title: str
    description: str
    completed: bool
    created_at: str


class ListTasksResult(BaseModel):
    """Result model for listing tasks"""
    success: bool = Field(..., description="Whether the operation was successful")
    tasks: List[TaskItem] = Field(..., description="List of tasks")
    message: str = Field(..., description="Status message")


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task"""
    task_id: str = Field(..., description="ID of the task to update")
    user_id: str = Field(..., description="ID of the user updating the task")
    title: str = Field(None, description="New title for the task")
    description: str = Field(None, description="New description for the task")
    completed: bool = Field(None, description="New completion status for the task")


class UpdateTaskResult(BaseModel):
    """Result model for updating a task"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Confirmation message")


class CompleteTaskRequest(BaseModel):
    """Request model for completing a task"""
    task_id: str = Field(..., description="ID of the task to complete")
    user_id: str = Field(..., description="ID of the user completing the task")


class CompleteTaskResult(BaseModel):
    """Result model for completing a task"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Confirmation message")


class DeleteTaskRequest(BaseModel):
    """Request model for deleting a task"""
    task_id: str = Field(..., description="ID of the task to delete")
    user_id: str = Field(..., description="ID of the user deleting the task")


class DeleteTaskResult(BaseModel):
    """Result model for deleting a task"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Confirmation message")


@server.list_resources()
async def list_resources():
    """List available resources"""
    yield ResourceTemplate(
        uri_template="todo://{user_id}/tasks",
        mime_types=["application/json"],
        name="User Tasks",
        description="Tasks belonging to a specific user"
    )


@server.read_resource()
async def read_resource(uri: str) -> List[TextContent]:
    """Read a resource"""
    logger.info(f"Reading resource: {uri}")
    # This would return task data for the specified URI
    return [TextContent(
        type="text",
        text=f"Resource content for {uri}"
    )]


@server.call_tool()
async def add_task(params: AddTaskRequest) -> List[TextContent]:
    """Add a new task for the user"""
    logger.info(f"MCP Tool: Adding task for user {params.user_id}")

    # In a real implementation, this would call the database service
    # For now, we'll return a mock response
    result = AddTaskResult(
        success=True,
        task_id="mock-task-id-123",
        message=f"Task '{params.title}' added successfully"
    )

    return [TextContent(type="text", text=result.model_dump_json())]


@server.call_tool()
async def list_tasks(params: ListTasksRequest) -> List[TextContent]:
    """List tasks for the user"""
    logger.info(f"MCP Tool: Listing tasks for user {params.user_id}, filter: {params.status_filter}")

    # In a real implementation, this would fetch from the database
    # For now, we'll return a mock response
    mock_tasks = [
        TaskItem(
            id="mock-task-1",
            title="Sample Task",
            description="This is a sample task",
            completed=False,
            created_at="2026-01-23T00:00:00Z"
        )
    ]

    result = ListTasksResult(
        success=True,
        tasks=mock_tasks,
        message=f"Found {len(mock_tasks)} tasks for user"
    )

    return [TextContent(type="text", text=result.model_dump_json())]


@server.call_tool()
async def update_task(params: UpdateTaskRequest) -> List[TextContent]:
    """Update an existing task"""
    logger.info(f"MCP Tool: Updating task {params.task_id} for user {params.user_id}")

    result = UpdateTaskResult(
        success=True,
        message=f"Task {params.task_id} updated successfully"
    )

    return [TextContent(type="text", text=result.model_dump_json())]


@server.call_tool()
async def complete_task(params: CompleteTaskRequest) -> List[TextContent]:
    """Mark a task as completed"""
    logger.info(f"MCP Tool: Completing task {params.task_id} for user {params.user_id}")

    result = CompleteTaskResult(
        success=True,
        message=f"Task {params.task_id} marked as completed"
    )

    return [TextContent(type="text", text=result.model_dump_json())]


@server.call_tool()
async def delete_task(params: DeleteTaskRequest) -> List[TextContent]:
    """Delete a task"""
    logger.info(f"MCP Tool: Deleting task {params.task_id} for user {params.user_id}")

    result = DeleteTaskResult(
        success=True,
        message=f"Task {params.task_id} deleted successfully"
    )

    return [TextContent(type="text", text=result.model_dump_json())]


async def run_mcp_server():
    """Run the MCP server"""
    logger.info("Starting MCP server...")
    # In a real implementation, this would start the server
    # For now, we'll just log that it's ready
    pass


if __name__ == "__main__":
    asyncio.run(run_mcp_server())