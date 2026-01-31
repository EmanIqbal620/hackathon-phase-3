---
id: 1
title: "Create AI chatbot implementation plan"
stage: plan
date_iso: "2026-01-23"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "ai-chatbot"
branch: "1-ai-chatbot"
user: "user"
command: "/sp.plan"
labels: ["plan", "ai", "chatbot", "mcp", "architecture"]
spec: "specs/1-ai-chatbot/spec.md"
ticket: null
adr: null
pr: null
files_yaml:
  - "specs/1-ai-chatbot/plan.md"
  - "specs/1-ai-chatbot/research.md"
  - "specs/1-ai-chatbot/data-model.md"
  - "specs/1-ai-chatbot/contracts/chat-api.yaml"
  - "specs/1-ai-chatbot/quickstart.md"
tests_yaml: []
prompt_text: |
  # /sp.plan.md

  ## Phase III – Spec 4 Plan: AI-Powered Todo Chatbot

  ---

  ## Purpose of This Plan

  This plan describes **how** the AI-powered Todo chatbot (Spec 4) will be built while strictly adhering to the Phase III Constitution and Specification. It defines the architecture, implementation phases, key design decisions, and validation strategy.

  This plan is intentionally **implementation-agnostic** and focuses on structure, flow, and correctness rather than code details.

  ---

  ## High-Level Architecture

  ### System Components

  1. **Frontend (Chat UI)**

     * OpenAI ChatKit-based conversational interface
     * Authenticated via Better Auth
     * Sends user messages to backend chat endpoint

  2. **Backend (FastAPI)**

     * Stateless chat API endpoint
     * Orchestrates conversation lifecycle
     * Integrates AI agent and MCP server

  3. **AI Agent Layer**

     * Built using OpenAI Agents SDK
     * Interprets user intent
     * Selects and invokes MCP tools

  4. **MCP Server**

     * Implemented with Official MCP SDK
     * Exposes task operations as tools
     * Stateless, database-backed

  5. **Database (Neon PostgreSQL)**

     * Stores tasks, conversations, and messages
     * Single source of truth for state

  ---

  ## Request Lifecycle (Stateless Flow)

  For every `POST /api/{user_id}/chat` request:

  1. Authenticate request using JWT (Better Auth)
  2. Validate `user_id` matches token subject
  3. Fetch conversation history from database (if conversation_id exists)
  4. Persist incoming user message
  5. Construct message array for agent (history + new input)
  6. Run AI agent with MCP tools enabled
  7. Agent invokes one or more MCP tools
  8. MCP tools perform database operations
  9. Persist assistant response
  10. Return response + tool usage metadata to client

  > No in-memory session state is retained at any point.

  ---

  ## Implementation Phases

  ### Phase 1: Foundation

  * Define database models for `Conversation` and `Message`
  * Create database migration scripts
  * Prepare environment variable configuration
  * Set up MCP server skeleton

  ### Phase 2: MCP Tool Layer

  * Implement MCP tools:

    * add_task
    * list_tasks
    * update_task
    * complete_task
    * delete_task
  * Enforce user ownership in all tools
  * Validate input/output schemas

  ### Phase 3: Agent Layer

  * Initialize OpenAI-compatible agent (via OpenRouter or similar)
  * Register MCP tools with agent
  * Define agent system prompt and behavior rules
  * Ensure agent cannot bypass MCP tools

  ### Phase 4: Chat Endpoint

  * Implement `POST /api/{user_id}/chat`
  * Integrate authentication and authorization
  * Reconstruct conversation context per request
  * Execute agent and handle responses

  ### Phase 5: Frontend Integration

  * Build ChatKit-based UI
  * Handle conversation creation and continuation
  * Display assistant responses and confirmations
  * Show loading and error states

  ---

  ## Key Design Decisions & Tradeoffs

  ### 1. Stateless Backend vs In-Memory Sessions

  * **Chosen:** Stateless backend
  * **Reason:** Scalability, fault tolerance, MCP compliance
  * **Tradeoff:** Slightly higher database reads per request

  ### 2. MCP Tools vs Direct ORM Access by Agent

  * **Chosen:** MCP tools only
  * **Reason:** Security, auditability, deterministic behavior
  * **Tradeoff:** Additional abstraction layer

  ### 3. OpenAI-Compatible API (OpenRouter)

  * **Chosen:** Provider-agnostic OpenAI-compatible API
  * **Reason:** Cost efficiency, flexibility, free-tier support
  * **Tradeoff:** Slight differences in model behavior

  ---

  ## Configuration & Secrets Management

  * All secrets loaded via environment variables
  * No API keys stored in code or specs
  * Example variables:

    * `OPENAI_API_KEY`
    * `OPENAI_BASE_URL`
    * `OPENAI_MODEL`

  ---

  ## Testing & Validation Strategy

  ### Functional Validation

  * Verify all natural language commands map to correct MCP tools
  * Validate task CRUD via chat matches UI behavior
  * Confirm conversation persistence across restarts

  ### Security Validation

  * Requests without JWT return 401
  * Cross-user task access is blocked
  * Agent cannot mutate data without MCP tools

  ### Statelessness Validatio
response_text: |
  Created comprehensive implementation plan for the AI-Powered Todo Chatbot feature. The plan includes:
  - Technical context with technology stack and unknowns resolution
  - Constitution compliance verification with all requirements satisfied
  - Detailed research document resolving all unknowns
  - Complete data model for conversations and messages
  - API contracts for the chat functionality
  - Quickstart guide for development and deployment
  - Implementation phases from foundation to frontend integration
  The plan ensures stateless architecture, MCP compliance, and user data isolation as required by the Phase III constitution.
outcome: "Successfully created implementation plan with all supporting documents for AI chatbot feature"
evaluation: "Plan comprehensively covers all required aspects, maintains constitutional compliance, includes all deliverables, and provides clear implementation roadmap"
---

# Prompt History Record

## Summary

Created comprehensive implementation plan for the AI-Powered Todo Chatbot feature with all supporting documentation.

## Details

- **Date**: 2026-01-23
- **Stage**: plan
- **Action**: Complete implementation planning
- **Files Created**:
  - specs/1-ai-chatbot/plan.md
  - specs/1-ai-chatbot/research.md
  - specs/1-ai-chatbot/data-model.md
  - specs/1-ai-chatbot/contracts/chat-api.yaml
  - specs/1-ai-chatbot/quickstart.md

## Key Deliverables

- Complete implementation plan with constitutional compliance
- Research document resolving all unknowns
- Data model for conversations and messages
- API contracts for chat functionality
- Development and deployment quickstart guide