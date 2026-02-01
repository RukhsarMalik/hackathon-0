# Silver Module 1: Orchestrator + LinkedIn Automation

## Feature Overview

**Feature**: Silver Module 1: Orchestrator + LinkedIn Automation
**Purpose**: Automated task processing and LinkedIn business promotion
**Time Estimate**: 8-10 hours
**Dependencies**: Bronze tier complete

## Description

This module implements an automated orchestrator that processes tasks in the Needs_Action folder without manual triggers, along with a LinkedIn watcher that creates scheduled business promotion posts. The system will include health monitoring and a unified startup script to manage all services.

## User Scenarios & Testing

### Scenario 1: Automatic Task Processing
**Actor**: Business Owner
**Trigger**: New task file appears in Needs_Action folder
**Steps**:
1. User places a task file (e.g., email, file_drop) in Needs_Action folder
2. Orchestrator detects the new file after a brief debounce period
3. Orchestrator automatically triggers Claude Code with appropriate processing prompt
4. Task is processed according to its type using appropriate skill
5. Processed task is moved to Done folder
6. Activity is logged and Dashboard is updated

**Success Criteria**: Task processed within 10 seconds of file creation

### Scenario 2: Scheduled LinkedIn Posts
**Actor**: Business Owner
**Trigger**: Scheduled time for LinkedIn post (Monday, Wednesday, Friday)
**Steps**:
1. LinkedIn watcher checks if it's time to create a post based on schedule
2. System generates post request file with appropriate topic for the day
3. Orchestrator picks up the post request and processes it using LinkedIn poster skill
4. Generated content is placed in Pending_Approval folder for human review
5. Business owner reviews and approves the post
6. Post is published via MCP system (in future module)

**Success Criteria**: Post request created at scheduled time with appropriate content

### Scenario 3: System Health Monitoring
**Actor**: System Administrator
**Trigger**: Hourly cron job or manual health check
**Steps**:
1. Health monitor checks if all required processes are running
2. System verifies dashboard has been updated recently
3. System identifies any tasks that have been pending for too long
4. Results are logged with clear pass/fail indicators
5. If issues are detected, appropriate alerts are generated

**Success Criteria**: All components healthy, or issues clearly identified

## Functional Requirements

### FR-1: Orchestrator Service
The system SHALL monitor the Needs_Action folder for new .md files.
The system SHALL implement a debounce mechanism to wait 10 seconds after file creation before processing.
The system SHALL exclude SKILL files from processing.
The system SHALL trigger Claude Code automatically when new task files are detected.
The system SHALL implement cooldown period of 30 seconds between processing cycles.
The system SHALL log all processing attempts with timestamps.
The system SHALL handle errors gracefully without stopping the entire service.
The system SHALL support multiple task types (file_drop, email, linkedin_post).

### FR-2: LinkedIn Watcher Service
The system SHALL schedule posts on Monday, Wednesday, and Friday at specified times.
The system SHALL generate different post types based on the day: weekly_update (Monday), tip_of_day (Wednesday), success_story (Friday).
The system SHALL track post history to prevent duplicate posts.
The system SHALL create post request files in the Needs_Action folder at scheduled times.
The system SHALL log all scheduled activities with timestamps.
The system SHALL verify that posts are not created multiple times on the same day.

### FR-3: LinkedIn Poster Skill
The system SHALL provide clear instructions for generating LinkedIn posts.
The system SHALL support three post types: weekly_update, tip_of_day, success_story.
The system SHALL generate posts with appropriate structure: hook, context, value, CTA, hashtags.
The system SHALL create approval request files in the Pending_Approval folder.
The system SHALL include post metadata (word count, hashtags, emojis) in approval files.
The system SHALL follow quality standards to ensure value-driven, engaging content.

### FR-4: System Startup Management
The system SHALL provide a single startup script to launch all services.
The system SHALL perform prerequisite checks before starting services (Python, Claude Code, vault existence).
The system SHALL start all watcher services (Gmail, File System, LinkedIn) in background.
The system SHALL start the orchestrator service in foreground.
The system SHALL implement graceful shutdown on Ctrl+C that stops all services.
The system SHALL create PID files for background processes for proper management.

### FR-5: Health Monitoring
The system SHALL check if all required processes are running (Gmail watcher, File System watcher, LinkedIn watcher, Orchestrator).
The system SHALL verify that the Dashboard has been updated within the last 24 hours.
The system SHALL identify tasks pending for more than 2 hours as "stuck".
The system SHALL log all health checks with clear status indicators.
The system SHALL return appropriate exit codes (0 for healthy, non-zero for issues).

## Non-functional Requirements

### Performance Requirements
- The orchestrator SHALL process new tasks within 10 seconds of file creation
- The system SHALL support 24+ hours of continuous operation without manual intervention
- The health check SHALL complete within 5 seconds

### Reliability Requirements
- The system SHALL continue operating if individual components fail
- The system SHALL log all errors for troubleshooting
- The system SHALL recover gracefully from transient failures

### Scalability Requirements
- The system SHALL handle multiple concurrent task files without conflicts
- The system SHALL support addition of new task types without code changes

## Success Criteria

### Quantitative Measures
- 100% of new task files processed within 10 seconds of creation
- 95% uptime over 24-hour period
- 0% duplicate LinkedIn posts generated
- Health checks return accurate status 100% of the time
- All services start successfully via startup script 100% of the time

### Qualitative Measures
- Generated LinkedIn posts are engaging and provide value to audience
- System operation is transparent with clear logging
- User experience is seamless with minimal manual intervention required
- Task processing follows appropriate skills based on file type

## Key Entities

### Task File
- Type: file identifier (email, file_drop, linkedin_post)
- Priority: processing priority level
- Status: pending, processing, completed
- Content: task-specific data and instructions

### Process
- Service: individual service (orchestrator, watchers)
- PID: process identifier for management
- Status: running, stopped, failed

### Post Request
- Topic: weekly_update, tip_of_day, success_story
- Schedule: day and time for creation
- Status: requested, generated, approved, published

## Assumptions

- Claude Code is installed and accessible via command line
- User has appropriate permissions to create and modify files in the vault directory
- System has internet connectivity for external services
- Company Handbook and other context files exist in vault
- MCP server functionality will be available in future modules

## Constraints

- Must run on both Mac/Linux and Windows systems
- Cannot make actual LinkedIn posts without MCP server (future module)
- Must preserve existing bronze tier functionality
- Limited to current file-based workflow without external database dependencies