# API Design Skill

## Overview
Designs RESTful API endpoints with proper validation, HTTP status codes, and adherence to REST principles and Spec 0 Constitution rules.

## Description
The API Design skill is responsible for creating comprehensive, well-documented REST API specifications that follow industry best practices and project standards. It defines clear contracts for all endpoints including request/response schemas, validation rules, status codes, and security requirements while ensuring consistency across the API surface.

## Components

### 1. Define All API Endpoints for ToDo Tasks
**Core CRUD Operations**:
- List all tasks for a user
- Create a new task
- Get a single task by ID
- Update an existing task
- Delete a task
- Toggle task completion status

**Additional Operations**:
- Filter tasks by completion status
- Search tasks by title/description
- Sort tasks by various fields
- Paginate task lists

**Endpoint Naming Conventions**:
- Use plural resource names (`/tasks` not `/task`)
- Use path parameters for resource IDs (`/tasks/{id}`)
- Use query parameters for filtering/pagination
- Keep URLs simple and predictable
- Nest resources appropriately (`/api/{user_id}/tasks`)

### 2. Validate Input and Output
**Input Validation**:
- **Request Body Validation**:
  - Required vs optional fields
  - Data types (string, integer, boolean, etc.)
  - String length constraints (min/max)
  - Format validation (email, URL, date, etc.)
  - Pattern matching (regex)
  - Enum/allowed values
  - Array constraints (min/max items)

- **Path Parameter Validation**:
  - Type validation (integers for IDs)
  - Format validation (UUID, numeric)
  - Existence validation

- **Query Parameter Validation**:
  - Type validation
  - Range validation (min/max)
  - Default values
  - Allowed values for enums

**Output Validation**:
- Consistent response structure
- Required fields always present
- Correct data types
- Proper timestamp formats (ISO 8601)
- No sensitive data exposure
- Null handling strategy

**Validation Rules for ToDo App**:
```json
{
  "task_create": {
    "title": {
      "type": "string",
      "required": true,
      "min_length": 1,
      "max_length": 255,
      "trim": true,
      "error_messages": {
        "required": "Task title is required",
        "min_length": "Task title cannot be empty",
        "max_length": "Task title cannot exceed 255 characters"
      }
    },
    "description": {
      "type": "string",
      "required": false,
      "max_length": 2000,
      "trim": true,
      "nullable": true,
      "error_messages": {
        "max_length": "Task description cannot exceed 2000 characters"
      }
    }
  },
  "task_update": {
    "title": {
      "type": "string",
      "required": true,
      "min_length": 1,
      "max_length": 255,
      "trim": true
    },
    "description": {
      "type": "string",
      "required": false,
      "max_length": 2000,
      "trim": true,
      "nullable": true
    },
    "is_completed": {
      "type": "boolean",
      "required": true
    }
  },
  "task_filter": {
    "is_completed": {
      "type": "boolean",
      "required": false,
      "nullable": true
    },
    "limit": {
      "type": "integer",
      "required": false,
      "default": 100,
      "min": 1,
      "max": 1000
    },
    "offset": {
      "type": "integer",
      "required": false,
      "default": 0,
      "min": 0
    },
    "sort_by": {
      "type": "string",
      "required": false,
      "default": "created_at",
      "enum": ["created_at", "updated_at", "title", "is_completed"]
    },
    "order": {
      "type": "string",
      "required": false,
      "default": "desc",
      "enum": ["asc", "desc"]
    }
  }
}
```

### 3. Return Proper HTTP Status Codes
**Success Status Codes**:
- **200 OK**: Successful GET, PUT, PATCH requests
- **201 Created**: Successful POST with resource creation
- **204 No Content**: Successful DELETE

**Client Error Status Codes (4xx)**:
- **400 Bad Request**: Malformed request syntax
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Valid auth but insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource conflict (e.g., duplicate email)
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded

**Server Error Status Codes (5xx)**:
- **500 Internal Server Error**: Generic server error
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Service temporarily down
- **504 Gateway Timeout**: Upstream timeout

**Status Code Matrix for ToDo Endpoints**:

