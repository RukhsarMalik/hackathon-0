---
name: Enhanced Email Processor v1.1
purpose: Process email action files with advanced cross-domain intelligence and payment detection
trigger: Manual invocation or scheduled check
created: 2026-02-06
version: 1.1
---

# Enhanced Email Processing Agent Skill

## Purpose
This enhanced skill extends the AI Employee's capability to process email action files with advanced cross-domain intelligence. It includes improved payment confirmation detection and automated workflow triggering for business events.

## Trigger Conditions
- An action file with `type: email` exists in Needs_Action/
- Manual invocation when reviewing email tasks
- Scheduled check during routine processing

## Process Flow

1. **Scan for Email Tasks**: List all `EMAIL_*.md` files in Needs_Action/
2. **Read Action File**: Parse frontmatter and content of each email action file
3. **Analyze Content**: Check for priority keywords, sender reputation, and payment/transaction indicators
4. **Detect Cross-Domain Triggers**: Identify payment confirmations, invoice requests, and other triggers
5. **Apply Company_Handbook Rules**: Follow communication guidelines from Company_Handbook.md
6. **Take Action**: Update Dashboard, trigger cross-domain workflows, process email, move to Done
7. **Log Activity**: Record processing in Dashboard and audit logs

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

## Payment Confirmation Detection

### Payment Confirmation Keywords
- "payment received", "payment confirmation", "payment completed", "payment processed"
- "received payment", "confirming payment", "payment acknowledged"
- "funds received", "transaction completed", "payment success"
- "paid invoice", "invoice paid", "payment settled"
- Specific amounts: "$", "USD", "EUR", "GBP", etc. with numerical values
- "credited", "settled", "cleared", "completed"

### Cross-Domain Workflow Triggers

When payment confirmation is detected, the following workflow is initiated:
1. **Extract Transaction Details** from email:
   - Amount (from email body)
   - Invoice number (if present)
   - Customer name (from sender or body)
   - Transaction date
   - Reference numbers or identifiers

2. **Trigger Accounting Workflow**:
   - Update invoice status in Odoo (via MCP call)
   - Log transaction milestone
   - Flag for LinkedIn post creation if amount is significant (>$1000)

3. **Update Business Intelligence**:
   - Record in revenue tracking
   - Update weekly audit data
   - Log for CEO briefing generation

### Response Guidelines

#### When to Draft Reply (Human Approval Required)
1. **Direct Questions**: Any email asking a question that requires response
2. **Client Requests**: Emails from clients/customers requesting specific actions
3. **Urgent Items**: High priority emails requiring immediate attention
4. **Business Inquiries**: New leads or business opportunities
5. **Meeting Requests**: Calendar invitations or scheduling requests

#### When to Just Log
1. **FYI Emails**: Informational emails with no required action
2. **Automated Notifications**: System alerts or status updates
3. **Newsletters**: Reading material or informational content
4. **Receipts**: Order confirmations or transaction records

#### Response Template Format
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
```

#### Cross-Domain Workflow Context
For payment confirmations, add workflow tracking:

```yaml
workflow_context:
  type: "payment_confirmation_workflow"
  transaction_details:
    amount: 0.00
    currency: "USD"
    customer: "Customer Name"
    invoice_id: "INV-XXXX"
    transaction_id: "TXN-XXXX"
  cross_domain_triggers:
    - "odoo_invoice_update"
    - "milestone_log"
    - "linkedin_post_draft"  # if amount significant
```

## Output Requirements

### Updated Dashboard.md
- Increment email processing counter
- Update "Last Email Activity" timestamp
- Add email to Recent Activity section
- Update email statistics
- Record cross-domain workflow initiation if applicable

### File Movement
- Move processed action file to Done/ folder
- Preserve original filename for reference
- If original email file exists, move it to Done/ as well

### Cross-Domain Logging
- Log payment confirmations to audit trail with transaction details
- Create workflow tracking entries
- Update business intelligence data sources

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

## Payment Detection Implementation

When the email contains payment confirmation keywords:

1. **Parse for Financial Data**:
   - Extract monetary amounts using regex patterns like `(\$|\€|£)?[\d,]+\.?\d*`
   - Look for invoice references like `INV-\d+`, `Invoice #\d+`, etc.
   - Identify customer names and company information

2. **Determine Significance**:
   - For amounts > $1000, flag for LinkedIn post workflow
   - For amounts > $5000, flag for immediate CEO notification
   - For recurring payments, note the pattern

3. **Create Cross-Domain Workflow**:
   - If payment is significant (> $1000), create a LinkedIn post draft task
   - Update accounting records via MCP
   - Log milestone in business tracking

## Company Handbook Integration
Always reference and apply rules from Company_Handbook.md, especially:
- Communication tone and style
- Financial transaction rules
- Privacy and security guidelines
- Work hour limitations
- Error handling procedures