---
name: Email Processor v1.0
purpose: Process email action files from Needs_Action
trigger: Manual invocation or scheduled check
created: 2026-01-29
version: 1.0
---

# Email Processing Agent Skill

## Purpose
This skill enables the AI Employee to process email action files created by the Gmail Watcher. It provides guidelines for analyzing email content, determining priority, and taking appropriate actions.

## Trigger Conditions
- An action file with `type: email` exists in Needs_Action/
- Manual invocation when reviewing email tasks
- Scheduled check during routine processing

## Process Flow

1. **Scan for Email Tasks**: List all `EMAIL_*.md` files in Needs_Action/
2. **Read Action File**: Parse frontmatter and content of each email action file
3. **Analyze Content**: Check for priority keywords, sender reputation, and urgency indicators
4. **Apply Company_Handbook Rules**: Follow communication guidelines from Company_Handbook.md
5. **Take Action**: Update Dashboard, process email, move to Done
6. **Log Activity**: Record processing in Dashboard and logs

## Input Format
Action files with YAML frontmatter containing:
- `type: email`
- `from`: Sender email address
- `from_name`: Sender display name
- `subject`: Email subject line
- `received`: Timestamp of email receipt
- `priority`: Priority level (high/medium/low)
- `status`: Processing status (pending/in_progress/completed)
- `gmail_id`: Original Gmail message ID

## Priority Detection Rules

### High Priority Keywords
- URGENT, ASAP, CRITICAL, EMERGENCY
- invoice, payment, overdue, billing
- meeting, deadline, today, tomorrow, immediate
- From: boss@company.com, ceo@company.com, important.client@company.com

### Medium Priority Keywords
- request, question, feedback, inquiry
- scheduled, reminder, follow-up, meeting
- From: team.members@company.com, colleagues

### Low Priority Keywords
- newsletter, notification, announcement
- automated, no-reply, system@
- marketing, promotional, advertisement
- From: noreply@*, notifications@*

### Auto-Archive (No Action Required)
- From: noreply@*, do-not-reply@*
- Subject contains: unsubscribe, digest, weekly update

## Response Guidelines

### When to Draft Reply (Human Approval Required)
1. **Direct Questions**: Any email asking a question that requires response
2. **Client Requests**: Emails from clients/customers requesting specific actions
3. **Urgent Items**: High priority emails requiring immediate attention
4. **Business Inquiries**: New leads or business opportunities
5. **Meeting Requests**: Calendar invitations or scheduling requests

### When to Just Log
1. **FYI Emails**: Informational emails with no required action
2. **Automated Notifications**: System alerts or status updates
3. **Newsletters**: Reading material or informational content
4. **Receipts**: Order confirmations or transaction records

### Response Template Format
If reply needed, create an approval request in **Pending_Approval/** (NOT Needs_Action/):

**File**: `Pending_Approval/APPROVAL_REPLY_{gmail_id}.md`

```yaml
---
type: email_approval
to: sender@example.com
subject: "Re: Original Subject"
original_gmail_id: msg_abc123
original_subject: "Original Subject"
created_date: 2026-01-30T12:00:00
priority: medium
status: awaiting_approval
---

## Drafted Reply

Dear [Name],

Thank you for your email regarding [subject].

[Professional reply following Company_Handbook tone guidelines]

Best regards,
[Business Name]
```

**Important**: The reply goes to Pending_Approval/ for human review. The human will:
1. Review the drafted reply in Obsidian
2. Edit if needed
3. Move to Approved/ to send, or Rejected/ to discard

The system will then automatically send the email via the MCP email server.

## Output Requirements

### Updated Dashboard.md
- Increment email processing counter
- Update "Last Email Activity" timestamp
- Add email to Recent Activity section
- Update email statistics

### File Movement
- Move processed action file to Done/ folder
- Preserve original filename for reference
- If original email file exists, move it to Done/ as well

### Logging
- Log processing activity to Logs/watcher_errors.log
- Record success/failure status
- Note any special handling required

## Error Handling

### Malformed Action File
- Move to Logs/malformed/ folder
- Log error with file path and issue description
- Continue processing other files

### Processing Error
- Log detailed error to Logs/gmail_errors.log
- Mark file as error state in Dashboard
- Continue processing other files

### Missing Original Email
- Process action file normally
- Note in logs that original email wasn't available
- Update Dashboard appropriately

### Critical Decision Needed
- Flag for human review
- Add REVIEW_ prefix to action file name
- Send notification per Company_Handbook rules

## Company Handbook Integration
Always reference and apply rules from Company_Handbook.md, especially:
- Communication tone and style
- Financial transaction rules
- Privacy and security guidelines
- Work hour limitations
- Error handling procedures