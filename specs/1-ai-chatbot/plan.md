# Implementation Plan: AI-Powered Todo Chatbot

**Plan Version**: 1.0
**Feature**: 1-ai-chatbot
**Created**: 2026-01-23
**Status**: Draft

---

## Technical Context

This plan describes how the AI-powered Todo chatbot (Spec 4) will be built while adhering to the Phase III Constitution and Specification. The system will use an agent + MCP (Model Context Protocol) architecture to enable users to manage their todo tasks through natural language.

### Technology Stack

- **Frontend**: Next.js 16+ with OpenAI ChatKit
- **Backend**: Python FastAPI
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (JWT-based)
- **AI Provider**: OpenAI-compatible API (e.g., OpenRouter)
- **MCP Server**: Official MCP SDK
- **ORM**: SQLModel

### Current Unknowns

*Resolved: See research.md for detailed analysis*

---

## Constitution Check

### Compliance Verification

#### Spec-Driven Development (SDD)
- [x] Plan follows the approved specification (specs/1-ai-chatbot/spec.md)
- [x] All design decisions trace back to functional requirements

#### Stateless-by-Design Architecture
- [x] Backend services will not retain in-memory state across requests
- [x] All state persisted in database
- [x] Services will tolerate restarts without losing functionality

#### Tool-Centric AI Control
- [x] AI agent will never directly modify application state
- [x] All task mutations will occur exclusively through MCP tools
- [x] AI actions will be mediated by well-defined interfaces

#### Deterministic & Auditable Behavior
- [x] Every AI action will be traceable to user messages
- [x] All operations will be reproducible and verifiable
- [x] Logging and audit trails will be comprehensive

#### Security & Privacy First
- [x] User data will be strictly isolated by user_id
- [x] No API keys/secrets hardcoded in code
- [x] Secrets loaded via environment variables
- [x] Authentication and authorization enforced server-side

#### Production-Readiness
- [x] System will tolerate restarts, scaling, and failures
- [x] Conversation continuity maintained across failures
- [x] Services resilient to transient failures

### Gate Status: PASS

All constitutional requirements satisfied.

---

## Phase 0: Research & Unknown Resolution

### Completed Research Tasks

1. **MCP SDK Configuration**: Researched the Official MCP SDK requirements and configuration
2. **AI Agent Setup**: Investigated best practices for configuring the OpenAI-compatible agent with MCP tools
3. **Provider Selection**: Compared OpenAI-compatible providers (OpenRouter, etc.) for cost/performance
4. **Data Model Design**: Defined database schemas for conversations and messages
5. **Authentication Integration**: Planned how Better Auth integrates with the chat endpoint

### Delivered Artifacts

- `research.md`: Resolved all unknowns and documented decisions
- `data-model.md`: Database schema definitions
- `contracts/`: API contract definitions
- `quickstart.md`: Deployment and setup guide

---

## Phase 1: Architecture & Design

### Component Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend  │───▶│    Backend   │───▶│    MCP       │
│   (Nextjs) │    │   (FastAPI)  │    │   (SDK)      │
└─────────────┘    └──────────────┘    └──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │  Database    │
                │ (PostgreSQL) │
                └──────────────┘
```

### Request Flow

For each `POST /api/{user_id}/chat` request:

1. **Authentication**: Verify JWT token with Better Auth
2. **Authorization**: Validate user_id matches token subject
3. **Context Reconstruction**: Fetch conversation history from DB
4. **Message Persistence**: Store incoming user message
5. **Agent Execution**: Run AI agent with MCP tools enabled
6. **Tool Invocation**: Agent selects and invokes appropriate MCP tool
7. **Data Operation**: MCP tool performs database operation
8. **Response Storage**: Store assistant response in DB
9. **Return Response**: Send response to client with metadata

### Database Schema

**Conversations Table**:
- id (UUID)
- user_id (foreign key to users)
- created_at (timestamp)
- updated_at (timestamp)

**Messages Table**:
- id (UUID)
- conversation_id (foreign key to conversations)
- user_id (foreign key to users)
- role ('user' or 'assistant')
- content (text)
- created_at (timestamp)

**Tasks Table** (existing from Phase II):
- id (UUID)
- user_id (foreign key to users)
- title (text)
- description (text)
- completed (boolean)
- created_at (timestamp)
- updated_at (timestamp)

---

## Phase 2: Implementation Strategy

### Phase 2A: Foundation Layer

1. **Database Models**: Create SQLModel classes for Conversation and Message
2. **Environment Setup**: Configure environment variables for AI provider
3. **MCP Server Skeleton**: Initialize MCP server with basic configuration
4. **Dependency Installation**: Install required packages (fastapi, sqlmodel, better-auth, mcp-sdk)

### Phase 2B: MCP Tool Layer

1. **Tool Definitions**: Implement MCP tools for task operations
2. **Validation**: Add input/output validation schemas
3. **User Isolation**: Ensure all tools enforce user_id ownership
4. **Error Handling**: Implement proper error responses

### Phase 2C: Agent Integration

1. **Agent Initialization**: Set up OpenAI-compatible agent
2. **Tool Registration**: Register MCP tools with the agent
3. **System Prompt**: Define agent behavior and constraints
4. **Testing**: Verify agent correctly invokes tools

### Phase 2D: API Endpoints

1. **Chat Endpoint**: Implement POST /api/{user_id}/chat
2. **Authentication**: Integrate Better Auth verification
3. **Context Management**: Implement conversation reconstruction
4. **Response Handling**: Format and return agent responses

### Phase 2E: Frontend Integration

1. **Chat Interface**: Implement OpenAI ChatKit UI
2. **Conversation State**: Manage conversation context
3. **Loading States**: Show typing indicators during agent processing
4. **Error Handling**: Handle API errors gracefully

---

## Validation Strategy

### Functional Validation

- [ ] Natural language commands correctly map to MCP tool invocations
- [ ] Task CRUD operations via chat match UI behavior
- [ ] Conversation history persists across server restarts
- [ ] User data isolation enforced for all operations

### Security Validation

- [ ] Unauthenticated requests return 401
- [ ] Cross-user access attempts return 403
- [ ] Agent cannot bypass MCP tools for direct database access
- [ ] JWT tokens properly validated for each request

### Performance Validation

- [ ] Response times under 5 seconds for 95% of requests
- [ ] Proper handling of concurrent users
- [ ] Efficient database queries for conversation history
- [ ] Rate limiting implemented as needed

### Statelessness Validation

- [ ] No in-memory session state retained
- [ ] Service restarts don't lose conversation context
- [ ] All state retrieved from database per request
- [ ] Horizontal scaling supported without session affinity

---

## Risk Analysis

### High-Risk Areas

1. **AI Provider Reliability**: Potential downtime or rate limits
2. **MCP Integration Complexity**: Learning curve for MCP SDK
3. **Performance Under Load**: AI processing may be slow
4. **Data Consistency**: Ensuring conversation integrity

### Mitigation Strategies

1. **Fallback Mechanisms**: Implement graceful degradation
2. **Thorough Testing**: Extensive integration testing
3. **Caching Strategies**: Cache frequently accessed data
4. **Monitoring**: Implement comprehensive logging and metrics

---

## Next Steps

1. Complete Phase 0 research to resolve all unknowns
2. Begin Phase 1 architecture implementation
3. Set up development environment with required dependencies
4. Create database migrations and models