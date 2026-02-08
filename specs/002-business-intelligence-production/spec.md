# Feature Specification: Business Intelligence & Production System (Gold Module 2)

**Feature Branch**: `002-business-intelligence-production`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Gold Module 2: Business Intelligence & Production (20-25 hours) - Business goals tracking, weekly CEO briefing, Ralph Wiggum loop, error recovery, watchdog monitoring, cross-domain intelligence, audit logging, and documentation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Weekly CEO Briefing Generation (Priority: P1)

As a CEO/business owner, I want to receive an automated weekly briefing every Sunday at 11 PM that summarizes business performance, completed tasks, revenue status, and potential issues so I can stay informed without manual effort.

**Why this priority**: This is the core business value proposition - transforming raw operational data into actionable executive insights. Without this, the system is just task automation without intelligence.

**Independent Test**: Can be fully tested by running the weekly audit script manually and verifying a CEO briefing document is generated with revenue data, completed tasks, and actionable recommendations.

**Acceptance Scenarios**:

1. **Given** Sunday 11 PM arrives, **When** the weekly audit runs, **Then** a CEO briefing document is generated in `/Briefings/YYYY-MM-DD_CEO_Briefing.md` with sections for revenue summary, completed tasks, bottlenecks, and unused subscriptions.

2. **Given** Odoo contains revenue data for the current month, **When** the weekly audit queries Odoo, **Then** the briefing includes accurate revenue figures compared against monthly targets.

3. **Given** multiple tasks were completed in `/Done/` during the week, **When** the audit scans the folder, **Then** the briefing lists all completed tasks with timestamps and categories.

4. **Given** some subscriptions have not been used in 30+ days, **When** the audit analyzes subscription activity, **Then** the briefing flags these as potentially unused with cost implications.

---

### User Story 2 - Continuous Task Processing (Ralph Wiggum Loop) (Priority: P1)

As a system operator, I want tasks in `/Needs_Action/` to be processed continuously until the queue is empty so that work doesn't pile up and processing happens without manual intervention.

**Why this priority**: Core operational capability that ensures the AI employee works autonomously until all tasks are complete, directly enabling business efficiency.

**Independent Test**: Create 5 test tasks in `/Needs_Action/`, start the Ralph loop, and verify all tasks are processed and moved to `/Done/` without manual intervention.

**Acceptance Scenarios**:

1. **Given** 5 tasks exist in `/Needs_Action/`, **When** the Ralph loop starts, **Then** all 5 tasks are processed sequentially and moved to `/Done/`.

2. **Given** the Ralph loop is running, **When** new tasks are added mid-processing, **Then** the loop detects and processes the new tasks in the same run (up to max iterations).

3. **Given** a task fails to complete after processing, **When** the loop re-evaluates, **Then** it re-injects the prompt for another attempt (up to configured retry limit).

4. **Given** the loop has run 10 iterations, **When** tasks still remain, **Then** the loop stops and logs a warning for human review.

---

### User Story 3 - Watchdog Process Monitoring (Priority: P1)

As a system administrator, I want crashed processes to automatically restart so the system maintains high availability without manual intervention.

**Why this priority**: Production reliability is essential - without automatic recovery, any crash requires human intervention, defeating the purpose of automation.

**Independent Test**: Kill the orchestrator process and verify the watchdog detects the crash and restarts it within 60 seconds.

**Acceptance Scenarios**:

1. **Given** the orchestrator process crashes, **When** the watchdog detects the failure, **Then** the process is restarted automatically within 60 seconds.

2. **Given** a process has crashed 5 times in one hour, **When** a 6th crash occurs, **Then** the watchdog does not restart it and sends an alert to the Dashboard.

3. **Given** all monitored processes are running, **When** the watchdog performs a health check, **Then** the Dashboard shows "All services operational" status.

4. **Given** a service is down, **When** the Dashboard is viewed, **Then** the service shows as "Down" with last crash time and restart count.

---

### User Story 4 - Error Recovery with Graceful Degradation (Priority: P2)

As a system operator, I want failed operations to be retried with exponential backoff and queued when services are unavailable so that temporary failures don't result in lost work.

