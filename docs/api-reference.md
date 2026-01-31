# API Reference

## Authentication Endpoints

### POST /api/auth/register
Register a new user account

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

#### Response (201 Created)
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-13T10:30:00"
}
```

### POST /api/auth/login
Authenticate user and return JWT token

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### Response (200 OK)
```json
{
  "access_token": "jwt-token-string",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "refresh-token-string",
  "user": {
    "user_id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-13T10:30:00"
  }
}
```

### POST /api/auth/refresh
Refresh an expired access token using a refresh token

#### Request
```json
{
  "refresh_token": "refresh-token-string"
}
```

#### Response (200 OK)
```json
{
  "access_token": "new-jwt-token-string",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### POST /api/auth/logout
Logout user and invalidate session

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (200 OK)
```json
{
  "message": "Successfully logged out"
}
```

## User Endpoints

### GET /api/user/profile
Get authenticated user's profile information

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (200 OK)
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### GET /api/user/{user_id}/validate
Validate JWT and return user information

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (200 OK)
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "valid": true
}
```

## Security

### Authentication
All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer {token}
```

### Error Responses
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Valid token but insufficient permissions
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Resource conflict (e.g., duplicate email)