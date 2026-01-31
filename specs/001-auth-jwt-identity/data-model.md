# Data Model: Authentication & User Identity

**Feature**: 001-auth-jwt-identity
**Date**: 2026-01-13

## JWT Token Structure

### Payload Claims
- `sub` (Subject): User identifier (UUID or similar)
- `iat` (Issued At): Timestamp when token was issued
- `exp` (Expiration Time): Timestamp when token expires
- `jti` (JWT ID): Unique identifier for the token (optional, for revocation)
- `user_id` (Custom Claim): User identifier for authorization purposes

### Token Headers
- `alg`: Algorithm used for signing (typically "RS256" or "HS256")
- `typ`: Token type ("JWT")

## User Identity Object

### Properties
- `user_id` (string): Unique identifier for the authenticated user
- `email` (string): User's email address (from Better Auth)
- `name` (string): User's name (optional, from Better Auth)
- `roles` (array<string>): User roles/permissions (optional)
- `created_at` (timestamp): When user account was created
- `updated_at` (timestamp): When user account was last updated

### Validation Rules
- `user_id` must be a valid UUID or similar unique identifier
- `email` must be a valid email format
- `user_id` must exist in the user database when token is validated

## Session Context Object

### Properties
- `token_valid` (boolean): Whether the JWT token is valid
- `user_identity` (User Identity Object): Extracted user information from token
- `token_expires_at` (timestamp): When the current token expires
- `scopes` (array<string>): Permissions granted by this token

## API Request Enhancement

### Enhanced Request Object
- `user` (User Identity Object): Populated by JWT middleware
- `authenticated` (boolean): Whether request is authenticated
- `permissions` (array<string>): Permissions associated with user

## Token Management Objects

### Token Request
- `email` (string): User's email for authentication
- `password` (string): User's password
- `refresh_token` (string): Optional refresh token

### Token Response
- `access_token` (string): JWT access token
- `token_type` (string): Token type (usually "Bearer")
- `expires_in` (integer): Seconds until token expires
- `refresh_token` (string): Optional refresh token

## Error Response Objects

### Authentication Error
- `error` (string): Error code (e.g., "invalid_token", "expired_token")
- `error_description` (string): Human-readable error description
- `status_code` (integer): HTTP status code (401 or 403)

### Authorization Error
- `error` (string): Error code (e.g., "insufficient_scope", "forbidden")
- `error_description` (string): Human-readable error description
- `status_code` (integer): HTTP status code (403)