**Why this priority**: Improves system resilience, but not as critical as basic monitoring since some manual recovery is acceptable during early deployment.

**Independent Test**: Simulate a service outage (e.g., disconnect from Odoo), attempt an operation, verify it's queued, restore service, verify operation completes.

**Acceptance Scenarios**:

1. **Given** an MCP call fails, **When** the retry handler processes it, **Then** it retries with exponential backoff (1s, 2s, 4s, 8s...) up to 5 attempts.

2. **Given** a service (Odoo, Email) is unavailable, **When** an action requires that service, **Then** the action is queued to a fallback file for later processing.

3. **Given** a queued action exists and the service recovers, **When** the next processing cycle runs, **Then** the queued action is attempted again.

4. **Given** service status is being tracked, **When** a service fails 3 consecutive health checks, **Then** its status changes to "degraded" in the Dashboard.

---

### User Story 5 - Cross-Domain Intelligence Workflows (Priority: P2)

As a business owner, I want automated workflows that connect email, accounting, and social media so that business events trigger appropriate follow-up actions across systems.

**Why this priority**: This represents the "intelligence" in business intelligence - connecting domains creates compound value beyond individual automations.

**Independent Test**: Send a payment confirmation email, verify it triggers an invoice-paid update in Odoo, a milestone update, and a LinkedIn post draft.

**Acceptance Scenarios**:

1. **Given** a payment confirmation email arrives, **When** it's processed, **Then** the system marks the invoice as paid in Odoo, logs a milestone, and creates a LinkedIn post draft if it's a significant payment.

2. **Given** a project deadline is approaching (within 7 days), **When** the daily check runs, **Then** a reminder task is created and an alert appears on the Dashboard.

3. **Given** a new invoice is created in Odoo, **When** it's detected by the accounting watcher, **Then** a notification email is queued and the Dashboard is updated.

---

### User Story 6 - Business Goals Tracking (Priority: P2)

As a CEO, I want to define business goals (revenue targets, KPIs, deadlines) in a central document so the system can track progress and alert me to deviations.

**Why this priority**: Provides the reference data needed for meaningful briefings and alerts, but can be added after basic automation is working.

**Independent Test**: Set a monthly revenue target, wait for weekly audit, verify the briefing shows actual vs target revenue with variance.

**Acceptance Scenarios**:

1. **Given** Business_Goals.md defines a monthly revenue target of $50,000, **When** actual revenue is $40,000, **Then** the CEO briefing shows 80% achievement and highlights the $10,000 gap.

2. **Given** a project deadline is defined for "Project Alpha" on Feb 15, **When** it's Feb 10 and no completion is logged, **Then** the briefing lists this as an at-risk deadline.

3. **Given** a subscription list exists with monthly costs, **When** a subscription hasn't been used in 30 days, **Then** the briefing recommends reviewing/canceling it.

---

### User Story 7 - Structured Audit Logging (Priority: P3)

As a system administrator, I want all MCP calls and system actions logged in structured JSON format so I can troubleshoot issues and analyze system behavior.

**Why this priority**: Important for production debugging and compliance, but the system can function without it initially.

**Independent Test**: Trigger several system actions, verify JSON log files are created with all required fields, verify 90-day retention policy.

**Acceptance Scenarios**:

1. **Given** an MCP call is made, **When** the call completes (success or failure), **Then** a structured JSON log entry is written with timestamp, tool name, parameters, result, and duration.

2. **Given** today is a new day, **When** the first log entry is written, **Then** a new daily log file is created in the format `YYYY-MM-DD_audit.json`.

3. **Given** log files older than 90 days exist, **When** the daily cleanup runs, **Then** old log files are archived or deleted per retention policy.

---

### Edge Cases

