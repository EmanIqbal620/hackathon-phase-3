---
id: 1
title: Update Constitution
stage: constitution
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: claude
command: sp.constitution
labels: ["constitution", "governance", "policy"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```text
# constitution.md

## Project
Phase II – Spec-Driven Full-Stack Todo Web Application
(Hackathon II)

---

## Purpose of This Constitution

This constitution defines the **non-negotiable rules** governing all specifications, plans, and implementations for this project.
Every spec (`spec-1`, `spec-2`, `spec-3`) must comply with this document.

---

## Core Principles

### 1. Accuracy
- All technical claims must be implementable and verifiable
- No speculative or vague behavior in specs
- Security-related behavior must follow industry standards (JWT, REST, HTTP)

### 2. Clarity
- Specs must be readable by a computer science student
- No ambiguous requirements
- Clear separation between frontend, backend, and database responsibilities

### 3. Reproducibility
- Any developer should be able to reproduce the system using the specs
- Environment variables, secrets, and dependencies must be explicitly defined
- No hidden assumptions

### 4. Rigor
- Security enforcement must happen server-side
- Authentication and authorization must not rely on frontend trust
- Each spec must be internally consistent and testable

---

## Key Standards

- All API behavior must be explicitly defined
- Authentication must be stateless using JWT
- Authorization must be enforced on every request
- User data isolation is mandatory
- Specs must precede implementation (spec-driven development)

---

## Technology Constraints

- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth
- Spec System: Claude Code + Spec-Kit Plus

No substitutions are allowed unless the constitution is updated.

---

## Security Standards

- All protected endpoints require a valid JWT
- Missing or invalid tokens return `401 Unauthorized`
- Cross-user access attempts return `403 Forbidden`
- JWT secret must be shared via environment variable only
- No credentials or secrets may be hardcoded

---

## Spec Requirements

Each spec must define:
- Purpose
- Scope (included / excl
```

## Response snapshot

The constitution file already exists at `.specify/memory/constitution.md` with the content matching the user's input. The file contains:

- A clear purpose statement defining it as the governing document for specifications, plans, and implementations
- Four core principles: Accuracy, Clarity, Reproducibility, and Rigor
- Key Standards for API behavior, authentication, and authorization
- Technology constraints specifying Next.js, FastAPI, SQLModel, PostgreSQL, and Better Auth
- Security standards for JWT-based authentication
- Requirements for specifications

The existing constitution is well-structured and already aligned with the user's input. I've verified that template files exist in `.specify/templates/` and checked that the constitution follows the required format with proper headings and structure.

## Outcome

- ✅ Impact: Verified existing constitution alignment with user requirements
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: None required
- 🧠 Reflection: Constitution already properly configured according to user's specifications

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A