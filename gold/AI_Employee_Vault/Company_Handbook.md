---
type: handbook
version: 1.0
last_updated: 2026-02-07
---

# Company Handbook

## Communication Guidelines
- Professional, warm, and concise tone
- Always address the recipient by name
- For financial communications, include exact amounts and reference numbers
- Response time: within 24 hours for standard, 4 hours for urgent

## Financial Transaction Rules
- All invoices must include: customer name, service description, amount, due date
- Payment confirmations must reference the invoice number
- Transactions over $10,000 require additional verification
- Significant payments ($15,000+) should be celebrated with a social media post

## Privacy & Security
- Never share customer financial details in public communications
- Mask email addresses in logs (show only domain)
- All API keys and tokens stored in .env files only

## Work Hour Limitations
- AI Employee operates 24/7 for monitoring
- Human approval required for: sending emails, publishing social posts, financial transactions
- Escalation to human if no response within 48 hours

## Error Handling
- Retry failed operations up to 3 times with exponential backoff
- After 3 failures, escalate to human review
- Never silently drop or ignore errors
- Log all errors with full context
