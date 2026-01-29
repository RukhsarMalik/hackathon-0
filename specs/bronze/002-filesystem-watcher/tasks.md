# Tasks: File System Watcher

**Input**: Design documents from `specs/bronze/002-filesystem-watcher/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/watcher-events.md

**Tests**: Not explicitly requested — test tasks omitted. Manual e2e validation included in Phase 7.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: Install dependencies and configure environment

- [x] T001 Install Python dependencies: run `pip install watchdog python-dotenv`
- [x] T002 [P] Update `.env.example` at repository root to include `VAULT_PATH=./bronze/AI_Employee_Vault`
- [x] T003 [P] Create `bronze/AI_Employee_Vault/Logs/quarantine/` directory if not already present

---

## Phase 2: Foundational (Script Skeleton)

**Purpose**: Create the watcher script skeleton with imports, config loading, logging, and main entry point

**CRITICAL**: All user story implementations build on this skeleton

- [x] T004 Create `bronze/filesystem_watcher.py` with: imports (time, logging, shutil, re, pathlib.Path, datetime, os, dotenv, watchdog.observers.Observer, watchdog.events.FileSystemEventHandler), load .env config for VAULT_PATH with default `./AI_Employee_Vault`, define path constants (VAULT_PATH, INBOX, NEEDS_ACTION, LOGS, QUARANTINE), configure dual logging (StreamHandler for console + FileHandler for `Logs/watcher_errors.log` with format `%(asctime)s - %(levelname)s - %(message)s`), empty `InboxHandler(FileSystemEventHandler)` class with pass in `on_created`, and `main()` function that creates Observer, schedules InboxHandler on INBOX (non-recursive), starts observer, runs `while True: time.sleep(1)` loop, and has empty KeyboardInterrupt handler. Include `if __name__ == "__main__": main()`

**Checkpoint**: `python bronze/filesystem_watcher.py` starts without errors and logs startup message

---

## Phase 3: User Story 1 - Continuous File Monitoring (Priority: P1)

**Goal**: Detect new files in Inbox/ and log detection events

**Independent Test**: Drop a file in Inbox/, verify "File detected: [name]" appears in console

### Implementation for User Story 1

- [x] T005 [US1] Implement `InboxHandler.on_created()` in `bronze/filesystem_watcher.py`: return early if `event.is_directory` is True, extract `source = Path(event.src_path)`, add brief `time.sleep(0.5)` to allow file write completion, log `f"File detected: {source.name}"` at INFO level

**Checkpoint**: Watcher detects file drops and logs them

---

## Phase 4: User Story 2 - Action File Generation (Priority: P1)

**Goal**: Create structured action files in Needs_Action/ for each detected file

**Independent Test**: Drop a file, verify `FILE_[name].md` appears in Needs_Action/ with correct frontmatter

**Note**: Depends on US1 (detection must work first)

### Implementation for User Story 2

- [x] T006 [US2] Add filename sanitization helper function `sanitize_filename(name: str) -> str` in `bronze/filesystem_watcher.py`: use `re.sub(r'[^a-zA-Z0-9._-]', '_', name)` to replace special characters with underscores
- [x] T007 [US2] Implement action file creation in `InboxHandler.on_created()` in `bronze/filesystem_watcher.py` (after the detection log from T005): get file size with `source.stat().st_size`, generate sanitized stem with `sanitize_filename(source.stem)`, build action file content string with YAML frontmatter (type: file_drop, original_name, size, detected as `datetime.now().isoformat()`, status: pending) and body (New File Dropped header, File Details with name/size/type, Suggested Actions with 4 checkboxes: review content, determine handling, process by type, move to Done), write to `NEEDS_ACTION / f"FILE_{sanitized_stem}.md"`, log `f"Action file created: FILE_{sanitized_stem}.md"` at INFO level

**Checkpoint**: Action files created with correct format and metadata

---

## Phase 5: User Story 3 - Error Resilience (Priority: P1)

**Goal**: Handle all error scenarios without crashing

**Independent Test**: Drop an oversized file, verify it's quarantined; drop a file with special chars, verify action file created; kill Needs_Action/ permissions temporarily, verify error logged and watcher continues

### Implementation for User Story 3

- [x] T008 [US3] Add file size check in `InboxHandler.on_created()` in `bronze/filesystem_watcher.py` (after `source.stat().st_size`, before action file creation): if size > 10_485_760 (10MB), log error `f"File too large: {source.name} ({size} bytes) — quarantined"`, move file to `QUARANTINE / source.name` using `shutil.move()`, return early (no action file)
- [x] T009 [US3] Wrap the entire body of `on_created()` in `bronze/filesystem_watcher.py` in a try/except block: catch `FileNotFoundError` with warning log "File vanished before processing: [name]", catch `PermissionError` with error log "Permission denied: [name]", catch `OSError` with error log "OS error processing [name]: [error]", catch generic `Exception` with error log "Unexpected error processing [path]: [error]" — all handlers continue (no re-raise)

**Checkpoint**: Watcher survives all error scenarios and continues monitoring

---

## Phase 6: User Story 5 - Graceful Lifecycle Management (Priority: P2)

**Goal**: Clean startup validation and shutdown handling

**Independent Test**: Start watcher with valid path (logs startup), start with invalid path (logs error and exits), press Ctrl+C (logs shutdown)

### Implementation for User Story 5

- [x] T010 [US5] Update `main()` in `bronze/filesystem_watcher.py`: before creating Observer, check if INBOX directory exists — if not, log error `f"Inbox directory not found: {INBOX}"` and `sys.exit(1)` (add `import sys`). Add startup logs: `logger.info("Starting File System Watcher...")` and `logger.info(f"Monitoring: {INBOX}")`. In KeyboardInterrupt handler: `logger.info("Shutting down watcher...")`, `observer.stop()`. After `observer.join()`: `logger.info("Watcher stopped.")`

**Checkpoint**: Clean startup with validation, clean shutdown on Ctrl+C

---

## Phase 7: User Story 4 - File Processing Agent Skill (Priority: P2)

**Goal**: Document processing rules for the AI Employee to follow when handling file_drop action files

**Independent Test**: Create a file_drop action file manually, follow the skill instructions, verify correct processing

### Implementation for User Story 4

- [x] T011 [US4] Create `bronze/AI_Employee_Vault/Needs_Action/SKILL_FileProcessor.md` with: Skill Name (File Drop Processor v1.0), Purpose (process file_drop action files from Needs_Action), Trigger (manual invocation or after watcher creates action files), Process Flow (1. list FILE_*.md in Needs_Action, 2. for each: read frontmatter, determine file type from original_name extension, apply type-specific rules, update Dashboard, move action file and original to Done), File Type Handling section with rules for .txt/.md (read first 500 chars, check keywords: urgent/invoice/payment/todo, flag if found, log summary), .pdf (note metadata, flag "PDF requires manual review", move to Done), .csv (count rows/columns, read header, check financial keywords: amount/price/invoice, flag if financial), Unknown (note extension, flag for manual review, log unknown type), Output (updated Dashboard.md, files moved to Done, activity logged), Error Handling (malformed action file → Logs/malformed, processing error → log and continue, missing original file → log warning and move action file to Done with note)

**Checkpoint**: Skill document complete with all 4 file type categories

---

## Phase 8: End-to-End Validation

**Goal**: Verify complete workflow with 4 test file types

**Independent Test**: Start watcher, drop 4 files, verify 4 action files, process with skill, verify Dashboard

### Implementation

- [x] T012 Start watcher (`python bronze/filesystem_watcher.py`), create 4 test files in `bronze/AI_Employee_Vault/Inbox/`: `test.txt` (content: "Test content for watcher"), `urgent_note.md` (content: "URGENT: Review this immediately"), a small `sample.pdf` (any valid PDF or just text file renamed), `data.csv` (content: "name,amount,date\nJohn,150,2026-01-29")
- [x] T013 Verify 4 action files exist in `bronze/AI_Employee_Vault/Needs_Action/`: FILE_test.md, FILE_urgent_note.md, FILE_sample.md, FILE_data.md — each with correct frontmatter and body
- [x] T014 Stop watcher with Ctrl+C and verify clean shutdown in logs and no errors in `bronze/AI_Employee_Vault/Logs/watcher_errors.log`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final deliverables

- [x] T015 [P] Create `bronze/README-Module2.md` with: prerequisites (Python 3.13+, watchdog, python-dotenv), setup steps (install deps, configure .env, start watcher), how the watcher works (monitors Inbox, creates action files, error handling), file structure, testing guide (4 test files), troubleshooting (common issues from spec), next steps (Module 3: Gmail Watcher)
- [x] T016 Verify `.env.example` includes VAULT_PATH and `.gitignore` excludes `.env` and vault directories

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2
- **US2 (Phase 4)**: Depends on US1 (detection must work)
- **US3 (Phase 5)**: Depends on US2 (error handling wraps action file creation)
- **US5 (Phase 6)**: Depends on Phase 2 — can run parallel with US1/US2/US3 (different code section)
- **US4 (Phase 7)**: Independent — markdown file only, can run parallel with any phase after Phase 2
- **E2E Validation (Phase 8)**: Depends on US1 + US2 + US3 + US5
- **Polish (Phase 9)**: Depends on all phases complete

### Parallel Opportunities

- T002 and T003 can run in parallel (Setup phase)
- US4 (T011, Agent Skill) can run in parallel with US1/US2/US3/US5 (separate file)
- US5 (T010, lifecycle) can run in parallel with US2/US3 (different code section in same file)
- T015 and T016 can run in parallel (Polish phase)

---

## Parallel Example: After Phase 2

```bash
# These can run in parallel:
Task: T011 [US4] Create SKILL_FileProcessor.md  (separate file)
# Sequential chain (same file, dependent logic):
Task: T005 [US1] → T006-T007 [US2] → T008-T009 [US3] → T010 [US5]
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational skeleton (T004)
3. Complete Phase 3: US1 file detection (T005)
4. Complete Phase 4: US2 action file creation (T006-T007)
5. **STOP and VALIDATE**: Drop a file, verify action file created

