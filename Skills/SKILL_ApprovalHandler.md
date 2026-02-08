---
name: Approval Handler v1.0
purpose: Process approved email requests by sending via MCP
trigger: APPROVED_EMAIL_*.md action file in Needs_Action/
created: 2026-01-30
version: 1.0
---

# Approval Handler Agent Skill

## Purpose
Process approved email requests by calling the MCP email server to send emails. Handles both successful sends and failures with retry logic.

## Trigger Conditions
- An action file with `type: email_approval` exists in Needs_Action/
- File follows naming convention: APPROVED_EMAIL_*.md
- The email has been approved by a human (moved from Pending_Approval/ to Approved/)

## Process Flow

1. **Read Approved Email File**: Parse YAML frontmatter to extract `to`, `subject`, and email body
2. **Validate Fields**: Ensure to, subject, and body are present and non-empty
3. **Call MCP send_email Tool**: Use the email MCP server to send the email
   - Pass: to, subject, body, approval_file (filename of the approval file)
4. **Handle Response**:
   - **Success**: Log successful send, update Dashboard, move task to Done/
   - **Failure**: Retry up to 3 times with 10-second delay between attempts
5. **Update Dashboard**: Record the email send activity
6. **Move to Done/**: Move the processed task file to Done/

## Retry Logic
- Maximum 3 attempts
- 10-second delay between attempts
- If all attempts fail:
  - Log the failure to approval_audit.log
  - Flag the file for human review (add REVIEW_ prefix)
  - Do NOT move to Done/ — keep in Needs_Action/ for retry

## Input Format
Action file with YAML frontmatter:
```yaml
---
type: email_approval
to: recipient@example.com
subject: Re: Original Subject
original_gmail_id: abc123
original_subject: Original Subject
created_date: 2026-01-30T12:00:00
status: approved
approval_file: APPROVAL_REPLY_abc123.md
---
```

## Email Body
The email body content follows the YAML frontmatter in the markdown body section.

## Output
- Email sent via Gmail API through MCP server
- Dashboard.md updated with send activity
- Task file moved to Done/
- Activity logged to approval_audit.log

## Multi-MCP Routing (Gold Tier)

The Approval Handler now supports multiple MCP server integrations. Route approvals based on the `type` field in YAML frontmatter:

### Routing Table

| Frontmatter Type | MCP Server | Tool to Call | Required Fields |
|-----------------|------------|--------------|-----------------|
| `email_approval` | Email MCP | `send_email` | to, subject, body |
| `linkedin_post_ready` | LinkedIn MCP | `post_to_linkedin` | content, approval_file |
| `facebook_approval` | Facebook MCP | `post_to_facebook` | message, approval_file |
| `invoice_approval` | Odoo MCP | `create_invoice` | customer_name, product_name, price_unit |

### LinkedIn Post Approval Flow

When `type: linkedin_approval` or `type: linkedin_post_ready` is detected:
1. Extract post content from the markdown body (the actual post text, excluding YAML frontmatter and instructions)
2. Call LinkedIn MCP: `post_to_linkedin`
   - content: [extracted post text — clean text only, no YAML or markdown headers]
   - approval_file: [FULL absolute path to this task file, e.g. `/mnt/d/hackathon-0/gold/AI_Employee_Vault/Needs_Action/APPROVED_LINKEDIN_xxx.md`]
3. Handle response:
   - **Success**: Log post URL, update Dashboard, move to Done/
   - **Failure**: Move to /Needs_Action/ with ERROR_ prefix, log error

**IMPORTANT**: The `approval_file` parameter MUST be the full absolute path to the task file being processed. The MCP server checks that the path contains `APPROVED_` or `/Approved/` or `/Done/`.

### Facebook Post Approval Flow

When `type: facebook_approval` is detected:
1. Extract post content from the markdown body (the actual post text, excluding YAML frontmatter and instructions)
2. Call Facebook MCP: `post_to_facebook`
   - message: [post text — clean text only, no YAML or markdown headers]
   - approval_file: [FULL absolute path to this task file, e.g. `/mnt/d/hackathon-0/gold/AI_Employee_Vault/Needs_Action/APPROVED_FACEBOOK_xxx.md`]
3. Handle response:
   - **Success**: Log post URL, update Dashboard, move to Done/
   - **Failure**: Log error, retry once after 5 min, then flag for human

**IMPORTANT**: The `approval_file` parameter MUST be the full absolute path to the task file being processed.

### Invoice Approval Flow

When `type: invoice_approval` is detected:
1. Extract invoice details from frontmatter/body
2. Call Odoo MCP: `create_invoice`
   - customer_name: [from file]
   - product_name: [from file]
   - quantity: [from file]
   - price_unit: [from file]
   - approval_file: [path to this file]
3. Handle response:
   - **Success**: Log invoice number, update Dashboard revenue, move to Done/
   - **Failure**: Log error, create pending task file

### Detection Logic

```
Read frontmatter 'type' field
  ↓
Switch on type:
  email_approval      → Email MCP send_email
  linkedin_post_ready → LinkedIn MCP post_to_linkedin
  facebook_approval   → Facebook MCP post_to_facebook
  invoice_approval    → Odoo MCP create_invoice
  unknown             → Flag for human review
```

## Error Handling
- **Invalid email address**: Log error, flag for human review
- **MCP server unavailable**: Retry 3x with backoff, then flag for human review
- **Gmail API error**: Retry with backoff, then flag for human review
- **LinkedIn token expired**: Alert human to refresh token, pause LinkedIn posting
- **Facebook rate limit**: Queue for retry in 1 hour
- **Odoo connection error**: Create PENDING_ODOO_ task file, retry 3x
- **Malformed file**: Move to Logs/malformed/, log error
- **Missing fields**: Log error, flag for human review
- **Unknown approval type**: Log warning, flag for human review
