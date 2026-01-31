# Task API Contracts

**Feature**: 002-task-api-db
**Date**: 2026-01-15

## Task Management Endpoints

### GET /api/tasks
Retrieve authenticated user's task list

#### Request
- **Method**: GET
- **Path**: `/api/tasks`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
- **Query Parameters**:
  - `completed` (optional, boolean): Filter by completion status
  - `limit` (optional, integer): Maximum number of results
  - `offset` (optional, integer): Number of results to skip

#### Responses
- **200 OK**: Successfully retrieved task list
  ```json
  {
    "tasks": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "completed": "boolean",
        "user_id": "string",
        "created_at": "ISO 8601 timestamp",
        "updated_at": "ISO 8601 timestamp"
      }
    ],
    "total_count": "integer"
  }
  ```

- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

### POST /api/tasks
Create a new task for the authenticated user

#### Request
- **Method**: POST
- **Path**: `/api/tasks`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "title": "string (required, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "completed": "boolean (optional, default: false)"
  }
  ```

#### Responses
- **201 Created**: Task successfully created
  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "user_id": "string",
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  }
  ```

- **400 Bad Request**: Validation error
  ```json
  {
    "error": "validation_error",
    "details": "array of validation errors"
  }
  ```

- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

### GET /api/tasks/{task_id}
Retrieve a specific task by ID

#### Request
- **Method**: GET
- **Path**: `/api/tasks/{task_id}`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
- **Path Parameters**:
  - `task_id` (string): ID of the task to retrieve

#### Responses
- **200 OK**: Task successfully retrieved
  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "user_id": "string",
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  }
  ```

- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

- **403 Forbidden**: Task belongs to another user
  ```json
  {
    "error": "forbidden",
    "message": "Access denied - task does not belong to user"
  }
  ```

- **404 Not Found**: Task does not exist
  ```json
  {
    "error": "not_found",
    "message": "Task not found"
  }
  ```

### PUT /api/tasks/{task_id}
Update an existing task

#### Request
- **Method**: PUT
- **Path**: `/api/tasks/{task_id}`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
  - `Content-Type: application/json`
- **Path Parameters**:
  - `task_id` (string): ID of the task to update
- **Body**:
  ```json
  {
    "title": "string (optional, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "completed": "boolean (optional)"
  }
  ```

#### Responses
- **200 OK**: Task successfully updated
  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "user_id": "string",
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  }
  ```

- **400 Bad Request**: Validation error
  ```json
  {
    "error": "validation_error",
    "details": "array of validation errors"
  }
  ```

- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

- **403 Forbidden**: Task belongs to another user
  ```json
  {
    "error": "forbidden",
    "message": "Access denied - task does not belong to user"
  }
  ```

- **404 Not Found**: Task does not exist
  ```json
  {
    "error": "not_found",
    "message": "Task not found"
  }
  ```

### DELETE /api/tasks/{task_id}
Delete a task

#### Request
- **Method**: DELETE
- **Path**: `/api/tasks/{task_id}`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
- **Path Parameters**:
  - `task_id` (string): ID of the task to delete

#### Responses
- **200 OK**: Task successfully deleted
  ```json
  {
    "message": "Task successfully deleted"
  }
  ```

- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

- **403 Forbidden**: Task belongs to another user
  ```json
  {
    "error": "forbidden",
    "message": "Access denied - task does not belong to user"
  }
  ```

- **404 Not Found**: Task does not exist
  ```json
  {
    "error": "not_found",
    "message": "Task not found"
  }
  ```

### PATCH /api/tasks/{task_id}/toggle
Toggle a task's completion status

#### Request
- **Method**: PATCH
- **Path**: `/api/tasks/{task_id}/toggle`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
- **Path Parameters**:
  - `task_id` (string): ID of the task to toggle

#### Responses
- **200 OK**: Task completion status successfully toggled
  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "user_id": "string",
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  }
  ```

- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

- **403 Forbidden**: Task belongs to another user
  ```json
  {
    "error": "forbidden",
    "message": "Access denied - task does not belong to user"
  }
  ```

- **404 Not Found**: Task does not exist
  ```json
  {
    "error": "not_found",
    "message": "Task not found"
  }
  ```

## Authentication & Authorization Requirements

### All Protected Endpoints
All endpoints that require authentication must:
1. Accept `Authorization: Bearer {JWT}` header
2. Validate JWT signature using shared secret
3. Extract `user_id` from token payload
4. Verify that the requested resource belongs to the authenticated user
5. Return 403 Forbidden if resource ownership doesn't match authenticated user

### Error Responses for Authorization Issues
- **401 Unauthorized**: Missing token, invalid signature, or expired token
- **403 Forbidden**: Valid token but user doesn't own the requested resource
- **404 Not Found**: Resource doesn't exist (even if user tries to access another's user's non-existent resource)