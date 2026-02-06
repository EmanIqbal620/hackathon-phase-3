from sqlmodel import Session, select
from sqlalchemy import case
from typing import List, Optional, Dict, Any
from ..models.conversation import Conversation, Message, MessageCreate
from ..models.tool_call_log import ToolCallLog
from datetime import datetime, timedelta
import uuid


class ConversationService:
    """
    Service class for handling conversation and message persistence operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for the user

        Args:
            user_id: The ID of the user creating the conversation
            title: Optional title for the conversation

        Returns:
            The created Conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int, user_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID for the specified user

        Args:
            conversation_id: The ID of the conversation to retrieve
            user_id: The ID of the user requesting the conversation

        Returns:
            The Conversation object if found and owned by user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(statement).first()
        return conversation

    def create_message(self, message_create: MessageCreate) -> Message:
        """
        Create a new message in a conversation

        Args:
            message_create: MessageCreate object with message data

        Returns:
            The created Message object
        """
        message = Message(
            user_id=message_create.user_id,
            conversation_id=message_create.conversation_id,
            role=message_create.role,
            content=message_create.content,
            tool_call_results=message_create.tool_call_results,
            timestamp=datetime.utcnow()
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        # Update conversation's updated_at timestamp
        conversation = self.session.get(Conversation, message.conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()

        return message

    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """
        Retrieve all messages for a specific conversation

        Args:
            conversation_id: The ID of the conversation

        Returns:
            List of Message objects in chronological order
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc())
        messages = self.session.exec(statement).all()
        return messages

    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """
        Retrieve all conversations for a specific user

        Args:
            user_id: The ID of the user

        Returns:
            List of Conversation objects in chronological order
        """
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc())
        conversations = self.session.exec(statement).all()
        return conversations

    def create_tool_call_log(
        self,
        user_id: str,
        conversation_id: int,
        message_id: Optional[int],
        tool_name: str,
        parameters: dict,
        result: Optional[dict] = None,
        status: str = "pending"
    ) -> ToolCallLog:
        """
        Create a log entry for a tool call

        Args:
            user_id: The ID of the user who triggered the tool call
            conversation_id: The ID of the conversation where the tool was called
            message_id: The ID of the message that triggered the tool call (optional)
            tool_name: The name of the tool that was called
            parameters: The parameters passed to the tool
            result: The result of the tool call (optional)
            status: The status of the tool call ("success", "error", "pending")

        Returns:
            The created ToolCallLog object
        """
        tool_call_log = ToolCallLog(
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            status=status,
            timestamp=datetime.utcnow()
        )
        self.session.add(tool_call_log)
        self.session.commit()
        self.session.refresh(tool_call_log)
        return tool_call_log

    def get_tool_call_logs(
        self,
        user_id: str,
        conversation_id: Optional[int] = None,
        tool_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = 50,
        offset: int = 0
    ) -> List[ToolCallLog]:
        """
        Retrieve tool call logs with optional filters

        Args:
            user_id: The ID of the user whose tool calls to retrieve
            conversation_id: Optional conversation ID to filter by
            tool_name: Optional tool name to filter by
            status: Optional status to filter by
            limit: Maximum number of logs to return
            offset: Number of logs to skip

        Returns:
            List of ToolCallLog objects
        """
        statement = select(ToolCallLog).where(ToolCallLog.user_id == user_id)

        if conversation_id is not None:
            statement = statement.where(ToolCallLog.conversation_id == conversation_id)
        if tool_name is not None:
            statement = statement.where(ToolCallLog.tool_name == tool_name)
        if status is not None:
            statement = statement.where(ToolCallLog.status == status)

        statement = statement.order_by(ToolCallLog.timestamp.desc())

        if limit is not None:
            statement = statement.limit(limit).offset(offset)

        logs = self.session.exec(statement).all()
        return logs

    def get_tool_call_summary(
        self,
        user_id: str,
        conversation_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get a summary of tool call activity

        Args:
            user_id: The ID of the user
            conversation_id: Optional conversation ID to filter by
            days_back: Number of days back to include in the summary

        Returns:
            Dictionary with summary statistics
        """
        from sqlalchemy import func
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        statement = select(
            func.count(ToolCallLog.id).label('total_calls'),
            func.sum(case((ToolCallLog.status == 'success', 1), else_=0)).label('successful_calls'),
            func.sum(case((ToolCallLog.status == 'error', 1), else_=0)).label('failed_calls')
        ).where(
            ToolCallLog.user_id == user_id,
            ToolCallLog.timestamp >= cutoff_date
        )

        if conversation_id is not None:
            statement = statement.where(ToolCallLog.conversation_id == conversation_id)

        result = self.session.exec(statement).first()

        # Get most frequently used tools
        tool_freq_statement = select(
            ToolCallLog.tool_name,
            func.count(ToolCallLog.id).label('usage_count')
        ).where(
            ToolCallLog.user_id == user_id,
            ToolCallLog.timestamp >= cutoff_date
        ).group_by(ToolCallLog.tool_name).order_by(func.count(ToolCallLog.id).desc()).limit(5)

        tool_frequencies = self.session.exec(tool_freq_statement).all()

        return {
            'total_calls': result.total_calls or 0,
            'successful_calls': result.successful_calls or 0,
            'failed_calls': result.failed_calls or 0,
            'success_rate': (result.successful_calls or 0) / max(result.total_calls or 1, 1) * 100,
            'most_used_tools': [{'tool_name': tf[0], 'count': tf[1]} for tf in tool_frequencies]
        }

    def update_tool_call_log_status(self, log_id: int, status: str, result: Optional[dict] = None) -> ToolCallLog:
        """
        Update the status and result of an existing tool call log

        Args:
            log_id: The ID of the tool call log to update
            status: The new status ("success", "error")
            result: The result of the tool call (optional)

        Returns:
            The updated ToolCallLog object
        """
        tool_call_log = self.session.get(ToolCallLog, log_id)
        if tool_call_log:
            tool_call_log.status = status
            if result is not None:
                tool_call_log.result = result
            tool_call_log.timestamp = datetime.utcnow()
            self.session.add(tool_call_log)
            self.session.commit()
            self.session.refresh(tool_call_log)
        return tool_call_log

    def get_recent_messages(self, user_id: str, limit: int = 10) -> List[Message]:
        """
        Retrieve recent messages for a user across all conversations

        Args:
            user_id: The ID of the user
            limit: Maximum number of messages to return

        Returns:
            List of Message objects in reverse chronological order
        """
        statement = select(Message).where(
            Message.user_id == user_id
        ).order_by(Message.timestamp.desc()).limit(limit)
        messages = self.session.exec(statement).all()
        return messages

    def get_contextual_conversation_history(
        self,
        conversation_id: int,
        current_message_id: Optional[int] = None,
        context_window: int = 5
    ) -> List[Message]:
        """
        Retrieve contextual conversation history with a sliding window around the current message

        Args:
            conversation_id: The ID of the conversation
            current_message_id: The ID of the current message (to center the context window)
            context_window: Number of messages before and after the current message to include

        Returns:
            List of Message objects in chronological order
        """
        if current_message_id:
            # Get the position of the current message in the conversation
            current_message = self.session.get(Message, current_message_id)
            if not current_message or current_message.conversation_id != conversation_id:
                # If current message not found or not in this conversation, fall back to recent messages
                return self.get_conversation_messages(conversation_id)[-context_window:]

            # Get messages before the current message (up to context_window)
            stmt_before = select(Message).where(
                Message.conversation_id == conversation_id,
                Message.timestamp < current_message.timestamp
            ).order_by(Message.timestamp.desc()).limit(context_window)
            messages_before = self.session.exec(stmt_before).all()

            # Get messages after the current message (up to context_window)
            stmt_after = select(Message).where(
                Message.conversation_id == conversation_id,
                Message.timestamp > current_message.timestamp
            ).order_by(Message.timestamp.asc()).limit(context_window)
            messages_after = self.session.exec(stmt_after).all()

            # Combine: before + current + after
            context_messages = list(reversed(messages_before)) + [current_message] + messages_after
            return sorted(context_messages, key=lambda x: x.timestamp)
        else:
            # Get the most recent messages
            all_messages = self.get_conversation_messages(conversation_id)
            return all_messages[-context_window:] if len(all_messages) >= context_window else all_messages

    def get_task_reference_context(
        self,
        user_id: str,
        conversation_id: int,
        task_title_hint: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context about tasks mentioned in the conversation or related to the user

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the current conversation
            task_title_hint: Optional hint about the task title to look for

        Returns:
            List of dictionaries containing task information for context
        """
        from ..models.task import Task

        # Get the most recent messages in the conversation to find task references
        recent_messages = self.get_conversation_messages(conversation_id)[-10:]  # Last 10 messages

        # Also fetch user's tasks from the database
        task_statement = select(Task).where(Task.user_id == user_id)
        user_tasks = self.session.exec(task_statement).all()

        # Create a context of relevant tasks
        task_context = []
        for task in user_tasks:
            task_info = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "recently_mentioned": any(
                    task.title.lower() in msg.content.lower() for msg in recent_messages
                )
            }
            task_context.append(task_info)

        # Sort by recently mentioned first, then by creation date
        task_context.sort(key=lambda x: (x["recently_mentioned"], x["created_at"]), reverse=True)

        return task_context