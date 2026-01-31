# System Architect Skill

## Overview
Defines coding rules, project structure, monorepo layout, and enforces Spec 0 Constitution rules.

## Description
The System Architect skill is responsible for establishing and maintaining the foundational architecture standards for Spec-Driven Development projects. It ensures consistency in project structure, coding standards, and architectural principles across the entire codebase.

## Components

### 1. Generate Spec 0 – Constitution file
- **Location**: `/specs/constitution.md`
- **Purpose**: Defines core principles, coding standards, security policies, and project-wide architectural guidelines
- **Content includes**:
  - Code quality standards
  - Testing requirements
  - Performance guidelines
  - Security principles
  - Architecture patterns

### 2. Generate Spec 1 – Project Structure file
- **Location**: `/specs/spec-1-project-structure.md`
- **Purpose**: Documents the complete project structure, monorepo layout, and folder organization
- **Content includes**:
  - Directory structure and naming conventions
  - Monorepo organization (if applicable)
  - Module boundaries and dependencies
  - Configuration file locations
  - Build and deployment structure

### 3. Enforce Standards
The skill actively enforces:
- **Coding Standards**: Style guides, naming conventions, code organization
- **Security Standards**: Authentication patterns, authorization rules, data protection
- **REST Standards**: API design principles, endpoint naming, HTTP methods, status codes
- **Folder Standards**: File organization, module structure, separation of concerns

## Reusability
**Yes** - This skill can be reused across all Spec-Driven Development projects to establish consistent architectural foundations.

## Usage

### Called By
- Main Agent (for project initialization and architecture review)
- Sub-Agents (for validation and standards enforcement)

### When to Invoke
1. **Project Initialization**: Setting up a new project or feature
2. **Architecture Review**: Validating compliance with established standards
3. **Refactoring**: Ensuring structural changes align with architecture principles
4. **Onboarding**: Providing architecture documentation to new team members

### Example Invocations
```bash
# Initialize project architecture
/system-architect init

# Generate or update constitution
/system-architect constitution

# Generate or update project structure spec
/system-architect structure

# Validate current project against standards
/system-architect validate

# Review specific aspect
/system-architect review --aspect security
```

## Outputs

### Primary Artifacts
1. `/specs/constitution.md` - Project constitution and principles
2. `/specs/spec-1-project-structure.md` - Project structure documentation

### Secondary Outputs
- Architecture validation reports
- Standards compliance checks
- Recommendation for improvements
- ADR suggestions for architectural decisions

## Integration with SDD Workflow

This skill integrates with the Spec-Driven Development workflow:
1. **Before Planning**: Establishes architectural constraints and standards
2. **During Planning**: Validates architectural decisions against constitution
3. **During Implementation**: Ensures code follows established patterns
4. **During Review**: Checks compliance with architectural principles

## Responsibilities

### What This Skill Does
✅ Define and document architectural standards
✅ Generate constitution and structure specifications
✅ Validate compliance with established patterns
✅ Suggest architectural improvements
✅ Enforce coding, security, and API standards

### What This Skill Does NOT Do
❌ Implement features or write application code
❌ Execute tests or deployments
❌ Make business decisions
❌ Override explicit user requirements

## Standards Enforced

### Coding Standards
- Language-specific style guides
- Naming conventions (variables, functions, classes, files)
- Code organization and module structure
- Documentation requirements
- Error handling patterns

### Security Standards
- Authentication and authorization patterns
- Secret management
- Data validation and sanitization
- API security (CORS, rate limiting, etc.)
- Dependency security

### REST API Standards
- Endpoint naming conventions
- HTTP method usage
- Status code patterns
- Request/response formats
- Versioning strategy
- Error response structure

### Folder Standards
- Directory naming conventions
- Module organization
- Separation of concerns
- Configuration management
- Test file locations
- Documentation structure

## Version History
- **v1.0**: Initial system-architect skill definition
