# Data Model: Advanced AI Chatbot with Analytics

**Created**: 2026-01-25
**Feature**: 2-ai-chatbot-analytics
**Status**: Draft

---

## Overview

This document defines the additional database schema extensions required for the Advanced AI Chatbot with Analytics feature. The design extends the existing Phase II/III database schema while maintaining user data isolation and security requirements.

## Entity Relationships

```
[Users] 1 ---- * [Tasks]
         |
         *---- * [AnalyticsData]
         |
         *---- * [Suggestions]
         |
         *---- * [Reminders]
         |
         *---- * [TaskPatterns]
```

## New Entity Definitions

### AnalyticsData Entity

**Description**: Stores aggregated analytics and productivity metrics for each user

**Fields**:
- `id` (UUID, Primary Key)
  - Unique identifier for the analytics record
  - Auto-generated
- `user_id` (UUID, Foreign Key)
  - Links to the user this analytics data belongs to
  - References `users.id` from existing schema
  - Required
- `period_start` (DATE)
  - Start date of the analytics period
  - Required
- `period_end` (DATE)
  - End date of the analytics period
  - Required
- `tasks_completed` (INTEGER)
  - Number of tasks completed in this period
  - Default: 0
- `tasks_pending` (INTEGER)
  - Number of tasks still pending in this period
  - Default: 0
- `completion_rate` (DECIMAL)
  - Percentage of tasks completed (0.0 to 1.0)
  - Default: 0.0
- `productivity_score` (DECIMAL)
  - Calculated productivity score based on various factors
  - Range: 0.0 to 10.0
  - Default: 0.0
- `avg_completion_time` (INTERVAL)
  - Average time taken to complete tasks (in hours)
  - Optional
- `peak_productivity_hour` (INTEGER)
  - Hour of day (0-23) when user is most productive
  - Optional
- `category_breakdown` (JSON)
  - Breakdown of tasks by category/type
  - Optional
- `trend_direction` (STRING ENUM: 'up', 'down', 'stable')
  - Direction of productivity trend
  - Default: 'stable'
- `created_at` (TIMESTAMP WITH TIME ZONE)
  - When this analytics record was created
  - Auto-populated
- `updated_at` (TIMESTAMP WITH TIME ZONE)
  - When this analytics record was last updated
  - Auto-updated

**Constraints**:
- Foreign key constraint on `user_id` referencing `users.id`
- Check constraint to ensure `completion_rate` is between 0.0 and 1.0
- Check constraint to ensure `productivity_score` is between 0.0 and 10.0
- Check constraint to ensure `period_start` <= `period_end`
- Index on `user_id` and `period_start` for efficient querying

**Validation Rules**:
- `user_id` must reference an existing user
- `period_start` and `period_end` must form a valid date range
- `tasks_completed` and `tasks_pending` must be non-negative

### Suggestion Entity

**Description**: Represents AI-generated task suggestions for a user based on pattern analysis

**Fields**:
- `id` (UUID, Primary Key)
  - Unique identifier for the suggestion
  - Auto-generated
- `user_id` (UUID, Foreign Key)
  - Links to the user this suggestion is for
  - References `users.id`
  - Required
- `suggested_task_title` (TEXT)
  - The suggested task title
  - Required
- `suggested_task_description` (TEXT)
  - Optional description for the suggested task
  - Optional
- `confidence_score` (DECIMAL)
  - AI's confidence in this suggestion (0.0 to 1.0)
  - Required
- `suggestion_reason` (TEXT)
  - Explanation of why this suggestion was made
  - Optional
- `pattern_match_type` (STRING ENUM: 'recurring', 'deadline', 'behavior', 'seasonal', 'temporal')
  - Type of pattern that triggered this suggestion
  - Optional
- `pattern_id` (UUID, Foreign Key)
  - Reference to the TaskPattern that generated this suggestion (if applicable)
  - References `task_patterns.id`
  - Optional
- `is_accepted` (BOOLEAN)
  - Whether the user accepted this suggestion
  - Default: False
- `accepted_at` (TIMESTAMP WITH TIME ZONE)
  - When the suggestion was accepted (if applicable)
  - Optional
- `is_dismissed` (BOOLEAN)
  - Whether the user dismissed this suggestion
  - Default: False
- `dismissed_at` (TIMESTAMP WITH TIME ZONE)
  - When the suggestion was dismissed (if applicable)
  - Optional
