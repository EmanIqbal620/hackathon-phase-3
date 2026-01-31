# Database Designer Skill

## Overview
Designs PostgreSQL database schema and SQLModel models for applications with a focus on data integrity, relationships, and best practices.

## Description
The Database Designer skill is responsible for creating comprehensive database schemas, defining entity relationships, and generating SQLModel-compatible specifications. It ensures data consistency, proper indexing, and adherence to database design principles while maintaining compatibility with the Spec-Kit Plus framework.

## Components

### 1. Create Core Tables
- **User Table**: User authentication and profile data
  - Primary key (id)
  - Authentication fields (email, password_hash)
  - Profile information
  - Timestamps (created_at, updated_at)

- **Task Table**: Task management data
  - Primary key (id)
  - Task content and metadata
  - Foreign key to User (user_id)
  - Completion status
  - Timestamps (created_at, updated_at, completed_at)

### 2. Define Relationships and Ownership
- **User-Task Relationship**: One-to-Many
  - Each task must belong to exactly one user
  - Users can have zero or many tasks
  - Enforce data ownership via `user_id` foreign key
  - Cascade delete behavior (optional, configurable)

- **Data Isolation**:
  - All queries filtered by `user_id` to ensure data privacy
  - No cross-user data access
  - Owner-based authorization at database level

### 3. Include Completion Status and Timestamps
- **Status Tracking**:
  - `is_completed`: Boolean flag for task completion
  - `completed_at`: Timestamp when task was completed

- **Audit Timestamps**:
  - `created_at`: Record creation time (auto-set)
  - `updated_at`: Last modification time (auto-update)

- **Soft Delete Support** (optional):
  - `deleted_at`: Timestamp for soft deletion
  - Allows data recovery and audit trails

### 4. Output Spec-Kit Plus Compatible DB Spec
- **Location**: `/specs/database/schema.md`
- **Format**: Markdown documentation with:
  - Entity definitions
  - Field specifications (name, type, constraints)
  - Relationships and cardinality
  - Indexes and performance considerations
  - Migration considerations
  - SQLModel code examples

## Reusability
**Yes** - This skill can be reused across database projects requiring:
- PostgreSQL database design
- SQLModel ORM integration
- User-owned resource patterns
- Audit trail requirements
- Spec-Kit Plus documentation

## Usage

### Called By
- Main Agent (for database architecture planning)
- Database Designer Sub-Agent (for schema implementation)
- Backend Engineer Agent (for model integration)

### When to Invoke
1. **New Project Setup**: Initial database schema design
2. **Feature Addition**: New tables or relationships needed
3. **Schema Migration**: Database structure changes
4. **Performance Optimization**: Index and query optimization
5. **Data Model Review**: Validation of existing schema

### Example Invocations
```bash
# Generate complete database schema
/database-designer schema

# Add new entity to existing schema
/database-designer add-entity --name Category

# Review and optimize existing schema
/database-designer review

# Generate migration plan
/database-designer migrate --from v1 --to v2

# Validate schema against spec
/database-designer validate
```

## Outputs

### Primary Artifacts
1. `/specs/database/schema.md` - Complete database schema specification
2. SQLModel class definitions (if generating code)
3. Migration scripts (if needed)

### Secondary Outputs
- Index recommendations
- Performance considerations document
- Relationship diagrams (textual/mermaid)
- Query pattern examples
- Data seeding scripts

## Database Design Principles

### 1. Normalization
- Follow 3rd Normal Form (3NF) by default
- Denormalize only when performance requires it
- Document denormalization decisions in ADRs

### 2. Constraints
- **Primary Keys**: Auto-incrementing integers or UUIDs
- **Foreign Keys**: Enforce referential integrity
- **Unique Constraints**: Prevent duplicate data
- **Check Constraints**: Validate data at database level
- **Not Null**: Required fields explicitly marked

### 3. Indexing Strategy
- Index all foreign keys
- Index frequently queried columns
- Composite indexes for common query patterns
- Consider partial indexes for filtered queries
- Balance read performance vs write overhead

### 4. Security
- No sensitive data in plain text
- Password hashing (never store raw passwords)
- Encryption at rest for sensitive fields
- Row-level security via `user_id` filtering
- Prepared statements to prevent SQL injection

