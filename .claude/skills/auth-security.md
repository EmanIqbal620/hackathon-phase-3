# Auth Security Skill

## Overview
Handles Better Auth + JWT integration for secure frontend-backend communication with comprehensive authentication and authorization mechanisms.

## Description
The Auth Security skill is responsible for implementing secure authentication and authorization across the application stack. It integrates Better Auth in the frontend for user session management and JWT token issuance, implements FastAPI middleware for token verification, enforces access control, and maps authenticated users to resource ownership to ensure data security and privacy.

## Components

### 1. Issue JWT Tokens
**Token Generation**:
- Generate JWT tokens upon successful authentication
- Include essential claims in token payload
- Set appropriate token expiration (15min-1hour)
- Use secure signing algorithm (HS256/RS256)
- Include refresh token mechanism

**Token Structure**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "iat": 1704196200,
    "exp": 1704199800,
    "jti": "unique-token-id"
  },
  "signature": "..."
}
```

**Token Claims**:
- `sub` (subject): User ID - primary identifier
- `email`: User email for reference
- `iat` (issued at): Token creation timestamp
- `exp` (expiration): Token expiration timestamp
- `jti` (JWT ID): Unique token identifier
- Custom claims: role, permissions (if needed)

**Better Auth Integration**:
- Configure Better Auth in Next.js frontend
- Handle user registration and login flows
- Store JWT tokens securely (httpOnly cookies preferred)
- Implement token refresh mechanism
- Handle logout and token cleanup

**Token Issuance Flow**:
```
1. User submits credentials (email/password)
2. Backend validates credentials
3. Backend generates JWT token
4. Token returned to frontend
5. Frontend stores token securely
6. Token included in subsequent requests
```

### 2. Verify Tokens in FastAPI Middleware
**Middleware Implementation**:
- Intercept all incoming requests
- Extract JWT from Authorization header
- Validate token signature
- Check token expiration
- Verify token hasn't been revoked
- Extract user_id from token claims
- Inject authenticated user into request context

**Verification Steps**:
```python
1. Extract token from Authorization: Bearer <token>
2. Decode and verify signature using secret key
3. Check expiration time (exp claim)
4. Validate required claims exist (sub, exp, iat)
5. Optional: Check token against revocation list
6. Load user from database using user_id (sub)
7. Attach user to request context
8. Continue to route handler
```

**Token Validation**:
- Verify signature matches secret key
- Ensure token hasn't expired
- Validate token format and structure
- Check issuer and audience (if configured)
- Validate custom claims

**Middleware Configuration**:
- Apply to all protected routes
- Exclude public endpoints (login, register)
- Handle OPTIONS requests for CORS
- Configure token extraction methods
- Set up error handling

### 3. Reject Unauthorized Requests (401)
**Unauthorized Scenarios**:
- Missing Authorization header
- Malformed token format
- Invalid token signature
- Expired token
- Revoked token
- User not found in database
- User account disabled/suspended

**Error Response Format**:
```json
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

**Specific Error Messages**:
```json
// Missing token
{
  "detail": "Authorization header is missing",
  "error_code": "MISSING_TOKEN"
}

// Invalid format
{
  "detail": "Invalid authorization header format. Expected: Bearer <token>",
  "error_code": "INVALID_FORMAT"
}

// Expired token
{
  "detail": "Token has expired",
  "error_code": "EXPIRED_TOKEN"
}

// Invalid signature
{
  "detail": "Invalid token signature",
  "error_code": "INVALID_SIGNATURE"
}

// User not found
{
  "detail": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

**HTTP 401 Response**:
- Return 401 status code
- Include WWW-Authenticate header
- Provide clear error message
- Don't expose sensitive details
- Log security events

### 4. Map user_id from Token to Resource Ownership
**User ID Extraction**:
- Extract user_id from JWT `sub` claim
- Validate user_id is valid integer/UUID
- Load user object from database
- Attach user to request context

**Resource Ownership Validation**:
- Compare JWT user_id with path parameter user_id
- Ensure authenticated user matches resource owner
- Return 403 Forbidden if mismatch
- Filter all queries by authenticated user_id
- Prevent cross-user data access

**Ownership Enforcement Pattern**:
```python
# Extract authenticated user from JWT
current_user_id = jwt_payload["sub"]

# Extract requested user from path
requested_user_id = path_params["user_id"]

# Validate ownership
if current_user_id != requested_user_id:
    raise HTTPException(
        status_code=403,
        detail="Not authorized to access this resource"
    )

