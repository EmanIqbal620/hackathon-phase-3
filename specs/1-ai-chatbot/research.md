# Research Document: AI-Powered Todo Chatbot

**Created**: 2026-01-23
**Feature**: 1-ai-chatbot
**Status**: Complete

---

## MCP SDK Configuration

### Decision: Use Official Model Context Protocol (MCP) SDK
- **Package**: `mcp`
- **Installation**: `pip install mcp`
- **Configuration**: Standard setup with tool registration

### Rationale
The Official MCP SDK provides the necessary framework for creating stateless tools that the AI agent can use to perform operations. This ensures compliance with the constitution's requirement that the agent never directly modifies application state.

### Alternatives Considered
- Custom tool implementation: Would require more development time and risk of non-compliance
- Direct API calls: Would violate the tool-centric AI control principle

---

## AI Agent Setup

### Decision: Use OpenAI-Compatible Agent with MCP Tools
- **Framework**: OpenAI-compatible API (via OpenRouter)
- **Configuration**: Agent with tools attached via MCP protocol
- **System Prompt**: Designed to enforce tool usage and maintain conversational context

### Rationale
This approach provides a clear separation between AI reasoning and data manipulation, ensuring all operations go through the proper MCP tools. It also provides flexibility in choosing AI providers.

### Alternatives Considered
- Direct database access by agent: Would violate tool-centric control principle
- Pre-built agents without customization: May not enforce proper tool usage

---

## Provider Selection Analysis

### Decision: OpenRouter as Primary Provider
- **Cost**: Free tier available with reasonable usage limits
- **Compatibility**: OpenAI-compatible API
- **Models**: Access to various models including GPT-4 and alternatives
- **Reliability**: Good uptime record

### Rationale
OpenRouter provides a cost-effective way to implement the AI functionality while maintaining compatibility with the OpenAI ecosystem. It offers flexibility in model selection and has good reliability.

### Alternatives Considered
- OpenAI API: Higher costs, especially for prototype/hackathon
- Self-hosted models: Higher complexity and resource requirements
- Other cloud providers: Limited OpenAI compatibility

---

## Data Model Design

### Decision: Extend Existing Database Schema
- **Conversations Table**: New table for chat context
- **Messages Table**: New table for storing conversation history
- **Integration**: Leverage existing user authentication and task models

### Rationale
Building on the existing Phase II database schema maintains consistency and leverages the established authentication and task management systems. This reduces implementation complexity and ensures data integrity.

### Schema Details
```
Conversations:
- id (UUID, primary key)
- user_id (UUID, foreign key to users)
- created_at (timestamp with timezone)
- updated_at (timestamp with timezone)

Messages:
- id (UUID, primary key)
- conversation_id (UUID, foreign key to conversations)
- user_id (UUID, foreign key to users)
- role (enum: 'user' or 'assistant')
- content (text)
- created_at (timestamp with timezone)
```

---

## Authentication Integration

### Decision: Leverage Existing Better Auth Infrastructure
- **JWT Token Validation**: Use existing middleware
- **User ID Verification**: Match token subject with request parameters
- **Authorization**: Ensure user can only access their own data

### Rationale
Using the existing authentication system maintains consistency with Phase II and reduces development time while ensuring security standards are met.

### Implementation Approach
1. Extract user_id from JWT token
2. Validate against the user_id in the request path
3. Filter all database queries by user_id to prevent cross-user access

---

## MCP Tool Specifications

### Decision: Five Core Task Operations as MCP Tools

**add_task**
- Input: task_title (string), task_description (optional string)
- Output: task_id (UUID), success message
- Validation: Ensure required fields present

**list_tasks**
- Input: status_filter (optional string: 'all', 'pending', 'completed')
- Output: array of task objects with id, title, completed status
- Validation: Ensure valid filter values

**update_task**
- Input: task_id (UUID), new_title (optional string), new_description (optional string)
- Output: success message
- Validation: Task exists and belongs to user

**complete_task**
- Input: task_id (UUID)
- Output: success message
- Validation: Task exists and belongs to user

**delete_task**
- Input: task_id (UUID)
- Output: success message
- Validation: Task exists and belongs to user

### Rationale
These five operations cover all the basic task management functions required by the specification while maintaining clear separation between AI reasoning and data operations.

---

## Error Handling Strategy

### Decision: Comprehensive Error Handling at Multiple Levels
- **API Level**: HTTP status codes (401, 403, 404, 500)
- **MCP Tool Level**: Structured error responses
- **AI Agent Level**: Friendly error messages to users
- **Database Level**: Transaction rollback on failures

### Rationale
Multi-level error handling ensures that problems are caught and communicated appropriately at each layer, providing both technical diagnostics and user-friendly messages.

---

## Performance Considerations

### Decision: Stateless but Optimized Architecture
- **Database Queries**: Indexed access patterns for conversations
- **Caching**: Consider Redis for frequently accessed data
- **Rate Limiting**: Implement per-user rate limiting
- **Timeouts**: Configurable timeouts for AI provider calls

### Rationale
While maintaining stateless architecture as required by the constitution, implementing performance optimizations ensures acceptable user experience.