---
description: "Task list template for feature implementation"
---

# Tasks: Task API & Database Layer

**Input**: Design documents from `/specs/002-task-api-db/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume web app structure - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan with backend/ and frontend/ directories
- [ ] T002 Initialize Python project in backend/ with FastAPI and SQLModel dependencies
- [ ] T003 [P] Set up database connection configuration in backend/src/database.py
- [ ] T004 [P] Configure environment variables for database connection

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [X] T005 Create Task SQLModel definition in backend/src/models/task.py
- [ ] T006 [P] Implement task service functions in backend/src/services/task_service.py
- [X] T007 [P] Set up JWT validation dependency for task endpoints in backend/src/dependencies/auth.py
- [X] T008 Create Pydantic models for task requests/responses in backend/src/models/task.py
- [X] T009 Configure error handling for task operations in backend/src/exceptions/task.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create tasks and view only their own tasks after authenticating to the system. The user should be able to see a list of their tasks when they access the application.

**Independent Test**: Can be fully tested by creating tasks for one user and verifying they can only see their own tasks, delivering the fundamental ability for users to manage their personal todo lists.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for GET /api/tasks in tests/contract/test_tasks.py
- [ ] T011 [P] [US1] Contract test for POST /api/tasks in tests/contract/test_tasks.py
- [ ] T012 [P] [US1] Integration test for task creation and retrieval flow in tests/integration/test_tasks.py

### Implementation for User Story 1

- [X] T013 [P] [US1] Create tasks router in backend/src/api/routes/tasks.py
- [X] T014 [US1] Implement GET /api/tasks endpoint in backend/src/api/routes/tasks.py
- [X] T015 [US1] Implement POST /api/tasks endpoint in backend/src/api/routes/tasks.py
- [X] T016 [US1] Add validation and error handling for task endpoints
- [X] T017 [US1] Add logging for task operations
- [X] T018 [US1] Create task repository functions for database operations in backend/src/services/task_service.py
- [X] T019 [US1] Implement user ID filtering in task queries to enforce data isolation

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Manage Task State (Priority: P2)

**Goal**: Allow authenticated users to update their tasks, including marking them as completed or editing their content, while ensuring they cannot modify tasks belonging to other users.

**Independent Test**: Can be fully tested by creating tasks for a user, updating them (completing or modifying), and verifying the changes persist correctly while preventing unauthorized access to other users' tasks.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T020 [P] [US2] Contract test for PUT /api/tasks/{task_id} in tests/contract/test_tasks.py
- [ ] T021 [P] [US2] Contract test for PATCH /api/tasks/{task_id}/toggle in tests/contract/test_tasks.py
- [ ] T022 [P] [US2] Integration test for cross-user access prevention in tests/integration/test_authz.py

### Implementation for User Story 2

- [X] T023 [P] [US2] Implement PUT /api/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py
- [X] T024 [US2] Implement PATCH /api/tasks/{task_id}/toggle endpoint in backend/src/api/routes/tasks.py
- [X] T025 [US2] Add task ownership validation middleware to protect update endpoints
- [X] T026 [US2] Implement cross-user access prevention logic
- [X] T027 [US2] Add authorization error handling and 403 responses
- [X] T028 [US2] Update task repository functions to include ownership verification

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Delete Personal Tasks (Priority: P3)

**Goal**: Allow authenticated users to delete their own tasks while being prevented from deleting tasks that belong to other users.

**Independent Test**: Can be fully tested by creating tasks for a user, deleting them, and verifying they're removed while ensuring users cannot delete tasks they don't own.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T029 [P] [US3] Contract test for DELETE /api/tasks/{task_id} in tests/contract/test_tasks.py
- [ ] T030 [P] [US3] Integration test for secure deletion in tests/integration/test_authz.py

### Implementation for User Story 3

- [X] T031 [P] [US3] Implement DELETE /api/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py
- [X] T032 [US3] Add deletion authorization validation to prevent cross-user deletion
- [X] T033 [US3] Update task repository functions to include delete operations
- [ ] T034 [US3] Add soft-delete capability if needed in backend/src/models/task.py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T035 [P] Documentation updates in docs/
- [ ] T036 Code cleanup and refactoring
- [ ] T037 Performance optimization across all stories
- [X] T038 [P] Additional unit tests (if requested) in tests/unit/
- [ ] T039 Security hardening
- [ ] T040 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for GET /api/tasks in tests/contract/test_tasks.py"
Task: "Contract test for POST /api/tasks in tests/contract/test_tasks.py"

# Launch all models for User Story 1 together:
Task: "Create tasks router in backend/src/api/routes/tasks.py"
Task: "Create task repository functions for database operations in backend/src/services/task_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence