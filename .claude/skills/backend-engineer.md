# Backend Engineer Skill

## Overview
Implements FastAPI backend endpoints, handles CRUD operations, and enforces JWT authentication for secure API access.

## Description
The Backend Engineer skill is responsible for creating robust, secure, and well-documented FastAPI endpoints. It implements complete CRUD operations, enforces JWT-based authentication, validates user ownership, and follows REST API best practices while maintaining compatibility with the Spec-Kit Plus framework.

## Components

### 1. GET /api/{user_id}/tasks
**Purpose**: Retrieve all tasks for a specific user

**Endpoint Details**:
- **Method**: GET
- **Path**: `/api/{user_id}/tasks`
- **Authentication**: Required (JWT)
- **Authorization**: User can only access their own tasks

**Query Parameters**:
- `is_completed` (optional): Filter by completion status (true/false)
- `limit` (optional): Pagination limit (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `sort_by` (optional): Sort field (created_at, updated_at, title)
- `order` (optional): Sort order (asc, desc)

**Response**:
- **200 OK**: Array of task objects
- **401 Unauthorized**: Invalid or missing JWT
- **403 Forbidden**: User attempting to access another user's tasks
- **500 Internal Server Error**: Server error

### 2. POST /api/{user_id}/tasks
**Purpose**: Create a new task for a user

**Endpoint Details**:
- **Method**: POST
- **Path**: `/api/{user_id}/tasks`
- **Authentication**: Required (JWT)
- **Authorization**: User can only create tasks for themselves

**Request Body**:
```json
{
  "title": "string (required, 1-255 chars)",
  "description": "string (optional, max 2000 chars)"
}
```

**Response**:
- **201 Created**: Created task object with id
- **400 Bad Request**: Invalid request body
- **401 Unauthorized**: Invalid or missing JWT
- **403 Forbidden**: User attempting to create task for another user
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### 3. PUT /api/{user_id}/tasks/{id}
**Purpose**: Update an existing task (full update)

**Endpoint Details**:
- **Method**: PUT
- **Path**: `/api/{user_id}/tasks/{id}`
- **Authentication**: Required (JWT)
- **Authorization**: User can only update their own tasks

**Request Body**:
```json
{
  "title": "string (required, 1-255 chars)",
  "description": "string (optional, max 2000 chars)",
  "is_completed": "boolean (required)"
}
```

**Response**:
- **200 OK**: Updated task object
- **400 Bad Request**: Invalid request body
- **401 Unauthorized**: Invalid or missing JWT
- **403 Forbidden**: User attempting to update another user's task
- **404 Not Found**: Task not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### 4. DELETE /api/{user_id}/tasks/{id}
**Purpose**: Delete a task

**Endpoint Details**:
- **Method**: DELETE
- **Path**: `/api/{user_id}/tasks/{id}`
- **Authentication**: Required (JWT)
- **Authorization**: User can only delete their own tasks

**Response**:
- **204 No Content**: Task successfully deleted
- **401 Unauthorized**: Invalid or missing JWT
- **403 Forbidden**: User attempting to delete another user's task
- **404 Not Found**: Task not found
- **500 Internal Server Error**: Server error

### 5. PATCH /api/{user_id}/tasks/{id}/complete
**Purpose**: Toggle task completion status

**Endpoint Details**:
- **Method**: PATCH
- **Path**: `/api/{user_id}/tasks/{id}/complete`
- **Authentication**: Required (JWT)
- **Authorization**: User can only complete their own tasks

**Request Body** (optional):
```json
{
  "is_completed": "boolean (default: true)"
}
```

**Response**:
- **200 OK**: Updated task object with completion status
- **401 Unauthorized**: Invalid or missing JWT
- **403 Forbidden**: User attempting to complete another user's task
- **404 Not Found**: Task not found
- **500 Internal Server Error**: Server error

### 6. JWT Authentication and User Ownership Validation
**Authentication Layer**:
- Extract JWT from `Authorization: Bearer <token>` header
- Verify JWT signature and expiration
- Extract user_id from JWT claims
- Validate user exists in database

**Authorization Layer**:
- Compare JWT user_id with path parameter user_id
- Ensure authenticated user can only access/modify their own resources
- Return 403 Forbidden if user_id mismatch
- Filter all database queries by authenticated user_id

**Security Measures**:
- Rate limiting per user
- Input validation and sanitization
- SQL injection prevention (use ORM)
- CORS configuration
- Secure password hashing (bcrypt/argon2)

## Reusability
**Yes** - This skill can be reused across FastAPI projects requiring:
- RESTful CRUD operations
- JWT-based authentication
- User-owned resource patterns
- SQLModel/PostgreSQL integration
- Spec-Kit Plus API documentation

## Usage

### Called By
- Main Agent (for API implementation planning)
- Backend Engineer Sub-Agent (for endpoint implementation)
- API Designer Agent (for contract validation)

### When to Invoke
1. **New API Development**: Implementing REST endpoints
2. **Feature Addition**: Adding new CRUD operations
3. **Security Enhancement**: Adding/updating authentication
4. **API Refactoring**: Updating existing endpoints
5. **Integration Testing**: Validating API behavior

### Example Invocations
```bash
# Implement all CRUD endpoints
/backend-engineer implement-crud --resource tasks

# Add authentication middleware
/backend-engineer add-auth --method jwt

# Create specific endpoint
/backend-engineer endpoint --method POST --path /api/{user_id}/tasks

# Review existing endpoints
/backend-engineer review

# Generate API tests
/backend-engineer tests --resource tasks
```

## Outputs

### Primary Artifacts
1. `/specs/api/rest-endpoints.md` - REST API contract documentation
2. FastAPI route implementations
3. Pydantic models for request/response validation
4. Authentication middleware
5. Database query functions

### Secondary Outputs
- API test cases (pytest)
- OpenAPI/Swagger documentation
- Error handling utilities
- Database session management
- JWT utility functions

## FastAPI Implementation Pattern

### Project Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration and environment
│   ├── database.py             # Database connection and session
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── tasks.py
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── task_service.py
│   ├── dependencies/           # Dependency injection
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT verification
│   │   └── database.py         # DB session
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── security.py         # Password hashing, JWT
│       └── validators.py       # Custom validators
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py
│   └── test_tasks.py
├── alembic/                    # Database migrations
├── requirements.txt
└── .env.example
```

### Endpoint Implementation Template

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.models.user import User

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    user_id: int,
    is_completed: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all tasks for the authenticated user.

    - **user_id**: User ID from path (must match authenticated user)
    - **is_completed**: Optional filter by completion status
    - **limit**: Maximum number of tasks to return
    - **offset**: Number of tasks to skip for pagination
    """
    # Verify user can only access their own tasks
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    if is_completed is not None:
        query = query.where(Task.is_completed == is_completed)

    query = query.offset(offset).limit(limit).order_by(Task.created_at.desc())

    # Execute query
    tasks = db.exec(query).all()

    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the authenticated user.

    - **user_id**: User ID from path (must match authenticated user)
    - **task_data**: Task creation payload
    """
    # Verify user can only create tasks for themselves
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for another user"
        )

    # Create task
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        is_completed=False
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.put("/{id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task (full update).

    - **user_id**: User ID from path (must match authenticated user)
    - **id**: Task ID to update
    - **task_data**: Complete task update payload
    """
    # Verify user ownership
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Get existing task
    task = db.get(Task, id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task
    task.title = task_data.title
    task.description = task_data.description
    task.is_completed = task_data.is_completed

    if task_data.is_completed and not task.completed_at:
        from datetime import datetime
        task.completed_at = datetime.utcnow()
    elif not task_data.is_completed:
        task.completed_at = None

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: int,
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task.

    - **user_id**: User ID from path (must match authenticated user)
    - **id**: Task ID to delete
    """
    # Verify user ownership
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Get existing task
    task = db.get(Task, id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete task
    db.delete(task)
    db.commit()

    return None


@router.patch("/{id}/complete", response_model=TaskResponse)
async def complete_task(
    user_id: int,
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle task completion status.

    - **user_id**: User ID from path (must match authenticated user)
    - **id**: Task ID to mark as complete
    """
    # Verify user ownership
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Get existing task
    task = db.get(Task, id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion
    from datetime import datetime
    task.is_completed = not task.is_completed
    task.completed_at = datetime.utcnow() if task.is_completed else None

    db.add(task)
    db.commit()
    db.refresh(task)

    return task
```

### Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.config import settings
from app.dependencies.database import get_db
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user
```

## REST API Best Practices

### 1. HTTP Status Codes
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST with resource creation
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid request format
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Valid auth but insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server-side errors

### 2. Request/Response Format
- Use JSON for all requests and responses
- Include proper Content-Type headers
- Use snake_case for JSON keys (Python convention)
- Return consistent error format:
```json
{
  "detail": "Error message",
  "error_code": "TASK_NOT_FOUND",
  "field_errors": {
    "title": ["Title is required"]
  }
}
```

### 3. Authentication
- Use `Authorization: Bearer <token>` header
- Validate JWT on every protected endpoint
- Return 401 for missing/invalid tokens
- Return 403 for insufficient permissions
- Include token expiration in JWT claims

### 4. Validation
- Use Pydantic models for request validation
- Validate all input at the API boundary
- Return 422 with detailed field errors
- Sanitize user input to prevent injection
- Enforce business rules at service layer

### 5. Error Handling
- Catch and log all exceptions
- Return appropriate HTTP status codes
- Include helpful error messages
- Don't expose internal implementation details
- Use custom exception classes for business errors

### 6. Performance
- Implement pagination for list endpoints
- Use database indexes on queried fields
- Cache frequently accessed data
- Minimize database queries (use eager loading)
- Implement rate limiting per user

### 7. Documentation
- Use FastAPI automatic OpenAPI generation
- Add endpoint descriptions and parameter docs
- Include request/response examples
- Document error responses
- Keep API docs in sync with implementation

## Security Checklist

Before deploying endpoints:
- [ ] JWT authentication on all protected routes
- [ ] User ownership validation on all user-scoped resources
- [ ] Input validation using Pydantic models
- [ ] SQL injection prevention (using ORM)
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Passwords hashed (never stored plain text)
- [ ] Secrets stored in environment variables
- [ ] Error messages don't expose sensitive data
- [ ] HTTPS enforced in production
- [ ] Security headers configured (HSTS, CSP, etc.)

## Testing Strategy

### Unit Tests
- Test each endpoint independently
- Mock database and dependencies
- Test success and error cases
- Validate request/response schemas

### Integration Tests
- Test with real database (test DB)
- Test authentication flow
- Test authorization rules
- Test end-to-end workflows

### Test Example
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.utils.security import create_access_token


def test_get_tasks_success(client: TestClient, db: Session, test_user):
    """Test successful retrieval of user tasks."""
    # Create auth token
    token = create_access_token({"sub": test_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Make request
    response = client.get(f"/api/{test_user.id}/tasks", headers=headers)

    # Assert response
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_tasks_unauthorized(client: TestClient, test_user):
    """Test accessing tasks without authentication."""
    response = client.get(f"/api/{test_user.id}/tasks")
    assert response.status_code == 401


def test_get_tasks_forbidden(client: TestClient, db: Session, test_user, other_user):
    """Test accessing another user's tasks."""
    # Create auth token for test_user
    token = create_access_token({"sub": test_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Try to access other_user's tasks
    response = client.get(f"/api/{other_user.id}/tasks", headers=headers)
    assert response.status_code == 403
```

## Integration with SDD Workflow

### Workflow Steps
1. Read API specification from `/specs/api/rest-endpoints.md`
2. Read database schema from `/specs/database/schema.md`
3. Implement route handlers following spec
4. Implement authentication/authorization
5. Create Pydantic request/response models
6. Write service layer business logic
7. Implement database queries with user_id filtering
8. Add comprehensive error handling
9. Write unit and integration tests
10. Generate/update OpenAPI documentation

## Responsibilities

### What This Skill Does
✅ Implement FastAPI REST endpoints
✅ Enforce JWT authentication and authorization
✅ Validate user ownership on all operations
✅ Handle CRUD operations with proper error handling
✅ Create Pydantic validation models
✅ Write database queries with SQLModel
✅ Generate OpenAPI documentation
✅ Implement comprehensive tests

### What This Skill Does NOT Do
❌ Design the API contract (use API Designer skill)
❌ Design the database schema (use Database Designer skill)
❌ Implement frontend components
❌ Deploy or configure servers
❌ Make business requirement decisions
❌ Design authentication strategy (follows spec)

## Version History
- **v1.0**: Initial backend-engineer skill definition for ToDo app FastAPI implementation
