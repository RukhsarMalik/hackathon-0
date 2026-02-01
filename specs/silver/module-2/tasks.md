# Tasks: Silver Module 2 — Email MCP Server + Approval Workflow

**Input**: Design documents from `specs/silver/module-2/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tools.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## User Stories (from spec.md)

- **US1**: MCP Server Operation (Email MCP Server + Integration) — Priority P1
- **US2**: Approval Workflow — Successful Send — Priority P2
- **US3**: Approval Workflow — Rejection — Priority P3

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: New directories, dependencies, Gmail scope expansion

- [X] T001 Create Approved/ and Rejected/ directories: `silver/AI_Employee_Vault/Approved/`, `silver/AI_Employee_Vault/Rejected/`
- [X] T002 [P] Install MCP SDK dependency: `pip install mcp`
- [X] T003 [P] Update Gmail API SCOPES in `silver/gmail_watcher.py` to add `https://www.googleapis.com/auth/gmail.send`

**Checkpoint**: Directories exist, MCP SDK installed, Gmail scopes updated

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: MCP config, shared logging setup

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create MCP configuration file `silver/mcp.json` with email server entry pointing to `email_mcp_server.py` using stdio transport
- [X] T005 [P] Create empty log files: `silver/AI_Employee_Vault/Logs/mcp_actions.log`, `silver/AI_Employee_Vault/Logs/approval_audit.log`

**Checkpoint**: MCP config ready, log files exist

---

## Phase 3: User Story 1 — MCP Server Operation (Priority: P1) MVP

**Goal**: Email MCP server starts, exposes send_email and draft_email tools, integrates with Claude Code via MCP protocol

**Independent Test**: Start email_mcp_server.py, verify Claude Code can discover the tools, use draft_email to preview an email without sending

### Implementation for User Story 1

- [X] T006 [US1] Create `silver/email_mcp_server.py` with imports: mcp, google OAuth, gmail API, base64, email.mime
- [X] T007 [US1] Implement Gmail authentication in `silver/email_mcp_server.py`: reuse token.pickle/credentials.json with expanded SCOPES including gmail.send
- [X] T008 [US1] Implement `validate_email(address)` helper in `silver/email_mcp_server.py` to check valid email format
- [X] T009 [US1] Implement `log_mcp_action(action, to, subject, status, message_id, error)` helper in `silver/email_mcp_server.py` appending to `AI_Employee_Vault/Logs/mcp_actions.log`
- [X] T010 [US1] Implement `draft_email` MCP tool in `silver/email_mcp_server.py`: accepts to, subject, body; validates email; returns formatted preview string
- [X] T011 [US1] Implement `send_email` MCP tool in `silver/email_mcp_server.py`: accepts to, subject, body, approval_file; validates approval_file exists in Approved/; validates email format; creates MIME message; sends via Gmail API; moves approval file to Done/; logs action
- [X] T012 [US1] Implement MCP server main entry point in `silver/email_mcp_server.py` using stdio transport with `server.run()`
- [X] T013 [US1] Verify `silver/mcp.json` works with Claude Code by testing tool discovery

**Checkpoint**: MCP server starts, draft_email returns previews, send_email validates approval files

---

## Phase 4: User Story 2 — Approval Workflow Successful Send (Priority: P2)

**Goal**: AI Employee drafts email reply → creates approval request in Pending_Approval/ → human approves by moving to Approved/ → approval watcher detects → orchestrator processes via SKILL_ApprovalHandler → MCP sends email

**Independent Test**: Place approval file in Pending_Approval/, move to Approved/, verify email is sent and file moves to Done/

### Implementation for User Story 2

- [X] T014 [P] [US2] Create `silver/AI_Employee_Vault/Needs_Action/SKILL_ApprovalHandler.md` with instructions for processing approved emails: read file, extract to/subject/body, call MCP send_email, handle success/failure, retry up to 3 times, update Dashboard, move to Done/
- [X] T015 [P] [US2] Update `silver/AI_Employee_Vault/Needs_Action/SKILL_EmailProcessor.md` to add reply drafting: when reply is needed, draft professional reply per Company_Handbook, create APPROVAL_REPLY_{gmail_id}.md in Pending_Approval/ with YAML frontmatter (type: email_approval, to, subject, body, original_gmail_id, status: awaiting_approval)
- [X] T016 [US2] Create `silver/approval_watcher.py` with imports, config constants: VAULT_PATH, APPROVED, REJECTED, NEEDS_ACTION, DONE, LOGS, poll interval 10s
- [X] T017 [US2] Implement `process_approved_files()` in `silver/approval_watcher.py`: scan Approved/ for *.md files, for each create an APPROVED_EMAIL_*.md task in Needs_Action/ with type: email_approval and the approval file content, move original to Needs_Action/ as context reference
- [X] T018 [US2] Implement `main()` loop in `silver/approval_watcher.py`: call process_approved_files() and process_rejected_files() every 10 seconds, handle KeyboardInterrupt
- [X] T019 [US2] Add logging configuration in `silver/approval_watcher.py` with dual output to `AI_Employee_Vault/Logs/approval_audit.log` and console
- [X] T020 [US2] Update `silver/orchestrator.py` SKILL_MAP to add mapping: `email_approval` → `SKILL_ApprovalHandler.md`
- [X] T021 [US2] Update `silver/orchestrator.py` SKILL_PATTERNS set to include `SKILL_ApprovalHandler.md`

