# Agent Skill: Accounting Manager

## Skill Name
Accounting Manager v1.0

## Purpose
Automatically manage invoicing, payment tracking, and revenue reporting using Odoo.

## Triggers
- Payment confirmation email
- Invoice request (email or task file)
- Monthly revenue check
- Manual accounting task

## Prerequisites
- Odoo MCP server running
- Customer exists in Odoo
- Product/service configured in Odoo

## Process Flow

### Workflow 1: Create Invoice from Email

**Trigger**: Email with keywords "invoice", "send invoice", "billing"

**Steps**:
```
1. Parse email for:
   - Customer name
   - Service/product description
   - Amount OR (quantity × rate)
   - Due date (optional)

2. Verify customer exists:
   - Call Odoo MCP: list_customers
   - Search for customer name
   - If not found: Create customer first

3. Map service to Odoo product:
   - "web development" → Web Development product
   - "consulting" → Consulting product
   - "automation" → Automation Setup product

4. Create invoice:
   - Call Odoo MCP: create_invoice
   - Parameters:
     - customer_name: [from email]
     - product_name: [mapped product]
     - quantity: [from email or 1]
     - price_unit: [from email]

5. Draft email reply:
   - Create approval file in /Pending_Approval/
   - Subject: "Re: Invoice Request"
   - Body: "Invoice [number] has been created for $[amount]. You can view it at [Odoo URL]."

6. Update Dashboard:
   - Add: "Invoice [number] created for [customer] - $[amount]"

7. Move original email to /Done/
```

**Example**:
````
Email: "Hi, can you send me an invoice for the 10 hours of web development work?"
From: client_a@example.com

Process:
1. Parse: Customer=Client A, Service=Web Development, Quantity=10
2. Check Odoo: Client A exists ✓
3. Map: Web Development → product_id=1
4. Create invoice: 10 hrs × $100 = $1,000
5. Draft reply: "Invoice INV/2026/00023 created for $1,000"
6. Dashboard: "Invoice INV/2026/00023 created for Client A - $1,000"
````

### Workflow 2: Mark Invoice Paid

**Trigger**: Email with keywords "payment received", "paid invoice", "payment confirmation"

**Steps**:
````
1. Parse email for:
   - Invoice number (e.g., "INV/2026/00023")
   - Amount paid
   - Payment date

2. Call Odoo MCP: mark_invoice_paid
   - invoice_number: [from email]
   - payment_amount: [from email]
   - payment_date: [from email or today]

3. Update Dashboard:
   - Revenue +$[amount]
   - Check monthly target progress

4. Check Business_Goals:
   - If milestone reached (e.g., 50% of monthly target):
     - Create LinkedIn post request
     - Topic: Achievement announcement

5. Draft confirmation reply:
   - "Payment received and logged. Invoice [number] is now marked as paid. Thank you!"

6. Move email to /Done/
````

**Example**:
````
Email: "Payment of $1,000 received for Invoice INV/2026/00023"

Process:
1. Parse: Invoice=INV/2026/00023, Amount=$1,000
2. Mark paid in Odoo ✓
3. Dashboard: Revenue +$1,000 (MTD: $4,500/$10,000)
4. Check goals: 45% of monthly target (no milestone)
5. Draft reply: "Payment received..."
````

### Workflow 3: Monthly Revenue Report

**Trigger**: First day of new month OR manual request

**Steps**:
````
1. Calculate date range:
   - start_date: First day of last month
   - end_date: Last day of last month

2. Call Odoo MCP: get_revenue
   - Get total, paid, unpaid revenue

3. Generate report:
   - File: /Briefings/Revenue_YYYY-MM.md
   - Format:
````markdown
# Revenue Report: [Month] [Year]

## Summary
- **Total Revenue**: $[total]
- **Paid**: $[paid]
- **Unpaid/Outstanding**: $[unpaid]
- **Number of Invoices**: [count]

## Comparison
- Previous month: $[last_month]
- Change: +/-[percentage]%

## Outstanding Invoices
[List unpaid invoices if any]

## Top Customers
[List top 3 customers by revenue]
````

### Workflow 4: Add New Customer

**Trigger**: Email from new contact requesting services

**Steps**:
````
1. Extract customer info:
   - Name (from email signature or content)
   - Email address
   - Phone (if provided)

2. Check if customer exists:
   - Call Odoo MCP: list_customers
   - Search by email

3. If new customer:
   - Call Odoo MCP: create_customer
   - Log: "New customer added: [name]"

4. Continue with invoice creation (Workflow 1)
````

## Integration with Other Skills

**With SKILL_EmailProcessor**:
````
EmailProcessor detects invoice keyword
  ↓
Hands off to AccountingManager
  ↓
AccountingManager creates invoice
  ↓
Hands back to EmailProcessor for reply
````

**With Business Goals**:
````
Invoice paid
  ↓
Update revenue
  ↓
Check Business_Goals.md targets
  ↓
If milestone: Create social post
````

## Error Handling

**If Odoo MCP unavailable**:
````
1. Create pending task file:
   /Needs_Action/PENDING_ODOO_[action]_[timestamp].md
2. Log error
3. Alert Dashboard: "Odoo offline - invoice queued"
4. Retry in 5 minutes (max 3 attempts)
5. If still fails: Alert human
````

**If customer not found**:
````
1. Check if name spelling issue
2. Try fuzzy match
3. If no match: Create approval request:
   "Create new customer: [name]?"
4. Wait for approval before creating invoice
````

**If invoice creation fails**:
````
1. Log error details
2. Create manual task for human:
   "Invoice creation failed for [customer] - please create manually"
3. Include all details in task file
````

## Quality Checks

Before creating invoice:
- ✓ Customer exists or will be created
- ✓ Product/service mapped correctly
- ✓ Amount is reasonable (not $0, not > $100k without approval)
- ✓ All required fields present

After creating invoice:
- ✓ Invoice number returned
- ✓ Amount matches request
- ✓ Logged in Odoo actions log
- ✓ Dashboard updated

## Dashboard Updates

Format:
````markdown
## Recent Accounting Activity
- [TIMESTAMP] Invoice INV/2026/00023 created for Client A - $1,000
- [TIMESTAMP] Payment received: $1,000 - Invoice INV/2026/00023
- [TIMESTAMP] Revenue MTD: $4,500 (45% of $10,000 target)
- [TIMESTAMP] New customer added: Client D
````

## Testing

**Test Case 1: Invoice Creation**
- Input: Email requesting invoice
- Expected: Invoice created in Odoo, reply drafted
- Verify: Check Odoo interface for new invoice

**Test Case 2: Payment Processing**
- Input: Payment confirmation email
- Expected: Invoice marked paid, revenue updated
- Verify: Odoo shows invoice as paid, Dashboard shows new revenue

**Test Case 3: Error Recovery**
- Input: Invoice request while Odoo offline
- Expected: Task queued, retried when Odoo returns
- Verify: Invoice created after Odoo restoration

## Version History
- v1.0: Initial accounting automation