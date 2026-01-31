# Authentication API Contracts

**Feature**: 001-auth-jwt-identity
**Date**: 2026-01-13

## Authentication Endpoints

### POST /api/auth/register
Register a new user account

#### Request
- **Method**: POST
- **Path**: `/api/auth/register`
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
```json
{
  "email": "string (required)",
  "password": "string (required, min 8 chars)",
  "name": "string (optional)"
}
```

#### Responses
- **201 Created**: User successfully registered
  ```json
  {
    "user_id": "string",
    "email": "string",
    "name": "string",
    "created_at": "ISO 8601 timestamp"
  }
  ```
- **400 Bad Request**: Invalid input
  ```json
  {
    "error": "validation_error",
    "details": "array of validation errors"
  }
  ```
- **409 Conflict**: Email already exists
  ```json
  {
    "error": "email_exists",
    "message": "Email already registered"
  }
  ```

### POST /api/auth/login
Authenticate user and return JWT token

#### Request
- **Method**: POST
- **Path**: `/api/auth/login`
- **Headers**:
  - `Content-Type: application/json`
- **Body**:
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

#### Responses
- **200 OK**: Login successful
  ```json
  {
    "access_token": "string (JWT)",
    "token_type": "Bearer",
    "expires_in": "integer (seconds)",
    "user": {
      "user_id": "string",
      "email": "string",
      "name": "string"
    }
  }
  ```
- **400 Bad Request**: Invalid input
  ```json
  {
    "error": "validation_error",
    "details": "array of validation errors"
  }
  ```
- **401 Unauthorized**: Invalid credentials
  ```json
  {
    "error": "invalid_credentials",
    "message": "Invalid email or password"
  }
  ```

### POST /api/auth/logout
Logout user and invalidate session

#### Request
- **Method**: POST
- **Path**: `/api/auth/logout`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`
- **Body**: `{}`

#### Responses
- **200 OK**: Logout successful
  ```json
  {
    "message": "Successfully logged out"
  }
  ```
- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

## Protected Endpoints (Require JWT Authentication)

### GET /api/user/profile
Get authenticated user's profile information

#### Request
- **Method**: GET
- **Path**: `/api/user/profile`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`

#### Responses
- **200 OK**: Profile retrieved successfully
  ```json
  {
    "user_id": "string",
    "email": "string",
    "name": "string",
    "created_at": "ISO 8601 timestamp"
  }
  ```
- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```

### GET /api/user/{user_id}/validate
Validate JWT and return user information (used by frontend to verify session)

#### Request
- **Method**: GET
- **Path**: `/api/user/{user_id}/validate`
- **Headers**:
  - `Authorization: Bearer {valid JWT token}`

#### Responses
- **200 OK**: Token valid and user matches
  ```json
  {
    "user_id": "string",
    "email": "string",
    "valid": true
  }
  ```
- **401 Unauthorized**: Invalid or missing token
  ```json
  {
    "error": "unauthorized",
    "message": "Invalid or missing token"
  }
  ```
- **403 Forbidden**: Token valid but user ID doesn't match
  ```json
  {
    "error": "forbidden",
    "message": "Access denied - user mismatch"
  }
  ```

## JWT Validation Requirements

### All Protected Endpoints
All endpoints that require authentication must:
1. Accept `Authorization: Bearer {JWT}` header
2. Validate JWT signature using shared secret
3. Check token expiration (`exp` claim)
4. Extract `user_id` from token payload
5. Verify user has access to requested resource

### Error Responses for JWT Issues
- **401 Unauthorized**: Missing token, invalid signature, or expired token
- **403 Forbidden**: Valid token but insufficient permissions for resource