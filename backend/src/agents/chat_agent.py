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
from ..mcp_tools.update_task import UpdateTaskParams, update_task
from ..mcp_tools.complete_task import CompleteTaskParams, complete_task
from ..mcp_tools.delete_task import DeleteTaskParams, delete_task

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Client will be initialized lazily inside the function to handle API key issues gracefully

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
    return """You are an AI assistant integrated with a task management system. Your job is to manage user tasks ONLY through the provided tools.

You MUST follow these rules strictly:

GENERAL RULES
- NEVER claim a task was updated, completed, or deleted unless the corresponding tool has been executed successfully.
- NEVER invent results.
- ALWAYS use tools when performing task operations.
- NEVER add a task unless the user clearly requests to add/create one.
- CRITICAL: When the user says "update task", "done the task", "mark task", "mark tasks", "complete task", or "complete tasks", DO NOT use add_task under ANY circumstances.
- ALWAYS follow the correct sequence: list_tasks first, then the appropriate operation (complete_task, update_task, delete_task).
- CRITICAL: You may need to call MULTIPLE TOOLS in sequence to fulfill a user request. For example, to complete a task by name, you must call BOTH list_tasks AND complete_task in sequence.
- CRITICAL: If you need to find a task first, ALWAYS call list_tasks before calling the operation tool.
- CRITICAL MULTI-STEP SEQUENCE: When a user wants to complete/update/delete a task by name, you MUST follow this exact sequence:
  1. First, call list_tasks to retrieve all tasks for the user
  2. Examine the returned tasks to find one that matches the user's description
  3. Then call the appropriate operation (complete_task, update_task, or delete_task) with the found task_id
- CRITICAL: NEVER skip the list_tasks step when the user refers to a task by name.
- CRITICAL PARSING RULES:
  * "mark tasks X" means find task named "X" and complete it (NOT create task named "tasks X")
  * "mark task X" means find task named "X" and complete it (NOT create task named "task X")
  * "update tasks X" means find task named "X" and update it (NOT create task named "tasks X")
  * "update task X" means find task named "X" and update it (NOT create task named "task X")
  * "delete tasks X" means find task named "X" and delete it (NOT create task named "tasks X")
  * "delete task X" means find task named "X" and delete it (NOT create task named "task X")
- If unsure which task the user means, ask clarification.

TOOL USAGE RULES

1. Adding tasks
Use add_task ONLY when the user explicitly says:
- add
- create
- new task
- remember to
- create a reminder

2. Listing tasks
Use list_tasks when user asks:
- show tasks
- list tasks
- what tasks do I have
- pending tasks
- completed tasks

3. Completing tasks
When the user says:
- mark task complete
- complete task
- done with task
- finished task
- mark task done
- complete task done
- mark task [task_name] done
- complete task [task_name] done
You MUST:
STEP 1: call list_tasks to find matching task
STEP 2: call complete_task using the correct task_id
DO NOT add a new task.

4. Updating tasks
When the user says:
- update task
- rename task
- change task
- modify task
You MUST call update_task with the provided changes.
DO NOT create a new task.

5. Deleting tasks
When user says:
- delete task
- remove task
- cancel task
You MUST call delete_task.
DO NOT create tasks.

6. Task name references
If the user refers to tasks by name:
Example: "complete project task"
You MUST first call list_tasks to find matching tasks, then operate using the task ID.

7. Ambiguous cases
If multiple tasks match:
Ask user which one instead of guessing.

RESPONSE RULES
- Confirm actions after tool success.
- Keep responses short and friendly.
- Never hallucinate task data.
- If tool fails, inform the user.

Example interactions:

ADDING TASKS:
User: "Add a task to buy groceries"
Assistant: [Uses add_task with title="buy groceries"]

User: "Create a new task called 'finish report'"
Assistant: [Uses add_task with title="finish report"]

LISTING TASKS:
User: "Show me my tasks"
Assistant: [Uses list_tasks to show all tasks]

User: "What's pending?"
Assistant: [Uses list_tasks with status_filter="pending"]

COMPLETING TASKS:
User: "Complete task project done"
Assistant: [Step 1: Uses list_tasks to find the task with title "project done"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Complete project task"
Assistant: [Step 1: Uses list_tasks to find the task with title "project"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Mark task 'buy groceries' complete"
Assistant: [Step 1: Uses list_tasks to find the task with title "buy groceries"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Mark task flower done"
Assistant: [Step 1: Uses list_tasks to find the task with title "flower"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Complete task buy done"
Assistant: [Step 1: Uses list_tasks to find the task with title "buy"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Mark task flower complete"
Assistant: [Step 1: Uses list_tasks to find the task with title "flower"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Complete task 'old task'"
Assistant: [Step 1: Uses list_tasks to find the task with title "old task"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

User: "Mark task 'shopping list' done"
Assistant: [Step 1: Uses list_tasks to find the task with title "shopping list"]
[Step 2: Uses complete_task with the found task_id to mark it as complete]

UPDATING TASKS:
User: "Update project task title to Final project"
Assistant: [Step 1: Uses list_tasks to find the task with title "project"]
[Step 2: Uses update_task with the found task_id and new title "Final project"]

User: "Change task 'buy groceries' to 'buy food'"
Assistant: [Step 1: Uses list_tasks to find the task with title "buy groceries"]
[Step 2: Uses update_task with the found task_id and new title "buy food"]

User: "update task reading to studying"
Assistant: [Step 1: Uses list_tasks to find the task with title "reading"]
[Step 2: Uses update_task with the found task_id and new title "studying"]

User: "change task reading to studying"
Assistant: [Step 1: Uses list_tasks to find the task with title "reading"]
[Step 2: Uses update_task with the found task_id and new title "studying"]

UPDATING TASKS BY PARSING NATURAL LANGUAGE:
User: "update task reading to studying"
Assistant: [Step 1: Parses the request to identify "reading" as current title and "studying" as new title]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses update_task with the found task_id and new title "studying"]

User: "update task 'buy groceries' to 'buy food'"
Assistant: [Step 1: Parses the request to identify "buy groceries" as current title and "buy food" as new title]
[Step 2: Uses list_tasks to find the task with title "buy groceries"]
[Step 3: Uses update_task with the found task_id and new title "buy food"]

User: "change task 'reading' to 'studying'"
Assistant: [Step 1: Parses the request to identify "reading" as current title and "studying" as new title]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses update_task with the found task_id and new title "studying"]

DELETING TASKS:
User: "Delete task project"
Assistant: [Step 1: Uses list_tasks to find the task with title "project"]
[Step 2: Uses delete_task with the found task_id to remove it]

User: "Remove task 'buy groceries'"
Assistant: [Step 1: Uses list_tasks to find the task with title "buy groceries"]
[Step 2: Uses delete_task with the found task_id to remove it]

User: "delete task reading"
Assistant: [Step 1: Uses list_tasks to find the task with title "reading"]
[Step 2: Uses delete_task with the found task_id to remove it]

User: "remove task reading"
Assistant: [Step 1: Uses list_tasks to find the task with title "reading"]
[Step 2: Uses delete_task with the found task_id to remove it]

DELETING TASKS BY PARSING NATURAL LANGUAGE:
User: "delete task reading"
Assistant: [Step 1: Parses the request to identify "reading" as the task to delete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses delete_task with the found task_id to remove it]

User: "remove task reading"
Assistant: [Step 1: Parses the request to identify "reading" as the task to delete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses delete_task with the found task_id to remove it]

User: "delete task 'buy groceries'"
Assistant: [Step 1: Parses the request to identify "buy groceries" as the task to delete]
[Step 2: Uses list_tasks to find the task with title "buy groceries"]
[Step 3: Uses delete_task with the found task_id to remove it]

SPECIFIC PROBLEM PATTERNS:
User: "update task"
Assistant: [Step 1: Uses list_tasks to find the relevant task]
[Step 2: Uses update_task with the found task_id to update it]
[CRITICAL: Do NOT use add_task]

User: "done the task"
Assistant: [Step 1: Uses list_tasks to find the relevant task]
[Step 2: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task]

User: "mark tasks reading"
Assistant: [Step 1: Uses list_tasks to find the task with title "reading"]
[Step 2: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task]

User: "mark task reading"
Assistant: [Step 1: Uses list_tasks to find the task with title "reading"]
[Step 2: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task]

User: "mark reading task"
Assistant: [Step 1: Parses the request to identify "reading" as the task to mark complete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task]

COMPLETING TASKS BY PARSING NATURAL LANGUAGE:
User: "mark task reading complete"
Assistant: [Step 1: Parses the request to identify "reading" as the task to mark complete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]

User: "mark tasks reading"
Assistant: [Step 1: Parses the request to identify "reading" as the task to mark complete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]

User: "complete task reading"
Assistant: [Step 1: Parses the request to identify "reading" as the task to mark complete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]

User: "complete tasks reading"
Assistant: [Step 1: Parses the request to identify "reading" as the task to mark complete]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]

User: "complete task braclate"
Assistant: [Step 1: Parses the request to identify "braclate" as the task to mark complete]
[Step 2: Uses list_tasks to find the task with title "braclate"]
[Step 3: Uses complete_task with the found task_id to mark it complete]

MULTI-STEP COMPLETION PROCESS EXAMPLES:
User: "mark task flower done"
Assistant: [Step 1: Recognizes this as a completion request for task named "flower"]
[Step 2: Calls list_tasks to find all tasks for the user]
[Step 3: Identifies the task with title "flower" from the list]
[Step 4: Calls complete_task with the found task_id]
[CRITICAL: Never skips the list_tasks step]

User: "complete task buy done"
Assistant: [Step 1: Recognizes this as a completion request for task named "buy"]
[Step 2: Calls list_tasks to find all tasks for the user]
[Step 3: Identifies the task with title "buy" from the list]
[Step 4: Calls complete_task with the found task_id]
[CRITICAL: Never skips the list_tasks step]

CRITICAL PARSING EXAMPLES - AVOIDING WRONG INTERPRETATIONS:
User: "mark tasks reading"
Assistant: [Step 1: CORRECTLY recognizes this as a completion request for task named "reading", NOT a request to create "tasks reading"]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task with title "tasks reading"]

User: "mark task reading"
Assistant: [Step 1: CORRECTLY recognizes this as a completion request for task named "reading", NOT a request to create "task reading"]
[Step 2: Uses list_tasks to find the task with title "reading"]
[Step 3: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task with title "task reading"]

User: "complete task braclate"
Assistant: [Step 1: CORRECTLY recognizes this as a completion request for task named "braclate", NOT a request to create "task braclate"]
[Step 2: Uses list_tasks to find the task with title "braclate"]
[Step 3: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task with title "task braclate"]

User: "complete tasks braclate"
Assistant: [Step 1: CORRECTLY recognizes this as a completion request for task named "braclate", NOT a request to create "tasks braclate"]
[Step 2: Uses list_tasks to find the task with title "braclate"]
[Step 3: Uses complete_task with the found task_id to mark it complete]
[CRITICAL: Do NOT use add_task with title "tasks braclate"]

ERROR HANDLING:
When a task is not found during completion, update, or deletion:
- If the user says "complete task X" but task X doesn't exist, inform the user: "I couldn't find a task named 'X'. Would you like to create it instead?"
- NEVER automatically create a task when the user intended to complete/update/delete
- ALWAYS respect the user's original intent

TASK IDENTIFICATION FOR EXISTING TASKS:
- When a user wants to operate on a task by name, ALWAYS use list_tasks first to retrieve all tasks for the user
- Look carefully through all existing tasks to find the one that matches the user's request
- Match based on title similarity, partial matches, and context
- If multiple tasks match the user's description, ask the user to clarify which one they mean
- If a close match exists, you may confirm with the user: "Did you mean task '[similar_task_title]'?"

USER GUIDANCE:
When users ask for help or seem confused, provide clear examples:
- To add a task: "Add task buy groceries" or "Create task finish report"
- To update a task: "Update task reading to studying" or "Change task 'buy groceries' to 'buy food'"
- To complete a task: "Complete task reading" or "Mark task 'buy groceries' complete" or "Done with task reading"
- To delete a task: "Delete task reading" or "Remove task 'buy groceries'"
- To see tasks: "Show my tasks" or "List all tasks" or "What's pending?"

You must always follow this exact behavior."""