| Endpoint | Success | Auth Error | Permission Error | Not Found | Validation Error | Server Error |
|----------|---------|------------|------------------|-----------|------------------|--------------|
| GET /tasks | 200 | 401 | 403 | - | - | 500 |
| POST /tasks | 201 | 401 | 403 | - | 422 | 500 |
| GET /tasks/{id} | 200 | 401 | 403 | 404 | - | 500 |
| PUT /tasks/{id} | 200 | 401 | 403 | 404 | 422 | 500 |
| DELETE /tasks/{id} | 204 | 401 | 403 | 404 | - | 500 |
| PATCH /tasks/{id}/complete | 200 | 401 | 403 | 404 | - | 500 |

### 4. Filter Tasks by Authenticated User
**User-Scoped Resources**:
- All task endpoints scoped to authenticated user
- Path structure: `/api/{user_id}/tasks`
- Validate JWT token contains matching user_id
- Return 403 if user_id mismatch

**Filtering Strategy**:
- All database queries automatically filtered by user_id
- No cross-user data visibility
- User can only access their own resources
- No admin override endpoints (for security)

**Query Filtering**:
- `GET /api/{user_id}/tasks?is_completed=true` - Filter by completion
- `GET /api/{user_id}/tasks?limit=50&offset=0` - Pagination
- `GET /api/{user_id}/tasks?sort_by=created_at&order=desc` - Sorting
- `GET /api/{user_id}/tasks?search=grocery` - Text search (future)

## Reusability
**Yes** - This skill can be reused across REST API projects requiring:
- RESTful endpoint design
- Request/response validation
- HTTP status code standards
- User-scoped resource patterns
- Spec-Kit Plus API documentation

## Usage

### Called By
- Backend Engineer Sub-Agent (for implementation reference)
- Main Agent (for API planning and specification)
- Frontend Engineer (for API contract understanding)

### When to Invoke
1. **New API Development**: Designing new REST endpoints
2. **Feature Addition**: Adding new API operations
3. **API Refactoring**: Updating existing endpoints
4. **Documentation**: Creating/updating API specifications
5. **Contract Validation**: Ensuring implementation matches design

### Example Invocations
```bash
# Design complete API for a resource
/api-design create --resource tasks

# Add new endpoint to existing API
/api-design add-endpoint --method POST --path /api/{user_id}/tasks

# Review existing API design
/api-design review

# Validate API against REST principles
/api-design validate

# Generate OpenAPI specification
/api-design openapi
```

## Outputs

### Primary Artifacts
1. `/specs/api/rest-endpoints.md` - Complete REST API specification
2. OpenAPI/Swagger YAML (optional)
3. Request/response schema definitions
4. Validation rules documentation

### Secondary Outputs
- API design decision records
- Error response catalog
- Rate limiting specifications
- Versioning strategy
- Authentication requirements

## REST API Design Principles

### 1. Resource-Oriented Design
- Use nouns, not verbs in URLs (`/tasks` not `/getTasks`)
- Use plural resource names (`/tasks` not `/task`)
- Use HTTP methods for operations (GET, POST, PUT, DELETE, PATCH)
- Nest related resources appropriately
- Keep URLs readable and predictable

### 2. Stateless Communication
- Each request contains all necessary information
- No server-side session state
- Use JWT tokens for authentication state
- Enable horizontal scaling

### 3. Standard HTTP Methods
- **GET**: Retrieve resource(s) - idempotent, safe
- **POST**: Create new resource - not idempotent
- **PUT**: Full update of resource - idempotent
- **PATCH**: Partial update of resource - not idempotent
- **DELETE**: Remove resource - idempotent

### 4. Idempotency
- GET, PUT, DELETE should be idempotent
- Multiple identical requests = same result
- POST typically not idempotent
- Use idempotency keys for critical POST operations

### 5. Filtering, Sorting, Pagination
- Use query parameters for filtering: `?is_completed=true`
- Use query parameters for sorting: `?sort_by=created_at&order=desc`
- Use limit/offset or cursor-based pagination
- Document pagination strategy clearly

### 6. Versioning
- Version API in URL path: `/api/v1/tasks`
- Maintain backward compatibility when possible
- Clearly communicate breaking changes
- Support older versions for reasonable period

