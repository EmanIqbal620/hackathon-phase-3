# AI Agent Integration Guide

This document explains how the AI agent integration works in the Todo App.

## Overview

The AI agent allows users to interact with their tasks using natural language. Users can:
- Add tasks: "Add a task to buy groceries"
- List tasks: "Show me my tasks"
- Update tasks: "Mark task 1 as completed"
- Delete tasks: "Delete task 2"

## Backend Implementation

### Endpoints

- `POST /api/ai-agent/message` - Main endpoint for AI agent communication

### How it Works

1. User sends a message to the AI agent endpoint
2. Intent detection analyzes the message to determine the action
3. Based on the intent, direct database operations are performed
4. AI generates a response based on the operation results
5. Response is sent back to the frontend

### Intent Detection

The AI agent detects the following intents:
- `add_task`: Adding new tasks
- `list_tasks`: Retrieving user's tasks
- `update_task`: Updating existing tasks
- `delete_task`: Deleting tasks
- `general`: General conversation

## Frontend Implementation

### Components

- `ChatWindow.tsx`: Main chat interface
- `ChatMessage.tsx`: Individual message display
- `MessageInput.tsx`: Message input field

### How it Works

1. User types a message in the input field
2. Message is sent to the AI agent endpoint
3. Response is displayed in the chat window
4. Task operation results are shown in the message

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Base URL for API calls (frontend)
- `BACKEND_API_URL`: Internal backend URL (used by AI agent to make direct calls)

## Example Requests

### Add Task
```json
{
  "user_id": "user123",
  "conversation_id": null,
  "message": "Add a task to buy groceries",
  "timestamp": "2023-12-07T10:30:00Z"
}
```

### List Tasks
```json
{
  "user_id": "user123",
  "conversation_id": null,
  "message": "Show me my tasks",
  "timestamp": "2023-12-07T10:31:00Z"
}
```

## Response Format

```json
{
  "response": "I've added the task 'Buy Groceries' to your list...",
  "conversation_id": "conv_20231207_1030_user123",
  "tool_usage": {
    "intent": "add_task",
    "parameters": {"title": "Buy Groceries"},
    "success": true
  },
  "task_operation": {
    "operation": "create",
    "result": {"id": "task456", "title": "Buy Groceries", "user_id": "user123"},
    "error": null
  }
}
```