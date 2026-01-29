# Tasks: Foundation Setup

**Input**: Design documents from `specs/bronze/001-foundation-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/vault-file-ops.md

**Tests**: Not requested in spec — test tasks omitted.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: Project-level configuration before vault creation

- [x] T001 Add `AI_Employee_Vault/` to `.gitignore` at repository root
- [x] T002 [P] Create `.env.example` at repository root with placeholder comments for future modules (Gmail API, etc.)

---

## Phase 2: Foundational (Vault Directory Structure)

**Purpose**: Create the vault directory tree that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create vault directory structure: `bronze/AI_Employee_Vault/{Inbox,Needs_Action,Done,Logs,Logs/malformed}` with `.gitkeep` in each empty directory

**Checkpoint**: Vault directory exists with all 4 top-level folders + Logs/malformed/ accessible

---

## Phase 3: User Story 1 - Create Vault Structure Validation (Priority: P1)

**Goal**: Verify the vault structure is complete, accessible, and Obsidian-compatible

**Independent Test**: List all subdirectories and confirm 4 folders exist with no permission errors

### Implementation for User Story 1

- [x] T004 [US1] Verify all directories are readable and writable by creating and removing a temp file in each: `bronze/AI_Employee_Vault/Inbox/`, `bronze/AI_Employee_Vault/Needs_Action/`, `bronze/AI_Employee_Vault/Done/`, `bronze/AI_Employee_Vault/Logs/`

**Checkpoint**: Vault structure verified — all folders accessible

---

## Phase 4: User Story 2 - Create Dashboard (Priority: P1)

**Goal**: Create Dashboard.md with status template that Claude Code can read and update

**Independent Test**: Create Dashboard.md, update its `last_updated` timestamp programmatically, verify change persists

### Implementation for User Story 2

- [x] T005 [US2] Create `bronze/AI_Employee_Vault/Dashboard.md` with YAML frontmatter (`last_updated: YYYY-MM-DDTHH:MM:SSZ`) and sections: System Status (status, active tasks, completed today, last activity), Recent Activity, Pending Actions, Quick Stats (total processed, success rate, avg processing time) — all counters initialized to 0
- [x] T006 [US2] Verify Claude Code can read `bronze/AI_Employee_Vault/Dashboard.md` and parse the `last_updated` frontmatter field
- [x] T007 [US2] Verify Claude Code can update `bronze/AI_Employee_Vault/Dashboard.md` by writing a new `last_updated` timestamp and confirm the change persists on re-read

**Checkpoint**: Dashboard.md exists, renders in Obsidian, and is programmatically updatable

---

## Phase 5: User Story 3 - Create Company Handbook (Priority: P1)

**Goal**: Create Company_Handbook.md with 7+ actionable rule categories

**Independent Test**: Create the file and verify it contains all 7 rule sections with clear, unambiguous rules

### Implementation for User Story 3

- [x] T008 [US3] Create `bronze/AI_Employee_Vault/Company_Handbook.md` with YAML frontmatter (`version: 1.0`, `created: YYYY-MM-DD`) and 7 rule categories: Core Principles (4 rules), Communication Guidelines (tone, response times, acknowledgment), Financial Rules (flag >$100, no auto-payments, verify recipients, log activity), File Management (no delete without approval, move to Done, cap Needs_Action at 20, archive after 30 days), Privacy & Security (no credential sharing, mark sensitive info, secure channels, report concerns), Work Hours (9-6 active, emergency-only off-hours, reduced weekends), Error Handling (ask if uncertain, log errors in Logs, no guessing on critical decisions, graceful degradation)

**Checkpoint**: Company_Handbook.md has 7 rule categories, each with actionable rules

---

## Phase 6: User Story 5 - Document Agent Skill (Priority: P2)

**Goal**: Create SKILLS.md with the Basic Task Processor v1.0 skill fully documented

**Independent Test**: Verify SKILLS.md contains all required sections: name, purpose, trigger, process flow, input format, output, error handling

### Implementation for User Story 5

- [x] T009 [US5] Create `bronze/AI_Employee_Vault/Needs_Action/SKILLS.md` with Basic Task Processor v1.0 skill containing: Skill Name and version, Purpose (process task files from Needs_Action), Trigger (manual invocation or scheduled check), Process Flow (list .md files → read content → extract action items → determine task type → execute per handbook → update dashboard → move to Done with timestamp), Input Format (markdown with optional YAML frontmatter: type, priority, created), Output (updated Dashboard.md, file moved to Done, activity logged), Error Handling (malformed → Logs/malformed, unclear → REVIEW_ prefix, critical → log and alert human)

**Checkpoint**: SKILLS.md has one fully documented skill with all 7 sections

---

## Phase 7: User Story 4 - Test File Workflow (Priority: P2)

**Goal**: End-to-end validation: create task → process → move to Done → update Dashboard

**Independent Test**: Place TEST_Task.md in Needs_Action, process it, verify it moves to Done and Dashboard updates

**Note**: Depends on US2 (Dashboard) and US5 (SKILLS.md) being complete

### Implementation for User Story 4

- [x] T010 [US4] Create `bronze/AI_Employee_Vault/Needs_Action/TEST_Task.md` with YAML frontmatter (`type: task`, `priority: medium`, `created: YYYY-MM-DD`) and body containing task description and action items: `- [ ] Read this file`, `- [ ] Log the activity`, `- [ ] Move to Done`
- [x] T011 [US4] Process TEST_Task.md: read its content, extract action items, update `bronze/AI_Employee_Vault/Dashboard.md` (set `last_updated` to current timestamp, increment `Completed Today` to 1, increment `Total Tasks Processed` to 1, add entry to Recent Activity with task name and timestamp, update `Last Activity`)
- [x] T012 [US4] Move `bronze/AI_Employee_Vault/Needs_Action/TEST_Task.md` to `bronze/AI_Employee_Vault/Done/TEST_Task.md`
- [x] T013 [US4] Verify final state: confirm TEST_Task.md exists in `bronze/AI_Employee_Vault/Done/`, confirm TEST_Task.md no longer in `bronze/AI_Employee_Vault/Needs_Action/`, confirm Dashboard.md shows updated activity and counters

**Checkpoint**: Full detect-process-complete cycle validated end-to-end

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final deliverables

- [x] T014 [P] Create `bronze/README-Module1.md` at bronze directory with: prerequisites, setup steps, vault structure overview, how to run the test workflow, troubleshooting guide, next steps (Module 2)
- [x] T015 Run quickstart.md validation: walk through all steps in `specs/bronze/001-foundation-setup/quickstart.md` and confirm each completes successfully

---

## Summary

- **Total tasks**: 15
- **Completed**: 15/15
- **Status**: COMPLETE
