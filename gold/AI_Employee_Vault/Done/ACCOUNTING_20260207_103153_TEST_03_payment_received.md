---
type: accounting
source_email: TEST_03_payment_received.md
created: 2026-02-07T10:31:53.913452
status: pending
---

## Accounting Task (auto-generated from email)

**Source**: TEST_03_payment_received.md

### Original Email Content

---
type: email
from: client.b@startupxyz.com
to: rukhsarmalik2211@gmail.com
subject: Payment Confirmation - Invoice INV/2026/00002
gmail_id: test_demo_payment_03
date: 2026-02-07T14:20:00Z
---

## Email Content

From: Client B <client.b@startupxyz.com>
Subject: Payment Confirmation - Invoice INV/2026/00002

Hi Rukhsar,

This is to confirm that we have made the payment for Invoice INV/2026/00002.

**Payment Details**:
- **Invoice Number**: INV/2026/00002
- **Amount Paid**: $1,170.00
- **Payment Date**: 2026-02-07
- **Payment Method**: Bank Transfer
- **Reference**: StartupXYZ-Feb2026

Please confirm receipt and update your records.

Best regards,
Client B
StartupXYZ


### Instructions

Process this email using SKILL_AccountingManager:
1. Detect if this is an invoice request or payment confirmation
2. Extract customer, service, amount details
3. Call appropriate Odoo MCP tool
4. Draft reply email
5. Update Dashboard with accounting activity
