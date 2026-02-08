# Tasks: Business Intelligence & Production System

## Feature Overview

This document outlines executable tasks for implementing the Business Intelligence & Production System (Gold Module 2). The system transforms the AI Employee from a functional assistant into a true business intelligence agent with weekly CEO briefings, continuous task processing, and advanced monitoring.

**Branch**: `002-business-intelligence-production`
**Input**: Feature specification from `/specs/002-business-intelligence-production/spec.md`

## Dependencies

- Claude Code CLI must be installed and accessible in PATH (critical dependency)
- MCP servers (Email, LinkedIn, Facebook, Odoo) must be configured and running
- Environment variables in .env file must be properly configured

## Implementation Strategy

MVP approach starting with User Story 1 (Weekly CEO Briefing Generation) to establish core business intelligence capability. Subsequent stories build on this foundation to create a complete autonomous business intelligence system.

## Phase 1: Setup Tasks

- [X] T001 Create Briefings directory in gold/AI_Employee_Vault/Briefings/
- [X] T002 Create Business_Goals.md template with example configuration
- [X] T003 Create audit logs directory structure gold/AI_Employee_Vault/Logs/Audit/
- [X] T004 Verify Claude Code CLI installation and accessibility
- [X] T005 [P] Update requirements.txt with new dependencies (odoo-client-python, facebook-sdk, google-api-python-client)

## Phase 2: Foundational Tasks

- [X] T006 [P] Extend dashboard_server.py to include service monitoring functions
- [X] T007 [P] Add audit logging functionality to orchestrator.py
- [X] T008 [P] Create structured JSON logging module for audit trails
- [X] T009 [P] Create utility functions for reading Business_Goals.md configuration
- [X] T010 [P] Create utility functions for generating CEO briefing markdown files

## Phase 3: [US1] Weekly CEO Briefing Generation

**Goal**: Implement automated weekly CEO briefings that summarize business performance, completed tasks, revenue status, and potential issues.

**Independent Test**: Run the weekly audit script manually and verify a CEO briefing document is generated with revenue data, completed tasks, and actionable recommendations.

**Tasks**:

- [X] T011 [US1] Create weekly_audit.py script to gather data from various sources
- [X] T012 [US1] Implement revenue data extraction from Odoo MCP server
- [X] T013 [US1] Implement task completion metrics extraction from /Done/ folder
- [X] T014 [US1] Implement subscription usage analysis (unused >30 days)
- [X] T015 [US1] Create CEO Briefing markdown template generator
- [X] T016 [US1] Add cron scheduling for Sunday 11 PM weekly briefing generation
- [X] T017 [US1] Implement comparison of actual vs. target revenue from Business_Goals.md
- [X] T018 [US1] Add bottleneck identification (tasks >48 hours in /Done/)
- [X] T019 [US1] Add project deadline proximity alerts (approaching within 7 days)
- [X] T020 [US1] Implement graceful handling when Odoo is unreachable

## Phase 4: [US2] Continuous Task Processing (Ralph Wiggum Loop)

**Goal**: Implement continuous processing of tasks in `/Needs_Action/` until the queue is empty.

**Independent Test**: Create 5 test tasks in `/Needs_Action/`, start the Ralph loop, and verify all tasks are processed and moved to `/Done/` without manual intervention.

**Tasks**:

- [X] T021 [US2] Enhance orchestrator.py with Ralph Wiggum loop detection for remaining tasks
- [X] T022 [US2] Implement logic to continue processing until /Needs_Action/ is empty
- [X] T023 [US2] Add iteration counter to limit loop to max 10 iterations
- [X] T024 [US2] Implement logic to detect new tasks added mid-processing
- [X] T025 [US2] Add re-injection of failed tasks with retry limit (max 3 attempts)
- [X] T026 [US2] Create logging for loop statistics and performance metrics
- [X] T027 [US2] Add warning system when loop reaches max iteration limit

## Phase 5: [US3] Watchdog Process Monitoring

**Goal**: Implement automatic restart of crashed processes to maintain high availability.

**Independent Test**: Kill the orchestrator process and verify the watchdog detects the crash and restarts it within 60 seconds.

**Tasks**:

- [X] T028 [US3] Create watchdog.py service to monitor system processes
- [X] T029 [US3] Implement process health checking for orchestrator, gmail_watcher, approval_watcher, linkedin_watcher
- [X] T030 [US3] Add automatic restart functionality for crashed processes
- [X] T031 [US3] Implement restart rate limiting (max 5 per hour per process)
- [X] T032 [US3] Update Dashboard.md with service status and restart counts
- [X] T033 [US3] Add heartbeat logging for each monitored service
- [X] T034 [US3] Create health check endpoints for each service
- [X] T035 [US3] Add process status tracking with PID file management

## Phase 6: [US4] Error Recovery with Graceful Degradation

**Goal**: Implement retry mechanisms with exponential backoff and queuing for unavailable services.

