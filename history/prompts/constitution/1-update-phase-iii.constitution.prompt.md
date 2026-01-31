---
id: 1
title: "Update constitution to Phase III AI-Powered Todo Chatbot"
stage: constitution
date_iso: "2026-01-23"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "006-ui-polish-theme"
user: "user"
command: "/sp.constitution"
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp"]
spec: null
ticket: null
adr: null
pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml: []
prompt_text: |
   # /sp.constitution.md

   ## Project

   **Phase III: AI-Powered Todo Chatbot (MCP-based)**

   An AI-native conversational interface that allows authenticated users to manage their todos via natural language, using a stateless server architecture, OpenAI-compatible agents, and MCP (Model Context Protocol) tools.

   ---

   ## Core Principles

   1. **Spec-Driven Development (SDD)**
      All design, implementation, and validation decisions must strictly follow the approved specifications (specify → plan → tasks → implement).

   2. **Stateless-by-Design Architecture**
      Backend services (chat endpoint, agent runner, MCP tools) must not retain in-memory state across requests. All state is persisted in the database.

   3. **Tool-Centric AI Control**
      The AI agent must never directly modify application state. All task mutations must occur exclusively through MCP tools.

   4. **Deterministic & Auditable Behavior**
      Every AI action must be traceable to:

      * A user message
      * An agent decision
      * A specific MCP tool invocation

   5. **Security & Privacy First**

      * User data is strictly isolated by user_id
      * No API keys, secrets, or credentials are hardcoded
      * All secrets are loaded via environment variables

   6. **Production-Readiness**
      The system must tolerate restarts, scaling, and failures without losing conversation continuity.

   ---

   ## Key Standards

   ### AI & Agent Standards

   * Agent logic must use an **OpenAI-compatible API** (e.g., OpenRouter)
   * Model selection must be configurable via environment variables
   * Agents must:

     * Interpret user intent
     * Select the correct MCP tool
     * Confirm actions in natural language
     * Gracefully handle errors

   ### MCP Standards

   * MCP tools must be:

     * Stateless
     * Idempotent where possible
     * Fully documented with input/output schemas
   * MCP server must be implemented using the **Official MCP SDK**

   ### Backend Standards

   * Backend framework: **FastAPI**
   * ORM: **SQLModel**
   * Database: **Neon Serverless PostgreSQL**
   * Authentication: **Better Auth**

   ### Frontend Standards

   * Conversational UI built using **OpenAI ChatKit**
   * Must support:

     * Streaming or near-real-time responses
     * Conversation continuation
     * Clear action confirmations

   ---

   ## API & Data Integrity Rules

   * All chat requests must:

     * Be authenticated
     * Be associated with a valid user_id
   * Conversation history must be:

     * Persisted before agent execution
     * Reconstructed from the database per request
   * Assistant responses must be stored verbatim

   ---

   ## Error Handling Principles

   * Errors must never crash the request cycle
   * Common errors to handle gracefully:

     * Task not found
     * Invalid task ID
     * Empty task list
     * Ambiguous user intent
   * The assistant must respond politely and informatively in all failure cases

   ---

   ## Constraints

   * No in-memory session storage
   * No UI-based direct database mutations
   * No hardcoded AI provider keys or secrets
   * No vendor-specific logic embedded in specs

   ---

   ## Success Criteria

   The chatbot implementation is considered successful if:

   * Users can manage todos entirely via natural language
   * All task operations are executed through MCP tools
   * Conversation context persists across server restarts
   * The backend remains stateless
   * AI responses are accurate, friendly, and confirm actions
   * System passes functional testing for all specified commands

   ---

   ## Non-Goals (Explicitly Out of Scope)

   * Ethical or philosophical discussion of AI
   * Multi-agent collaboration
   * Voice-based interaction
   * UI-heavy visual chatbot customizations

   ---

   ## Compliance Check (Required Before Next Spec)

   Before proceeding to the next phase, verify:

   * [ ] No secrets in code or specs
   * [ ] All state stored in database
   * [ ] MCP tools fully defined
   * [ ] Agent behavior fully specified
   * [ ] Stateless request cycle validated

   ---

   **This constitution governs all Phase III chatbot specifications, plans, tasks, and implementations.**
response_text: |
   Updated the project constitution to reflect Phase III AI-Powered Todo Chatbot specifications, moving from Phase II web application to an MCP-based AI chatbot system. The new constitution establishes core principles around Spec-Driven Development, Stateless Architecture, Tool-Centric AI Control, Deterministic Behavior, Security & Privacy, and Production-Readiness. Technology stack now includes MCP SDK, OpenAI-compatible API, and OpenAI ChatKit for the frontend conversational interface.
outcome: "Successfully updated constitution from version 2.1.0 to 3.0.0, replacing UI/UX-focused principles with AI/MCP-focused principles for Phase III development"
evaluation: "Constitution properly updated with new Phase III requirements, maintaining compliance with project standards and governance procedures"
---

# Prompt History Record

## Summary

Updated the project constitution to reflect Phase III AI-Powered Todo Chatbot specifications, moving from Phase II web application to an MCP-based AI chatbot system.

## Details

- **Date**: 2026-01-23
- **Stage**: constitution
- **Action**: Major version update (2.1.0 → 3.0.0)
- **Files Modified**: .specify/memory/constitution.md

## Changes Made

Replaced Phase II UI/UX-focused principles with Phase III AI/MCP-focused principles including:
- Spec-Driven Development (SDD)
- Stateless-by-Design Architecture
- Tool-Centric AI Control
- Deterministic & Auditable Behavior
- Security & Privacy First
- Production-Readiness

## Compliance Verification

- [x] No remaining unexplained bracket tokens
- [x] Version line matches report
- [x] Dates in ISO format YYYY-MM-DD
- [x] Principles are declarative, testable, and free of vague language
- [x] Updated technology stack to include MCP SDK, OpenAI-compatible API, and OpenAI ChatKit