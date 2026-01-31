# Quickstart Guide: Advanced Enhancements & Cross-Cutting Features

## Overview
This guide provides setup and usage instructions for the enhanced Todo App with advanced UI/UX features, performance optimizations, and AI capabilities.

## Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL database (or Neon for cloud)
- OpenAI API key
- MCP tools framework

## Setup Instructions

### 1. Environment Configuration
```bash
# Copy the environment template
cp .env.example .env

# Update with your configuration:
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/todo_app
NEON_DATABASE_URL=your_neon_database_url
```

### 2. Backend Installation
```bash
cd backend
pip install -r requirements.txt

# Run database migrations
python -m src.database.migrate

# Start the backend server
uvicorn src.main:app --reload
```

### 3. Frontend Installation
```bash
cd frontend
npm install

# Start the frontend development server
npm run dev
```

## Usage Examples

### 1. Using the Enhanced Analytics Dashboard
1. Navigate to `/dashboard/analytics`
2. Select a time range (day, week, month, quarter)
3. View productivity metrics, completion rates, and task trends
4. Use the interactive charts to drill down into specific time periods

### 2. Interacting with AI Suggestions
1. Go to the suggestions panel on the dashboard
2. Review AI-generated suggestions based on your task patterns
3. Click "Accept" to create the task or "Dismiss" to reject
4. Provide feedback to improve future suggestions

### 3. Managing Smart Reminders
1. Use natural language in the chat interface: "Remind me about the meeting tomorrow"
2. Or use the reminder UI in the dashboard
3. View upcoming reminders in the reminders section
4. Customize delivery methods (notification, email) in settings

### 4. Leveraging Advanced NLP
The AI agent understands complex commands like:
- "Show me my productivity this week"
- "What tasks should I prioritize today?"
- "Remind me about high-priority tasks due soon"
- "Suggest tasks based on my patterns"

## API Examples

### Getting Analytics Data
```javascript
// Fetch user analytics
const response = await fetch('/api/analytics/user123/dashboard?time_range=week', {
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  }
});

const analytics = await response.json();
console.log(analytics.metrics);
```

### Creating Smart Reminders
```javascript
// Create a reminder via API
const response = await fetch('/api/reminders/user123/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task_id: 'task123',
    scheduled_time: '2026-01-27T09:00:00Z',
    delivery_method: 'notification',
    reminder_type: 'deadline'
  })
});
```

## Configuration Options

### Theme Settings
The application supports light/dark mode with smooth transitions:
- Toggle in the top-right corner of any page
- Automatically respects system preference
- Stores user preference in localStorage

### Animation Settings
Animations can be adjusted for performance or accessibility:
- Framer Motion powers all complex animations
- Respect user's reduced motion preferences
- Configurable animation intensity in settings

### Performance Optimization
The app includes several performance enhancements:
- Component lazy loading
- Virtual scrolling for large task lists
- API response caching
- Bundle size optimization

## Troubleshooting

### Common Issues
1. **Slow Performance**: Enable reduced motion mode in settings
2. **API Errors**: Verify your OpenAI API key and network connectivity
3. **Theme Not Saving**: Clear browser cache and reload
4. **Animations Lagging**: Disable hardware acceleration or reduce animation intensity

### Verification Steps
1. Check that all environment variables are set correctly
2. Verify database connectivity with `python -c "from src.database import sync_engine; print(sync_engine.execute('SELECT 1').fetchone())"`
3. Test API endpoints with the examples above
4. Confirm the UI shows the new theme and animation elements

## Advanced Features

### AI Confidence Scoring
All AI-generated suggestions include confidence scores (0-100%) to help users understand the AI's certainty level.

### Productivity Analytics
The system calculates productivity scores based on completion rates, average completion time, and priority management.

### Pattern Recognition
The AI identifies recurring task patterns in your behavior and suggests appropriate tasks based on those patterns.

### Cross-Platform Notifications
Reminders can be delivered via multiple channels (browser notifications, email) based on user preferences.