- `created_at` (TIMESTAMP WITH TIME ZONE)
  - When the suggestion was generated
  - Auto-populated

**Constraints**:
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `pattern_id` referencing `task_patterns.id` (if provided)
- Check constraint to ensure `confidence_score` is between 0.0 and 1.0
- Check constraint to ensure `is_accepted` and `is_dismissed` are not both true
- Index on `user_id` and `created_at` for chronological ordering
- Index on `user_id` and `is_accepted` for tracking acceptance rates
- Index on `user_id` and `pattern_match_type` for pattern-based analysis

**Validation Rules**:
- `user_id` must reference an existing user
- `confidence_score` must be between 0.0 and 1.0
- `suggested_task_title` cannot be empty
- A suggestion cannot be both accepted and dismissed

### Reminder Entity

**Description**: Represents scheduled reminders for tasks with multi-channel delivery

**Fields**:
- `id` (UUID, Primary Key)
  - Unique identifier for the reminder
  - Auto-generated
- `user_id` (UUID, Foreign Key)
  - Links to the user this reminder is for
  - References `users.id`
  - Required
- `task_id` (UUID, Foreign Key)
  - Links to the task this reminder is for
  - References `tasks.id`
  - Required
- `scheduled_time` (TIMESTAMP WITH TIME ZONE)
  - When the reminder should be sent
  - Required
- `reminder_type` (STRING ENUM: 'deadline', 'priority', 'followup', 'pattern')
  - Type of reminder trigger
  - Required
- `delivery_status` (STRING ENUM: 'pending', 'sent', 'delivered', 'failed')
  - Current status of the reminder
  - Default: 'pending'
- `delivery_channels` (JSON)
  - List of channels to deliver the reminder (e.g., ['push', 'email'])
  - Optional
- `sent_at` (TIMESTAMP WITH TIME ZONE)
  - When the reminder was actually sent (if applicable)
  - Optional
- `delivery_attempts` (INTEGER)
  - Number of delivery attempts made
  - Default: 0
- `escalation_level` (INTEGER)
  - Current escalation level for high-priority items
  - Default: 0
- `created_at` (TIMESTAMP WITH TIME ZONE)
  - When the reminder was created
  - Auto-populated
- `updated_at` (TIMESTAMP WITH TIME ZONE)
  - When the reminder was last updated
  - Auto-updated

**Constraints**:
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `task_id` referencing `tasks.id`
- Check constraint to ensure `scheduled_time` is in the future
- Check constraint to ensure `escalation_level` is non-negative
- Index on `user_id` and `scheduled_time` for efficient scheduling queries
- Index on `delivery_status` for tracking delivery
- Index on `reminder_type` for categorizing reminders

**Validation Rules**:
- `user_id` must reference an existing user
- `task_id` must reference an existing task belonging to the user
- `scheduled_time` must be in the future
- `delivery_channels` must be a valid list of supported channels
- `escalation_level` must be non-negative

### TaskPattern Entity

**Description**: Represents identified patterns in a user's task behavior for AI-driven suggestions

**Fields**:
- `id` (UUID, Primary Key)
  - Unique identifier for the pattern
  - Auto-generated
- `user_id` (UUID, Foreign Key)
  - Links to the user this pattern belongs to
  - References `users.id`
  - Required
- `pattern_type` (STRING ENUM: 'recurring', 'deadline', 'behavior', 'seasonal', 'temporal')
  - Type of pattern that was identified
  - Required
- `pattern_identifier` (STRING)
  - Unique identifier for this specific pattern
  - Required
