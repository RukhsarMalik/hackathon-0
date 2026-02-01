# Tasks: Silver Module 1 — Orchestrator + LinkedIn Automation

**Input**: Design documents from `specs/silver/module-1/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## User Stories (from spec.md)

- **US1**: Automatic Task Processing (Orchestrator) — Priority P1
- **US2**: Scheduled LinkedIn Posts — Priority P2
- **US3**: System Health Monitoring — Priority P3

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Silver directory structure, config, vault setup

- [X] T001 Create silver directory structure: `silver/`, `silver/.pids/`, `silver/AI_Employee_Vault/{Inbox,Needs_Action,Pending_Approval,Done,Logs}`
- [X] T002 [P] Copy bronze vault content to silver vault: Dashboard.md, Company_Handbook.md, SKILLS.md, SKILL_FileProcessor.md, SKILL_EmailProcessor.md from `bronze/AI_Employee_Vault/Needs_Action/`
- [X] T003 [P] Copy bronze watchers to silver: `bronze/filesystem_watcher.py` → `silver/filesystem_watcher.py`, `bronze/gmail_watcher.py` → `silver/gmail_watcher.py`
- [X] T004 [P] Create `silver/.env.example` with VAULT_PATH, GMAIL_CHECK_INTERVAL, LINKEDIN_POST_TIMES, ORCHESTRATOR_COOLDOWN settings
- [X] T005 [P] Create `silver/.gitignore` excluding .env, credentials.json, token.pickle, .pids/, __pycache__/

**Checkpoint**: Silver directory ready with bronze foundation copied over

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update vault paths in copied watchers, ensure Pending_Approval folder exists

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Update `silver/filesystem_watcher.py` VAULT_PATH default to `./AI_Employee_Vault`
- [X] T007 [P] Update `silver/gmail_watcher.py` VAULT_PATH default to `./AI_Employee_Vault`
- [X] T008 [P] Create `silver/AI_Employee_Vault/Logs/linkedin_posts.json` with empty array `[]`

**Checkpoint**: Foundation ready — all watchers point to silver vault, LinkedIn tracking file exists

---

## Phase 3: User Story 1 — Automatic Task Processing (Priority: P1) MVP

**Goal**: Orchestrator monitors Needs_Action/ and automatically triggers Claude Code to process tasks without manual intervention

**Independent Test**: Place a test EMAIL or FILE task in Needs_Action/, verify orchestrator detects it, invokes Claude Code, and the task is processed and moved to Done/ within 10 seconds

### Implementation for User Story 1

- [X] T009 [US1] Create orchestrator config constants in `silver/orchestrator.py`: VAULT_PATH, NEEDS_ACTION, DONE, LOGS, SKILL_FILES list, DEBOUNCE_SECONDS=10, COOLDOWN_SECONDS=30
- [X] T010 [US1] Implement `parse_frontmatter(file_path)` function in `silver/orchestrator.py` to extract YAML type field from task files
- [X] T011 [US1] Implement `get_skill_for_type(task_type)` function in `silver/orchestrator.py` mapping task types to skill files: email→SKILL_EmailProcessor.md, file_drop→SKILL_FileProcessor.md, linkedin_post→SKILL_LinkedInPoster.md
- [X] T012 [US1] Implement `get_actionable_files()` function in `silver/orchestrator.py` to list .md files in Needs_Action/ excluding SKILL_* and SKILLS.md, filtering by mtime > DEBOUNCE_SECONDS ago
- [X] T013 [US1] Implement `build_claude_prompt(task_content, skill_content)` function in `silver/orchestrator.py` to construct the processing prompt
- [X] T014 [US1] Implement `invoke_claude(prompt)` function in `silver/orchestrator.py` using `subprocess.run(["claude", "--print", "-p", prompt])` with timeout and error handling
- [X] T015 [US1] Implement `process_task(file_path)` function in `silver/orchestrator.py` that reads task file, reads skill file, builds prompt, invokes Claude, and logs result
- [X] T016 [US1] Implement `main()` loop in `silver/orchestrator.py`: scan for actionable files, process each, sleep COOLDOWN_SECONDS, handle KeyboardInterrupt for graceful shutdown
- [X] T017 [US1] Add logging configuration in `silver/orchestrator.py` with dual output to `AI_Employee_Vault/Logs/orchestrator.log` and console

**Checkpoint**: Orchestrator automatically detects and processes task files via Claude Code

---

## Phase 4: User Story 2 — Scheduled LinkedIn Posts (Priority: P2)

**Goal**: LinkedIn watcher creates post request files on Mon/Wed/Fri, orchestrator processes them using LinkedIn poster skill, generated content goes to Pending_Approval for human review

**Independent Test**: Run LinkedIn watcher, verify it creates LINKEDIN_POST_*.md in Needs_Action/ on scheduled days, verify no duplicate posts for same day

### Implementation for User Story 2

- [X] T018 [P] [US2] Create `silver/AI_Employee_Vault/Needs_Action/SKILL_LinkedInPoster.md` with post generation instructions: hook→context→value→CTA→hashtags structure, templates for weekly_update/tip_of_day/success_story, output to Pending_Approval/
- [X] T019 [P] [US2] Create LinkedIn watcher config in `silver/linkedin_watcher.py`: VAULT_PATH, NEEDS_ACTION, LOGS, POST_HISTORY_FILE, SCHEDULE dict mapping Monday→weekly_update, Wednesday→tip_of_day, Friday→success_story, POST_TIME="09:00"
- [X] T020 [US2] Implement `load_post_history()` function in `silver/linkedin_watcher.py` reading from `AI_Employee_Vault/Logs/linkedin_posts.json`
- [X] T021 [US2] Implement `save_post_entry(date, post_type, filename)` function in `silver/linkedin_watcher.py` appending to linkedin_posts.json
- [X] T022 [US2] Implement `has_posted_today(post_type)` function in `silver/linkedin_watcher.py` checking linkedin_posts.json for today's date and type
- [X] T023 [US2] Implement `create_post_request(post_type)` function in `silver/linkedin_watcher.py` creating LINKEDIN_POST_{date}_{type}.md in Needs_Action/ with YAML frontmatter (type: linkedin_post, topic, scheduled_date, status: pending)
- [X] T024 [US2] Implement `check_schedule()` function in `silver/linkedin_watcher.py` checking current day/time against SCHEDULE, calling create_post_request if matched and not posted today
- [X] T025 [US2] Implement `main()` loop in `silver/linkedin_watcher.py`: call check_schedule every 60 seconds, handle KeyboardInterrupt
- [X] T026 [US2] Add logging configuration in `silver/linkedin_watcher.py` with dual output to `AI_Employee_Vault/Logs/linkedin_watcher.log` and console

**Checkpoint**: LinkedIn watcher creates scheduled post requests, orchestrator processes them, content appears in Pending_Approval/

---

## Phase 5: User Story 3 — System Health Monitoring (Priority: P3)

**Goal**: Health check script verifies all services are running, Dashboard is fresh, and no tasks are stuck

**Independent Test**: Start all services, run health_check.py, verify it reports all healthy. Stop one service, run again, verify it reports the issue.

### Implementation for User Story 3

- [X] T027 [US3] Create health check config in `silver/health_check.py`: PID_DIR, VAULT_PATH, EXPECTED_SERVICES list (gmail, filesystem, linkedin, orchestrator), MAX_DASHBOARD_AGE_HOURS=24, MAX_TASK_AGE_HOURS=2
- [X] T028 [US3] Implement `check_process_alive(pid_file)` function in `silver/health_check.py` reading PID from file and checking with `os.kill(pid, 0)`
- [X] T029 [US3] Implement `check_dashboard_freshness()` function in `silver/health_check.py` parsing last_updated from Dashboard.md YAML frontmatter
- [X] T030 [US3] Implement `check_stuck_tasks()` function in `silver/health_check.py` listing Needs_Action/ files (excluding SKILL_*) and checking mtime > MAX_TASK_AGE_HOURS
- [X] T031 [US3] Implement `run_health_check()` function in `silver/health_check.py` calling all checks, printing status table, returning exit code 0 (healthy) or 1 (issues)
- [X] T032 [US3] Implement `main()` in `silver/health_check.py` with argument parsing for --json output option

**Checkpoint**: Health check accurately reports system status

---

## Phase 6: Startup Script (Cross-cutting)

**Goal**: Single script to launch all services with graceful shutdown

- [X] T033 Create `silver/start_all.sh` with prerequisite checks: verify python3, claude CLI, and vault directory exist
- [X] T034 Add service startup logic in `silver/start_all.sh`: launch gmail_watcher.py, filesystem_watcher.py, linkedin_watcher.py as background processes, write PIDs to `.pids/`
- [X] T035 Add trap-based cleanup in `silver/start_all.sh`: trap SIGINT/SIGTERM, kill all PIDs from .pids/, remove PID files
- [X] T036 Add orchestrator foreground launch in `silver/start_all.sh` as the final command after all background services start
- [X] T037 Make `silver/start_all.sh` executable and add startup logging

**Checkpoint**: `./start_all.sh` launches all services, Ctrl+C shuts them all down cleanly

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, README, final validation

- [X] T038 [P] Create `silver/README.md` documenting all components, setup, usage, and troubleshooting
- [X] T039 [P] Update `silver/AI_Employee_Vault/Dashboard.md` to include LinkedIn and orchestrator sections
- [X] T040 Run quickstart.md validation: test full workflow end-to-end per `specs/silver/module-1/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 Orchestrator (Phase 3)**: Depends on Phase 2
- **US2 LinkedIn (Phase 4)**: Depends on Phase 2; integrates with US1 orchestrator for processing
- **US3 Health Check (Phase 5)**: Depends on Phase 2; works best after US1+US2 for full validation
- **Startup Script (Phase 6)**: Depends on US1, US2, US3 (needs all services to exist)
- **Polish (Phase 7)**: Depends on all previous phases

