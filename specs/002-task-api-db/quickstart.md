# Quickstart Guide: Task API & Database Layer

**Feature**: 002-task-api-db
**Date**: 2026-01-15

## Overview

This guide explains how to set up and use the task management system with the backend API, database, and authentication integration.

## Prerequisites

- Python 3.11+
- FastAPI framework
- SQLModel ORM
- Neon Serverless PostgreSQL database
- Valid JWT authentication from SPEC-1

## Environment Setup

### Backend Configuration

1. Set database connection in environment variables:
```bash
export DATABASE_URL="postgresql://username:password@host:port/database_name"
```

2. Install required Python packages:
```bash
pip install fastapi sqlmodel psycopg2-binary python-jose[cryptography] python-multipart
```

## Running the Task Management System

### Database Initialization

The task management system requires proper database setup:

1. Create the tasks table based on the defined schema
2. Ensure proper indexing on user_id for efficient queries
3. Set up connection pooling for optimal performance

### API Usage Examples

#### Create a Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample task", "description": "This is a sample task"}'
```

#### Get User's Tasks
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update a Task
```bash
curl -X PUT http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated task title", "completed": true}'
```

#### Toggle Task Completion
```bash
curl -X PATCH http://localhost:8000/api/tasks/TASK_ID/toggle \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Delete a Task
```bash
curl -X DELETE http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing the Task System

### Manual Testing

1. Ensure you have a valid JWT token from the authentication system (SPEC-1)

2. Test task creation:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_VALID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "This is a test"}'
```

3. Verify task retrieval:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_VALID_TOKEN"
```

4. Test cross-user access protection by attempting to access another user's task ID with your token - this should return a 403 Forbidden error.

### Expected Behavior

- Requests without JWT return `401 Unauthorized`
- Requests with valid JWT for user's own tasks return `200 OK`
- Requests with valid JWT attempting to access another user's tasks return `403 Forbidden`
- Requests for non-existent tasks return `404 Not Found`

## Troubleshooting

### Common Issues

1. **Database Connection**: Verify DATABASE_URL is properly configured
2. **Authentication Failure**: Ensure JWT token is valid and properly formatted
3. **Cross-User Access**: Verify that user_id filtering is working correctly in queries
4. **Missing Authorization Header**: All task endpoints require the Authorization header

### Debugging Steps

1. Verify database connectivity and table existence
2. Check that authentication middleware is properly extracting user_id from JWT
3. Confirm that all database queries are filtered by the authenticated user's ID
4. Validate that error responses match the contract specifications
</content>