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

## Error Handling
- **Invalid email address**: Log error, flag for human review
- **MCP server unavailable**: Retry, then flag for human review
- **Gmail API error**: Retry with backoff, then flag for human review
- **Malformed file**: Move to Logs/malformed/, log error
- **Missing fields**: Log error, flag for human review
