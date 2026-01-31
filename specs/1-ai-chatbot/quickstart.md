# Quickstart Guide: AI-Powered Todo Chatbot

**Created**: 2026-01-23
**Feature**: 1-ai-chatbot

---

## Overview

This guide provides instructions for setting up, developing, and deploying the AI-Powered Todo Chatbot feature. The chatbot allows users to manage their todo tasks through natural language conversations.

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (or Neon Serverless PostgreSQL)
- Better Auth configured
- OpenAI-compatible API key (e.g., from OpenRouter)

## Development Setup

### 1. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/todo_app"

# Authentication
BETTER_AUTH_SECRET="your-secret-key"

# AI Provider (OpenRouter example)
OPENAI_API_KEY="your-openrouter-api-key"
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_MODEL="openrouter/auto"  # or specific model like "gpt-3.5-turbo"

# Application
APP_URL="http://localhost:3000"
```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python create_tables.py
   ```

4. Start the development server:
   ```bash
   python main.py
   ```

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Key Components

### MCP Server
The Model Context Protocol server exposes task operations as tools that the AI agent can use:

- `add_task`: Create new tasks
- `list_tasks`: Retrieve user's tasks
- `update_task`: Modify existing tasks
- `complete_task`: Mark tasks as completed
- `delete_task`: Remove tasks

### Chat Endpoint
The main API endpoint at `POST /api/{user_id}/chat` handles the conversation flow:
1. Authenticates the user via JWT
2. Reconstructs conversation history from the database
3. Processes the user's message with the AI agent
4. Executes MCP tools as needed
5. Returns the AI's response

## Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### API Tests
Test the chat endpoint with curl:
```bash
curl -X POST http://localhost:8000/api/USER_ID/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": "EXISTING_CONVERSATION_ID_OR_OMIT_FOR_NEW"
  }'
```

## Configuration

### MCP Tools Configuration
The MCP tools are configured in `backend/src/mcp_tools/` and registered with the AI agent. Each tool validates user permissions and ensures data isolation.

### Agent Configuration
The AI agent is configured in `backend/src/agents/chat_agent.py` with:
- System prompt that enforces tool usage
- Available MCP tools
- Response formatting rules

## Deployment

### Environment Setup
For production deployment, ensure the following environment variables are set:
- `DATABASE_URL`: Production database connection string
- `BETTER_AUTH_SECRET`: Secure authentication secret
- `OPENAI_API_KEY`: Production AI provider API key
- `APP_URL`: Production application URL

### Database Migration
Run migrations in production:
```bash
python migrate.py
```

### Production Build
Build and serve the application:
```bash
# Backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
npm run start
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify JWT token format and expiration
2. **Database Connection**: Check DATABASE_URL and network connectivity
3. **AI Provider Errors**: Validate API key and rate limits
4. **MCP Tool Failures**: Ensure tools are properly registered and validated

### Logging
Check application logs for detailed error information:
- Backend: `logs/app.log`
- Frontend: Browser console

## Next Steps

1. Implement the MCP tools with proper validation
2. Fine-tune the AI agent's system prompt
3. Add comprehensive error handling
4. Implement monitoring and alerting