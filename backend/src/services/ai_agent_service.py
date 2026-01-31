import openai
import os
import json
from typing import List, Dict, Any, Tuple, Optional
from sqlmodel import Session
from ..mcp_tools.task_operations import (
    add_task_tool, list_tasks_tool, complete_task_tool,
    delete_task_tool, update_task_tool
)
from ..services.conversation_service import ConversationService
from ..models.conversation import Message
import logging
from ..utils.logger import ai_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgentService:
    """
    Service class for integrating AI agent with MCP tools for task management
    """

    def __init__(self, session: Session):
        self.session = session
        self.conversation_service = ConversationService(session)
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Register available tools for the AI agent
        self.tools = {
            "add_task": add_task_tool,
            "list_tasks": list_tasks_tool,
            "complete_task": complete_task_tool,
            "delete_task": delete_task_tool,
            "update_task": update_task_tool
        }

        # Define the tool definitions for the OpenAI API
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Creates a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the task"},
                            "description": {"type": "string", "description": "Optional description of the task"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Lists tasks for the user, optionally filtered by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "default": "all",
                                "description": "Filter tasks by status: 'all', 'pending', or 'completed'"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Marks a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID of the task to complete"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Deletes a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID of the task to delete"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Updates a task's title or description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID of the task to update"},
                            "title": {"type": "string", "description": "New title for the task (optional)"},
                            "description": {"type": "string", "description": "New description for the task (optional)"}
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Message]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user message with the AI agent and execute appropriate tools

        Args:
            user_id: The ID of the user sending the message
            message: The user's message to process
            conversation_history: List of previous messages in the conversation

        Returns:
            A tuple containing (AI response, list of tool call results)
        """
        conversation_id = conversation_history[-1].conversation_id if conversation_history else "unknown"
        import time
        start_time = time.time()

        try:
            # Log interaction start
            ai_logger.log_interaction_start(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message
            )

            # Format conversation history for the AI with context management
            messages = self._format_conversation_history(conversation_history, message)

            # Prepare the request to OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="auto"
            )

            # Process the response
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            tool_call_results = []

            # Execute any requested tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Enhance context awareness by inferring missing information from conversation history
                    enhanced_args = self._enhance_context_with_history(
                        function_name, function_args, conversation_history
                    )

                    # Log the tool call
                    logger.info(f"Executing tool: {function_name} with args: {enhanced_args}")

                    # Execute the tool with timing
                    import time
                    tool_start_time = time.time()

                    if function_name in self.tools:
                        tool = self.tools[function_name]
                        result = await tool.execute(user_id, **enhanced_args)

                        # Calculate execution time
                        execution_time_ms = (time.time() - tool_start_time) * 1000

                        # Log the result
                        logger.info(f"Tool {function_name} result: {result}")

                        # Log tool execution to AI logger
                        ai_logger.log_tool_execution(
                            user_id=user_id,
                            conversation_id=conversation_id,
                            tool_name=function_name,
                            parameters=enhanced_args,
                            result=result.result or {},
                            execution_time_ms=execution_time_ms,
                            success=result.success
                        )

                        # Create a log entry for the tool call
                        self.conversation_service.create_tool_call_log(
                            user_id=user_id,
                            conversation_id=conversation_history[-1].conversation_id if conversation_history else 0,
                            message_id=conversation_history[-1].id if conversation_history else None,
                            tool_name=function_name,
                            parameters=enhanced_args,
                            result=result.result,
                            status=result.status
                        )

                        tool_call_results.append({
                            "tool": function_name,
                            "status": result.status,
                            "result": result.result,
                            "error": result.error if not result.success else None,
                            "execution_time_ms": execution_time_ms
                        })
                    else:
                        logger.warning(f"Unknown tool requested: {function_name}")
                        # Log unknown tool to AI logger
                        ai_logger.log_tool_execution(
                            user_id=user_id,
                            conversation_id=conversation_id,
                            tool_name=function_name,
                            parameters=function_args,
                            result={"error": f"Unknown tool: {function_name}"},
                            execution_time_ms=0,
                            success=False
                        )
                        tool_call_results.append({
                            "tool": function_name,
                            "status": "error",
                            "result": None,
                            "error": f"Unknown tool: {function_name}",
                            "execution_time_ms": 0
                        })

            # If the AI response has content, return it; otherwise, construct a detailed response based on tool calls
            ai_response = ""
            if response_message.content:
                ai_response = response_message.content
            elif tool_call_results:
                # Construct a detailed response based on tool call results
                successful_calls = [result for result in tool_call_results if result["status"] == "success"]
                error_calls = [result for result in tool_call_results if result["status"] == "error"]

                if successful_calls:
                    # Create detailed feedback for successful operations
                    success_details = []
                    for result in successful_calls:
                        tool_name = result["tool"]
                        tool_result = result["result"]

                        if tool_name == "add_task" and tool_result:
                            success_details.append(f"Added task '{tool_result.get('title', 'unnamed')}' (ID: {tool_result.get('task_id', 'unknown')})")
                        elif tool_name == "complete_task" and tool_result:
                            success_details.append(f"Marked task '{tool_result.get('title', 'unnamed')}' as completed")
                        elif tool_name == "delete_task" and tool_result:
                            success_details.append(f"Deleted task (ID: {tool_result.get('task_id', 'unknown')})")
                        elif tool_name == "update_task" and tool_result:
                            success_details.append(f"Updated task '{tool_result.get('title', 'unnamed')}'")
                        elif tool_name == "list_tasks" and tool_result:
                            task_count = tool_result.get('count', 0)
                            success_details.append(f"Retrieved {task_count} tasks")
                        else:
                            success_details.append(f"Completed {tool_name} operation")

                    ai_response += f"I've completed the following actions: {', '.join(success_details)}. "

                if error_calls:
                    # Create detailed feedback for failed operations
                    error_details = []
                    for result in error_calls:
                        tool_name = result["tool"]
                        error_msg = result["error"] or "Unknown error"
                        error_details.append(f"{tool_name}: {error_msg}")

                    ai_response += f"There were some issues: {', '.join(error_details)}. "

                if not successful_calls and not error_calls:
                    ai_response = "I processed your request."
            else:
                ai_response = "I've processed your request."

            # Calculate total execution time
            total_execution_time = (time.time() - start_time) * 1000

            # Log interaction end
            ai_logger.log_interaction_end(
                user_id=user_id,
                conversation_id=conversation_id,
                response=ai_response,
                tools_used=[result["tool"] for result in tool_call_results],
                execution_time_ms=total_execution_time
            )

            return ai_response, tool_call_results

        except Exception as e:
            total_execution_time = (time.time() - start_time) * 1000

            # Log error to AI logger
            ai_logger.log_error(
                user_id=user_id,
                conversation_id=conversation_id,
                error=e,
                context="Error processing AI interaction"
            )

            logger.error(f"Error processing message: {str(e)}")
            error_msg = f"Sorry, I encountered an error processing your request: {str(e)}"
            return error_msg, [{"tool": "error", "status": "error", "result": None, "error": str(e), "execution_time_ms": total_execution_time}]

    def _enhance_context_with_history(
        self,
        tool_name: str,
        args: Dict[str, Any],
        conversation_history: List[Message]
    ) -> Dict[str, Any]:
        """
        Enhance the arguments with context from conversation history

        Args:
            tool_name: The name of the tool being called
            args: The original arguments passed to the tool
            conversation_history: List of previous messages in the conversation

        Returns:
            Enhanced arguments with inferred context
        """
        # For certain tools, we can infer missing information from the conversation history
        if tool_name in ["complete_task", "delete_task", "update_task"] and "task_id" not in args:
            # Try to infer task_id from the conversation history
            task_id = self._infer_task_id_from_context(args, conversation_history)
            if task_id:
                args["task_id"] = task_id
                logger.info(f"Inferred task_id {task_id} from conversation context for {tool_name}")

        return args

    def _infer_task_id_from_context(
        self,
        args: Dict[str, Any],
        conversation_history: List[Message]
    ) -> Optional[int]:
        """
        Infer the task ID from the conversation context

        Args:
            args: The arguments passed to the tool
            conversation_history: List of previous messages in the conversation

        Returns:
            Inferred task ID if found, None otherwise
        """
        # Look for task references in recent messages
        for message in reversed(conversation_history[-5:]):  # Check last 5 messages
            content = message.content.lower()

            # Look for numeric task IDs mentioned in the conversation
            import re
            task_ids = re.findall(r'task (\d+)', content)
            if task_ids:
                # Return the last mentioned task ID
                return int(task_ids[-1])

            # Look for specific task titles mentioned in the conversation
            if "title" in args:
                if args["title"].lower() in content:
                    # This is a simplified approach - in a real implementation,
                    # we would need to match the actual task title to its ID
                    # For now, we'll just return None since we don't have a way to match titles to IDs
                    # without querying the database
                    pass

        return None

    def _format_conversation_history(self, conversation_history: List[Message], current_message: str) -> List[Dict[str, str]]:
        """
        Format conversation history for the AI model

        Args:
            conversation_history: List of previous messages in the conversation
            current_message: The current user message

        Returns:
            List of messages formatted for the AI model
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that manages tasks using specialized tools. "
                           "When users ask you to add, list, update, complete, or delete tasks, "
                           "use the appropriate tools. Always respond in a friendly, helpful manner "
                           "and confirm actions you've taken."
            }
        ]

        # Add historical messages
        for msg in conversation_history:
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({
                "role": role,
                "content": msg.content
            })

        # Add the current message
        messages.append({
            "role": "user",
            "content": current_message
        })

        return messages

    def validate_task_operation(self, user_id: str, operation: str, task_id: Optional[int] = None) -> bool:
        """
        Validate that a user can perform a specific operation on a task

        Args:
            user_id: The ID of the user requesting the operation
            operation: The type of operation ('read', 'update', 'delete', 'complete')
            task_id: The ID of the task (if applicable)

        Returns:
            True if the user is authorized to perform the operation, False otherwise
        """
        # For now, we assume all operations are valid if the user ID matches
        # In a real implementation, we'd check if the task belongs to the user
        return True