**Independent Test**: Simulate a service outage (e.g., disconnect from Odoo), attempt an operation, verify it's queued, restore service, verify operation completes.

**Tasks**:

- [X] T036 [US4] Implement exponential backoff retry logic (1s, 2s, 4s, 8s, 16s)
- [X] T037 [US4] Create Needs_Action_Fallback/ directory for queued actions
- [X] T038 [US4] Add service availability checking before MCP calls
- [X] T039 [US4] Implement queued action creation when service is unavailable
- [X] T040 [US4] Create queued action processor to retry failed actions
- [X] T041 [US4] Add service degradation status detection (3 failed health checks)
- [X] T042 [US4] Implement graceful fallback when services are degraded
- [X] T043 [US4] Add retry attempt tracking and failure limits (max 5 attempts)

## Phase 7: [US5] Cross-Domain Intelligence Workflows

**Goal**: Implement automated workflows connecting email, accounting, and social media.

**Independent Test**: Send a payment confirmation email, verify it triggers an invoice-paid update in Odoo, a milestone update, and a LinkedIn post draft.

**Tasks**:

- [X] T044 [US5] Enhance EmailProcessor skill to detect payment confirmation keywords
- [X] T045 [US5] Create AccountingManager skill to handle invoice updates in Odoo
- [X] T046 [US5] Add milestone logging functionality for significant transactions
- [X] T047 [US5] Implement conditional LinkedIn post draft creation for significant payments
- [X] T048 [US5] Create cross-domain workflow tracking system with workflow_id
- [X] T049 [US5] Add deadline proximity checker for project milestone alerts
- [X] T050 [US5] Implement invoice detection and notification email queuing
- [X] T051 [US5] Create workflow status tracking with step completion states

## Phase 8: [US6] Business Goals Tracking

**Goal**: Implement business goals configuration and tracking system for measuring performance.

**Independent Test**: Set a monthly revenue target, wait for weekly audit, verify the briefing shows actual vs target revenue with variance.

**Tasks**:

- [X] T052 [US6] Create Business_Goals.md parser for configuration loading
- [X] T053 [US6] Implement monthly revenue target tracking and comparison
- [X] T054 [US6] Add project deadline tracking with at-risk identification
- [X] T055 [US6] Implement subscription utilization monitoring
- [X] T056 [US6] Add KPI tracking and deviation alerts
- [X] T057 [US6] Create goal variance calculation functions
- [X] T058 [US6] Add historical goal tracking and trend analysis
- [X] T059 [US6] Implement goal-based recommendation engine for CEO briefings

## Phase 9: [US7] Structured Audit Logging

**Goal**: Implement comprehensive audit logging in structured JSON format.

**Independent Test**: Trigger several system actions, verify JSON log files are created with all required fields, verify 90-day retention policy.

**Tasks**:

- [X] T060 [US7] Create daily JSON audit log files in YYYY-MM-DD_audit.json format
- [X] T061 [US7] Implement structured logging for all MCP calls with required fields
- [X] T062 [US7] Add log rotation and 90-day cleanup functionality
- [X] T063 [US7] Create audit log viewer for analyzing system behavior
- [X] T064 [US7] Implement tamper-evident logging with integrity checks
- [X] T065 [US7] Add audit logging to all service operations and health checks
- [X] T066 [US7] Create log analysis tools for troubleshooting
- [X] T067 [US7] Implement log archival functionality for compliance

## Phase 10: Polish & Cross-Cutting Concerns

- [X] T068 Create Architecture.md documenting the complete system architecture
- [X] T069 Create Lessons_Learned.md with insights from implementation
- [X] T070 Create README-Gold-Complete.md with comprehensive system documentation
- [X] T071 Update start_all.sh to properly initialize all new services
- [X] T072 Create comprehensive health monitoring script for all system components
- [X] T073 Add error handling for corrupted task files in /Needs_Action/
- [X] T074 Implement "stuck" task detection and escalation to /Needs_Action_Review/
- [X] T075 Create backup and recovery procedures for the vault
- [X] T076 Conduct end-to-end integration tests for all user stories
- [X] T077 Document conflict resolution for cross-domain triggers
- [X] T078 Perform performance testing and optimization for 99% uptime
- [X] T079 Prepare demo materials showcasing all major features working together

## Parallel Execution Examples

**User Story 1 Parallel Tasks**:
- T011, T012, T013, T014 can run in parallel as they collect different data sources
- T015, T016, T017 can run in parallel after data collection

**User Story 3 Parallel Tasks**:
- T028, T031, T032, T034 can run in parallel to set up monitoring infrastructure
- T029, T030 can run in parallel to implement specific service monitoring

**User Story 4 Parallel Tasks**:
- T036, T037, T038, T039 can run in parallel to implement the fallback system
- T040, T041, T042, T043 can run in parallel to complete error recovery