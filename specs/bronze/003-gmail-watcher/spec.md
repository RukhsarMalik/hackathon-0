# Feature Specification: Gmail Watcher

**Feature Branch**: `003-gmail-watcher`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Module 3: Email Monitoring & Task Creation — Monitor Gmail for important emails and automate triage"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gmail API Setup (Priority: P1)

As a developer, I want secure access to Gmail API so that my AI Employee can read emails.

**Why this priority**: This is the foundational requirement for all email functionality. Without API access, no email monitoring can occur.

**Independent Test**: Complete OAuth 2.0 flow with credentials.json and token.json, then make a test API call to get user profile information.

**Acceptance Scenarios**:

1. **Given** Google Cloud project with Gmail API enabled, **When** OAuth 2.0 credentials are configured, **Then** credentials.json and token.json are generated successfully
2. **Given** valid credentials, **When** Gmail API service is initialized, **Then** API calls return expected user information without authentication errors
3. **Given** OAuth tokens exist, **When** API credentials expire, **Then** tokens are refreshed automatically without user intervention

---

### User Story 2 - Install Gmail Dependencies (Priority: P1)

As a developer, I want Gmail API libraries installed so that the watcher can access email.

**Why this priority**: Dependencies must be available before any Gmail functionality can be implemented.

**Independent Test**: Install required packages and verify imports work without errors.

**Acceptance Scenarios**:

1. **Given** system without Gmail dependencies, **When** pip install command is run, **Then** all required packages are installed successfully
2. **Given** installed packages, **When** import statements are executed, **Then** no ImportError exceptions occur
3. **Given** installed dependencies, **When** version conflicts exist, **Then** compatible versions are resolved automatically

---

### User Story 3 - Create Gmail Watcher Script (Priority: P1)

As a system, I want to monitor Gmail for important messages so that tasks are created automatically.

**Why this priority**: This is the core functionality of the email monitoring system. Without this, no automated task creation occurs.

**Independent Test**: Start the watcher, send an important email, and verify an action file appears in Needs_Action/ within 2 minutes.

**Acceptance Scenarios**:

1. **Given** the watcher is running and monitoring Gmail, **When** an important unread email arrives, **Then** the watcher logs "Email detected: [subject]" and creates a corresponding action file in Needs_Action/
2. **Given** the watcher is running, **When** multiple important emails arrive simultaneously, **Then** each email gets its own action file without any being missed
3. **Given** the watcher is running, **When** API rate limits are approached, **Then** exponential backoff is applied to prevent quota violations

---

### User Story 4 - Implement Duplicate Detection (Priority: P1)

As a system, I want to avoid processing the same email twice so that tasks aren't duplicated.

**Why this priority**: Duplicate detection prevents workflow chaos and maintains data integrity in the system.

**Independent Test**: Process an email, restart the watcher, and verify the same email is not re-processed.

**Acceptance Scenarios**:

1. **Given** an email has been processed and its ID stored, **When** the same email appears again in Gmail, **Then** no duplicate action file is created
2. **Given** the processed email IDs file exists, **When** the watcher starts, **Then** it loads previously processed IDs without errors
3. **Given** many processed emails over time, **When** the ID list grows large, **Then** lookup performance remains acceptable (<100ms for 10k entries)

---

### User Story 5 - Create Email Processing Agent Skill (Priority: P2)

As an AI Employee, I want instructions for handling emails so that I can triage intelligently.

**Why this priority**: The skill provides the processing logic that completes the automation loop. It builds on US1-4 which provide the detection layer.

**Independent Test**: Create an email action file manually, follow the skill instructions, and verify the email is processed correctly with Dashboard updated.

**Acceptance Scenarios**:

1. **Given** an action file with `type: email` for an urgent message exists in Needs_Action/, **When** the AI Employee follows the skill instructions, **Then** it analyzes the content for priority keywords, updates Dashboard, and moves the file appropriately
2. **Given** an action file for a financial email exists, **When** the AI Employee processes it, **Then** it checks for payment/invoice keywords and flags if financial action is needed
3. **Given** an action file for an unknown sender exists, **When** the AI Employee processes it, **Then** it flags the email for manual review and logs the unknown sender

---

### User Story 6 - Test Complete Email Workflow (Priority: P2)

As a developer, I want to verify email automation works end-to-end so that I can trust the system.

**Why this priority**: End-to-end validation ensures all components work together as intended before deployment.

**Independent Test**: Send a test email, verify action file creation, process with AI, and confirm Dashboard update.

**Acceptance Scenarios**:

