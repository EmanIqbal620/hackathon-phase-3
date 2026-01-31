# Data Model: AI-Powered Todo Chatbot

## Entities

### Conversation
Represents a single chat session with associated metadata and message history

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String (Foreign Key to User, required for isolation)
- `created_at`: DateTime (Timestamp when conversation started, required)
- `updated_at`: DateTime (Timestamp of last activity, required)
- `title`: String (Optional, auto-generated from first message or user-edited)

**Validation Rules**:
- `user_id` must exist in Users table
- `created_at` and `updated_at` are immutable after creation
- `title` max length 200 characters

**Relationships**:
- One-to-many with Message (conversation has many messages)

### Message
Individual chat message with sender (user/assistant), timestamp, and content

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String (Foreign Key to User, required for isolation)
- `conversation_id`: Integer (Foreign Key to Conversation, required)
- `role`: String (Enum: "user"|"assistant", required)
- `content`: String (Message content, required)
- `timestamp`: DateTime (When message was sent/received, required)
- `tool_call_results`: JSON (Optional, stores results from tool calls)

**Validation Rules**:
- `user_id` must match the conversation's user_id
- `role` must be one of allowed values
- `content` max length 10000 characters
- `timestamp` is immutable after creation

**Relationships**:
- Many-to-one with Conversation (message belongs to one conversation)

### ToolCallLog
Record of AI agent's tool invocations with status and results for transparency

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String (Foreign Key to User, required for isolation)
- `conversation_id`: Integer (Foreign Key to Conversation, required)
- `message_id`: Integer (Foreign Key to Message that triggered the tool call)
- `tool_name`: String (Name of the tool called, required)
- `parameters`: JSON (Parameters passed to the tool, required)
- `result`: JSON (Result from the tool call, optional)
- `status`: String (Enum: "success"|"error"|"pending", required)
- `timestamp`: DateTime (When tool was called, required)

**Validation Rules**:
- `tool_name` must be one of allowed MCP tools
- `status` must be one of allowed values
- `timestamp` is immutable after creation

**Relationships**:
- Many-to-one with Conversation (log entry belongs to one conversation)
- Many-to-one with Message (log entry associated with triggering message)

## State Transitions

### Conversation States
- Active: New messages can be added
- Archived: Conversation completed, read-only access

### Message States
- Pending: Message received, awaiting AI processing
- Processing: AI agent currently handling message
- Completed: AI response generated and stored

### ToolCallLog States
- Pending: Tool call initiated
- Success: Tool executed successfully
- Error: Tool execution failed