- What happens when Odoo is unreachable during weekly audit? → Generate partial briefing with available data and note "Odoo data unavailable"
- How does the system handle corrupted task files in `/Needs_Action/`? → Move to `/Logs/malformed/` with error details
- What if the Ralph loop encounters the same failing task repeatedly? → Mark task as "stuck" after 3 attempts, move to `/Needs_Action_Review/`
- What happens if the watchdog itself crashes? → System relies on OS-level service manager (systemd/supervisor) to restart watchdog
- How are conflicting cross-domain triggers handled? → Process in order received, use timestamps to determine priority

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate weekly CEO briefings every Sunday at 11 PM local time
- **FR-002**: Weekly briefing MUST include revenue summary from Odoo (actual vs. target)
- **FR-003**: Weekly briefing MUST list all tasks completed during the week from `/Done/`
- **FR-004**: Weekly briefing MUST identify bottlenecks (tasks taking >48 hours to complete)
- **FR-005**: Weekly briefing MUST flag subscriptions unused for 30+ days
- **FR-006**: Ralph loop MUST process tasks continuously until `/Needs_Action/` is empty or max iterations (10) reached
- **FR-007**: Ralph loop MUST re-inject prompts for incomplete tasks (max 3 retries per task)
- **FR-008**: Watchdog MUST monitor orchestrator, gmail_watcher, approval_watcher, linkedin_watcher processes
- **FR-009**: Watchdog MUST auto-restart crashed processes within 60 seconds of detection
- **FR-010**: Watchdog MUST limit restarts to 5 per hour per process to prevent restart storms
- **FR-011**: Retry handler MUST implement exponential backoff (1s base, max 5 retries)
- **FR-012**: Graceful degradation MUST queue actions when target service is unavailable
- **FR-013**: Cross-domain workflow MUST connect payment emails → Odoo invoice update → milestone → LinkedIn post
- **FR-014**: Cross-domain workflow MUST connect deadlines → reminders → Dashboard alerts
- **FR-015**: Business goals file MUST support monthly revenue targets, KPI thresholds, subscription list, and project deadlines
- **FR-016**: Audit logger MUST write structured JSON logs for all MCP calls
- **FR-017**: Audit logger MUST create daily log files and enforce 90-day retention
- **FR-018**: Dashboard MUST display real-time status of all monitored services
- **FR-019**: Dashboard MUST show service health, restart counts, and last error time

### Key Entities

- **CEO Briefing**: Weekly report document containing revenue summary, completed tasks, bottlenecks, and recommendations
- **Business Goals**: Configuration document defining targets (revenue, KPIs), subscriptions, and deadlines
- **Service Status**: Runtime state of each monitored process (healthy, degraded, down, restart count)
- **Audit Log Entry**: Structured record of a system action (timestamp, action type, parameters, result, duration)
- **Queued Action**: Deferred operation stored when target service is unavailable

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CEO briefing auto-generates every Sunday at 11 PM with all required sections (revenue, tasks, bottlenecks, subscriptions)
- **SC-002**: Ralph loop successfully processes 5+ consecutive tasks without manual intervention
- **SC-003**: Watchdog detects and restarts crashed services within 60 seconds (verified 3 times)
- **SC-004**: Odoo revenue data appears accurately in weekly briefing (within 1% of actual)
- **SC-005**: At least 3 cross-domain workflows function end-to-end (payment→invoice, deadline→reminder, email→accounting)
- **SC-006**: All system actions are logged to structured JSON with complete audit trail
- **SC-007**: System maintains 99% uptime with automatic recovery (measured over 1 week)
- **SC-008**: Complete documentation exists: Architecture.md, Lessons_Learned.md, README-Gold-Complete.md
- **SC-009**: Demo video (12-15 min) demonstrates all major features working together

## Assumptions

- Odoo MCP server is configured and accessible for revenue/invoice queries
- Email MCP server (Gmail API) is functional for email-triggered workflows
- LinkedIn posting MCP integration exists from Silver tier
- System runs on a server capable of scheduled tasks (cron or equivalent)
- Local filesystem is used for task queues (no external message broker required)
- Python 3.9+ runtime environment available
- Claude Code CLI is installed and configured with appropriate permissions

## Out of Scope

- Real-time push notifications (email/SMS alerts) - Dashboard polling is sufficient
- Multi-tenant support - single business/user deployment
- Historical trend analysis beyond current week - future enhancement
- Custom reporting templates - fixed briefing format for MVP
- Mobile-specific Dashboard interface - web/desktop browser access only
- Integration with services beyond Odoo, Gmail, LinkedIn, Facebook