1. **Given** the watcher is running, **When** an important email is sent to the monitored account, **Then** an action file is created in Needs_Action/ within 2 minutes
2. **Given** an email action file exists, **When** the AI Employee processes it using the documented skill, **Then** the file moves to Done/ and Dashboard is updated with email activity
3. **Given** duplicate emails exist, **When** they are processed, **Then** only one action file is created and the duplicate is ignored

---

### Edge Cases

- What happens when the Gmail API quota is exceeded? (Apply exponential backoff and log error, continue monitoring)
- What happens when network connectivity is lost temporarily? (Log connection errors, retry with backoff, continue monitoring when restored)
- What happens when an email is deleted from Gmail before processing? (Log error, skip email, continue monitoring)
- What happens when the processed_emails.txt file becomes corrupted? (Create backup, regenerate from recent activity, continue monitoring)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate with Gmail API using OAuth 2.0 with scopes: `gmail.readonly` and `gmail.modify`
- **FR-002**: System MUST check Gmail every 120 seconds for emails matching query: "is:unread is:important"
- **FR-003**: System MUST create an action file in Needs_Action/ for each new email detected, named `EMAIL_[message_id_prefix].md`
- **FR-004**: Email action files MUST contain YAML frontmatter with fields: `type` (email), `from`, `subject`, `received` (ISO timestamp), `priority` (high/medium/low), `status` (pending), `gmail_id`
- **FR-005**: Email action files MUST contain a body with email content preview, sender details, and suggested action checkboxes
- **FR-006**: System MUST track processed message IDs in `Logs/processed_emails.txt` to prevent duplicate processing
- **FR-007**: System MUST implement exponential backoff for Gmail API rate limiting (start at 1s, max 60s)
- **FR-008**: System MUST log all email detection events to both console and `Logs/gmail_errors.log`
- **FR-009**: System MUST handle all errors without crashing, logging each error with timestamp and description
- **FR-010**: System MUST shut down gracefully on Ctrl+C (KeyboardInterrupt), stopping the monitoring loop and logging the shutdown
- **FR-011**: System MUST read vault path configuration from environment variables with a sensible default
- **FR-012**: A Email Processing Agent Skill document MUST exist with priority detection rules for urgent/normal/low emails and response guidelines

### Key Entities

- **Monitored Email**: Any important unread email in the Gmail inbox. Has attributes: sender, subject, content, timestamp, labels. Triggers action file creation.
- **Email Action File**: A markdown file in Needs_Action/ representing a detected email. Contains structured frontmatter and suggested processing steps. Named `EMAIL_[id].md`.
- **Processed Email ID**: A Gmail message ID stored in Logs/processed_emails.txt to prevent re-processing of the same email.
- **Agent Skill (Email Processor)**: A markdown document defining processing rules for different email types, referenced by the AI Employee during task execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Watcher detects and creates action files for 95% of important unread emails (excluding those already processed)
- **SC-002**: Email action files are created within 3 minutes of email arrival (allowing for polling interval)
- **SC-003**: Watcher runs continuously for at least 24 hours without crashing, even when encountering API rate limits
- **SC-004**: All 3 email priority levels (high/medium/low) are correctly categorized based on content analysis
- **SC-005**: Duplicate detection prevents 100% of re-processing for emails with same message ID
- **SC-006**: Graceful shutdown completes within 5 seconds of Ctrl+C
- **SC-007**: Error log captures all API and connection errors with timestamps
- **SC-008**: Email Processing Agent Skill covers at least 4 categorization rules with clear processing guidelines

## Assumptions

- Module 1 (Foundation Setup) and Module 2 (File System Watcher) are complete — vault directory structure exists
- Google Cloud project is created with Gmail API enabled and OAuth 2.0 credentials obtained
- Python 3.13+ is installed on the system with internet access for API calls
- The google-api-python-client, google-auth, and python-dotenv libraries can be installed via pip
- The vault is stored locally (not on a network drive or cloud-synced folder during active monitoring)
- Only one instance of the watcher runs at a time (no concurrency handling needed)
- Emails arrive complete when they appear in Gmail (no partial email handling needed)
- User has granted appropriate OAuth permissions for Gmail access

## Constraints

- No email sending capability (deferred to Silver tier with MCP)
- No multiple email account support (single account only)
- No advanced email threading or conversation handling
- No attachment processing (text-only content preview)
- No IMAP/POP3 support (Gmail API only)
- Watcher script runs under `bronze/` directory structure
- No credentials or secrets in version control

## Dependencies

- Module 1 complete (vault structure with Needs_Action/, Done/, Logs/)
- Module 2 complete (existing file processing infrastructure)
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (credentials.json and token.json)
- Python 3.13+
- google-api-python-client library
- google-auth library
- python-dotenv library
- Dashboard.md and Company_Handbook.md from Module 1