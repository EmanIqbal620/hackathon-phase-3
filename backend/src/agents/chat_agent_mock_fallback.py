"""
Mock fallback version of chat agent for when AI provider is unavailable
"""
import os
import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from ..config import config
from ..mcp_tools.add_task import AddTaskParams, add_task
from ..mcp_tools.list_tasks import ListTasksParams, list_tasks
from ..mcp_tools.analytics_tool import AnalyticsParams, analytics_tool
from ..mcp_tools.update_task import UpdateTaskParams, update_task
from ..mcp_tools.complete_task import CompleteTaskParams, complete_task
from ..mcp_tools.delete_task import DeleteTaskParams, delete_task
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def process_chat_request_with_fallback(chat_request: ChatRequest) -> ChatResponse:
    """
    Process a chat request with fallback for when AI provider is unavailable
    """
    logger.info(f"Processing chat request for user {chat_request.user_id}")

    try:
        # Try the normal AI processing first
        # But since we're creating a fallback, we'll handle the parsing directly
        message = chat_request.message.lower().strip()

        # Parse the message to determine intent
        if 'add' in message or 'create' in message or 'new task' in message:
            # Extract task title from the message
            title_match = re.search(r'(?:add|create|new task to|new task)\s+(?:task\s+)?(.+)', message)
            if title_match:
                title = title_match.group(1).strip().capitalize()
                params = AddTaskParams(user_id=chat_request.user_id, title=title)
                result = add_task(params)

                # Extract task details from result for response
                import ast
                result_text = result[0].text
                task_data = ast.literal_eval(result_text)

                response = f"✅ I've added \"{task_data['task_details']['title']}\" to your tasks."
                tool_usage = {"tools_called": ["add_task"], "success": True}
            else:
                response = "I can help you add a task. Try saying 'Add task buy groceries' or 'Create task finish report'."
                tool_usage = {"tools_called": [], "success": False}

        elif 'complete' in message or 'done' in message or 'finish' in message or 'mark' in message:
            # Handle completion - first list tasks, then complete
            list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
            list_result = list_tasks(list_params)

            import ast
            list_response = ast.literal_eval(list_result[0].text)
            tasks = list_response.get('tasks', [])

            # Try to find a matching task based on keywords in the message
            task_found = None
            for task in tasks:
                if not task.get('is_completed', False):  # Only look for incomplete tasks
                    if any(keyword in message for keyword in [task['title'].lower(), task['title'].split()[0].lower() if task['title'].split() else ""]):
                        task_found = task
                        break

            if task_found:
                # Complete the found task
                complete_params = CompleteTaskParams(
                    user_id=chat_request.user_id,
                    task_id=task_found['id']
                )
                complete_result = complete_task(complete_params)

                import ast
                result_text = complete_result[0].text
                task_data = ast.literal_eval(result_text)

                response = f"✅ I've completed \"{task_data['task_details']['title']}\" for you."
                tool_usage = {"tools_called": ["list_tasks", "complete_task"], "success": True}
            else:
                # If no task found, suggest adding it instead
                response = f"I couldn't find a task matching your request. Would you like me to add a new task instead?"
                tool_usage = {"tools_called": ["list_tasks"], "success": False}

        elif 'update' in message or 'change' in message or 'rename' in message:
            # Handle update - first list tasks, then update
            list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
            list_result = list_tasks(list_params)

            import ast
            list_response = ast.literal_eval(list_result[0].text)
            tasks = list_response.get('tasks', [])

            # Try to find a matching task and new title
            task_found = None
            new_title = None

            # Look for patterns like "update task X to Y"
            update_match = re.search(r'(?:update|change|rename)\s+(?:task\s+)?(.+?)\s+to\s+(.+)', message)
            if update_match:
                old_part = update_match.group(1).strip()
                new_title = update_match.group(2).strip().capitalize()

                for task in tasks:
                    if old_part.lower() in task['title'].lower():
                        task_found = task
                        break

            if task_found and new_title:
                # Update the found task
                update_params = UpdateTaskParams(
                    user_id=chat_request.user_id,
                    task_id=task_found['id'],
                    title=new_title
                )
                update_result = update_task(update_params)

                import ast
                result_text = update_result[0].text
                task_data = ast.literal_eval(result_text)

                response = f"✏️ I've updated \"{task_data['task_details']['title']}\" in your tasks."
                tool_usage = {"tools_called": ["list_tasks", "update_task"], "success": True}
            else:
                response = f"To update a task, please specify what you'd like to change it to. For example: 'update task study to study physics'."
                tool_usage = {"tools_called": ["list_tasks"], "success": False}

        elif 'delete' in message or 'remove' in message or 'cancel' in message:
            # Handle delete - first list tasks, then delete
            list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
            list_result = list_tasks(list_params)

            import ast
            list_response = ast.literal_eval(list_result[0].text)
            tasks = list_response.get('tasks', [])

            # Try to find a matching task
            task_found = None
            for task in tasks:
                if task['title'].lower() in message:
                    task_found = task
                    break

            if task_found:
                # Delete the found task
                delete_params = DeleteTaskParams(
                    user_id=chat_request.user_id,
                    task_id=task_found['id']
                )
                delete_result = delete_task(delete_params)

                import ast
                result_text = delete_result[0].text
                task_data = ast.literal_eval(result_text)

                response = f"🗑️ I've deleted \"{task_data['task_details']['title']}\" from your tasks."
                tool_usage = {"tools_called": ["list_tasks", "delete_task"], "success": True}
            else:
                response = f"I couldn't find a task matching your request to delete."
                tool_usage = {"tools_called": ["list_tasks"], "success": False}

        elif 'show' in message or 'list' in message or 'what' in message or 'tasks' in message:
            # Handle list tasks
            list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
            list_result = list_tasks(list_params)

            import ast
            list_response = ast.literal_eval(list_result[0].text)
            tasks = list_response.get('tasks', [])

            if tasks:
                task_list = "\n".join([
                    f"• {task.get('title', 'Untitled')} ({'Completed' if task.get('is_completed', False) else 'Pending'})"
                    for task in tasks
                ])
                response = f"📋 Here are your tasks:\n{task_list}"
            else:
                response = "📋 You don't have any tasks on your list right now."

            tool_usage = {"tools_called": ["list_tasks"], "success": True}
        else:
            response = "I can help you manage your tasks! Try commands like 'Add task buy groceries', 'Complete task', 'Show my tasks', etc."
            tool_usage = {"tools_called": [], "success": False}

        # Generate a conversation ID
        conversation_id = f"conv_{chat_request.user_id}_{hash(chat_request.message)}"

        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            tool_usage=tool_usage
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            response="I'm having trouble processing your request right now. Please try again.",
            conversation_id=f"error_conv_{chat_request.user_id}",
            tool_usage={"tools_called": [], "success": False, "error": str(e)}
        )


def create_system_prompt():
    return """You are an AI assistant integrated with a task management system. Your job is to manage user tasks ONLY through the provided tools."""