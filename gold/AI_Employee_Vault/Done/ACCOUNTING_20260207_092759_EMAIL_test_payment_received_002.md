---
type: accounting
source_email: EMAIL_test_payment_received_002.md
created: 2026-02-07T09:27:59.813645
status: pending
---

## Accounting Task (auto-generated from email)

**Source**: EMAIL_test_payment_received_002.md

### Original Email Content

---
type: email
from: sara.ali@digitalmarketing.com
to: rukhsarmalik2211@gmail.com
subject: Payment Confirmation - Invoice INV/2026/00025
gmail_id: test_payment_002
date: 2026-02-07T11:00:00Z
---

## Email Content

From: Sara Ali <sara.ali@digitalmarketing.com>
Subject: Payment Confirmation - Invoice INV/2026/00025

Hi Rukhsar,

This is to confirm that we have made the payment for Invoice INV/2026/00025.

**Payment Details**:
- **Invoice Number**: INV/2026/00025
- **Amount Paid**: $15,000.00
- **Payment Date**: 2026-02-07
- **Payment Method**: Bank Transfer

Please confirm receipt and update your records accordingly.

Thank you for your excellent service!

Best regards,
Sara Ali
Digital Marketing Co.


### Instructions

Process this email using SKILL_AccountingManager:
1. Detect if this is an invoice request or payment confirmation
2. Extract customer, service, amount details
3. Call appropriate Odoo MCP tool
4. Draft reply email
5. Update Dashboard with accounting activity
