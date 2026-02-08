---
type: accounting
source_email: TEST_02_invoice_request.md
created: 2026-02-07T10:27:07.734473
status: pending
---

## Accounting Task (auto-generated from email)

**Source**: TEST_02_invoice_request.md

### Original Email Content

---
type: email
from: client.a@techcorp.com
to: rukhsarmalik2211@gmail.com
subject: Invoice Request - Monthly Consulting
gmail_id: test_demo_invoice_02
date: 2026-02-07T14:10:00Z
---

## Email Content

From: Client A <client.a@techcorp.com>
Subject: Invoice Request - Monthly Consulting

Hi Rukhsar,

Please send me an invoice for the consulting work completed this month.

**Invoice Details**:
- **Service**: Consulting
- **Hours**: 20 hours
- **Rate**: $75 per hour
- **Total**: $1,500

My company name is **Client A - TechCorp** and my email is client.a@techcorp.com.

Please send the invoice so we can process payment promptly.

Thank you,
Client A
TechCorp


### Instructions

Process this email using SKILL_AccountingManager:
1. Detect if this is an invoice request or payment confirmation
2. Extract customer, service, amount details
3. Call appropriate Odoo MCP tool
4. Draft reply email
5. Update Dashboard with accounting activity