- `pattern_frequency` (STRING ENUM: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly')
  - How often the pattern occurs
  - Required
- `pattern_confidence` (DECIMAL)
  - Confidence in this pattern (0.0 to 1.0)
  - Required
- `pattern_attributes` (JSON)
  - Additional attributes of the pattern (times, categories, related tasks, etc.)
  - Required
- `is_active` (BOOLEAN)
  - Whether this pattern should generate suggestions
  - Default: True
- `suggestion_ranking_weight` (DECIMAL)
  - Weight to apply to suggestions from this pattern (0.0 to 1.0)
  - Default: 0.5
- `last_occurrence` (TIMESTAMP WITH TIME ZONE)
  - When this pattern last occurred
  - Optional
- `next_expected` (TIMESTAMP WITH TIME ZONE)
  - When this pattern is next expected to occur
  - Optional
- `created_at` (TIMESTAMP WITH TIME ZONE)
  - When the pattern was first identified
  - Auto-populated
- `updated_at` (TIMESTAMP WITH TIME ZONE)
  - When the pattern was last updated
  - Auto-updated

**Constraints**:
- Foreign key constraint on `user_id` referencing `users.id`
- Check constraint to ensure `pattern_confidence` is between 0.0 and 1.0
- Check constraint to ensure `suggestion_ranking_weight` is between 0.0 and 1.0
- Index on `user_id` and `pattern_type` for efficient queries
- Index on `user_id` and `is_active` for active pattern filtering
- Index on `user_id` and `pattern_frequency` for frequency-based analysis

**Validation Rules**:
- `user_id` must reference an existing user
- `pattern_confidence` must be between 0.0 and 1.0
- `suggestion_ranking_weight` must be between 0.0 and 1.0
- `pattern_type` must be a valid pattern type
- `pattern_frequency` must be a valid frequency type

## Relationship Constraints

**User-AnalyticsData Relationship**:
- Each analytics record belongs to exactly one user
- A user can have multiple analytics records (for different periods)

**User-Suggestion Relationship**:
- Each suggestion belongs to exactly one user
- A user can have multiple suggestions over time

**User-Reminder Relationship**:
- Each reminder belongs to exactly one user
- A user can have multiple reminders scheduled

**User-TaskPattern Relationship**:
- Each pattern belongs to exactly one user
- A user can have multiple identified patterns

## State Transitions

### Suggestion Lifecycle
```
GENERATED (when AI creates the suggestion)
  ↓
PENDING (waiting for user response)
  ↓
ACCEPTED (user accepts and creates task) OR REJECTED (user dismisses)
```

### Reminder Lifecycle
```
CREATED (when reminder is scheduled)
  ↓
PENDING (waiting for scheduled time)
  ↓
SENT (notification sent to user)
  ↓
DELIVERED (user receives notification) OR FAILED (delivery error)
```

### TaskPattern Lifecycle
```
DETECTED (when pattern is first identified)
  ↓
ACTIVE (generating suggestions/notifications)
  ↓
INACTIVE (user disables pattern recognition)
```

## Indexing Strategy

**Primary Indexes**:
- `analytics_data.id` (primary key)
- `suggestions.id` (primary key)
- `reminders.id` (primary key)
- `task_patterns.id` (primary key)

**Secondary Indexes**:
- `analytics_data.user_id` - for user-specific analytics queries
- `analytics_data.period_start` - for chronological analytics
- `suggestions.user_id` - for user-specific suggestions
- `suggestions.is_accepted` - for tracking acceptance rates
- `reminders.user_id` - for user-specific reminders
- `reminders.scheduled_time` - for scheduling queries
- `reminders.delivery_status` - for delivery tracking
- `task_patterns.user_id` - for user-specific patterns
- `task_patterns.pattern_type` - for pattern type queries
- `task_patterns.is_active` - for active pattern filtering

## Data Integrity Rules

1. **User Isolation**: All queries must be filtered by `user_id` to prevent cross-user data access
2. **Referential Integrity**: Foreign key constraints enforce relationship validity
3. **Temporal Consistency**: Dates and times maintain logical order
4. **Numeric Bounds**: Decimal values stay within specified ranges
5. **Audit Trail**: Creation timestamps provide complete history

## Access Patterns

**Frequently Used Queries**:
1. Retrieve user's analytics for a specific period
2. Get recent suggestions for a user
3. Find upcoming reminders for a user
4. List active patterns for a user

**Query Optimization**:
- Use indexed columns in WHERE clauses
- Filter by user_id in all queries
- Consider partitioning analytics data by date ranges for large datasets

## Security Considerations

1. **Row-Level Security**: Always filter by `user_id` in queries
2. **Input Sanitization**: Validate all pattern attributes and suggestion content
3. **Access Control**: Verify user identity before allowing operations
4. **Data Encryption**: Ensure sensitive analytics data is encrypted at rest
5. **Privacy Compliance**: Ensure analytics collection complies with privacy regulations

## Integration with Existing Schema

The new entities integrate with the existing Phase II/III schema by:
- Leveraging the existing `users` table for authentication
- Referencing the existing `tasks` table for task associations
- Using the same user_id foreign key pattern for data isolation
- Following the same security and validation patterns
- Maintaining transactional consistency with existing operations