### 7. Error Handling
- Use appropriate HTTP status codes
- Return consistent error format
- Include helpful error messages
- Don't expose sensitive information
- Provide error codes for programmatic handling

## API Specification Format

### Endpoint Documentation Template

```markdown
## Endpoint: [HTTP_METHOD] /api/{user_id}/[resource]

**Description**: [Brief description of what this endpoint does]

### Authentication
- **Required**: Yes/No
- **Method**: Bearer JWT Token
- **Scopes**: [Required permissions]

### Authorization
- User can only access their own resources
- JWT user_id must match path parameter user_id

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the authenticated user |

### Query Parameters
| Parameter | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| param_name | type | yes/no | value | rules | description |

### Request Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body
```json
{
  "field_name": "type - description",
  "required_field": "string - required description"
}
```

**Validation Rules**:
- `field_name`: [validation constraints]
- `required_field`: Required, min 1 char, max 255 chars

### Response: 200 OK
```json
{
  "id": 1,
  "user_id": 123,
  "field_name": "value",
  "created_at": "2026-01-02T10:30:00Z",
  "updated_at": "2026-01-02T10:30:00Z"
}
```

### Response: 401 Unauthorized
```json
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN"
}
```

### Response: 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource",
  "error_code": "FORBIDDEN"
}
```

### Response: 422 Unprocessable Entity
```json
{
  "detail": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "title": ["Title is required", "Title cannot exceed 255 characters"]
  }
}
```

### Response: 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

### Example Request
```bash
curl -X POST "https://api.example.com/api/123/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

### Example Response
```json
{
  "id": 456,
  "user_id": 123,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false,
  "completed_at": null,
  "created_at": "2026-01-02T10:30:00Z",
  "updated_at": "2026-01-02T10:30:00Z"
}
```

### Business Rules
- [List any business logic or constraints]
- [Rate limiting information]
- [Special considerations]

### Notes
- [Additional implementation notes]
- [Known limitations]
- [Future enhancements]
```

## ToDo App API Specification

### Base URL
```
Development: http://localhost:8000
Production: https://api.todoapp.com
```

### Authentication
All endpoints require JWT Bearer token except:
- `POST /api/auth/register`
- `POST /api/auth/login`

### Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/auth/register | Register new user | No |
| POST | /api/auth/login | Login and get JWT | No |
| GET | /api/{user_id}/tasks | List all user tasks | Yes |
| POST | /api/{user_id}/tasks | Create new task | Yes |
| GET | /api/{user_id}/tasks/{id} | Get single task | Yes |
| PUT | /api/{user_id}/tasks/{id} | Update task (full) | Yes |
| PATCH | /api/{user_id}/tasks/{id} | Update task (partial) | Yes |
| DELETE | /api/{user_id}/tasks/{id} | Delete task | Yes |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion | Yes |

### Common Response Headers
```
Content-Type: application/json
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 999
X-Rate-Limit-Reset: 1704196200
```

