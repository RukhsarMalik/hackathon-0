# Data Model: Silver Module 2

## Entities

### ApprovalRequest (Pending_Approval/APPROVAL_REPLY_*.md)

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| type | string | YAML frontmatter | Required. `email_approval` |
| to | string | YAML frontmatter | Required. Valid email address |
| subject | string | YAML frontmatter | Required. Non-empty |
| original_gmail_id | string | YAML frontmatter | Required. Links to original email |
| original_subject | string | YAML frontmatter | Original email subject for context |
| created_date | ISO datetime | YAML frontmatter | When the approval was created |
| priority | string | YAML frontmatter | high/medium/low |
| status | string | YAML frontmatter | `awaiting_approval` |
| body | markdown | Body section | The drafted email reply content |

**State transitions**: `awaiting_approval` (in Pending_Approval/) → `approved` (moved to Approved/) → `sent` (moved to Done/) OR `rejected` (moved to Rejected/ → Done/)

### ApprovalTask (Needs_Action/APPROVED_EMAIL_*.md)

Created by approval_watcher when file appears in Approved/.

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| type | string | YAML frontmatter | `email_approval` |
| to | string | YAML frontmatter | Inherited from ApprovalRequest |
| subject | string | YAML frontmatter | Inherited from ApprovalRequest |
| body | markdown | Body | Inherited from ApprovalRequest |
| approval_file | string | YAML frontmatter | Path to original approval file |
| status | string | YAML frontmatter | `approved` |

### MCPActionLog (Logs/mcp_actions.log)

| Field | Type | Description |
|-------|------|-------------|
| timestamp | ISO datetime | When the action occurred |
| action | string | `send_email`, `draft_email`, `send_failed` |
| to | string | Recipient email |
| subject | string | Email subject |
| message_id | string | Gmail message ID (on success) |
| status | string | `success`, `failed` |
| error | string | Error message (on failure) |

### ApprovalAuditLog (Logs/approval_audit.log)

| Field | Type | Description |
|-------|------|-------------|
| timestamp | ISO datetime | When the action occurred |
| action | string | `approved`, `rejected`, `sent`, `send_failed` |
| file | string | Approval file name |
| to | string | Recipient email |
| reason | string | Rejection reason (if rejected) |

### MCP Tool: send_email

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| to | string | Yes | Valid email format (contains @) |
| subject | string | Yes | Non-empty, max 200 chars |
| body | string | Yes | Non-empty |
| approval_file | string | Yes | Must exist in Approved/ folder |

**Returns**: `{success: bool, message_id: string, error: string}`

### MCP Tool: draft_email

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| to | string | Yes | Valid email format |
| subject | string | Yes | Non-empty |
| body | string | Yes | Non-empty |

**Returns**: `{preview: string}` — formatted email preview

## Relationships

```
EmailTask (Needs_Action/) --processed by--> SKILL_EmailProcessor
  --if reply needed--> ApprovalRequest (Pending_Approval/)
    --human approves--> Approved/
      --approval_watcher--> ApprovalTask (Needs_Action/)
        --orchestrator + SKILL_ApprovalHandler--> MCP send_email
          --success--> Done/ + MCPActionLog
    --human rejects--> Rejected/
      --approval_watcher--> Done/ + ApprovalAuditLog
```
