# AI-Powered Todo Chatbot Documentation

Welcome to the AI-Powered Todo Chatbot, a conversational interface that allows users to manage their todo tasks through natural language commands.

## Features

- **Natural Language Processing**: Manage tasks using everyday language
- **Conversational Interface**: Chat with an AI assistant to handle your tasks
- **Full Task Management**: Create, read, update, complete, and delete tasks
- **Secure Authentication**: JWT-based authentication with Better Auth
- **Persistent Conversations**: Conversation history maintained across sessions

## Available Documentation

- [API Reference](./api-reference.md) - Detailed API endpoints and usage
- [Quickstart Guide](../specs/1-ai-chatbot/quickstart.md) - How to set up and use the AI chatbot system
- [AI Chatbot Specification](../specs/1-ai-chatbot/spec.md) - Feature requirements and user stories
- [AI Chatbot Plan](../specs/1-ai-chatbot/plan.md) - Implementation plan and architecture decisions
- [AI Chatbot Data Model](../specs/1-ai-chatbot/data-model.md) - Data structures and relationships

## Supported Commands

The chatbot understands various natural language commands:

### Creating Tasks
- "Add a task to buy groceries"
- "Create a task to call mom"
- "Add task: finish project report"

### Viewing Tasks
- "Show me my tasks"
- "What's pending?"
- "List all my tasks"
- "Show completed tasks"

### Updating Tasks
- "Change task 1 to 'call mom tomorrow'"
- "Update the grocery task to include milk"
- "Mark task 3 as complete"

### Managing Tasks
- "Delete the meeting task"
- "Complete the homework task"
- "Remove task with ID abc123"

## Architecture

The system follows a stateless, tool-centric architecture:

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend  │───▶│    Backend   │───▶│    MCP       │
│   (ChatKit) │    │   (FastAPI)  │    │   (SDK)      │
└─────────────┘    └──────────────┘    └──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │  Database    │
                │ (PostgreSQL) │
                └──────────────┘
```

### Components

- **Frontend**: Next.js application with OpenAI ChatKit interface
- **Backend**: FastAPI server handling authentication and requests
- **AI Agent**: OpenAI-compatible agent that processes natural language
- **MCP Tools**: Model Context Protocol tools for database operations
- **Database**: PostgreSQL with user-isolated task and conversation data

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/todoapp"

# Authentication
JWT_SECRET="your-jwt-secret"
BETTER_AUTH_SECRET="your-better-auth-secret"

# AI Provider
OPENAI_API_KEY="your-openai-api-key"
OPENAI_BASE_URL="https://api.openai.com/v1"  # or OpenRouter URL
OPENAI_MODEL="gpt-3.5-turbo"  # or preferred model
```

## API Endpoints

- `POST /api/{user_id}/chat` - Main chat endpoint
- `GET /api/conversations/{user_id}` - List user conversations
- `GET /api/conversations/{user_id}/{conversation_id}` - Get conversation history

## Security

- All requests require JWT authentication
- User data is isolated by user_id
- MCP tools ensure the AI agent cannot directly access the database
- Input validation on all endpoints
- Rate limiting (to be implemented)

## Development

1. Clone the repository
2. Install dependencies
3. Set up environment variables
4. Run database migrations
5. Start the backend and frontend

```bash
# Backend
cd backend
pip install -r requirements.txt
python create_tables.py
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Contributing

Please follow the existing code patterns and ensure all new functionality is tested.