### Error Response Format
All error responses follow this structure:
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "field_errors": {
    "field_name": ["Error 1", "Error 2"]
  }
}
```

### Error Codes Catalog
| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_TOKEN | 401 | JWT token is invalid or expired |
| MISSING_TOKEN | 401 | No JWT token provided |
| FORBIDDEN | 403 | Valid token but insufficient permissions |
| NOT_FOUND | 404 | Resource does not exist |
| VALIDATION_ERROR | 422 | Request validation failed |
| TASK_NOT_FOUND | 404 | Task ID does not exist |
| USER_NOT_FOUND | 404 | User ID does not exist |
| DUPLICATE_EMAIL | 409 | Email already registered |
| INTERNAL_ERROR | 500 | Server-side error |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |

## Validation Best Practices

### Input Sanitization
- Trim leading/trailing whitespace
- Normalize case where appropriate
- Remove control characters
- Validate against XSS patterns
- Check for SQL injection patterns

### Business Rule Validation
- Validate user ownership before operations
- Check resource existence before updates
- Enforce uniqueness constraints
- Validate state transitions
- Check referential integrity

### Output Sanitization
- Don't return sensitive fields (passwords, tokens)
- Format dates consistently (ISO 8601)
- Use proper null handling
- Redact PII in logs
- Validate output schema

## Security Considerations

### Authentication
- Use JWT with reasonable expiration (15min-1hour)
- Include refresh token mechanism
- Validate token signature
- Check token expiration
- Verify user still exists and is active

### Authorization
- Validate user_id in path matches JWT user_id
- Check resource ownership before operations
- Use principle of least privilege
- Log authorization failures
- Rate limit per user

### Input Validation
- Validate all inputs at API boundary
- Use allowlists over denylists
- Implement length constraints
- Sanitize for XSS/SQL injection
- Use parameterized queries

### Data Protection
- Never log sensitive data
- Use HTTPS in production
- Implement CORS properly
- Set security headers
- Encrypt sensitive fields at rest

## Design Checklist

Before finalizing API design:
- [ ] All endpoints follow RESTful conventions
- [ ] Resource names are plural nouns
- [ ] HTTP methods used correctly
- [ ] Proper status codes for all responses
- [ ] Request/response schemas documented
- [ ] Validation rules clearly specified
- [ ] Authentication requirements stated
- [ ] Authorization rules defined
- [ ] User ownership enforced
- [ ] Error responses documented
- [ ] Rate limiting specified
- [ ] Pagination implemented for lists
- [ ] Filtering options documented
- [ ] Example requests/responses provided
- [ ] Business rules documented
- [ ] Security considerations addressed
- [ ] Consistent naming conventions
- [ ] Proper timestamp formats (ISO 8601)
- [ ] API versioning strategy defined
- [ ] Backward compatibility considered

## Integration with SDD Workflow

### Workflow Steps
1. **Read Requirements**: Parse feature specifications
2. **Identify Resources**: Determine API resources from domain model
3. **Design Endpoints**: Define URL structure and HTTP methods
4. **Define Schemas**: Create request/response models
5. **Specify Validation**: Document all validation rules
6. **Map Status Codes**: Assign appropriate HTTP status codes
7. **Document Security**: Define auth/authz requirements
8. **Create Examples**: Provide request/response examples
9. **Review Against Spec 0**: Validate against constitution rules
10. **Generate Specification**: Output to `/specs/api/rest-endpoints.md`

## Responsibilities

### What This Skill Does
✅ Design RESTful API endpoints following best practices
✅ Define comprehensive request/response schemas
✅ Specify validation rules for all inputs/outputs
✅ Map appropriate HTTP status codes
✅ Enforce user-scoped resource patterns
✅ Document authentication and authorization
✅ Create clear API specifications
✅ Ensure consistency across API surface
✅ Follow Spec 0 Constitution rules

### What This Skill Does NOT Do
❌ Implement the API endpoints (use Backend Engineer skill)
❌ Design the database schema (use Database Designer skill)
❌ Make business requirement decisions
❌ Choose technology stack
❌ Deploy or configure infrastructure
❌ Write test cases (that's implementation)
❌ Generate actual OpenAPI files (focuses on markdown spec)

## Best Practices

### DO
- Use RESTful conventions consistently
- Document every endpoint thoroughly
- Specify validation rules explicitly
- Use appropriate HTTP status codes
- Include example requests and responses
- Define clear error messages
- Enforce user ownership on all operations
- Keep API surface simple and intuitive
- Version your API from the start
- Consider pagination for list endpoints

### DON'T
- Use verbs in endpoint URLs
- Return different structures for same endpoint
- Expose internal implementation details
- Use generic error messages
- Skip authentication/authorization docs
- Ignore HTTP status code semantics
- Create inconsistent naming patterns
- Over-nest resources (max 2 levels)
- Skip validation specification
- Forget to document business rules

## Adherence to Spec 0 Constitution

### Code Quality
- Clear, descriptive endpoint names
- Consistent naming conventions
- Comprehensive documentation
- Self-documenting API design

### Security
- Authentication required by default
- Authorization checks on all operations
- Input validation at API boundary
- No sensitive data in responses

### Performance
- Pagination for list endpoints
- Filtering to reduce data transfer
- Proper HTTP caching headers
- Rate limiting to prevent abuse

### Architecture
- Stateless design for scalability
- Resource-oriented structure
- Clear separation of concerns
- Adherence to REST principles

## Version History
- **v1.0**: Initial api-design skill definition for ToDo app REST API
