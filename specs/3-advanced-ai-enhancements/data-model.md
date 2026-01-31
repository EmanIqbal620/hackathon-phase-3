# Data Model: Advanced AI and Full-Stack Enhancements for Todo App

## Overview
This document describes the data entities and relationships for the advanced AI and full-stack enhancements, extending the existing todo application data model.

## Entity Definitions

### Task (Extended)
**Description**: Represents a user's task item with enhanced attributes for AI processing
**Attributes**:
- id: UUID (Primary Key)
- title: String (required, max 255)
- description: Text (optional)
- priority: Enum ('low', 'medium', 'high') (required, default 'medium')
- due_date: DateTime (optional)
- completed: Boolean (required, default false)
- completed_at: DateTime (optional)
- created_at: DateTime (required, auto-generated)
- updated_at: DateTime (required, auto-generated)
- user_id: UUID (Foreign Key to User, required)
- category: String (optional, max 100)
- estimated_duration: Integer (minutes, optional)
- actual_duration: Integer (minutes, optional)
- ai_suggestion_source: String (optional, indicates if created from AI suggestion)

### AnalyticsData
**Description**: Stores aggregated analytics metrics for users
**Attributes**:
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to User, required)
- metric_type: Enum ('daily', 'weekly', 'monthly', 'quarterly') (required)
- date_range_start: DateTime (required)
- date_range_end: DateTime (required)
- tasks_created: Integer (required, default 0)
- tasks_completed: Integer (required, default 0)
- tasks_missed: Integer (required, default 0)
- average_completion_time: Float (hours, optional)
- productivity_score: Float (0-100 scale, optional)
- created_at: DateTime (required, auto-generated)
- updated_at: DateTime (required, auto-generated)

### Suggestion
**Description**: Represents AI-generated task suggestions for users
**Attributes**:
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to User, required)
- suggested_task_title: String (required, max 255)
- suggested_task_description: Text (optional)
- suggestion_type: Enum ('pattern_based', 'priority_based', 'deadline_based', 'contextual') (required)
- confidence_score: Float (0-1) (required)
- accepted: Boolean (optional, null if not yet responded)
- created_at: DateTime (required, auto-generated)
- dismissed_at: DateTime (optional)
- converted_to_task_id: UUID (Foreign Key to Task, optional)

### Reminder
**Description**: Represents scheduled reminders for tasks
**Attributes**:
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to User, required)
- task_id: UUID (Foreign Key to Task, required)
- reminder_type: Enum ('deadline', 'follow_up', 'recurring', 'custom') (required)
- scheduled_time: DateTime (required)
- delivery_method: Enum ('notification', 'email', 'sms') (required, default 'notification')
- sent: Boolean (required, default false)
- sent_at: DateTime (optional)
- created_at: DateTime (required, auto-generated)
- acknowledged_at: DateTime (optional)

### UserInteraction
**Description**: Tracks user interactions with the AI system
**Attributes**:
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to User, required)
- interaction_type: Enum ('chat_message', 'suggestion_response', 'analytics_view', 'task_action') (required)
- input_content: Text (required)
- output_content: Text (required)
- intent_classification: String (optional)
- conversation_context: JSON (optional)
- created_at: DateTime (required, auto-generated)
- ai_processing_time_ms: Integer (optional)

## Relationship Diagram

```
User (1) <---> (Many) Task
User (1) <---> (Many) AnalyticsData
User (1) <---> (Many) Suggestion
User (1) <---> (Many) Reminder
User (1) <---> (Many) UserInteraction

Task (1) <---> (Many) Reminder
Task (1) <---> (0 or 1) Suggestion (converted_to_task_id)
```

## Indexes for Performance

### Task Table
- INDEX: user_id (for user-specific queries)
- INDEX: due_date (for deadline-based queries)
- INDEX: completed (for filtering completed/pending)
- INDEX: created_at (for chronological ordering)
- COMPOSITE INDEX: (user_id, completed) (for user dashboard queries)

### AnalyticsData Table
- INDEX: user_id (for user-specific analytics)
- INDEX: metric_type (for filtering by time range type)
- INDEX: date_range_start (for date-based queries)
- COMPOSITE INDEX: (user_id, metric_type, date_range_start) (for dashboard analytics)

### Suggestion Table
- INDEX: user_id (for user-specific suggestions)
- INDEX: accepted (for tracking suggestion effectiveness)
- INDEX: created_at (for chronological ordering)
- COMPOSITE INDEX: (user_id, accepted) (for analytics)

### Reminder Table
- INDEX: user_id (for user-specific reminders)
- INDEX: scheduled_time (for scheduling queries)
- INDEX: sent (for tracking sent reminders)
- COMPOSITE INDEX: (user_id, scheduled_time, sent) (for reminder processing)

### UserInteraction Table
- INDEX: user_id (for user-specific logs)
- INDEX: interaction_type (for filtering by type)
- INDEX: created_at (for chronological ordering)
- COMPOSITE INDEX: (user_id, interaction_type, created_at) (for analytics)

## Data Flow Patterns

### Analytics Aggregation
1. Task updates trigger analytics calculations
2. Batch jobs aggregate data by time periods
3. AnalyticsData records are created/updated periodically
4. Dashboard queries read pre-calculated AnalyticsData

### AI Suggestion Lifecycle
1. User patterns analyzed periodically
2. Suggestion records created with confidence scores
3. User accepts/dismisses suggestions
4. Conversion tracked when suggestions become tasks

### Reminder Processing
1. Task due dates monitored
2. Reminder records created based on settings
3. Scheduled service processes reminders
4. Notifications sent to users

## Constraints and Validation

### Task Constraints
- Due date must be in the future if set
- Priority must be one of the defined enum values
- User must exist for foreign key relationship
- Title must be between 1 and 255 characters

### AnalyticsData Constraints
- Date range end must be after date range start
- Productivity score must be between 0 and 100
- User must exist for foreign key relationship
- Metric type must be one of the defined enum values

### Suggestion Constraints
- Confidence score must be between 0 and 1
- User must exist for foreign key relationship
- Cannot convert the same suggestion multiple times

### Reminder Constraints
- Scheduled time must be in the future
- User and task must exist for foreign key relationships
- Sent status cannot be reversed

## Privacy and Security Considerations

- All user-specific data is partitioned by user_id
- Sensitive interaction data is stored securely
- Analytics data is aggregated and anonymized where possible
- Access controls enforce user data isolation
- Personalization data is tied to user accounts only