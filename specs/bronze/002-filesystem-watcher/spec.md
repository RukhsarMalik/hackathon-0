# Feature Specification: File System Watcher

**Feature Branch**: `002-filesystem-watcher`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Module 2: Automated File Drop Detection — Monitor /Inbox/ folder and create tasks automatically"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Continuous File Monitoring (Priority: P1)

As a user, I want new files dropped into my Inbox folder to be automatically detected so that tasks are created without manual intervention.

**Why this priority**: This is the core automation capability. Without file detection, no tasks can be auto-created.

**Independent Test**: Start the watcher, drop a file into Inbox/, and verify an action file appears in Needs_Action/ within seconds.

**Acceptance Scenarios**:

1. **Given** the watcher is running and monitoring Inbox/, **When** a new file is dropped into Inbox/, **Then** the watcher logs "File detected: [filename]" and creates a corresponding action file in Needs_Action/
2. **Given** the watcher is running, **When** multiple files are dropped in rapid succession, **Then** each file gets its own action file without any being missed
3. **Given** the watcher is running, **When** a directory is created in Inbox/, **Then** the watcher ignores it (only processes files)

---

### User Story 2 - Action File Generation (Priority: P1)

As a user, I want each detected file to produce a structured action file so that the AI Employee can process it according to defined rules.

**Why this priority**: Action files are the interface between the watcher and the AI Employee. They must contain enough metadata for intelligent processing.

**Independent Test**: Drop a file into Inbox/ and verify the resulting action file in Needs_Action/ has correct frontmatter (type, original_name, size, detected, status) and suggested actions.

**Acceptance Scenarios**:

1. **Given** a text file "report.txt" (500 bytes) is dropped in Inbox/, **When** the watcher processes it, **Then** an action file `FILE_report.md` is created in Needs_Action/ with frontmatter containing `type: file_drop`, `original_name: report.txt`, `size: 500`, `detected: [ISO timestamp]`, `status: pending`
2. **Given** a file with spaces or special characters in the name is dropped, **When** the watcher processes it, **Then** the action file is created with a sanitized filename while preserving the original name in frontmatter
3. **Given** any file type (.txt, .md, .pdf, .csv, .docx, etc.) is dropped, **When** the watcher processes it, **Then** the action file includes the file extension in the details section

---

### User Story 3 - Error Resilience (Priority: P1)

As a developer, I want the watcher to handle errors gracefully so that it never crashes and continues monitoring after encountering problems.

**Why this priority**: A watcher that crashes on edge cases defeats the purpose of continuous monitoring. Resilience is essential for autonomous operation.

**Independent Test**: Trigger each error scenario (oversized file, permission error, malformed filename) and verify the watcher continues running with errors logged.

**Acceptance Scenarios**:

1. **Given** a file larger than 10MB is dropped in Inbox/, **When** the watcher detects it, **Then** the file is moved to Logs/quarantine/, an error is logged, and the watcher continues running
2. **Given** a file with unreadable permissions is dropped, **When** the watcher attempts to process it, **Then** an error is logged with the filename and error description, and the watcher continues
3. **Given** the Needs_Action/ directory is temporarily unavailable, **When** the watcher tries to create an action file, **Then** an error is logged and the watcher retries on the next detection cycle
4. **Given** any unexpected error occurs during file processing, **When** the error is caught, **Then** it is logged to both console and the error log file, and the watcher continues

---

### User Story 4 - File Processing Agent Skill (Priority: P2)

As an AI Employee, I want documented instructions for processing file drop action files so that I can handle different file types intelligently.

**Why this priority**: The skill provides the processing logic that completes the automation loop. It builds on US1-3 which provide the detection layer.

**Independent Test**: Create a file_drop action file manually, follow the skill instructions, and verify the file is processed correctly with Dashboard updated.

**Acceptance Scenarios**:

1. **Given** an action file with `type: file_drop` for a .txt file exists in Needs_Action/, **When** the AI Employee follows the skill instructions, **Then** it reads the first 500 characters, checks for priority keywords (urgent, invoice, payment, todo), updates Dashboard, and moves the file to Done/
2. **Given** an action file for a .csv file exists, **When** the AI Employee processes it, **Then** it reads the header row, counts rows/columns, checks for financial keywords, and flags if financial data is detected
3. **Given** an action file for an unknown file type exists, **When** the AI Employee processes it, **Then** it flags the file for manual review and logs the unknown extension

---

### User Story 5 - Graceful Lifecycle Management (Priority: P2)

As a developer, I want the watcher to start and stop cleanly so that it integrates well with system operations.

