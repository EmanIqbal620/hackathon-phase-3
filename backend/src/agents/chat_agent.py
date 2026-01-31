"""
AI Chat Agent for the Todo Chatbot
This module implements an OpenAI-compatible agent that uses MCP tools to interact with the task management system.
"""
import os
import logging
from typing import Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel
from ..config import config
from ..mcp_tools.add_task import AddTaskParams, add_task
from ..mcp_tools.list_tasks import ListTasksParams, list_tasks
from ..mcp_tools.analytics_tool import AnalyticsParams, analytics_tool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL
)

class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    user_id: str
    message: str
    conversation_history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    response: str
    conversation_id: str
    tool_usage: Dict[str, Any]


def create_system_prompt():
    """Create the system prompt for the AI agent"""
    return f"""You are an AI assistant integrated with a task management system. Your purpose is to help users manage their tasks through natural language conversations.

You have access to the following tools:
1. add_task: Add a new task for the user
   Parameters: {{user_id, title, description}}

2. list_tasks: List tasks for the user
   Parameters: {{user_id, status_filter}} (status_filter can be "all", "pending", or "completed")

3. update_task: Update an existing task for the user
   Parameters: {{user_id, task_id, title?, description?, completed?}} (title, description, and completed are optional)

4. complete_task: Mark a task as completed for the user
   Parameters: {{user_id, task_id}}

5. delete_task: Delete a task for the user
   Parameters: {{user_id, task_id}}

6. analytics_tool: Get analytics and insights about user's tasks
   Parameters: {{user_id, time_range}} (time_range can be "day", "week", "month", "quarter", "year")

Rules:
- Always use the appropriate tool when a user wants to manage tasks
- The user_id parameter is provided automatically - you don't need to ask for it
- Be helpful, friendly, and confirm actions taken
- If a user asks about their tasks, use list_tasks with the appropriate filter
- If a user wants to add a task, use add_task with the task details
- If a user wants to update a task, use update_task with the task ID and new details
- If a user wants to mark a task complete, use complete_task with the task ID
- If a user wants to delete a task, use delete_task with the task ID
- If a user asks for insights, analytics, or statistics about their tasks, use analytics_tool
- For update_task, only include parameters that the user wants to change
- When a user refers to a task without specifying which one (e.g., "delete the meeting task" when multiple meeting tasks exist), ask for clarification before taking action
- When a user's request is ambiguous, always seek clarification rather than guessing

Example interactions:
User: "Add a task to buy groceries"
Assistant: [Uses add_task with title="buy groceries"]

User: "Show me my tasks"
Assistant: [Uses list_tasks to show all tasks]

User: "What's pending?"
Assistant: [Uses list_tasks with status_filter="pending"]

User: "Mark task abc123 as complete"
Assistant: [Uses complete_task with task_id="abc123"]

User: "How am I doing with my tasks?"
Assistant: [Uses analytics_tool to get insights]

User: "Show me my productivity this month"
Assistant: [Uses analytics_tool with time_range="month"]

User: "Delete the meeting task" (when multiple meeting tasks exist)
Assistant: "I see multiple tasks related to meetings. Could you please specify which one you'd like to delete?"

User: "Update task xyz789 to 'call mom tomorrow'"
Assistant: [Uses update_task with task_id="xyz789" and title="call mom tomorrow"]"""


