# Tasks: Gmail Watcher

**Input**: Design documents from `specs/bronze/003-gmail-watcher/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/watcher-events.md

**Tests**: Comprehensive test suite included for validation during implementation.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: Install dependencies and configure environment

- [ ] T001 Install Gmail API dependencies: run `pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 python-dotenv`
- [ ] T002 [P] Update `.env.example` at repository root to include `VAULT_PATH=./bronze/AI_Employee_Vault` and `GMAIL_CHECK_INTERVAL=120`
- [ ] T003 [P] Ensure `bronze/AI_Employee_Vault/Logs/` directory exists with subdirectory `gmail_errors.log`

---

## Phase 2: Foundational (Script Skeleton)

**Purpose**: Create the watcher script skeleton with imports, config loading, logging, and main entry point

**CRITICAL**: All user story implementations build on this skeleton

- [ ] T004 Create `bronze/gmail_watcher.py` with: imports (time, logging, os, json, pickle, re, pathlib.Path, datetime, google.oauth2.credentials, google_auth_oauthlib.flow, googleapiclient.discovery, google.auth.transport.requests), load .env config for VAULT_PATH with default `./AI_Employee_Vault`, define path constants (VAULT_PATH, NEEDS_ACTION, LOGS, PROCESSED_FILE), configure dual logging (StreamHandler for console + FileHandler for `Logs/gmail_errors.log` with format `%(asctime)s - %(levelname)s - %(message)s`), and `main()` function with placeholder for Gmail service initialization and infinite loop with Ctrl+C handler. Include `if __name__ == "__main__": main()`

**Checkpoint**: `python bronze/gmail_watcher.py` starts without errors (may fail auth until credentials added)

---

## Phase 3: User Story 1 - Gmail API Setup (Priority: P1)

**Goal**: Authenticate with Gmail API using OAuth 2.0 and verify access

**Independent Test**: Complete OAuth flow and make test API call to get user profile

### Implementation for User Story 1

- [ ] T005 Implement `get_gmail_service()` function in `bronze/gmail_watcher.py`: load credentials from `credentials.json`, handle token refresh using `token.pickle`, run OAuth flow if no valid token exists, return authenticated Gmail service object using `googleapiclient.discovery.build`
- [ ] T006 Add authentication validation in `main()` function: call a simple Gmail API method (like getting user profile) to verify authentication works, log success/error appropriately

**Checkpoint**: OAuth authentication completes successfully and API access is verified

---

## Phase 4: User Story 2 - Dependencies & Configuration (Priority: P1)

**Goal**: Ensure all dependencies are properly configured and available

**Independent Test**: Import all required libraries without errors

### Implementation for User Story 2

- [ ] T007 Verify all imports work by adding try/catch blocks around each import statement in `bronze/gmail_watcher.py` and logging any import errors with helpful messages
- [ ] T008 Add configuration validation in `main()` function: check if `credentials.json` exists, verify VAULT_PATH directory exists, validate that all required paths are accessible

**Checkpoint**: All dependencies available and configuration validated

---

## Phase 5: User Story 3 - Core Email Monitoring (Priority: P1)

**Goal**: Monitor Gmail for important unread emails and log detection events

**Independent Test**: Start watcher, send test email marked important, verify "Email detected" log appears

**Note**: Depends on US1 (authentication must work first)

### Implementation for User Story 3

- [ ] T009 Implement `check_emails()` function in `bronze/gmail_watcher.py`: use Gmail API to query for "is:unread is:important" emails, extract message headers (from, subject, date), add basic logging for detected emails, implement polling delay of 120 seconds
- [ ] T010 Update `main()` function to call `check_emails()` in the main loop every 120 seconds, add proper exception handling around API calls

**Checkpoint**: Watcher detects important unread emails and logs them

---

## Phase 6: User Story 4 - Duplicate Detection (Priority: P1)

**Goal**: Prevent processing the same email twice by tracking processed message IDs

**Independent Test**: Process an email, restart watcher, verify same email is not re-processed

### Implementation for User Story 4

- [ ] T011 Add `load_processed_ids()` and `save_processed_id()` helper functions in `bronze/gmail_watcher.py`: read/write to `Logs/processed_emails.txt`, return/set Gmail message IDs as a set for efficient lookup
- [ ] T012 Update `check_emails()` function to check if email ID exists in processed IDs before processing, skip if already processed, save ID after successful processing

**Checkpoint**: Duplicate emails are detected and skipped

---

## Phase 7: User Story 3 Continued - Action File Generation (Priority: P1)

**Goal**: Create structured action files in Needs_Action/ for each detected email

**Independent Test**: Send test email, verify EMAIL_*.md file appears in Needs_Action/ with correct frontmatter

**Note**: Depends on US3 (detection must work first) and US4 (duplicate detection)

### Implementation for User Story 3 (continued)

- [ ] T013 Implement action file creation in `check_emails()` function in `bronze/gmail_watcher.py`: generate content with YAML frontmatter (type: email, from, subject, received timestamp, priority: high, status: pending, gmail_id), body with email content preview and suggested actions, write to `NEEDS_ACTION / f"EMAIL_{gmail_id[:8]}.md"`
- [ ] T014 Add filename sanitization for email subjects that might contain special characters when creating action file names

**Checkpoint**: Action files created with correct format and metadata

---

## Phase 8: User Story 5 - Email Processing Agent Skill (Priority: P2)

**Goal**: Document processing rules for the AI Employee to follow when handling email action files

**Independent Test**: Create email action file manually, follow skill instructions, verify correct processing

### Implementation for User Story 5

- [ ] T015 Create `bronze/AI_Employee_Vault/Needs_Action/SKILL_EmailProcessor.md` with: Skill Name (Email Processor v1.0), Purpose (process email action files from Needs_Action), Trigger (manual invocation or scheduled check), Process Flow (list EMAIL_*.md in Needs_Action, for each: read frontmatter, analyze content for priority keywords, apply Company_Handbook rules, update Dashboard, move to Done), Priority Detection rules (high: urgent/asap/critical/invoice/payment, medium: request/question/meeting, low: newsletter/notification), Response Guidelines (when to draft reply vs just log), Output (updated Dashboard.md, file moved to Done, activity logged), Error Handling (malformed action file → Logs/malformed, processing error → log and continue)

**Checkpoint**: Skill document complete with all processing rules

---

## Phase 9: Error Resilience & Logging (Priority: P1)

**Goal**: Handle all error scenarios without crashing

**Independent Test**: Simulate various error conditions, verify watcher continues running

### Implementation

- [ ] T016 Add comprehensive error handling in `bronze/gmail_watcher.py`: wrap API calls in try/catch, handle authentication errors with token refresh, handle rate limit errors with exponential backoff, log all errors appropriately
- [ ] T017 Implement exponential backoff for API errors: start with 1s delay, multiply by 2 each retry up to 60s max, add jitter to prevent thundering herd
- [ ] T018 Add graceful shutdown handling: properly close API connections, log shutdown event, ensure Ctrl+C stops the watcher cleanly

**Checkpoint**: Watcher survives error scenarios and continues monitoring

---

## Phase 10: Testing Suite Implementation

**Goal**: Create comprehensive tests to validate functionality during implementation

### Unit Tests

- [ ] T026 Create `tests/test_gmail_service.py`: unit tests for `get_gmail_service()` function including mock authentication, token refresh, and error handling
- [ ] T027 Create `tests/test_email_detection.py`: unit tests for `check_emails()` function including mock Gmail API responses, email parsing, and logging
- [ ] T028 Create `tests/test_duplicate_detection.py`: unit tests for `load_processed_ids()` and `save_processed_id()` functions including file I/O, ID lookup, and persistence
- [ ] T029 Create `tests/test_action_file_generation.py`: unit tests for action file creation including YAML frontmatter validation, content formatting, and file writing

### Integration Tests

- [ ] T030 Create `tests/test_full_workflow.py`: integration test simulating the complete email detection and action file creation process
- [ ] T031 Create `tests/test_duplicate_prevention.py`: integration test verifying duplicate emails are not re-processed
- [ ] T032 Create `tests/test_error_handling.py`: integration test verifying the system handles API errors gracefully

### Validation Tests

- [ ] T033 Create `tests/test_validation.py`: tests to validate that action files have correct format, required fields, and proper structure
- [ ] T034 Create `tests/test_performance.py`: performance tests to validate processing speed and resource usage under load
- [ ] T035 Create `tests/test_security.py`: tests to validate secure credential handling and proper file permissions

---

## Phase 11: User Story 6 - End-to-End Validation (Priority: P2)

**Goal**: Verify complete email workflow with test scenarios

**Independent Test**: Send test email, verify action file creation, process with AI, confirm Dashboard update

**Note**: Depends on all previous user stories

### Implementation for User Story 6

- [ ] T036 Start watcher (`python bronze/gmail_watcher.py`), send test email marked as important to monitored account, wait 2 minutes, verify EMAIL_*.md file created in `bronze/AI_Employee_Vault/Needs_Action/`
- [ ] T037 Verify action file has correct frontmatter (type, from, subject, received, priority, status, gmail_id) and body content
- [ ] T038 Stop watcher with Ctrl+C and verify clean shutdown with no errors in `bronze/AI_Employee_Vault/Logs/gmail_errors.log`
- [ ] T039 Test duplicate prevention: send same email again, verify no duplicate action file created
- [ ] T040 Run automated test suite: execute all unit and integration tests, verify all tests pass

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final deliverables

- [ ] T041 [P] Create `bronze/README-Module3.md` with: prerequisites (Python 3.13+, Google Cloud account, Gmail API enabled), setup steps (enable API, get credentials, install deps, configure .env, run initial auth), how the watcher works (polls Gmail, creates action files, prevents duplicates), file structure, testing guide (send important email), troubleshooting (common issues from spec), next steps (Silver tier features)
- [ ] T042 Verify `.env.example` includes VAULT_PATH and GMAIL_CHECK_INTERVAL and `.gitignore` excludes `.env`, `credentials.json`, and `token.json`
- [ ] T043 Run quickstart.md validation: walk through all steps in `specs/bronze/003-gmail-watcher/quickstart.md` and confirm each completes successfully
- [ ] T044 Execute full test suite and document results: run all tests (T026-T035), record pass/fail status, document any issues found

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 and credentials.json existence
- **US2 (Phase 4)**: Depends on Phase 1 — can run parallel with US1
- **US3 (Phase 5)**: Depends on US1 (authentication must work)
- **US4 (Phase 6)**: Depends on Phase 2 — can run parallel with US3
- **US3 Continued (Phase 7)**: Depends on US3 and US4
- **US5 (Phase 8)**: Independent — markdown file only, can run anytime after Phase 2
- **Error Resilience (Phase 9)**: Can run parallel with any other phase
- **Testing (Phase 10)**: Can run parallel with other phases as implementation progresses
- **US6 (Phase 11)**: Depends on US1 + US3 + US4 + US5 + Testing implementation
- **Polish (Phase 12)**: Depends on all phases complete

### Parallel Opportunities

- T002 and T003 can run in parallel (Setup phase)
- US2 (T007-T008) can run in parallel with US1 (T005-T006)
- US4 (T011-T012) can run in parallel with US3 (T009-T010)
- US5 (T015, Agent Skill) can run in parallel with other phases (separate file)
- Error resilience (T016-T018) can run in parallel with other phases
- Testing suite (T026-T035) can run in parallel with implementation
- T041 and T042 can run in parallel (Polish phase)

---

## Implementation Strategy

### MVP First (US1 + US3 + US4)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational skeleton (T004)
3. Complete Phase 3: US1 authentication (T005-T006)
4. Complete Phase 5: US3 email detection (T009-T010)
5. Complete Phase 6: US4 duplicate detection (T011-T012)
6. Complete Phase 7: US3 action file creation (T013-T014)
7. **STOP and VALIDATE**: Send test email, verify action file created

### Incremental Delivery

1. Setup + Skeleton → Script runs, fails auth initially
2. Add US1 → Authentication works, API accessible
3. Add US3 → Detects emails, logs events (MVP functional)
4. Add US4 → Prevents duplicates (production-ready)
5. Add US5 → Processing skill (AI Employee ready)
6. Add Error Handling → Robust operation (reliable)
7. Add Testing → Validation during dev (quality assurance)
8. Add US6 → Full validation (complete)
9. Add Polish → Documentation complete

---

## Summary

- **Total tasks**: 44
- **Completed**: 0/44
- **Status**: TODO

- **US1 (Gmail API)**: 2 tasks (T005-T006)
- **US2 (Dependencies)**: 2 tasks (T007-T008)
- **US3 (Email Monitoring)**: 4 tasks (T009-T014)
- **US4 (Duplicate Detection)**: 2 tasks (T011-T012)
- **US5 (Agent Skill)**: 1 task (T015)
- **Testing Suite**: 10 tasks (T026-T035)
- **US6 (End-to-End Testing)**: 5 tasks (T036-T040)
- **Setup/Foundational**: 4 tasks (T001-T004, T016-T018)
- **Polish**: 4 tasks (T041-T044)
- **Parallel opportunities**: Testing suite runs parallel with implementation
- **Suggested MVP scope**: US1 + US3 + US4 + basic testing (authentication + detection + duplication prevention + validation)

## Notes

- Most tasks modify the same file (`bronze/gmail_watcher.py`) so must be developed incrementally
- US5 (SKILL_EmailProcessor.md) is the only fully parallel task (separate file)
- Testing tasks (T026-T035) can be implemented alongside functional tasks to validate during development
- US6 validation tasks (T036-T040) include both manual and automated testing
- Automated test tasks now included (T026-T035) to ensure quality during implementation