# All subsequent queries filtered by current_user_id
tasks = db.query(Task).filter(Task.user_id == current_user_id).all()
```

**Database Query Filtering**:
- Always include user_id filter in WHERE clause
- Use authenticated user_id (never trust path parameter alone)
- Prevent SQL injection through ORM
- Use parameterized queries
- Validate resource belongs to user before operations

## Reusability
**Yes** - This skill can be reused across secure web applications requiring:
- JWT-based authentication
- Better Auth integration
- FastAPI backend security
- User-owned resource patterns
- Token-based authorization

## Usage

### Called By
- Main Agent (for authentication setup)
- Auth/Security Engineer Sub-Agent (for implementation)
- Backend Engineer (for middleware integration)
- Frontend Engineer (for token handling)

### When to Invoke
1. **Initial Setup**: Configuring authentication system
2. **Security Review**: Auditing auth implementation
3. **Token Management**: Implementing refresh/revocation
4. **Authorization**: Adding access control rules
5. **Security Hardening**: Improving auth security

### Example Invocations
```bash
# Setup complete authentication system
/auth-security setup

# Implement JWT middleware
/auth-security middleware

# Configure Better Auth frontend
/auth-security better-auth

# Add token refresh mechanism
/auth-security refresh-token

# Review security implementation
/auth-security audit

# Setup user ownership validation
/auth-security ownership
```

## Outputs

### Primary Artifacts
1. `/specs/auth/authentication.md` - Authentication specification
2. JWT utility functions (encode/decode/verify)
3. FastAPI authentication middleware
4. Better Auth configuration
5. User ownership validation functions

### Secondary Outputs
- Token refresh endpoints
- Logout/revocation logic
- Security test cases
- Rate limiting configuration
- CORS settings
- Security headers setup

## Implementation Guide

### Backend Implementation (FastAPI)

#### 1. JWT Utilities (`backend/app/utils/security.py`)
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload data (must include 'sub' for user_id)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")
```

#### 2. Authentication Dependency (`backend/app/dependencies/auth.py`)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlmodel import Session, select

from app.dependencies.database import get_db
from app.models.user import User
from app.utils.security import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify and decode token
        payload = verify_token(token)
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    # Optional: Check if user is active
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def verify_user_ownership(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that the authenticated user matches the requested user_id.

    Args:
        user_id: Requested user_id from path parameter
        current_user: Authenticated user from JWT

    Returns:
        Current user if ownership is verified

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    return current_user
```

#### 3. Authentication Routes (`backend/app/routers/auth.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.utils.security import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user and return JWT token.

    - **email**: User email (must be unique)
    - **password**: User password (min 8 characters)
    - **full_name**: Optional full name
    """
    # Check if email already exists
    existing_user = db.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
            headers={"error_code": "DUPLICATE_EMAIL"}
        )

    # Create new user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    - **email**: User email
    - **password**: User password
    """
    # Find user by email
    user = db.exec(
        select(User).where(User.email == credentials.email)
    ).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }
```

### Frontend Implementation (Next.js + Better Auth)

#### 1. Better Auth Configuration (`frontend/lib/auth.ts`)
```typescript
import { betterAuth } from "better-auth/client"

export const authClient = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  endpoints: {
    signIn: "/api/auth/login",
    signUp: "/api/auth/register",
    signOut: "/api/auth/logout",
  },
  storage: {
    type: "cookie",
    options: {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
    },
  },
})