**Why this priority**: Clean startup/shutdown prevents resource leaks and data corruption. Important for reliability but not core functionality.

**Independent Test**: Start the watcher, verify startup log, press Ctrl+C, and verify shutdown log with no errors.

**Acceptance Scenarios**:

1. **Given** the watcher is started, **When** it initializes, **Then** it logs "Starting File System Watcher..." and the monitored directory path
2. **Given** the watcher is running, **When** the user presses Ctrl+C, **Then** it logs "Shutting down watcher...", stops the observer, and exits cleanly with no error output
3. **Given** the watcher is started, **When** the monitored Inbox/ directory does not exist, **Then** it logs an error and exits with a clear message rather than crashing

---

### Edge Cases

- What happens when two files with the same name are dropped in quick succession? (Second action file gets a timestamp suffix to avoid overwriting)
- What happens when a file is dropped and immediately deleted before the watcher reads its size? (Log error, skip file, continue monitoring)
- What happens when the watcher is restarted while files exist in Inbox/? (Existing files are not re-processed; only new files trigger events)
- What happens when disk space is critically low? (Log error, continue monitoring, do not create action file)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST continuously monitor the Inbox/ directory for new file creation events
- **FR-002**: System MUST create an action file in Needs_Action/ for each new file detected, named `FILE_[sanitized_stem].md`
- **FR-003**: Action files MUST contain YAML frontmatter with fields: `type` (file_drop), `original_name`, `size` (bytes), `detected` (ISO timestamp), `status` (pending)
- **FR-004**: Action files MUST contain a body with file details (name, size, type/extension) and suggested action checkboxes
- **FR-005**: System MUST log all file detection events to both console and a log file at Logs/watcher_errors.log
- **FR-006**: System MUST move files larger than 10MB to Logs/quarantine/ instead of creating action files
- **FR-007**: System MUST sanitize filenames containing special characters when creating action file names, while preserving original names in frontmatter
- **FR-008**: System MUST handle all errors without crashing, logging each error with timestamp and description
- **FR-009**: System MUST shut down gracefully on Ctrl+C (KeyboardInterrupt), stopping the file observer and logging the shutdown
- **FR-010**: System MUST ignore directory creation events (only process file events)
- **FR-011**: System MUST read vault path configuration from environment variables with a sensible default
- **FR-012**: A File Processing Agent Skill document MUST exist with processing rules for .txt/.md, .pdf, .csv, and unknown file types

### Key Entities

- **Watched File**: Any file created in the Inbox/ directory. Has attributes: name, size, extension, creation timestamp. Triggers action file creation.
- **Action File**: A markdown file in Needs_Action/ representing a detected file drop. Contains structured frontmatter and suggested processing steps. Named `FILE_[stem].md`.
- **Quarantined File**: A file exceeding 10MB, moved from Inbox/ to Logs/quarantine/ with an error log entry.
- **Agent Skill (File Processor)**: A markdown document defining processing rules for different file types, referenced by the AI Employee during task execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Watcher detects and creates action files for 100% of files dropped in Inbox/ (excluding >10MB files which are quarantined)
- **SC-002**: Action files are created within 5 seconds of file detection
- **SC-003**: Watcher runs continuously for at least 1 hour without crashing, even when encountering error scenarios
- **SC-004**: All 4 test file types (.txt, .md, .pdf, .csv) produce correctly formatted action files
- **SC-005**: Files over 10MB are quarantined with no action file created
- **SC-006**: Graceful shutdown completes within 5 seconds of Ctrl+C
- **SC-007**: Error log captures all error events with timestamps
- **SC-008**: File Processing Agent Skill covers at least 4 file type categories with clear processing rules

## Assumptions

- Module 1 (Foundation Setup) is complete — vault directory structure exists
- Python 3.13+ is installed on the system
- The watchdog and python-dotenv libraries can be installed via pip
- The vault is stored locally (not on a network drive or cloud-synced folder during active monitoring)
- Only one instance of the watcher runs at a time (no concurrency handling needed)
- Files dropped in Inbox/ are complete when they appear (no partial upload handling)

## Constraints

- No Gmail or email integration (deferred to Module 3)
- No MCP servers
- No process management (PM2) — bonus only, not in scope
- Watcher script runs under `bronze/` directory structure
- No credentials or secrets in version control

## Dependencies

- Module 1 complete (vault structure with Inbox/, Needs_Action/, Done/, Logs/)
- Python 3.13+
- watchdog library
- python-dotenv library
- Dashboard.md and Company_Handbook.md from Module 1
