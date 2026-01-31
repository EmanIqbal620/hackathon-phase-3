# Quickstart Guide: Advanced AI and Full-Stack Enhancements

## Setup

1. Ensure you're on the `3-advanced-ai-enhancements` branch
2. Install dependencies if not already done:
   ```bash
   cd backend
   pip install -r requirements.txt

   cd ../frontend
   npm install
   ```

## Key Features Overview

### AI-Powered Task Suggestions
The system analyzes your task patterns and suggests relevant tasks:
- Pattern-based suggestions (e.g., "You usually add groceries on Sundays")
- Priority-based suggestions for important tasks
- Deadline-based suggestions for time-sensitive items

### Smart Reminders
Intelligent reminder system that:
- Sends notifications for upcoming deadlines
- Learns from your task completion patterns
- Offers customizable delivery methods

### Real-Time Analytics Dashboard
Interactive dashboard showing:
- Task completion rates over time
- Productivity trends and metrics
- Category breakdown of your tasks
- Comparative analytics (completed vs pending)

## API Usage Examples

### Getting Analytics Dashboard Data
```javascript
// Retrieve user analytics for the current week
fetch('/api/analytics/{user_id}/dashboard?time_range=weekly', {
  headers: {
    'Authorization': 'Bearer {your-token}',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data.metrics));
```

### Managing AI Suggestions
```javascript
// Get AI-generated suggestions
fetch('/api/analytics/{user_id}/suggestions?limit=5', {
  headers: {
    'Authorization': 'Bearer {your-token}'
  }
})
.then(response => response.json())
.then(suggestions => {
  // Display suggestions to user
  suggestions.forEach(suggestion => {
    console.log(`${suggestion.title} (${suggestion.confidence_score})`);
  });
});

// Accept a suggestion
fetch('/api/analytics/{user_id}/suggestions/{suggestion_id}/accept', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer {your-token}',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    create_task: true,
    custom_due_date: '2026-01-27T18:00:00Z'
  })
});
```

### Working with Reminders
```javascript
// Get upcoming reminders
fetch('/api/analytics/{user_id}/reminders?status=pending&time_range=week', {
  headers: {
    'Authorization': 'Bearer {your-token}'
  }
});

// Create a new reminder
fetch('/api/analytics/{user_id}/reminders', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer {your-token}',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task_id: 'task-uuid',
    scheduled_time: '2026-01-26T09:00:00Z',
    delivery_method: 'notification',
    reminder_type: 'custom',
    custom_message: 'Remember to submit the report'
  })
});
```

## Testing the Features

### Test AI Suggestions
1. Add several tasks with similar patterns (e.g., "Buy groceries" on Sundays)
2. Wait for the system to learn the pattern (or manually trigger pattern analysis)
3. Check the suggestions endpoint for pattern-based suggestions

### Test Analytics Dashboard
1. Create various tasks with different priorities and due dates
2. Complete some tasks and leave others pending
3. Visit the analytics dashboard to see the metrics and visualizations

### Test Smart Reminders
1. Create tasks with near-future due dates
2. Set up reminders for important tasks
3. Monitor the reminder notifications

## Integration Points

### With Existing Chat Interface
- The enhanced AI features integrate with the existing chat interface
- Natural language commands can trigger analytics queries
- Suggestion acceptance can be done through chat commands

### With Existing Task Management
- All new features work with the existing task model
- Analytics are computed based on existing task data
- Reminders are linked to existing tasks

## Quality Assurance

### Performance Benchmarks
- Dashboard loads in under 2 seconds with up to 5,000 tasks
- AI suggestions generated in under 500ms
- API endpoints respond within 300ms for simple queries

### Error Handling
- Graceful degradation when AI services are unavailable
- Fallback analytics when real-time data isn't available
- User-friendly error messages for all failure scenarios

## Troubleshooting

### Common Issues
- If analytics don't appear immediately, check that tasks have been created with proper timestamps
- If suggestions aren't appearing, ensure you have sufficient task history for pattern analysis
- If reminders aren't working, verify that the reminder service is running

### API Limits
- Suggestions endpoint is limited to 20 results per request
- Analytics data is cached for 30 seconds to improve performance
- Rate limiting applies to all analytics endpoints (100 requests per minute per user)