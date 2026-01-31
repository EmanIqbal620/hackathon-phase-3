# Data Model: Advanced Enhancements & Cross-Cutting Features

## Overview
This document describes the data entities and relationships for the advanced UI/UX enhancements, performance optimizations, and AI improvements to the Todo App. The model extends existing entities with additional fields for analytics, suggestions, and enhanced AI capabilities.

## Entity Extensions

### Task (Extended)
**Description**: Enhanced task model with additional fields for AI and analytics
**Attributes**:
- id: string (Primary Key)
- title: string (required, max 255)
- description: string (optional)
- priority: string (enum: 'low', 'medium', 'high', default: 'medium')
- due_date: datetime (optional)
- is_completed: boolean (default: false)
- created_at: datetime (required, auto-generated)
- updated_at: datetime (required, auto-generated)
- completed_at: datetime (optional)
- deleted_at: datetime (optional, for soft deletes)
- ai_suggestion_source: string (optional, indicates if created from AI suggestion)
- estimated_duration_minutes: integer (optional, estimated time to complete)
- actual_duration_minutes: integer (optional, actual time taken to complete)
- category: string (optional, max 100, task category)

**Relationships**:
- One User to Many Tasks (user_id foreign key)
- One Task to Many Reminders (via task_id)

### AnalyticsData
**Description**: Stores aggregated analytics metrics for users
**Attributes**:
- id: uuid (Primary Key)
- user_id: string (Foreign Key to User)
- metric_type: string (enum: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly')
- date_range_start: datetime (required)
- date_range_end: datetime (required)
- tasks_created: integer (default: 0)
- tasks_completed: integer (default: 0)
- tasks_pending: integer (default: 0)
- tasks_missed: integer (default: 0)
- average_completion_time_days: float (optional)
- completion_rate_percent: float (optional)
- productivity_score: float (0-100 scale, optional)
- created_at: datetime (auto-generated)
- updated_at: datetime (auto-generated)

**Relationships**:
- One User to Many AnalyticsData records

### Suggestion
**Description**: Represents AI-generated task suggestions for users
**Attributes**:
- id: uuid (Primary Key)
- user_id: string (Foreign Key to User)
- suggested_task_title: string (required, max 255)
- suggested_task_description: string (optional)
- suggestion_type: string (enum: 'pattern_based', 'priority_based', 'deadline_based', 'contextual')
- confidence_score: float (0-1, required)
- reasoning: string (optional, explanation for the suggestion)
- accepted: boolean (optional, null if not yet responded)
- dismissed_at: datetime (optional, when user dismissed the suggestion)
- converted_to_task_id: string (optional, Foreign Key to Task if accepted)
- created_at: datetime (auto-generated)
- updated_at: datetime (auto-generated)

**Relationships**:
- One User to Many Suggestions
- One Task (optional) to One Suggestion (converted_to_task_id)

### Reminder
**Description**: Represents scheduled reminders for tasks
**Attributes**:
- id: uuid (Primary Key)
- user_id: string (Foreign Key to User)
- task_id: string (Foreign Key to Task)
- scheduled_time: datetime (required, when to send the reminder)
- delivery_method: string (enum: 'notification', 'email', 'sms', default: 'notification')
- reminder_type: string (enum: 'deadline', 'follow_up', 'recurring', 'custom', default: 'deadline')
- custom_message: string (optional)
- sent: boolean (default: false)
- sent_at: datetime (optional, when the reminder was sent)
- acknowledged_at: datetime (optional, when user acknowledged the reminder)
- created_at: datetime (auto-generated)

**Relationships**:
- One User to Many Reminders
- One Task to Many Reminders

### UserInteraction
**Description**: Tracks user interactions with the AI system for analytics and improvement
**Attributes**:
- id: uuid (Primary Key)
- user_id: string (Foreign Key to User)
- interaction_type: string (enum: 'chat_message', 'suggestion_response', 'analytics_view', 'task_action')
- input_content: string (required, user's input)
- output_content: string (required, system's response)
- intent_classification: string (optional, classified intent of user input)
- conversation_context: json (optional, JSON context for the conversation)
- ai_processing_time_ms: integer (optional, time for AI to process)
- created_at: datetime (auto-generated)

**Relationships**:
- One User to Many UserInteractions

## Relationship Diagram

```
User (1) <---> (Many) Task
User (1) <---> (Many) AnalyticsData
User (1) <---> (Many) Suggestion
User (1) <---> (Many) Reminder
User (1) <---> (Many) UserInteraction

Task (1) <---> (Many) Reminder
Task (0 or 1) <---> (Many) Suggestion (converted_to_task_id)
```

## Indexes for Performance

### Task Table
- INDEX: user_id (for user-specific queries)
- INDEX: created_at (for chronological ordering)
- INDEX: due_date (for deadline-based queries)
- INDEX: is_completed (for filtering completed/pending)
- INDEX: priority (for priority-based queries)
- COMPOSITE INDEX: (user_id, is_completed) (for dashboard queries)
- COMPOSITE INDEX: (user_id, due_date, is_completed) (for reminder queries)

### AnalyticsData Table
- INDEX: user_id (for user-specific analytics)
- INDEX: metric_type (for filtering by time range type)
- INDEX: date_range_start (for date-based queries)
- COMPOSITE INDEX: (user_id, metric_type, date_range_start) (for dashboard analytics)

### Suggestion Table
- INDEX: user_id (for user-specific suggestions)
- INDEX: accepted (for filtering by response status)
- INDEX: created_at (for chronological ordering)
- COMPOSITE INDEX: (user_id, accepted, created_at) (for suggestion management)

### Reminder Table
- INDEX: user_id (for user-specific reminders)
- INDEX: scheduled_time (for scheduling queries)
- INDEX: sent (for tracking sent status)
- COMPOSITE INDEX: (user_id, scheduled_time, sent) (for reminder processing)

### UserInteraction Table
- INDEX: user_id (for user-specific logs)
- INDEX: interaction_type (for filtering by type)
- INDEX: created_at (for chronological ordering)
- COMPOSITE INDEX: (user_id, interaction_type, created_at) (for analytics)

## Data Flow Patterns

### Analytics Aggregation
1. Task updates trigger analytics calculations
2. Batch jobs aggregate data by time periods (daily, weekly, monthly)
3. AnalyticsData records are created/updated periodically
4. Dashboard queries read pre-calculated AnalyticsData

### Suggestion Lifecycle
1. User patterns analyzed periodically
2. Suggestion records created with confidence scores
3. User accepts/dismisses suggestions
4. Conversion tracked when suggestions become tasks
5. Feedback used to improve future suggestions

### Reminder Processing
1. Task due dates monitored
2. Reminder records created based on user settings
3. Scheduled service processes reminders
4. Notifications sent to users via preferred method
5. Acknowledgment tracked

### Interaction Tracking
1. All user interactions with AI logged
2. Intent classification for analytics
3. Processing time metrics collected
4. Used for system improvement and personalization

## Constraints and Validation

### Task Constraints
- Title must be 1-255 characters
- Priority must be one of the defined values
- Due date must be in the future if set
- User must exist for foreign key relationship

### AnalyticsData Constraints
- Date range end must be after date range start
- Productivity score must be between 0 and 100
- User must exist for foreign key relationship
- Metric type must be one of the defined values

### Suggestion Constraints
- Confidence score must be between 0 and 1
- User must exist for foreign key relationship
- Cannot be both accepted and dismissed
- Converted task must exist if converted_to_task_id is set

### Reminder Constraints
- Scheduled time must be in the future
- User and task must exist for foreign key relationships
- Sent status cannot be reversed

### UserInteraction Constraints
- Interaction type must be one of the defined values
- User must exist for foreign key relationship
- Input and output content must not be empty

## Privacy and Security Considerations

- All user-specific data is partitioned by user_id
- Sensitive interaction data is stored securely
- Analytics data is aggregated and anonymized where possible
- Access controls enforce user data isolation
- Personalization data is tied to user accounts only
- Telemetry data excludes personally identifiable information