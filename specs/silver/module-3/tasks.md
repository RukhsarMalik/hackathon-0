# Tasks: Silver Module 3 — Plan Generation + Integration

**Input**: Design documents from `specs/silver/module-3/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## User Stories (from spec.md)

- **US1**: Plan Generation — Priority P1
- **US2**: Silver Integration — Priority P2
- **US3**: Documentation — Priority P3
- **US4**: Demo Video — Priority P4

---

## Phase 1: Setup

**Purpose**: New skill file, orchestrator mapping

- [X] T001 Create `silver/AI_Employee_Vault/Needs_Action/SKILL_PlanGenerator.md` with instructions for analyzing complex tasks, creating PLAN_*.md files with checkboxes, executing steps sequentially, updating checkboxes on completion, updating Dashboard, and moving completed plans to Done/
- [X] T002 Update `silver/orchestrator.py` SKILL_MAP to add mapping: `'complex_task': 'SKILL_PlanGenerator.md'`
- [X] T003 Update `silver/orchestrator.py` SKILL_PATTERNS set to include `'SKILL_PlanGenerator.md'`
- [X] T004 Update `silver/orchestrator.py` `get_actionable_files()` to skip files starting with `PLAN_` (they are generated plans, not new tasks)

**Checkpoint**: Orchestrator routes complex_task type to SKILL_PlanGenerator, skips PLAN_* files

---

## Phase 2: User Story 1 — Plan Generation (Priority: P1) MVP

**Goal**: Complex tasks (type: complex_task) trigger plan creation with checkbox tracking and sequential execution

**Independent Test**: Create a TEST_ComplexTask.md with `type: complex_task` in Needs_Action/, verify orchestrator invokes SKILL_PlanGenerator, plan file created with checkboxes

### Implementation for User Story 1

- [X] T005 [US1] Define plan file YAML frontmatter format in `silver/AI_Employee_Vault/Needs_Action/SKILL_PlanGenerator.md`: type: plan, source_task, created, status, total_steps, completed_steps
- [X] T006 [US1] Add step breakdown instructions to `silver/AI_Employee_Vault/Needs_Action/SKILL_PlanGenerator.md`: analyze task description, identify 3+ discrete steps, create numbered checkbox list
- [X] T007 [US1] Add execution tracking instructions to `silver/AI_Employee_Vault/Needs_Action/SKILL_PlanGenerator.md`: execute each step, update checkbox [ ] → [X], append progress log entry with timestamp
- [X] T008 [US1] Add completion handling instructions to `silver/AI_Employee_Vault/Needs_Action/SKILL_PlanGenerator.md`: update status to completed, update Dashboard with plan summary, move plan and source task to Done/
- [X] T009 [US1] Add error handling instructions to `silver/AI_Employee_Vault/Needs_Action/SKILL_PlanGenerator.md`: log step failures, set status to failed if unrecoverable, flag for human review
- [X] T010 [US1] Create test file `silver/AI_Employee_Vault/Needs_Action/TEST_ComplexTask.md` with type: complex_task frontmatter and multi-step requirements to verify plan generation workflow

**Checkpoint**: Complex task triggers plan generation, steps tracked with checkboxes, plan moves to Done/ on completion

---

## Phase 3: User Story 2 — Silver Integration (Priority: P2)

**Goal**: All Silver components work together end-to-end: watchers, orchestrator, MCP, approvals, plan generation

**Independent Test**: Start all services, send test email, verify full processing chain from detection to completion

### Implementation for User Story 2

- [X] T011 [US2] Verify `silver/start_all.sh` launches all 6 services (gmail, filesystem, linkedin, orchestrator, approval, mcp_email) and all PID files are created in `.pids/`
- [X] T012 [US2] Verify `silver/health_check.py` reports accurate status for all 6 services when running
- [X] T013 [US2] Run end-to-end email workflow test per `specs/silver/module-3/quickstart.md` Test 2: send email → watcher detects → orchestrator processes → verify Dashboard updated
- [X] T014 [US2] Run end-to-end plan generation test per `specs/silver/module-3/quickstart.md` Test 1: create complex task → verify plan created → steps executed → Dashboard updated

**Checkpoint**: All services start, communicate, and process tasks end-to-end

---

## Phase 4: User Story 3 — Documentation (Priority: P3)

**Goal**: Complete documentation enabling independent setup and operation

**Independent Test**: Follow README from scratch to verify a new user can set up and run the system

### Implementation for User Story 3

- [X] T015 [P] [US3] Update `silver/README.md` to add Plan Generation section documenting SKILL_PlanGenerator, complex_task type, PLAN_* file format, and plan execution workflow
- [X] T016 [P] [US3] Update `silver/README.md` troubleshooting table to add entries for plan generation issues (plan not created, steps stuck, plan not completing)
- [X] T017 [P] [US3] Update `silver/AI_Employee_Vault/Dashboard.md` to add Plan Generation section with plan stats (Plans Created: 0, Plans Completed: 0, Plans Failed: 0)

**Checkpoint**: README covers all Silver components including plan generation, Dashboard has plan tracking section

---

## Phase 5: User Story 4 — Demo Script (Priority: P4)

**Goal**: Step-by-step demo script for showcasing Silver tier capabilities

**Independent Test**: Follow demo script to verify all steps work and produce expected output

### Implementation for User Story 4

- [X] T018 [US4] Create `silver/DEMO_SCRIPT.md` with step-by-step walkthrough: system overview, start services, health check, email detection demo, approval workflow demo (approve + reject), LinkedIn post demo, plan generation demo, Dashboard review
- [X] T019 [US4] Run through `silver/DEMO_SCRIPT.md` to validate all demo steps produce expected results per `specs/silver/module-3/quickstart.md` Test 3

**Checkpoint**: Demo script covers all Silver capabilities with reproducible steps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 Plan Generation (Phase 2)**: Depends on Phase 1 (SKILL_PlanGenerator and orchestrator mapping)
- **US2 Silver Integration (Phase 3)**: Depends on Phase 2 (plan generation must work for full integration)
- **US3 Documentation (Phase 4)**: Depends on Phase 2 (need working plan generation to document)
- **US4 Demo Script (Phase 5)**: Depends on all previous phases

### Parallel Opportunities

- T002, T003, T004 can run in parallel (same file but independent changes)
- T005, T006, T007, T008, T009 are sequential (building up same skill file, but T001 creates it first)
- T015, T016, T017 can run in parallel (different files or independent sections)

### User Story Dependencies

- **US1 (Plan Generation)**: Independent after Phase 1 — **MVP target**
- **US2 (Integration)**: Requires US1 for plan generation verification
- **US3 (Documentation)**: Can start after US1, in parallel with US2
- **US4 (Demo Script)**: Requires all previous stories

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Plan Generation (T005-T010)
3. **STOP and VALIDATE**: Create complex task, verify plan generation works
4. Demo MVP

### Incremental Delivery

1. Setup → Foundation ready
2. Add US1 Plan Generation → Test plan creation → MVP
3. Add US2 Integration → Verify end-to-end → Enhanced
4. Add US3 Documentation → Complete README → Documented
5. Add US4 Demo Script → Walkthrough ready → Ship

---

## Notes

- Total tasks: 19
- US1 (Plan Generation): 6 tasks
- US2 (Integration): 4 tasks
- US3 (Documentation): 3 tasks
- US4 (Demo Script): 2 tasks
- Setup: 4 tasks
- Suggested MVP: Phase 1 + Phase 2 (US1) = 10 tasks
- This module is lighter than Modules 1 & 2 since most infrastructure exists
