# Feature Specification: Foundation Setup

**Feature Branch**: `001-foundation-setup`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Module 1: Vault Structure + Claude Code Integration for Personal AI Employee"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Vault Structure (Priority: P1)

As a developer, I want a structured Obsidian vault so that my AI Employee has organized storage for tasks, completed work, and logs.

**Why this priority**: The vault is the foundational storage layer. Nothing else works without it.

**Independent Test**: Create the vault directory with all 4 subfolders and verify each is readable/writable from the command line.

**Acceptance Scenarios**:

1. **Given** no vault exists, **When** the setup process runs, **Then** a directory named `AI_Employee_Vault/` is created with subdirectories: `Inbox/`, `Needs_Action/`, `Done/`, `Logs/`
2. **Given** the vault exists, **When** Claude Code attempts to list files in each folder, **Then** no permission errors occur and all folders are accessible
3. **Given** the vault is opened in Obsidian, **When** the user navigates the sidebar, **Then** all 4 folders appear and are browsable

---

### User Story 2 - Create Dashboard (Priority: P1)

As a user, I want a real-time status dashboard so that I can see my AI Employee's current state and recent activity at a glance.

**Why this priority**: The dashboard is the primary interface for monitoring the AI Employee. It validates that the system is operational.

**Independent Test**: Create Dashboard.md, then programmatically update its `last_updated` timestamp and verify the change persists.

**Acceptance Scenarios**:

1. **Given** the vault exists, **When** Dashboard.md is created, **Then** it contains sections for System Status, Recent Activity, Pending Actions, and Quick Stats
2. **Given** Dashboard.md exists, **When** Claude Code updates the `last_updated` frontmatter field, **Then** the new timestamp is saved and readable
3. **Given** Dashboard.md is open in Obsidian, **When** the file is viewed, **Then** all sections render correctly as formatted markdown

---

### User Story 3 - Create Company Handbook (Priority: P1)

As a user, I want behavior rules for my AI Employee so that it operates according to my preferences for communication, finances, privacy, and error handling.

**Why this priority**: The handbook defines operational boundaries. The AI Employee must have rules before processing any tasks.

**Independent Test**: Create Company_Handbook.md and verify it contains at least 7 distinct rule categories that are clear and actionable.

**Acceptance Scenarios**:

1. **Given** the vault exists, **When** Company_Handbook.md is created, **Then** it contains rules for: Core Principles, Communication, Financial, File Management, Privacy & Security, Work Hours, and Error Handling
2. **Given** the handbook exists, **When** a user reads any rule section, **Then** each rule is unambiguous and actionable (no vague directives)
3. **Given** the handbook exists, **When** a user wants to customize rules, **Then** rules can be edited in-place without breaking the document structure

---

### User Story 4 - Test File Workflow (Priority: P2)

As a developer, I want to verify Claude Code can read, process, and move files within the vault so that the end-to-end automation pipeline works correctly.

**Why this priority**: This validates the core automation loop (detect-process-complete) that all watchers depend on.

**Independent Test**: Place a test task file in `Needs_Action/`, have Claude Code process it, and verify it moves to `Done/` with Dashboard updated.

**Acceptance Scenarios**:

1. **Given** a file `TEST_Task.md` exists in `Needs_Action/`, **When** Claude Code processes the file, **Then** it reads the content and extracts action items
2. **Given** processing completes, **When** the file is finalized, **Then** `TEST_Task.md` is moved to `Done/`
3. **Given** a file was processed, **When** Dashboard.md is checked, **Then** it shows an updated timestamp, incremented task count, and the task in Recent Activity

---

### User Story 5 - Document Agent Skill (Priority: P2)

As a developer, I want reusable AI capabilities documented as Skills so that I can scale my AI Employee's abilities and maintain consistent behavior.

**Why this priority**: Skills define repeatable AI behaviors. They are needed for consistent task processing but not for initial vault setup.

**Independent Test**: Create SKILLS.md with one fully documented skill and verify it contains all required sections (name, purpose, trigger, process flow, input/output, error handling).

**Acceptance Scenarios**:

