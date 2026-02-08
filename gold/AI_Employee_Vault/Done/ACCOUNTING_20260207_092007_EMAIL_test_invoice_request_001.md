---
type: accounting
source_email: EMAIL_test_invoice_request_001.md
created: 2026-02-07T09:20:07.845877
status: pending
---

## Accounting Task (auto-generated from email)

**Source**: EMAIL_test_invoice_request_001.md

### Original Email Content

---
type: email
from: ahmed.khan@techsolutions.pk
to: rukhsarmalik2211@gmail.com
subject: Invoice Request - Web Development Project
gmail_id: test_invoice_001
date: 2026-02-07T10:00:00Z
---

## Email Content

From: Ahmed Khan <ahmed.khan@techsolutions.pk>
Subject: Invoice Request - Web Development Project

Hi Rukhsar,

I hope you're doing well. We've completed the web development project we discussed last month.

Could you please send me an invoice for the following:

- **Service**: Web Development
- **Hours**: 15 hours
- **Rate**: $50 per hour
- **Total**: $750

My company name is **Tech Solutions PK** and my email is ahmed.khan@techsolutions.pk.

Please send the invoice at your earliest convenience so we can process the payment.

Best regards,
Ahmed Khan
Tech Solutions PK


### Instructions

Process this email using SKILL_AccountingManager:
1. Detect if this is an invoice request or payment confirmation
2. Extract customer, service, amount details
3. Call appropriate Odoo MCP tool
4. Draft reply email
5. Update Dashboard with accounting activity
