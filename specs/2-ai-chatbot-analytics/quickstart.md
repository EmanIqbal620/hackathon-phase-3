# Quickstart Guide: Advanced AI Chatbot with Analytics

## Overview

This guide provides instructions for setting up, developing, and using the Advanced AI Chatbot with Analytics feature that adds AI-driven task suggestions, smart reminders, and productivity analytics to the Todo app.

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (or Neon Serverless PostgreSQL)
- Better Auth configured
- OpenAI-compatible API key (e.g., from OpenRouter)
- Frontend with charting library support (e.g., Chart.js or D3)

## Development Setup

### 1. Environment Variables

Add these variables to your `.env` file:

```bash
# Analytics Configuration
ANALYTICS_RETENTION_DAYS=90
TASK_PATTERN_DETECTION_ENABLED=true
REMINDER_LEAD_TIME_HOURS=24

# AI Provider for Advanced Features
OPENAI_API_KEY="your-openai-api-key"
OPENAI_BASE_URL="https://api.openai.com/v1"  # or OpenRouter URL
OPENAI_MODEL="gpt-4-turbo"  # Recommended for advanced NLP
```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install additional dependencies for analytics:
   ```bash
   pip install pandas numpy scikit-learn
   ```

3. Run database migrations (if new analytics tables are needed):
   ```bash
   python create_analytics_tables.py
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

2. Install charting dependencies:
   ```bash
   npm install chart.js react-chartjs-2
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Key Features

### AI-Driven Task Suggestions
- The system learns from your task patterns and suggests recurring tasks
- Example: "You usually add 'grocery shopping' on Sundays, would you like to add it for this Sunday?"

### Smart Reminders
- Intelligent notifications based on deadlines and importance
- Customizable reminder preferences

### Analytics Dashboard
- Visualizations of task completion rates
- Productivity trends over time
- Task category breakdowns

### Advanced NLP
- Complex command interpretation
- Contextual task management
- Priority and scheduling commands

## API Endpoints

- `POST /api/{user_id}/suggest-tasks` - Get AI-generated task suggestions
- `GET /api/{user_id}/analytics` - Get productivity analytics data
- `PUT /api/{user_id}/preferences` - Update notification preferences

## Testing

### Backend Tests
```bash
cd backend
pytest tests/analytics_tests.py
```

### Example Advanced Commands
Try these commands with the chatbot:
- "What should I focus on today?"
- "Remind me about urgent tasks"
- "Show me my productivity this week"
- "Prioritize my top 3 tasks"