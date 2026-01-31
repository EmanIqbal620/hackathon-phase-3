<!-- SYNC IMPACT REPORT:
Version change: 2.1.0 → 3.0.0
Modified principles: Completely replaced Core Principles with Phase III principles (Spec-Driven Development, Stateless Architecture, Tool-Centric AI, Deterministic Behavior, Security & Privacy, Production-Readiness)
Added sections: AI & Agent Standards, MCP Standards, Backend Standards, Frontend Standards, API & Data Integrity Rules, Error Handling Principles
Removed sections: UI/UX Principles from Phase II
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
- .specify/templates/commands/*.md ⚠ pending
Follow-up TODOs: Update all templates to align with Phase III constitution principles
-->
# Phase III – AI-Powered Todo Chatbot (MCP-based)

## Purpose of This Constitution

This constitution defines the **non-negotiable rules** governing all specifications, plans, and implementations for this project. Every spec (`spec-1`, `spec-2`, `spec-3`) must comply with this document.

## Core Principles

### 1. Spec-Driven Development (SDD)
- All design, implementation, and validation decisions must strictly follow the approved specifications (specify → plan → tasks → implement)
- No implementation without prior specification
- All changes must be reflected in specs before code modifications

### 2. Stateless-by-Design Architecture
- Backend services (chat endpoint, agent runner, MCP tools) must not retain in-memory state across requests
- All state is persisted in the database
- Services must tolerate restarts without losing functionality

### 3. Tool-Centric AI Control
- The AI agent must never directly modify application state
- All task mutations must occur exclusively through MCP tools
- AI actions must be mediated by well-defined interfaces

### 4. Deterministic & Auditable Behavior
- Every AI action must be traceable to a user message, an agent decision, and a specific MCP tool invocation
- All operations must be reproducible and verifiable
- Logging and audit trails must be comprehensive

### 5. Security & Privacy First
- User data is strictly isolated by user_id
- No API keys, secrets, or credentials are hardcoded
- All secrets are loaded via environment variables
- Authentication and authorization must be enforced server-side

### 6. Production-Readiness
- The system must tolerate restarts, scaling, and failures without losing conversation continuity
- Services must be resilient to transient failures
- Error handling must be graceful and informative

## Key Standards

### AI & Agent Standards
- Agent logic must use an **OpenAI-compatible API** (e.g., OpenRouter)
- Model selection must be configurable via environment variables
- Agents must:
  - Interpret user intent
  - Select the correct MCP tool
  - Confirm actions in natural language
  - Gracefully handle errors

### MCP Standards
- MCP tools must be:
  - Stateless
  - Idempotent where possible
  - Fully documented with input/output schemas
- MCP server must be implemented using the **Official MCP SDK**
- Tools must have clear error reporting and validation

### Backend Standards
- Backend framework: **FastAPI**
- ORM: **SQLModel**
- Database: **Neon Serverless PostgreSQL**
- Authentication: **Better Auth**
- All API endpoints must be properly typed and documented

### Frontend Standards
- Conversational UI built using **OpenAI ChatKit**
- Must support:
  - Streaming or near-real-time responses
  - Conversation continuation
  - Clear action confirmations
- UI must provide feedback for all AI operations

## API & Data Integrity Rules

- All chat requests must be authenticated and associated with a valid user_id
- Conversation history must be persisted before agent execution and reconstructed from the database per request
- Assistant responses must be stored verbatim
- All data operations must be atomic and consistent
- Database transactions must be used for complex operations

## Error Handling Principles

- Errors must never crash the request cycle
- Common errors to handle gracefully:
  - Task not found
  - Invalid task ID
  - Empty task list
  - Ambiguous user intent
  - API connection failures
  - Database connection issues
- The assistant must respond politely and informatively in all failure cases
- All errors must be logged with appropriate severity levels

## Technology Constraints

- Frontend: Next.js 16+ (App Router) with OpenAI ChatKit
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth
- AI Provider: OpenAI-compatible API (configurable via env vars)
- MCP Server: Official MCP SDK
- Spec System: Claude Code + Spec-Kit Plus

No substitutions are allowed unless the constitution is updated.

## Security Standards

- All protected endpoints require a valid JWT
- Missing or invalid tokens return `401 Unauthorized`
- Cross-user access attempts return `403 Forbidden`
- JWT secret must be shared via environment variable only
- No credentials or secrets may be hardcoded
- MCP tools must validate user permissions before executing operations
- Conversation data must be encrypted at rest

## Spec Requirements

Each spec must define:
- Purpose
- Scope (included / excluded)
- API endpoints with methods & status codes
- Authentication & authorization rules
- Data models & validation
- Error handling & edge cases
- MCP tool specifications
- Agent behavior and response patterns
- Conversation persistence requirements
- Constraints
- Success criteria
- Validation checklist

## Constraints

- No in-memory session storage
- No UI-based direct database mutations
- No hardcoded AI provider keys or secrets
- No vendor-specific logic embedded in specs
- No direct database access from frontend
- No stateful agent behavior

## Success Criteria

The chatbot implementation is considered successful if:
- Users can manage todos entirely via natural language
- All task operations are executed through MCP tools
- Conversation context persists across server restarts
- The backend remains stateless
- AI responses are accurate, friendly, and confirm actions
- System passes functional testing for all specified commands
- All security requirements are met

## Governance

This constitution supersedes all other development practices and standards. All team members must comply with these principles. Amendments to this constitution require explicit documentation, approval from project maintainers, and a migration plan for existing code. All pull requests and code reviews must verify compliance with these principles. Complexity must be justified with clear benefits and documented trade-offs. Use this constitution as the primary guidance for development decisions.

**Version**: 3.0.0 | **Ratified**: 2026-01-23 | **Last Amended**: 2026-01-23