1. **Given** the vault exists, **When** SKILLS.md is created in `Needs_Action/`, **Then** it documents the "Basic Task Processor v1.0" skill with all required sections
2. **Given** the skill is documented, **When** Claude Code reads the skill definition, **Then** it can follow the process flow instructions to process task files
3. **Given** the skill defines error handling, **When** a malformed file is encountered, **Then** the skill specifies moving it to `Logs/malformed/`

---

### Edge Cases

- What happens when the vault directory already exists during setup? (Preserve existing content, only create missing subdirectories)
- What happens when Dashboard.md is open in Obsidian while Claude Code writes to it? (Write should succeed; Obsidian auto-reloads)
- What happens when a file in `Needs_Action/` has no frontmatter? (Treat as plain task, process based on content, log warning)
- What happens when `Done/` already contains a file with the same name? (Append timestamp suffix to avoid overwriting)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create an Obsidian vault directory named `AI_Employee_Vault/` with subdirectories `Inbox/`, `Needs_Action/`, `Done/`, and `Logs/`
- **FR-002**: System MUST create `Dashboard.md` at the vault root with YAML frontmatter containing `last_updated` and sections for System Status, Recent Activity, Pending Actions, and Quick Stats
- **FR-003**: System MUST create `Company_Handbook.md` at the vault root with versioned frontmatter and at least 7 rule categories (Core Principles, Communication, Financial, File Management, Privacy & Security, Work Hours, Error Handling)
- **FR-004**: System MUST support reading any markdown file from any vault subdirectory without permission errors
- **FR-005**: System MUST support writing/updating markdown files including frontmatter fields (timestamps, counters)
- **FR-006**: System MUST support moving files between vault subdirectories (e.g., `Needs_Action/` to `Done/`)
- **FR-007**: System MUST update `Dashboard.md` after each task processing event with: updated timestamp, incremented task count, and entry in Recent Activity
- **FR-008**: System MUST create `SKILLS.md` documenting at least one agent skill with sections for name, purpose, trigger, process flow, input format, output, and error handling
- **FR-009**: System MUST append a timestamp suffix when moving a file to `Done/` if a file with the same name already exists
- **FR-010**: System MUST create a `Logs/malformed/` subdirectory for files that cannot be parsed

### Key Entities

- **Task File**: A markdown file in `Needs_Action/` with optional YAML frontmatter (type, priority, created) and action items. Moves through `Needs_Action/` -> `Done/` lifecycle.
- **Dashboard**: A single markdown file (`Dashboard.md`) at vault root tracking system status, recent activity, pending actions, and aggregate stats.
- **Company Handbook**: A single markdown file (`Company_Handbook.md`) at vault root defining AI behavior rules across 7+ categories.
- **Agent Skill**: A documented capability in `SKILLS.md` defining a repeatable AI behavior with trigger, process flow, and error handling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Vault contains exactly 4 subdirectories accessible without permission errors
- **SC-002**: Dashboard.md renders correctly in Obsidian and can be programmatically updated (timestamp changes persist)
- **SC-003**: Company_Handbook.md contains 7 or more distinct, actionable rule categories
- **SC-004**: A test file placed in `Needs_Action/` is successfully read, processed, and moved to `Done/` in a single workflow run
- **SC-005**: Dashboard reflects task processing activity (updated timestamp, incremented count, activity entry) after test workflow
- **SC-006**: At least 1 agent skill is fully documented with all required sections
- **SC-007**: No credentials, tokens, or secrets are stored in any vault file or version-controlled directory

## Assumptions

- Obsidian v1.10.6+ is installed and can open local vault directories
- Claude Code has read/write/move permissions on the local filesystem where the vault resides
- The vault is stored locally (not in a cloud-synced folder during active testing)
- Python is not required for Module 1 (watchers are Module 2/3)
- File operations use standard filesystem commands (no database or API needed)
- The user will customize Company_Handbook.md rules to their preferences after initial creation

## Constraints

- No external API calls or network dependencies in Module 1
- No Python scripts (deferred to Module 2)
- No Gmail integration (deferred to Module 3)
- Vault must remain compatible with standard Obsidian (no custom plugins required)
- No credentials or secrets in version control; use `.env` and `.gitignore`

## Dependencies

- Obsidian installed locally
- Claude Code installed and authenticated
- Terminal/shell access for file operations
- Git for version control (vault directory added to `.gitignore`)