### User Story Dependencies

- **US1 (Orchestrator)**: Independent after Phase 2 — **MVP target**
- **US2 (LinkedIn)**: Can start after Phase 2, but full flow requires US1 orchestrator to process posts
- **US3 (Health Check)**: Independent after Phase 2, but most useful after US1+US2

### Parallel Opportunities

- T002, T003, T004, T005 can all run in parallel (Phase 1)
- T006, T007, T008 can run in parallel (Phase 2)
- T018, T019 can run in parallel (Phase 4)
- T038, T039 can run in parallel (Phase 7)
- US1 and US2 implementation can proceed in parallel after Phase 2

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T008)
3. Complete Phase 3: Orchestrator (T009-T017)
4. **STOP and VALIDATE**: Place a test task in Needs_Action/, verify auto-processing
5. Demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 Orchestrator → Test independently → MVP
3. Add US2 LinkedIn → Test with orchestrator → Enhanced
4. Add US3 Health Check → Validate full system → Complete
5. Add Startup Script → Single command launch → Production-ready
6. Polish → Documentation and validation → Ship

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Total tasks: 40
- US1 (Orchestrator): 9 tasks
- US2 (LinkedIn): 9 tasks
- US3 (Health Check): 6 tasks
- Startup: 5 tasks
- Setup/Foundation/Polish: 11 tasks
- Suggested MVP: Phase 1 + Phase 2 + Phase 3 (US1) = 17 tasks
