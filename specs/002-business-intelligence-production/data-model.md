# Data Model: Business Intelligence & Production System

## Overview

This document defines the data structures and entities used in the Business Intelligence & Production System. The system uses a file-based architecture with YAML frontmatter for metadata, following the Obsidian vault approach.

## Core Entities

### 1. CEO Briefing Document

**File Pattern**: `YYYY-MM-DD_CEO_Briefing.md`

**YAML Frontmatter**:
```yaml
---
type: ceo_briefing
generation_date: YYYY-MM-DDTHH:MM:SS
week_start: YYYY-MM-DD
week_end: YYYY-MM-DD
period: "Week of YYYY-MM-DD"
generated_by: "Business_Intelligence_Agent_v1.0"
status: "completed" # draft|completed|archived
---
```

**Body Structure**:
- Executive Summary (high-level metrics)
- Revenue Analysis (actual vs. target)
- Task Completion Metrics (completed during period)
- Bottleneck Identification (tasks >48 hours)
- Subscription Utilization (unused >30 days)
- Cross-Domain Insights (connected workflow results)
- Recommendations (action items for human review)

### 2. Business Goals Configuration

**File**: `Business_Goals.md`

**YAML Frontmatter**:
```yaml
---
type: business_goals_config
last_updated: YYYY-MM-DDTHH:MM:SS
version: 1.0
---
```

**Body Structure**:
```yaml
monthly_revenue_target: 50000
current_month: 2026-02
revenue_targets:
  - month: 2026-02
    target: 50000
    description: "February revenue goal"
    stretch_goal: 60000

project_deadlines:
  - name: "Project Alpha"
    due_date: 2026-02-15
    description: "Critical milestone delivery"
    priority: high
    status: in_progress

subscriptions:
  - name: "Cloud Service Pro"
    monthly_cost: 199.99
    renewal_date: 2026-03-01
    last_used: 2026-01-28
    category: "Infrastructure"
    owner: "Engineering Team"

kpis:
  - name: "Customer Acquisition Rate"
    target: 10
    unit: "customers/month"
    description: "New customers acquired per month"
  - name: "Task Completion Rate"
    target: 95
    unit: "%"
    description: "Percentage of tasks completed within SLA"
```

### 3. Service Status Entity

**Stored in**: Dashboard.md and memory

**Structure**:
```javascript
{
  "service_name": "orchestrator",
  "status": "healthy|degraded|down", // Current operational state
  "last_heartbeat": "YYYY-MM-DDTHH:MM:SS", // Last successful operation
  "restart_count": 0, // Number of restarts in the last hour
  "uptime_seconds": 3600, // Duration since last restart
  "last_error": null, // Error message if status is degraded/down
  "health_checks_passed": 3, // Count of consecutive successful health checks
  "process_pid": 12345 // Process ID if running
}
```

### 4. Audit Log Entry

**File Pattern**: `YYYY-MM-DD_audit.json`

**JSON Structure**:
```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.sssZ",
  "event_type": "mcp_call|task_processed|service_monitor|error_event",
  "service": "orchestrator|gmail_watcher|linkedin_mcp|etc",
  "action": "process_task|send_email|post_to_linkedin|create_invoice",
  "correlation_id": "unique-task-or-session-id",
  "status": "success|failure|partial_success",
  "duration_ms": 1500,
  "input_size_bytes": 2048,
  "result_summary": "Brief description of what happened",
  "error_details": { /* Only present on failure */
    "type": "NetworkError|ValidationError|AuthenticationError",
    "message": "Detailed error message",
    "retry_count": 2
  },
  "tags": ["email", "critical", "external_api"],
  "user_context": "Context of triggering event"
}
```

### 5. Queued Action Entity

**File Pattern**: `PENDING_MCP_CALL_{timestamp}_{service}_{action}.md`

**YAML Frontmatter**:
```yaml
---
type: queued_action
status: pending_retry|hold_for_review|failed_permanently
created_at: YYYY-MM-DDTHH:MM:SS
target_service: "linkedin|facebook|email|odoo"
action_type: "post_to_linkedin|send_email|create_invoice|etc"
retry_count: 2
max_retries: 5
next_attempt_after: YYYY-MM-DDTHH:MM:SS
original_trigger: "APPROVAL_REPLY_abc123.md"
---
```

**Body**: Contains original action parameters in the same format as the original task

### 6. Cross-Domain Workflow Entity

**Triggers**: Email content with payment/transaction keywords

**Data Flow**:
```
Incoming Email (Payment Confirmation)
  -> Extract Transaction Details (via EmailProcessor)
  -> MCP Call: update_invoice_status (via AccountingManager)
  -> Log Milestone (to Dashboard)
  -> Conditional: Create LinkedIn Post Draft (if significant amount)
```

**Workflow Context**:
```yaml
workflow_id: "WF_PAYMENT_20260206_123456"
type: "payment_confirmation_workflow"
status: "initiated|processing|completed|failed"
steps:
  - name: "email_received"
    timestamp: "2026-02-06T10:00:00"
    details: "Payment confirmation email received"
    status: "completed"
  - name: "invoice_update"
    timestamp: "2026-02-06T10:01:00"
    service: "odoo_mcp"
    params: {invoice_id: "INV-2026-001", status: "paid"}
    status: "pending"
  - name: "milestone_log"
    timestamp: "2026-02-06T10:01:30"
    details: "Logged significant payment milestone"
    status: "pending"
  - name: "social_draft"
    timestamp: "2026-02-06T10:02:00"
    details: "LinkedIn post draft created for significant payment"
    status: "pending"
```

## Relationships

### File-Based Dependencies
- CEO Briefing ← Business Goals Configuration (for target comparison)
- Service Status ← Individual Service Processes (for monitoring)
- Audit Logs ↔ All System Components (bidirectional logging)
- Queued Actions ← Failed MCP Calls → Service Availability (retry mechanism)
- Cross-Domain Workflows ← Triggering Events → Multiple MCP Services

### State Transitions

#### Service Status Transitions
```
healthy --(failure detected)--> degraded --(persistent failure)--> down
  ↑                                      |                        |
  |--(recovery)--------------------------|--(manual restart)------|
```

#### Task Status Transitions
```
pending --> processing --> success/failed --> (if failed) queued_for_retry --> processing
                                              (or hold_for_review)
```

#### Workflow Status Transitions
```
initiated --> processing --> partially_completed --> completed
                           |                         |
                           --> failed --> retry_needed
                           |                         |
                           --> hold_for_human_input --|
```

## Validation Rules

### CEO Briefing
- Must contain data from at least the past week
- Revenue figures must be reconciled with actual MCP calls
- Cannot be generated more frequently than once per week
- Must include comparison against business goals if available

### Business Goals
- Monthly targets must be reasonable based on historical data
- Project deadlines cannot be in the past (except for tracking)
- Subscription costs must be reconciled periodically with actual charges
- KPI definitions must be quantifiable and measurable

### Service Status
- Downgrade to degraded after 3 consecutive health check failures
- Upgrade to healthy after 5 consecutive successful health checks
- Restart limits: maximum 5 restarts per hour per service
- Must log all status transitions with timestamps

### Audit Logs
- Must contain timestamps accurate to millisecond precision
- Must not expose sensitive data (credentials, personally identifiable information)
- Must implement 90-day automatic rotation and cleanup
- Must be tamper-evident with integrity checks

### Queued Actions
- Must preserve original action parameters exactly
- Retry intervals must use exponential backoff (1s, 2s, 4s, 8s, 16s...)
- Maximum retry attempts: 5 before marking as permanently failed
- Must maintain priority ordering when possible