def process_chat_request(chat_request: ChatRequest) -> ChatResponse:
    """
    Process a chat request using the AI agent and MCP tools
    """
    logger.info(f"Processing chat request for user {chat_request.user_id}")

    # FIRST: Try direct MCP tool detection for faster response
    import re

    # Parse the message to determine intent for direct MCP execution
    message_lower = chat_request.message.lower().strip()

    # Handle ADD TASK directly
    if any(keyword in message_lower for keyword in ['add ', 'create ', 'new task']):
        title_match = re.search(r'(?:add|create|new task to|new task)\s+(?:task\s+)?(.+)', message_lower)
        if title_match:
            title = title_match.group(1).strip().capitalize()

            # Execute the add_task tool directly
            params = AddTaskParams(user_id=chat_request.user_id, title=title)
            result = add_task(params)

            # Extract task details from result for response
            import ast
            result_text = result[0].text
            task_data = ast.literal_eval(result_text)

            response_text = f"I've added \"{task_data['task_details']['title']}\" to your tasks."

            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["add_task"], "success": True}
            )

    # Handle LIST TASKS directly
    elif any(keyword in message_lower for keyword in ['show', 'list', 'what', 'tasks']):
        # Execute the list_tasks tool directly
        params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
        result = list_tasks(params)

        import ast
        result_text = result[0].text
        tasks_data = ast.literal_eval(result_text)
        tasks = tasks_data.get('tasks', [])

        if not tasks:
            response_text = "You don't have any tasks on your list right now."
        else:
            task_list = "\n".join([
                f"• {task.get('title', 'Untitled')} ({'Completed' if task.get('is_completed', False) else 'Pending'})"
                for task in tasks
            ])
            response_text = f"Here are your tasks:\n{task_list}"

        return ChatResponse(
            response=response_text,
            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
            tool_usage={"tools_called": ["list_tasks"], "success": True}
        )

    # Handle COMPLETE TASK directly
    elif any(keyword in message_lower for keyword in ['complete task', 'mark task', 'mark', 'complete', 'finish task', 'finish']) and ('complete' in message_lower or 'done' in message_lower or 'finish' in message_lower):
        # First list tasks to find matching task
        list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
        list_result = list_tasks(list_params)

        import ast
        list_response = ast.literal_eval(list_result[0].text)
        tasks = list_response.get('tasks', [])

        # Try to find a matching task based on keywords in the message
        task_found = None
        # Extract potential task identifiers from message
        import re

        # Extract task name from various command patterns
        # Patterns to handle: "mark task X complete", "complete task X", "mark X done", etc.
        import re

        # Try multiple patterns to extract the task name
        patterns = [
            r'(?:mark|complete|finish)\s+(?:task\s+)?(.*?)\s+(?:as\s+)?(?:complete|done|finished)',
            r'(?:mark|complete|finish)\s+(?:task\s+)?([^,.!?]+?)(?=\s|$|,|\.|!|\?)',
            r'(?:mark|complete|finish)\s+(?:the\s+)?(.*?)\s+(?:as\s+)?(?:complete|done|finished)'
        ]

        task_keyword = None
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                task_keyword = match.group(1).strip()
                if task_keyword:  # Make sure we got a non-empty match
                    break

        # If still no task keyword found, try simpler extraction
        if not task_keyword:
            # Look for "mark X" or "complete X" patterns
            simple_match = re.search(r'(?:mark|complete|finish)\s+(?:task\s+)?(\w+(?:\s+\w+)*)', message_lower)
            if simple_match:
                task_keyword = simple_match.group(1).strip()

        if task_keyword:
            # Look for matching task - try exact match first, then partial match
            for task in tasks:
                if not task.get('is_completed', False):  # Only look for incomplete tasks
                    # Try exact match first (case-insensitive)
                    if task['title'].lower().strip() == task_keyword.lower().strip():
                        task_found = task
                        break
                    # Then try if the task title starts with or contains the keyword
                    elif task_keyword.lower().strip() in task['title'].lower().strip():
                        # Prioritize exact matches over partial matches
                        if not task_found or len(task['title'].lower().strip()) <= len(task_found['title'].lower().strip()):
                            task_found = task

            # If still no exact match found, use the first partial match as fallback
            if not task_found:
                for task in tasks:
                    if not task.get('is_completed', False):  # Only look for incomplete tasks
                        if task_keyword.lower().strip() in task['title'].lower().strip():
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
            try:
                result_text = complete_result[0].text
                task_data = ast.literal_eval(result_text)

                response_text = f"I've completed \"{task_data['task_details']['title']}\" for you."
            except Exception as e:
                logger.error(f"Error parsing complete result: {str(e)}")
                response_text = f"I've completed the task for you."

            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["list_tasks", "complete_task"], "success": True}
            )
        else:
            # If no task found, suggest to user
            response_text = f"I couldn't find a task matching your request to complete. Would you like to add a new task instead?"
            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["list_tasks"], "success": False}
            )

    # Handle UPDATE TASK directly
    elif any(keyword in message_lower for keyword in ['update task', 'change task', 'rename task', 'update', 'change', 'rename']):
        # First list tasks to find matching task
        list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
        list_result = list_tasks(list_params)

        import ast
        list_response = ast.literal_eval(list_result[0].text)
        tasks = list_response.get('tasks', [])

        # Try to find a matching task and new title
        task_found = None
        new_title = None

        # Look for various patterns like "update task X to Y", "change X to Y", etc.
        import re
        patterns = [
            r'(?:update|change|rename)\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
            r'(?:update|change|rename)\s+(?:the\s+)?(.+?)\s+(?:to|into)\s+(.+)'
        ]

        # Try multiple patterns to extract the task name and new title
        patterns = [
            r'(?:update|change|rename)\s+(?:task\s+)?(.*?)\s+to\s+(.+)',
            r'(?:update|change|rename)\s+(?:the\s+)?(.*?)\s+(?:to|into)\s+(.+)'
        ]

        for pattern in patterns:
            update_match = re.search(pattern, message_lower)
            if update_match:
                old_part = update_match.group(1).strip()
                new_title = update_match.group(2).strip().capitalize()

                # Look for matching task - try exact match first, then partial match
                for task in tasks:
                    # Try exact match first (case-insensitive)
                    if task['title'].lower().strip() == old_part.lower().strip():
                        task_found = task
                        break
                    # Then try if the task title contains the keyword
                    elif old_part.lower().strip() in task['title'].lower().strip():
                        # Prioritize exact matches over partial matches
                        if not task_found or len(task['title'].lower().strip()) <= len(task_found['title'].lower().strip()):
                            task_found = task

                # If still no exact match found, use the first partial match as fallback
                if not task_found and old_part:
                    for task in tasks:
                        if old_part.lower().strip() in task['title'].lower().strip():
                            task_found = task
                            break

                if task_found and new_title:
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
            try:
                result_text = update_result[0].text
                task_data = ast.literal_eval(result_text)

                response_text = f"I've updated \"{task_data['task_details']['title']}\" in your tasks."
            except Exception as e:
                logger.error(f"Error parsing update result: {str(e)}")
                response_text = f"I've updated the task for you."

            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["list_tasks", "update_task"], "success": True}
            )
        else:
            response_text = f"To update a task, please specify what you'd like to change it to. For example: 'update task study to study physics'."
            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["list_tasks"], "success": False}
            )

    # Handle DELETE TASK directly
    elif any(keyword in message_lower for keyword in ['delete task', 'remove task', 'delete', 'remove', 'cancel']):
        # First list tasks to find matching task
        list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
        list_result = list_tasks(list_params)

        import ast
        list_response = ast.literal_eval(list_result[0].text)
        tasks = list_response.get('tasks', [])

        # Try to find a matching task based on keywords in the message
        task_found = None
        # Extract potential task identifiers from message
        import re

        # Look for various patterns like "delete task X", "remove X", "delete X", etc.
        patterns = [
            r'(?:delete|remove|cancel)\s+(?:task\s+)?(\w+(?:\s+\w+)*)',
            r'(?:delete|remove|cancel)\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+(?:task|one)'
        ]

        # Extract task name from various command patterns
        import re

        # Try multiple patterns to extract the task name
        patterns = [
            r'(?:delete|remove|cancel)\s+(?:task\s+)?(.*?)\s*(?=\s|$|,|\.|!|\?)',
            r'(?:delete|remove|cancel)\s+(?:the\s+)?(.*?)\s*(?=\s|$|,|\.|!|\?)'
        ]

        task_keyword = None
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                task_keyword = match.group(1).strip()
                if task_keyword:  # Make sure we got a non-empty match
                    break

        # If still no task keyword found, try simpler extraction
        if not task_keyword:
            # Look for "delete X" or "remove X" patterns
            simple_match = re.search(r'(?:delete|remove|cancel)\s+(?:task\s+)?(\w+(?:\s+\w+)*)', message_lower)
            if simple_match:
                task_keyword = simple_match.group(1).strip()

        if task_keyword:
            # Look for matching task - try exact match first, then partial match
            for task in tasks:
                # Try exact match first (case-insensitive)
                if task['title'].lower().strip() == task_keyword.lower().strip():
                    task_found = task
                    break
                # Then try if the task title starts with or contains the keyword
                elif task_keyword.lower().strip() in task['title'].lower().strip():
                    # Prioritize exact matches over partial matches
                    if not task_found or len(task['title'].lower().strip()) <= len(task_found['title'].lower().strip()):
                        task_found = task

            # If still no exact match found, use the first partial match as fallback
            if not task_found:
                for task in tasks:
                    if task_keyword.lower().strip() in task['title'].lower().strip():
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
            try:
                result_text = delete_result[0].text
                task_data = ast.literal_eval(result_text)

                response_text = f"I've deleted \"{task_data['task_details']['title']}\" from your tasks."
            except Exception as e:
                logger.error(f"Error parsing delete result: {str(e)}")
                response_text = f"I've deleted the task for you."

            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["list_tasks", "delete_task"], "success": True}
            )
        else:
            # If no task found, suggest to user
            response_text = f"I couldn't find a task matching your request to delete."
            return ChatResponse(
                response=response_text,
                conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                tool_usage={"tools_called": ["list_tasks"], "success": False}
            )

    # If no direct MCP pattern matched, proceed with AI provider
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
            # Initialize AI client based on provider configuration (lazy initialization)
            if config.AI_PROVIDER.lower() == 'openrouter':
                client = OpenAI(
                    api_key=config.OPENROUTER_API_KEY,
                    base_url=config.OPENROUTER_BASE_URL
                )
                model_to_use = config.OPENROUTER_MODEL
            else:  # Default to OpenAI
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL
                )
                model_to_use = config.OPENAI_MODEL

            response = client.chat.completions.create(
                model=model_to_use,
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
                    },
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
                    }
                ],
                tool_choice="auto"
            )
        except Exception as ai_error:
            logger.error(f"AI provider error: {str(ai_error)}")

            # Intelligent fallback for task operations when AI provider is unavailable
            import re

            # Parse the message to determine intent for fallback
            message_lower = chat_request.message.lower().strip()

            # Handle ADD TASK
            if any(keyword in message_lower for keyword in ['add ', 'create ', 'new task']):
                title_match = re.search(r'(?:add|create|new task to|new task)\s+(?:task\s+)?(.+)', message_lower)
                if title_match:
                    title = title_match.group(1).strip().capitalize()

                    # Execute the add_task tool directly
                    params = AddTaskParams(user_id=chat_request.user_id, title=title)
                    result = add_task(params)

                    # Extract task details from result for response
                    import ast
                    result_text = result[0].text
                    task_data = ast.literal_eval(result_text)

                    response_text = f"✅ I've added \"{task_data['task_details']['title']}\" to your tasks."

                    return ChatResponse(
                        response=response_text,
                        conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                        tool_usage={"tools_called": ["add_task"], "success": True}
                    )

            # Handle LIST TASKS
            elif any(keyword in message_lower for keyword in ['show', 'list', 'what', 'tasks']):
                # Execute the list_tasks tool directly
                params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
                result = list_tasks(params)

                import ast
                result_text = result[0].text
                tasks_data = ast.literal_eval(result_text)
                tasks = tasks_data.get('tasks', [])

                if not tasks:
                    response_text = "📋 You don't have any tasks on your list right now."
                else:
                    task_list = "\n".join([
                        f"• {task.get('title', 'Untitled')} ({'Completed' if task.get('is_completed', False) else 'Pending'})"
                        for task in tasks
                    ])
                    response_text = f"📋 Here are your tasks:\n{task_list}"

                return ChatResponse(
                    response=response_text,
                    conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                    tool_usage={"tools_called": ["list_tasks"], "success": True}
                )

            # Handle COMPLETE TASK
            elif any(keyword in message_lower for keyword in ['complete ', 'mark ', 'finish ', 'done']):
                # First list tasks to find matching task
                list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
                list_result = list_tasks(list_params)

                import ast
                list_response = ast.literal_eval(list_result[0].text)
                tasks = list_response.get('tasks', [])

                # Try to find a matching task based on keywords in the message
                task_found = None
                # Extract potential task identifiers from message
                import re
                # Look for patterns like "complete task X" or "mark X done"
                task_name_match = re.search(r'(?:complete|mark|finish)\s+(?:task\s+)?(\w+)(?:\s+done|as\s+done|complete)?', message_lower)

                if task_name_match:
                    task_keyword = task_name_match.group(1)

                    # Look for matching task
                    for task in tasks:
                        if not task.get('is_completed', False):  # Only look for incomplete tasks
                            if task_keyword.lower() in task['title'].lower() or task['title'].lower() in task_keyword.lower():
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
                    try:
                        result_text = complete_result[0].text
                        task_data = ast.literal_eval(result_text)

                        response_text = f"I've completed \"{task_data['task_details']['title']}\" for you."
                        return ChatResponse(
                            response=response_text,
                            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                            tool_usage={"tools_called": ["list_tasks", "complete_task"], "success": True}
                        )
                    except Exception as e:
                        logger.error(f"Error parsing complete result: {str(e)}")
                        response_text = f"I've completed the task for you."
                        return ChatResponse(
                            response=response_text,
                            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                            tool_usage={"tools_called": ["list_tasks", "complete_task"], "success": True}
                        )
                else:
                    # If no task found, suggest to user
                    response_text = f"I couldn't find a task matching your request to complete. Would you like to add a new task instead?"
                    return ChatResponse(
                        response=response_text,
                        conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                        tool_usage={"tools_called": ["list_tasks"], "success": False}
                    )

            # Handle UPDATE TASK
            elif any(keyword in message_lower for keyword in ['update ', 'change ', 'rename ']):
                # First list tasks to find matching task
                list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
                list_result = list_tasks(list_params)

                import ast
                list_response = ast.literal_eval(list_result[0].text)
                tasks = list_response.get('tasks', [])

                # Try to find a matching task and new title
                task_found = None
                new_title = None

                # Look for patterns like "update task X to Y"
                import re
                update_match = re.search(r'(?:update|change|rename)\s+(?:task\s+)?(.+?)\s+to\s+(.+)', message_lower)
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
                    try:
                        result_text = update_result[0].text
                        task_data = ast.literal_eval(result_text)

                        response_text = f"I've updated \"{task_data['task_details']['title']}\" in your tasks."
                        return ChatResponse(
                            response=response_text,
                            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                            tool_usage={"tools_called": ["list_tasks", "update_task"], "success": True}
                        )
                    except Exception as e:
                        logger.error(f"Error parsing update result: {str(e)}")
                        response_text = f"I've updated the task for you."
                        return ChatResponse(
                            response=response_text,
                            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                            tool_usage={"tools_called": ["list_tasks", "update_task"], "success": True}
                        )
                else:
                    response_text = f"To update a task, please specify what you'd like to change it to. For example: 'update task study to study physics'."
                    return ChatResponse(
                        response=response_text,
                        conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                        tool_usage={"tools_called": ["list_tasks"], "success": False}
                    )

            # Handle DELETE TASK
            elif any(keyword in message_lower for keyword in ['delete ', 'remove ', 'cancel ']):
                # First list tasks to find matching task
                list_params = ListTasksParams(user_id=chat_request.user_id, status_filter="all")
                list_result = list_tasks(list_params)

                import ast
                list_response = ast.literal_eval(list_result[0].text)
                tasks = list_response.get('tasks', [])

                # Try to find a matching task based on keywords in the message
                task_found = None
                # Extract potential task identifiers from message
                import re
                # Look for patterns like "delete task X" or "remove X" - capture multi-word task names
                task_name_match = re.search(r'(?:delete|remove|cancel)\s+(?:task\s+)?(\w+(?:\s+\w+)*)', message_lower)

                if task_name_match:
                    task_keyword = task_name_match.group(1)

                    # Look for matching task
                    for task in tasks:
                        if task_keyword.lower() in task['title'].lower() or task['title'].lower() in task_keyword.lower():
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
                    try:
                        result_text = delete_result[0].text
                        task_data = ast.literal_eval(result_text)

                        response_text = f"I've deleted \"{task_data['task_details']['title']}\" from your tasks."
                        return ChatResponse(
                            response=response_text,
                            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                            tool_usage={"tools_called": ["list_tasks", "delete_task"], "success": True}
                        )
                    except Exception as e:
                        logger.error(f"Error parsing delete result: {str(e)}")
                        response_text = f"I've deleted the task for you."
                        return ChatResponse(
                            response=response_text,
                            conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                            tool_usage={"tools_called": ["list_tasks", "delete_task"], "success": True}
                        )
                else:
                    # If no task found, suggest to user
                    response_text = f"I couldn't find a task matching your request to delete."
                    return ChatResponse(
                        response=response_text,
                        conversation_id=f"conv_{chat_request.user_id}_{hash(chat_request.message)}",
                        tool_usage={"tools_called": ["list_tasks"], "success": False}
                    )

            # For other operations, provide helpful response
            else:
                # Return a more helpful response that suggests common commands
                response_text = ("I'm having trouble connecting to my AI brain right now, but I can still help with basic task operations!\n"
                               "Try commands like: 'Add task buy groceries', 'Show my tasks', 'Complete task X', 'Update task X to Y'")

                return ChatResponse(
                    response=response_text,
                    conversation_id=f"error_conv_{chat_request.user_id}",
                    tool_usage={"tools_called": [], "success": False, "error": "AI provider unavailable, using limited functionality"}
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

                elif function_name == "update_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    params = UpdateTaskParams(**function_args)
                    result = update_task(params)
                    logger.info(f"update_task result: {result}")

                elif function_name == "list_tasks":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    # Set default filter if not provided
                    if "status_filter" not in function_args:
                        function_args["status_filter"] = "all"
                    params = ListTasksParams(**function_args)
                    result = list_tasks(params)
                    logger.info(f"list_tasks result: {result}")

                elif function_name == "complete_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    params = CompleteTaskParams(**function_args)
                    result = complete_task(params)
                    logger.info(f"complete_task result: {result}")

                elif function_name == "delete_task":
                    # Ensure user_id is set from the request
                    function_args["user_id"] = chat_request.user_id
                    params = DeleteTaskParams(**function_args)
                    result = delete_task(params)
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