### 5. Scalability
- Avoid circular dependencies
- Design for horizontal scaling where possible
- Consider partitioning for large tables
- Optimize for common query patterns
- Plan for data archival

## Schema Specification Format

### Entity Definition Template
```markdown
## Entity: [EntityName]

**Description**: [Brief description of entity purpose]

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| user_id | Integer | FK(User.id), NOT NULL, Index | Owner reference |
| field_name | Type | Constraints | Description |
| created_at | DateTime | NOT NULL, Default: NOW() | Creation timestamp |
| updated_at | DateTime | NOT NULL, Default: NOW() | Last update timestamp |

### Relationships

- **Belongs To**: User (via user_id)
- **Has Many**: [RelatedEntity] (optional)

### Indexes

- PRIMARY KEY: id
- FOREIGN KEY: user_id → users(id)
- INDEX: idx_[entity]_user_id ON user_id
- INDEX: [additional indexes]

### Constraints

- `user_id` cannot be null
- [Additional business rules]

### SQLModel Example

\`\`\`python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class [EntityName](SQLModel, table=True):
    __tablename__ = "[table_name]"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    field_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="[entities]")
\`\`\`
```

## ToDo App Schema Example

### Core Tables

#### User Table
- `id`: Primary key
- `email`: Unique, indexed
- `password_hash`: Hashed password (never plain text)
- `full_name`: Optional user name
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update

#### Task Table
- `id`: Primary key
- `user_id`: Foreign key to User, indexed
- `title`: Task title (required)
- `description`: Task details (optional)
- `is_completed`: Boolean, default false
- `completed_at`: Timestamp when completed (nullable)
- `created_at`: Task creation timestamp
- `updated_at`: Last modification timestamp

### Relationships
- User **has many** Tasks
- Task **belongs to** User

### Key Indexes
- `users.email` (unique)
- `tasks.user_id` (foreign key index)
- `tasks.is_completed` (for filtering)
- `tasks.created_at` (for sorting)

## Integration with SDD Workflow

### Phase Integration
1. **Specification Phase**: Define data requirements
2. **Planning Phase**: Design schema and relationships
3. **Implementation Phase**: Generate SQLModel classes
4. **Testing Phase**: Validate constraints and relationships
5. **Migration Phase**: Version and deploy schema changes

### Workflow Steps
1. Read feature requirements from spec
2. Identify entities and attributes
3. Define relationships and constraints
4. Generate schema documentation
5. Create SQLModel class definitions
6. Suggest indexes and optimizations
7. Document migration strategy

## Responsibilities

### What This Skill Does
✅ Design database schema and entity relationships
✅ Generate Spec-Kit Plus compatible documentation
✅ Define SQLModel class structures
✅ Recommend indexes and constraints
✅ Ensure data integrity and security
✅ Plan migration strategies
✅ Validate schema against requirements

### What This Skill Does NOT Do
❌ Execute database migrations
❌ Write application business logic
❌ Implement API endpoints
❌ Configure database servers
❌ Make business requirement decisions
❌ Handle authentication/authorization logic

## Best Practices

### DO
- Always include `created_at` and `updated_at` timestamps
- Use foreign keys to enforce referential integrity
- Index all foreign key columns
- Filter by `user_id` for user-owned resources
- Document all constraints and their business rationale
- Use meaningful, consistent naming conventions
- Consider query patterns when designing indexes

### DON'T
- Store sensitive data in plain text
- Create circular dependencies between tables
- Over-index (balance read/write performance)
- Use generic names like "data" or "info"
- Forget to document relationship cardinality
- Skip constraint definitions
- Design schema without considering queries

## Validation Checklist

Before finalizing schema:
- [ ] All entities have primary keys
- [ ] Foreign keys are properly defined and indexed
- [ ] Required fields marked as NOT NULL
- [ ] Unique constraints on appropriate fields
- [ ] Timestamps included for audit trail
- [ ] User ownership enforced via user_id
- [ ] Indexes align with query patterns
- [ ] SQLModel examples provided
- [ ] Migration path documented
- [ ] Security considerations addressed

## Version History
- **v1.0**: Initial database-designer skill definition for ToDo app