def process_chat_request(chat_request: ChatRequest) -> ChatResponse:
    """
    Process a chat request using the AI agent and MCP tools
    """
    logger.info(f"Processing chat request for user {chat_request.user_id}")

    try:
        # Prepare the messages for the AI
        messages = [
            {"role": "system", "content": create_system_prompt()}
        ]

        # Add conversation history if available
        for msg in chat_request.conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add the current user message
        messages.append({
            "role": "user",
            "content": chat_request.message
        })

        # Call the AI with tool availability - add error handling for AI provider outages
        try:
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "add_task",
                            "description": "Add a new task for the user",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user creating the task"},
                                    "title": {"type": "string", "description": "Title of the task to create"},
                                    "description": {"type": "string", "description": "Optional description of the task"}
                                },
                                "required": ["user_id", "title"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "list_tasks",
                            "description": "List tasks for the user",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose tasks to list"},
                                    "status_filter": {"type": "string", "description": "Filter for task status: 'all', 'pending', 'completed'", "default": "all"}
                                },
                                "required": ["user_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "update_task",
                            "description": "Update an existing task for the user",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user updating the task"},
                                    "task_id": {"type": "string", "description": "ID of the task to update"},
                                    "title": {"type": "string", "description": "New title for the task (optional)"},
                                    "description": {"type": "string", "description": "New description for the task (optional)"},
                                    "completed": {"type": "boolean", "description": "New completion status for the task (optional)"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "complete_task",
                            "description": "Mark a task as completed for the user",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user completing the task"},
                                    "task_id": {"type": "string", "description": "ID of the task to complete"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "delete_task",
                            "description": "Delete a task for the user",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user deleting the task"},
                                    "task_id": {"type": "string", "description": "ID of the task to delete"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        }
                    }
                ],
                {
                    "type": "function",
                    "function": {
                        "name": "analytics_tool",
                        "description": "Get analytics and insights about user's tasks",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "ID of the user to get analytics for"},
                                "time_range": {"type": "string", "description": "Time range for analytics: 'day', 'week', 'month', 'quarter', 'year'", "default": "week"}
                            },
                            "required": ["user_id"]
                        }
                    }
                }],
                tool_choice="auto"
            )
        except Exception as ai_error:
            logger.error(f"AI provider error: {str(ai_error)}")
            # Return a graceful response when AI provider is unavailable
            return ChatResponse(
                response="I'm sorry, but I'm currently experiencing technical difficulties. Please try again later.",
                conversation_id=f"error_conv_{chat_request.user_id}",
                tool_usage={"tools_called": [], "success": False, "error": "AI provider unavailable"}
            )

        # Process the response
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Track which tools were used
        tool_usage = {"tools_called": [], "success": True}

        if tool_calls:
            # Execute the tools
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                import json
                function_args = json.loads(tool_call.function.arguments)

                tool_usage["tools_called"].append(function_name)

                if function_name == "add_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    params = AddTaskParams(**function_args)
                    result = add_task(params)
                    logger.info(f"add_task result: {result}")

                elif function_name == "list_tasks":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    # Set default filter if not provided
                    if "status_filter" not in function_args:
                        function_args["status_filter"] = "all"
                    params = ListTasksParams(**function_args)
                    result = list_tasks(params)
                    logger.info(f"list_tasks result: {result}")

                elif function_name == "update_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    from ..mcp_tools.update_task import UpdateTaskParams, update_task as update_task_func
                    params = UpdateTaskParams(**function_args)
                    result = update_task_func(params)
                    logger.info(f"update_task result: {result}")

                elif function_name == "complete_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    from ..mcp_tools.complete_task import CompleteTaskParams, complete_task as complete_task_func
                    params = CompleteTaskParams(**function_args)
                    result = complete_task_func(params)
                    logger.info(f"complete_task result: {result}")

                elif function_name == "delete_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    from ..mcp_tools.delete_task import DeleteTaskParams, delete_task as delete_task_func
                    params = DeleteTaskParams(**function_args)
                    result = delete_task_func(params)
                    logger.info(f"delete_task result: {result}")

                elif function_name == "analytics_tool":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    # Set default time range if not provided
                    if "time_range" not in function_args:
                        function_args["time_range"] = "week"
                    params = AnalyticsParams(**function_args)
                    result = analytics_tool(params)
                    logger.info(f"analytics_tool result: {result}")

        # Get the final response from the AI
        final_response = response_message.content

        # If no content was returned, synthesize a response based on tool usage
        if not final_response and tool_calls:
            if "add_task" in tool_usage["tools_called"]:
                final_response = "I've added the task for you."
            elif "list_tasks" in tool_usage["tools_called"]:
                final_response = "I've retrieved your tasks."
            else:
                final_response = "I've processed your request."

        # Generate a mock conversation ID
        conversation_id = f"conv_{chat_request.user_id}_{hash(chat_request.message)}"

        return ChatResponse(
            response=final_response or "I've processed your request.",
            conversation_id=conversation_id,
            tool_usage=tool_usage
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            response="Sorry, I encountered an error processing your request. Please try again.",
            conversation_id=f"error_conv_{chat_request.user_id}",
            tool_usage={"tools_called": [], "success": False, "error": str(e)}
        )


# Mock function for testing purposes
def mock_process_chat_request(chat_request: ChatRequest) -> ChatResponse:
    """
    Mock implementation of chat processing for testing
    """
    logger.info(f"(MOCK) Processing chat request for user {chat_request.user_id}")

    # Mock responses based on the message content
    message_lower = chat_request.message.lower()

    if "add" in message_lower or "create" in message_lower:
        response_text = "I've added that task for you!"
        tools_used = ["add_task"]
    elif "show" in message_lower or "list" in message_lower or "what" in message_lower:
        response_text = "Here are your tasks: Buy groceries, Call mom, Finish report."
        tools_used = ["list_tasks"]
    else:
        response_text = "I understood your message and processed it."
        tools_used = []

    return ChatResponse(
        response=response_text,
        conversation_id=f"mock_conv_{chat_request.user_id}_{len(chat_request.message)}",
        tool_usage={"tools_called": tools_used, "success": True}
    )