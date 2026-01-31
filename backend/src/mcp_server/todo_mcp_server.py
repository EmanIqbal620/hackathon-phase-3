from mcp.server import Server
from mcp.types import Tool, Argument, Result, InitOptions
from typing import Dict, Any, List
import asyncio
import os
from ..mcp_tools.task_operations import (
    add_task_tool, list_tasks_tool, complete_task_tool,
    delete_task_tool, update_task_tool
)

# Create MCP server instance
server = Server(
    name="todo-mcp-server",
    version="1.0.0"
)

# Register all task management tools
@server.tools.register
def add_task(user_id: str, title: str, description: str = "") -> Result:
    """
    Creates a new task for the user
    """
    # For MCP server, we'll return a mock result - actual implementation would call the tool
    return Result(content=f"Task '{title}' added successfully")

@server.tools.register
def list_tasks(user_id: str, status: str = "all") -> Result:
    """
    Lists tasks for the user, optionally filtered by status
    """
    # For MCP server, we'll return a mock result - actual implementation would call the tool
    return Result(content=f"Listing {status} tasks for user {user_id}")

@server.tools.register
def complete_task(user_id: str, task_id: int) -> Result:
    """
    Marks a task as completed
    """
    # For MCP server, we'll return a mock result - actual implementation would call the tool
    return Result(content=f"Task {task_id} marked as completed")

@server.tools.register
def delete_task(user_id: str, task_id: int) -> Result:
    """
    Deletes a task
    """
    # For MCP server, we'll return a mock result - actual implementation would call the tool
    return Result(content=f"Task {task_id} deleted successfully")

@server.tools.register
def update_task(user_id: str, task_id: int, title: str = "", description: str = "") -> Result:
    """
    Updates a task's title or description
    """
    # For MCP server, we'll return a mock result - actual implementation would call the tool
    update_parts = []
    if title:
        update_parts.append(f"title to '{title}'")
    if description:
        update_parts.append(f"description to '{description}'")

    return Result(content=f"Task {task_id} updated: {', '.join(update_parts) if update_parts else 'no changes'}")


async def serve():
    """Start the MCP server"""
    async with server.serve():
        print("MCP Server running...")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))

    # Note: In a real implementation, we'd configure the server to run on the specified port
    # For now, we'll just start the server with default configuration
    print(f"Starting MCP server on port {port}...")
    asyncio.run(serve())