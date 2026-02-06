from typing import Tuple, List, Dict, Any, Optional
from sqlmodel import Session
import logging
import re
from ..mcp.tools import mcp_tools
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class AIAgentService:
    def __init__(self, session: Session):
        self.session = session

    def _find_task_by_name_or_index(self, user_id: str, task_identifier: str):
        """
        Find a task by name (using fuzzy matching) or by index in the list.
        """
        # Get all tasks for the user
        all_tasks_result = mcp_tools.list_tasks(user_id=user_id)
        if not all_tasks_result.get("success"):
            return None

        tasks = all_tasks_result.get("tasks", [])

        # First, try to interpret as an index (e.g., "first", "second", "third", "1", "2", "3", etc.)
        task_identifier_clean = re.sub(r'[^\w\s]', '', task_identifier.lower().strip())

        # Map ordinal words to numbers
        ordinals = {
            "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
            "sixth": 5, "seventh": 6, "eighth": 7, "ninth": 8, "tenth": 9,
            "1": 0, "2": 1, "3": 2, "4": 3, "5": 4,
            "6": 5, "7": 6, "8": 7, "9": 8, "10": 9
        }

        if task_identifier_clean in ordinals:
            idx = ordinals[task_identifier_clean]
            if 0 <= idx < len(tasks):
                return tasks[idx]

        # If not an ordinal, try fuzzy matching by title with enhanced logic
        best_match = None
        best_ratio = 0

        for task in tasks:
            task_title = task.get("title", "")
            task_title_clean = re.sub(r'[^\w\s]', '', task_title.lower().strip())

            # Exact match (case-insensitive)
            if task_identifier_clean == task_title_clean:
                return task

            # Partial substring match
            if task_identifier_clean in task_title_clean or task_title_clean in task_identifier_clean:
                # Return the one with higher overlap ratio
                if len(task_identifier_clean) >= len(task_title_clean):
                    ratio = len(task_title_clean) / len(task_identifier_clean)
                else:
                    ratio = len(task_identifier_clean) / len(task_title_clean)

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = task

            # Fuzzy match using SequenceMatcher
            ratio = SequenceMatcher(None, task_identifier_clean, task_title_clean).ratio()
            if ratio > best_ratio and ratio > 0.5:  # Require at least 50% similarity
                best_ratio = ratio
                best_match = task

        return best_match

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user message using AI and MCP tools

        Args:
            user_id: The ID of the user
            message: The user's message
            conversation_history: Previous messages in the conversation

        Returns:
            Tuple of (AI response, list of tool call results)
        """
        # Parse the message to determine intent
        intent, params = self._parse_intent(message)

        # Special handling for update_task and delete_task to allow natural language identification
        if intent in ['update_task', 'delete_task', 'complete_task'] and 'task_id' in params:
            task_identifier = params['task_id']
            # Check if this looks like a UUID or if it's a natural language reference
            uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'

            if not re.match(uuid_pattern, task_identifier):
                # This is likely a natural language reference, try to find the actual task
                matched_task = self._find_task_by_name_or_index(user_id, task_identifier)
                if matched_task:
                    params['task_id'] = matched_task['id']
                else:
                    # Could not find the task
                    return f"Sorry, I couldn't find a task matching '{task_identifier}'. Please check the task name or use 'show my tasks' to see all tasks.", []

        # Execute the appropriate MCP tool based on intent
        tool_result = await self._execute_tool(intent, user_id, params)

        # Generate AI response based on tool result
        ai_response = self._generate_response(intent, tool_result, message)

        # Format tool call results
        tool_call_results = [{
            "tool": intent,
            "status": "success" if tool_result.get("success") else "error",
            "result": tool_result,
            "arguments": params
        }] if tool_result else []

        return ai_response, tool_call_results

    def _parse_intent(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """Parse user message to determine intent and extract parameters."""
        message_lower = message.lower().strip()

        # Define patterns for different intents - order matters, more specific first
        patterns = {
            'list_tasks': [
                r'(?:show|list|display|view|see)\s+(?:my\s+)?tasks?',
                r'(?:what\s+do\s+i\s+have|what\'?s\s+on\s+my\s+list|my\s+todos?)',
                r'(?:show|list|display|view|see)\s+(?:my\s+)?(?:completed|done)\s+tasks?',
            ],
            'add_task': [
                r'(?:add|create|new|make)\s+(?:a\s+)?task\s+to\s+(.+)',
                r'(?:add|create|new|make)\s+(.+)',
                r'(?:buy|get|complete|finish|remind me to|schedule|plan)\s+(.+)',
            ],
            'complete_task': [
                r'(?:mark|complete|done|finish)\s+(?:task\s+)?([a-zA-Z0-9\-]+|\w+(?:\s+\w+)*)(?:\s+as)?\s*(?:done|completed|finished)?',
                r'(?:complete|finish)\s+(?:task\s+)?([a-zA-Z0-9\-]+|\w+(?:\s+\w+)*)',
                r'(?:mark|complete|done|finish)\s+(?:the\s+)?(.+?)\s+(?:task|as)?\s*(?:done|completed|finished)?',
            ],
            'delete_task': [
                r'(?:delete|remove|cancel)\s+(?:task\s+)?([a-zA-Z0-9\-]+|\w+(?:\s+\w+)*)',
                r'(?:remove|delete)\s+(?:task\s+)?([a-zA-Z0-9\-]+|\w+(?:\s+\w+)*)',
                r'(?:delete|remove|cancel)\s+(?:the\s+)?(.+?)\s+task',
            ],
            'update_task': [
                r'(?:update|change|edit)\s+(?:task\s+)?([a-zA-Z0-9\-]+|\w+(?:\s+\w+)*)\s+to\s+(.+)',
                r'(?:update|change|edit)\s+(?:the\s+)?(.+?)\s+task\s+to\s+(.+)',
                r'(?:update|change|edit)\s+(?:task\s+)?(.+?)$',  # For "update task X" without "to" clause
            ]
        }

        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, message_lower)
                if match:
                    groups = match.groups()

                    if intent == 'add_task':
                        return intent, {'title': groups[0].strip().capitalize()}
                    elif intent in ['complete_task', 'delete_task']:
                        # Handle different group patterns
                        if len(groups) >= 1:
                            return intent, {'task_id': groups[0].strip()}
                    elif intent == 'update_task':
                        # Handle different group patterns for update
                        if len(groups) == 2:
                            # Pattern: ([task_id_or_name])\s+to\s+(.+) or (.+?)\s+task\s+to\s+(.+)
                            # Both cases: first group is task identifier, second is new title
                            return intent, {'task_id': groups[0].strip(), 'title': groups[1].strip().capitalize()}
                        elif len(groups) == 1:
                            # Pattern: "update task X" without "to" clause - need to ask for new title
                            return intent, {'task_id': groups[0].strip()}
                    elif intent == 'list_tasks':
                        return intent, {}

        return 'unknown', {}

    async def _execute_tool(self, intent: str, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate MCP tool based on intent."""
        try:
            if intent == 'add_task':
                return mcp_tools.add_task(
                    user_id=user_id,
                    title=params.get('title', 'New Task'),
                    description=params.get('description')
                )
            elif intent == 'list_tasks':
                return mcp_tools.list_tasks(user_id=user_id)
            elif intent == 'complete_task':
                return mcp_tools.complete_task(
                    user_id=user_id,
                    task_id=params.get('task_id')
                )
            elif intent == 'delete_task':
                return mcp_tools.delete_task(
                    user_id=user_id,
                    task_id=params.get('task_id')
                )
            elif intent == 'update_task':
                # Validate that both task_id and title are provided
                if not params.get('task_id'):
                    return {"success": False, "error": "Please specify which task you'd like to update."}
                if not params.get('title'):
                    return {"success": False, "error": "To update a task, please specify what you'd like to change it to. For example: 'update task study to study physics' or 'update task study to complete assignment'."}

                return mcp_tools.update_task(
                    user_id=user_id,
                    task_id=params.get('task_id'),
                    title=params.get('title')
                )
            else:
                # For unknown intents, return a general response
                return {"success": True, "message": f"Received: {params.get('message', 'unknown')}"}
        except Exception as e:
            logger.error(f"Error executing tool {intent}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _generate_response(self, intent: str, result: Dict[str, Any], original_message: str) -> str:
        """Generate appropriate AI response based on intent and result."""
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error occurred')
            return f"Sorry, I couldn't perform that action: {error_msg}"

        if intent == 'add_task':
            task = result.get('task', {})
            title = task.get('title', 'Untitled')
            return f"✅ I've added \"{title}\" to your tasks."

        elif intent == 'list_tasks':
            tasks = result.get('tasks', [])
            if not tasks:
                return "📋 You don't have any tasks on your list right now."

            # Show all tasks, but indicate if there are many
            if len(tasks) > 10:
                task_list = "\n".join([
                    f"• {task.get('title', 'Untitled')} ({'Completed' if task.get('completed', False) else 'Pending'})"
                    for task in tasks
                ])
                return f"📋 Here are all your tasks ({len(tasks)} total):\n{task_list}\n\n(Total: {len(tasks)} tasks)"
            else:
                task_list = "\n".join([
                    f"• {task.get('title', 'Untitled')} ({'Completed' if task.get('completed', False) else 'Pending'})"
                    for task in tasks
                ])
                return f"📋 Here are your tasks:\n{task_list}"

        elif intent in ['complete_task', 'delete_task', 'update_task']:
            if intent == 'complete_task':
                task = result.get('task', {})
                title = task.get('title', 'unknown')
                return f"✅ I've completed \"{title}\" for you."
            elif intent == 'delete_task':
                task = result.get('task', {})
                title = task.get('title', 'Task')
                return f"🗑️ I've deleted \"{title}\" from your tasks."
            elif intent == 'update_task':
                # Check if update failed due to missing title parameter
                if not params.get('title'):
                    return "To update a task, please specify what you'd like to change it to. For example: 'update task study to study physics' or 'update task study to complete assignment'."

                task = result.get('task', {})
                title = task.get('title', 'untitled')
                return f"✏️ I've updated \"{title}\" in your tasks."

        else:
            return f"Got it! How can I help you with your tasks?"