**Checkpoint**: Full approval-to-send workflow works end-to-end

---

## Phase 5: User Story 3 — Approval Workflow Rejection (Priority: P3)

**Goal**: Human rejects an email by moving to Rejected/, system logs rejection and moves to Done/ without sending

**Independent Test**: Place approval file in Rejected/, verify it's logged in approval_audit.log and moved to Done/

### Implementation for User Story 3

- [X] T022 [US3] Implement `process_rejected_files()` in `silver/approval_watcher.py`: scan Rejected/ for *.md files, log rejection with filename/recipient/reason to approval_audit.log, move file to Done/ with rejection note appended
- [X] T023 [US3] Implement `log_audit(action, filename, to, reason)` helper in `silver/approval_watcher.py` appending structured entries to `AI_Employee_Vault/Logs/approval_audit.log`

**Checkpoint**: Rejected files are logged and moved to Done/ without sending

---

## Phase 6: Startup Integration (Cross-cutting)

**Goal**: Update start_all.sh to launch MCP server and approval watcher alongside existing services

- [X] T024 Update `silver/start_all.sh` to start `approval_watcher.py` as background process with PID file `.pids/approval.pid`
- [X] T025 Update `silver/start_all.sh` to start `email_mcp_server.py` as background process with PID file `.pids/mcp_email.pid`
- [X] T026 Update `silver/health_check.py` EXPECTED_SERVICES list to include `approval` and `mcp_email`

**Checkpoint**: `./start_all.sh` launches all services including MCP server and approval watcher

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, dashboard updates, validation

- [X] T027 [P] Update `silver/README.md` to document MCP server, approval workflow, new directories, and mcp.json configuration
- [X] T028 [P] Update `silver/AI_Employee_Vault/Dashboard.md` to add Email MCP and Approval Workflow sections
- [X] T029 Run quickstart.md validation: test draft_email, approval-to-send, and rejection workflows per `specs/silver/module-2/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 MCP Server (Phase 3)**: Depends on Phase 2
- **US2 Approval Send (Phase 4)**: Depends on Phase 2; uses MCP server from US1 for actual sending
- **US3 Approval Rejection (Phase 5)**: Depends on Phase 4 (approval_watcher.py created in US2)
- **Startup Integration (Phase 6)**: Depends on US1, US2, US3
- **Polish (Phase 7)**: Depends on all previous phases

### User Story Dependencies

- **US1 (MCP Server)**: Independent after Phase 2 — **MVP target**
- **US2 (Approval Send)**: Requires US1 MCP server for end-to-end send, but approval_watcher and skills can be built independently
- **US3 (Approval Rejection)**: Requires approval_watcher from US2

### Parallel Opportunities

- T002, T003 can run in parallel (Phase 1)
- T004, T005 can run in parallel (Phase 2)
- T014, T015 can run in parallel (Phase 4 — different files)
- T027, T028 can run in parallel (Phase 7)

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T005)
3. Complete Phase 3: MCP Server (T006-T013)
4. **STOP and VALIDATE**: Start MCP server, test draft_email tool
5. Demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 MCP Server → Test draft_email → MVP
3. Add US2 Approval Send → Test full workflow → Enhanced
4. Add US3 Rejection → Test rejection logging → Complete
5. Startup Integration → Single command launch → Production-ready
6. Polish → Documentation and validation → Ship

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Total tasks: 29
- US1 (MCP Server): 8 tasks
- US2 (Approval Send): 8 tasks
- US3 (Rejection): 2 tasks
- Startup: 3 tasks
- Setup/Foundation/Polish: 8 tasks
- Suggested MVP: Phase 1 + Phase 2 + Phase 3 (US1) = 13 tasks