export type AuthClient = typeof authClient
```

#### 2. API Client with JWT (`frontend/lib/api-client.ts`)
```typescript
import axios from "axios"
import { authClient } from "./auth"

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  async (config) => {
    const session = await authClient.getSession()

    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      await authClient.signOut()
      window.location.href = "/login"
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

#### 3. Protected Route Component (`frontend/components/ProtectedRoute.tsx`)
```typescript
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { authClient } from "@/lib/auth"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      const session = await authClient.getSession()

      if (!session) {
        router.push("/login")
      } else {
        setIsAuthenticated(true)
      }
    }

    checkAuth()
  }, [router])

  if (isAuthenticated === null) {
    return <div>Loading...</div>
  }

  return <>{children}</>
}
```

## Security Best Practices

### Token Security
- **Use HTTPS**: Always transmit tokens over encrypted connections
- **Short Expiration**: Keep access tokens short-lived (15-60 minutes)
- **Refresh Tokens**: Implement refresh token mechanism for better UX
- **Secure Storage**: Store tokens in httpOnly cookies (not localStorage)
- **Token Rotation**: Rotate tokens on refresh
- **Revocation**: Implement token revocation list for logout

### Password Security
- **Strong Hashing**: Use bcrypt or argon2 (not MD5/SHA1)
- **Salt**: Use unique salt per password (handled by bcrypt)
- **Minimum Length**: Enforce minimum 8 characters
- **Complexity**: Require mix of characters (optional)
- **No Plain Text**: Never store or log plain passwords
- **Rate Limiting**: Prevent brute force attacks

### API Security
- **CORS**: Configure proper CORS policy
- **Rate Limiting**: Implement per-user rate limits
- **Input Validation**: Validate all inputs at API boundary
- **Output Sanitization**: Don't expose sensitive data
- **Error Messages**: Don't leak implementation details
- **Security Headers**: Set HSTS, CSP, X-Frame-Options, etc.

### Authorization Security
- **User Ownership**: Always validate user owns resources
- **Path Traversal**: Prevent access to other users' data
- **SQL Injection**: Use ORM and parameterized queries
- **XSS Prevention**: Sanitize user input
- **CSRF Protection**: Use CSRF tokens for state changes
- **Principle of Least Privilege**: Grant minimal necessary permissions

## Security Checklist

Before production deployment:
- [ ] JWT secret key is strong and stored securely (environment variable)
- [ ] Tokens use secure signing algorithm (HS256 or RS256)
- [ ] Access tokens have short expiration (15-60 minutes)
- [ ] Refresh token mechanism implemented
- [ ] Passwords hashed with bcrypt/argon2
- [ ] HTTPS enforced in production
- [ ] CORS configured properly
- [ ] Rate limiting enabled per user
- [ ] Input validation on all endpoints
- [ ] User ownership validated on all operations
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention (input sanitization)
- [ ] CSRF protection for state-changing operations
- [ ] Security headers configured (HSTS, CSP, etc.)
- [ ] Error messages don't expose sensitive information
- [ ] Tokens stored in httpOnly cookies (not localStorage)
- [ ] Token revocation mechanism for logout
- [ ] Audit logging for security events
- [ ] Account lockout after failed login attempts
- [ ] Session timeout configured

## Testing Strategy

### Unit Tests
- Test JWT encoding/decoding
- Test password hashing/verification
- Test token expiration logic
- Mock authentication dependencies

### Integration Tests
- Test login flow end-to-end
- Test registration flow
- Test protected endpoint access
- Test token refresh mechanism
- Test logout and revocation

### Security Tests
- Test with expired tokens
- Test with invalid tokens
- Test with missing tokens
- Test cross-user access attempts
- Test brute force protection
- Test SQL injection attempts
- Test XSS attempts

### Test Example
```python
import pytest
from fastapi.testclient import TestClient
from app.utils.security import create_access_token, verify_token


def test_create_and_verify_token():
    """Test JWT token creation and verification."""
    payload = {"sub": 123, "email": "test@example.com"}
    token = create_access_token(payload)

    decoded = verify_token(token)

    assert decoded["sub"] == 123
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded
    assert "iat" in decoded


def test_protected_endpoint_requires_auth(client: TestClient):
    """Test that protected endpoint requires authentication."""
    response = client.get("/api/1/tasks")
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(client: TestClient, test_user):
    """Test protected endpoint with valid JWT."""
    token = create_access_token({"sub": test_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/api/{test_user.id}/tasks", headers=headers)
    assert response.status_code == 200


def test_cross_user_access_forbidden(client: TestClient, test_user, other_user):
    """Test that users cannot access other users' resources."""
    token = create_access_token({"sub": test_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Try to access other_user's tasks
    response = client.get(f"/api/{other_user.id}/tasks", headers=headers)
    assert response.status_code == 403
```

## Integration with SDD Workflow

### Workflow Steps
1. **Requirements Analysis**: Define auth requirements from specs
2. **Design Authentication Flow**: Login, registration, token management
3. **Implement JWT Utilities**: Token creation and verification
4. **Create Auth Middleware**: FastAPI dependency injection
5. **Implement Auth Endpoints**: Register, login, logout
6. **Setup Better Auth Frontend**: Client-side auth integration
7. **Add User Ownership Validation**: Resource access control
8. **Implement Security Headers**: CORS, HSTS, CSP
9. **Add Rate Limiting**: Prevent abuse
10. **Write Security Tests**: Comprehensive test coverage
11. **Security Audit**: Review and harden implementation

## Responsibilities

### What This Skill Does
✅ Design and implement JWT authentication
✅ Configure Better Auth in frontend
✅ Create FastAPI authentication middleware
✅ Enforce user ownership validation
✅ Implement password hashing and verification
✅ Handle token refresh and revocation
✅ Configure security headers and CORS
✅ Implement rate limiting
✅ Provide security test coverage

### What This Skill Does NOT Do
❌ Design the overall application architecture
❌ Implement business logic features
❌ Design the database schema
❌ Create UI components
❌ Deploy or configure infrastructure
❌ Make business requirement decisions
❌ Implement OAuth/social login (unless specified)

## Common Security Vulnerabilities to Avoid

### Authentication Vulnerabilities
- ❌ Storing passwords in plain text
- ❌ Using weak hashing algorithms (MD5, SHA1)
- ❌ Not validating token expiration
- ❌ Exposing JWT secret key
- ❌ Not implementing token refresh
- ❌ Allowing unlimited login attempts

### Authorization Vulnerabilities
- ❌ Not validating user ownership
- ❌ Trusting path parameters without verification
- ❌ Not filtering queries by user_id
- ❌ Exposing other users' data
- ❌ Not implementing rate limiting
- ❌ Missing access control checks

### Token Vulnerabilities
- ❌ Storing tokens in localStorage (XSS risk)
- ❌ Long token expiration times
- ❌ Not implementing token revocation
- ❌ Not validating token signature
- ❌ Exposing tokens in URLs or logs
- ❌ Not using HTTPS for token transmission

## Version History
- **v1.0**: Initial auth-security skill definition for Better Auth + JWT integration