### Incremental Delivery

1. Setup + Skeleton → Script runs, does nothing
2. Add US1 → Detects files, logs events
3. Add US2 → Creates action files (MVP functional)
4. Add US3 → Error resilience (production-ready)
5. Add US5 → Clean lifecycle (operational)
6. Add US4 → Processing skill (AI Employee ready)
7. E2E Validation → Full workflow confirmed
8. Polish → Documentation complete

---

## Summary

- **Total tasks**: 16 — **Completed: 16/16** — **Status: COMPLETE**
- **US1 (Monitoring)**: 1 task
- **US2 (Action Files)**: 2 tasks
- **US3 (Error Handling)**: 2 tasks
- **US4 (Agent Skill)**: 1 task
- **US5 (Lifecycle)**: 1 task
- **Setup/Foundational**: 4 tasks
- **E2E Validation**: 3 tasks
- **Polish**: 2 tasks
- **Parallel opportunities**: US4 independent; T002/T003 parallel; T015/T016 parallel
- **Suggested MVP scope**: US1 + US2 (file detection + action file creation)

## Notes

- Most tasks modify the same file (`bronze/filesystem_watcher.py`) so must be sequential
- US4 (SKILL_FileProcessor.md) is the only fully parallel user story (separate file)
- E2E validation tasks (T012-T014) are manual verification steps
- No automated test tasks generated (not requested in spec)
