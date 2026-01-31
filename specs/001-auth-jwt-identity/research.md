# Research: Authentication & User Identity

**Feature**: 001-auth-jwt-identity
**Date**: 2026-01-13

## Executive Summary

This research document outlines the technical decisions and findings for implementing JWT-based authentication using Better Auth for the frontend and FastAPI middleware for backend verification. The implementation follows security-first principles with stateless authentication and proper user data isolation.

## Decision: JWT Implementation Strategy

**Rationale**: JWT was selected as the authentication method based on constitutional requirements for stateless authentication. This approach provides scalability without requiring server-side session storage.

**Alternatives considered**:
- Server-side sessions with shared storage
- OAuth 2.0 tokens
- Custom token format

## Decision: Better Auth Integration

**Rationale**: Better Auth was selected as the frontend authentication provider as specified in the constitution. It provides secure JWT issuance and integrates well with Next.js applications.

**Alternatives considered**:
- Auth0
- Firebase Auth
- Custom authentication system

## Decision: FastAPI JWT Middleware

**Rationale**: FastAPI middleware was chosen for token verification to ensure all requests are checked uniformly. This satisfies the constitutional requirement that authorization must be enforced on every request.

**Alternatives considered**:
- Individual route decorators
- Dependency injection per endpoint
- Custom authentication classes

## Decision: User Identity Extraction

**Rationale**: User identity will be extracted solely from the JWT payload to satisfy constitutional requirements that backend must not trust frontend-provided user IDs. The JWT signature provides cryptographic verification of the identity claim.

**Alternatives considered**:
- Allowing client-provided user_id with validation
- Storing user context in request headers separately

## Security Considerations Resolved

### Token Storage
- Frontend: Stored in secure HTTP-only cookies or memory (not localStorage for sensitive applications)
- Backend: Never stored, only validated on each request

### Secret Management
- JWT secret stored in environment variables only
- Not hardcoded in source code
- Access controlled through deployment pipeline

### Token Expiration
- JWTs include expiration times (exp claim)
- Backend validates token expiration
- Refresh token mechanism to be implemented if needed

### Cross-Site Request Forgery (CSRF)
- Proper CORS configuration to prevent unauthorized cross-origin requests
- Authorization header usage prevents simple form submissions

## Technology Stack Confirmation

### Frontend Dependencies
- `better-auth`: Official Better Auth client for Next.js
- `jose`: JWT signing/verification library (recommended by Better Auth)

### Backend Dependencies
- `fastapi`: Web framework with excellent middleware support
- `python-jose`: JWT decoding and validation
- `passlib`: Password hashing if needed for custom flows

## Error Handling Strategy

### 401 Unauthorized Cases
- Missing Authorization header
- Malformed JWT token
- Expired JWT token
- Invalid JWT signature

### 403 Forbidden Cases
- Valid JWT but attempting to access another user's resources
- Insufficient permissions for requested action

## Integration Patterns

### Frontend API Calls
- All authenticated API calls include `Authorization: Bearer <JWT>` header
- Better Auth session management handles token refresh
- Error handling for authentication failures

### Backend Request Processing
- JWT middleware extracts and validates token
- User identity injected into request context
- Resource authorization based on extracted identity
- Proper error responses for authentication failures