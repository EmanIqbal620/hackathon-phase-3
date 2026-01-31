# Data Model: Task API & Database Layer

**Feature**: 002-task-api-db
**Date**: 2026-01-15

## Task Entity

### Properties
- `id` (string/UUID): Unique identifier for the task
- `title` (string): Task title/description (required, max 255 characters)
- `description` (string): Detailed task description (optional, max 1000 characters)
- `completed` (boolean): Completion status (default: false)
- `user_id` (string/UUID): Foreign key linking to the owning user
- `created_at` (timestamp): Creation timestamp (auto-generated)
- `updated_at` (timestamp): Last update timestamp (auto-generated)

### Validation Rules
- `title` must be 1-255 characters
- `description` can be null or 1-1000 characters
- `completed` must be boolean (true/false)
- `user_id` must exist in the users table when creating/updating
- `id` must be unique across all tasks
- `created_at` is set automatically on creation
- `updated_at` is updated automatically on any change

### Relationships
- Belongs to one User (many-to-one relationship)
- Each user can have multiple tasks

## Task Request/Response Objects

### Create Task Request
- `title` (string, required): Task title
- `description` (string, optional): Task description
- `completed` (boolean, optional): Initial completion status (default: false)

### Update Task Request
- `title` (string, optional): New task title
- `description` (string, optional): New task description
- `completed` (boolean, optional): New completion status

### Task Response
- `id` (string): Task identifier
- `title` (string): Task title
- `description` (string): Task description
- `completed` (boolean): Completion status
- `user_id` (string): Owner user identifier
- `created_at` (string): Creation timestamp (ISO 8601 format)
- `updated_at` (string): Last update timestamp (ISO 8601 format)

## User Identity Integration

### Properties (from authentication system)
- `user_id` (string): Authenticated user identifier extracted from JWT
- `email` (string): User email (for reference)
- `authenticated` (boolean): Whether user is currently authenticated

### Validation Rules
- All task operations require valid `user_id` from JWT
- `user_id` from JWT must match the task's `user_id` for access
- Cross-user access attempts must be rejected

## Error Response Objects

### General Error
- `error` (string): Error code (e.g., "validation_error", "not_found", "forbidden")
- `message` (string): Human-readable error description
- `status_code` (integer): HTTP status code

### Validation Error
- `error` (string): "validation_error"
- `details` (array): Array of validation error objects with field and message

### Authorization Error
- `error` (string): "forbidden" or "unauthorized"
- `message` (string): Specific reason for access denial
- `status_code` (integer): 403 for forbidden, 401 for unauthorized

## Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

### Indexes
- Index on `user_id` for efficient user-based queries
- Index on `completed` for efficient filtering
- Primary key index on `id` for direct access