# Quickstart Guide: AI-Powered Todo Chatbot

## Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL database (Neon recommended)
- Better Auth configured
- OpenAI-compatible API key (OpenRouter, etc.)

## Environment Variables
```bash
# Database
DATABASE_URL=postgresql://...

# Authentication
JWT_SECRET=your-jwt-secret

# AI Provider
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini  # or compatible model

# MCP Server (optional, for development)
MCP_SERVER_PORT=8080
```

## Setup Steps

### 1. Database Setup
```bash
# Install dependencies
pip install sqlmodel alembic psycopg2-binary

# Create tables
python -c "from backend.create_tables import create_tables; create_tables()"
```

### 2. MCP Server Setup
```bash
# Install MCP SDK
pip install 'mcp>=1.0.0'

# Start MCP server
python backend/src/mcp_server/todo_mcp_server.py
```

### 3. Backend Setup
```bash
# Install dependencies
pip install fastapi uvicorn openai python-multipart

# Start backend
uvicorn backend.main:app --reload
```

### 4. Frontend Setup
```bash
# Install dependencies
npm install @openai/chat-components

# Start frontend
npm run dev
```

## API Usage

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'
```

## Development Commands
```bash
# Run tests
pytest tests/

# Format code
black .
isort .

# Lint code
flake8 .
```

## Troubleshooting
- Check that MCP server is running and accessible
- Verify database connection
- Ensure JWT token is valid and has proper user_id
- Check AI provider API key validity