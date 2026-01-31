# Quickstart Guide: Authentication & User Identity

**Feature**: 001-auth-jwt-identity
**Date**: 2026-01-13

## Overview

This guide explains how to set up and use the JWT-based authentication system with Better Auth and FastAPI middleware for the todo application.

## Prerequisites

- Node.js 18+ for frontend
- Python 3.11+ for backend
- Better Auth configured for the frontend
- FastAPI backend with JWT middleware
- Environment variables configured for JWT secrets

## Environment Setup

### Backend Configuration

1. Set JWT secret in environment variables:
```bash
export JWT_SECRET="your-super-secret-jwt-key-here"
export BETTER_AUTH_SECRET="your-better-auth-secret"
```

2. Install required Python packages:
```bash
pip install fastapi python-jose[cryptography] passlib[bcrypt] python-multipart
```

### Frontend Configuration

1. Install Better Auth dependencies:
```bash
npm install better-auth @better-auth/react
```

2. Configure Better Auth with JWT settings matching backend.

## Running the Authentication System

### Backend JWT Middleware

The authentication system implements a FastAPI dependency that:

1. Extracts JWT from `Authorization: Bearer <token>` header
2. Validates JWT signature using the shared secret
3. Checks token expiration
4. Extracts user_id from the token payload
5. Makes user information available to route handlers

Example usage in a route:
```python
from fastapi import Depends

@app.get("/api/user/{user_id}/todos")
async def get_user_todos(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Verify user_id in URL matches user_id in JWT
    if current_user['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Return user's todos
    return get_todos_for_user(user_id)
```

### Frontend API Client

The frontend implements an API client that:

1. Obtains JWT from Better Auth session
2. Attaches JWT to all authenticated requests
3. Handles 401 responses by redirecting to login
4. Refreshes session if needed

Example usage:
```typescript
const apiClient = {
  async get(path: string) {
    const token = await getAuthToken();
    return fetch(`/api${path}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  }
};
```

## Testing Authentication

### Manual Testing

1. Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

2. Login to obtain JWT:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

3. Use JWT to access protected endpoint:
```bash
curl -X GET http://localhost:8000/api/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Expected Behavior

- Requests without JWT return `401 Unauthorized`
- Requests with invalid/expired JWT return `401 Unauthorized`
- Requests with valid JWT for correct user return `200 OK`
- Requests with valid JWT but wrong user return `403 Forbidden`

## Troubleshooting

### Common Issues

1. **JWT Secret Mismatch**: Ensure frontend and backend use the same JWT secret
2. **Token Expiration**: JWTs expire after a set time; implement refresh logic
3. **User ID Mismatch**: Verify that user_id in JWT matches user_id in URL/route
4. **Missing Authorization Header**: All protected endpoints require the header

### Debugging Steps

1. Verify JWT secret configuration in environment variables
2. Check that Better Auth is properly issuing JWTs
3. Confirm FastAPI middleware is validating tokens correctly
4. Validate that user_id extraction from JWT is working