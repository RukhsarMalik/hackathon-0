# Data Model: Gold Module 1 - External Integrations & Automation

## 1. Core Entities

### 1.1 LinkedIn Post
- **Fields**:
  - id: String (LinkedIn-generated post ID)
  - content: String (post text content)
  - approval_file: String (path to approval file that triggered this post)
  - created_at: DateTime (timestamp when post was created)
  - published_url: String (URL of published post on LinkedIn)
  - status: Enum (pending, published, failed)
  - engagement_metrics: Object (likes, comments, shares, impressions)

- **Validation**:
  - content length ≤ 1300 characters (LinkedIn limit)
  - approval_file must exist and be in /Approved/ directory
  - status must be one of allowed enum values

- **Relationships**:
  - 1 approval_file → 1 LinkedIn Post
  - 1 LinkedIn Post → 0..1 engagement_metrics

### 1.2 Twitter Post
- **Fields**:
  - id: String (Twitter-generated tweet ID)
  - content: String (tweet text content)
  - approval_file: String (path to approval file that triggered this post)
  - created_at: DateTime (timestamp when tweet was created)
  - published_url: String (URL of published tweet on Twitter)
  - status: Enum (pending, published, failed)
  - engagement_metrics: Object (likes, retweets, replies, impressions)
  - is_thread: Boolean (whether this is part of a thread)

- **Validation**:
  - content length ≤ 280 characters (Twitter limit)
  - approval_file must exist and be in /Approved/ directory
  - if is_thread is true, content must be part of a multi-tweet sequence

- **Relationships**:
  - 1 approval_file → 1..N Twitter Posts (for threads)
  - 1 Twitter Post → 0..1 engagement_metrics

### 1.3 Odoo Invoice
- **Fields**:
  - id: String (Odoo-generated invoice ID)
  - invoice_number: String (formatted invoice number like INV/2026/00001)
  - customer_id: String (Odoo customer ID)
  - customer_name: String (customer name for reference)
  - product_name: String (product/service name)
  - quantity: Number (quantity of product/service)
  - price_unit: Number (unit price)
  - total_amount: Number (calculated total)
  - created_at: DateTime (timestamp when invoice was created)
  - payment_status: Enum (draft, posted, paid, cancelled)
  - payment_date: DateTime (when payment was recorded)
  - approval_file: String (path to approval file that triggered this invoice)

- **Validation**:
  - total_amount = quantity * price_unit
  - payment_status must be one of allowed enum values
  - approval_file must exist if invoice was created from email

- **Relationships**:
  - 1 customer_id → N invoices
  - 1 approval_file → 0..1 invoice (for email-triggered invoices)

### 1.4 Customer
- **Fields**:
  - id: String (Odoo customer ID)
  - name: String (customer name)
  - email: String (customer email)
  - phone: String (customer phone)
  - created_at: DateTime (timestamp when customer was created)
  - total_invoices: Number (count of invoices for this customer)
  - total_revenue: Number (sum of all invoices for this customer)

- **Validation**:
  - name is required
  - email format must be valid if provided
  - phone format must be valid if provided

- **Relationships**:
  - 1 customer → N invoices
  - 1 customer → N interactions (through invoices)

## 2. Supporting Entities

### 2.1 MCP Action Log
- **Fields**:
  - id: String (unique log entry ID)
  - action: String (tool name that was called)
  - parameters: Object (parameters passed to the tool)
  - result: Object (result returned by the tool)
  - status: Enum (success, failed, partial)
  - timestamp: DateTime (when action was performed)
  - service: String (which service was affected: linkedin, twitter, odoo)

- **Validation**:
  - action must be a valid MCP tool name
  - status must be one of allowed enum values
  - service must be one of the supported services

- **Relationships**:
  - 1 MCP Action Log → 1 service

### 2.2 Social Media Summary
- **Fields**:
  - id: String (unique summary ID)
  - period_start: DateTime (start date of reporting period)
  - period_end: DateTime (end date of reporting period)
  - platforms: Array of Objects (summary data per platform)
  - total_posts: Number (total posts across all platforms)
  - total_engagement: Number (total likes, comments, shares)
  - top_performers: Array of Objects (best performing posts)
  - created_at: DateTime (when summary was generated)

- **Validation**:
  - period_end must be after period_start
  - total_posts must equal sum of posts across platforms
  - top_performers limited to top 5 posts

- **Relationships**:
  - 1 Social Media Summary → N MCP Action Logs (for posts)

### 2.3 Accounting Summary
- **Fields**:
  - id: String (unique summary ID)
  - period_start: DateTime (start date of reporting period)
  - period_end: DateTime (end date of reporting period)
  - total_revenue: Number (revenue for the period)
  - paid_revenue: Number (paid invoices only)
  - unpaid_revenue: Number (unpaid invoices only)
  - invoice_count: Number (total invoices created)
  - customer_count: Number (new customers acquired)
  - created_at: DateTime (when summary was generated)

- **Validation**:
  - period_end must be after period_start
  - total_revenue = paid_revenue + unpaid_revenue
  - invoice_count must be >= 0

- **Relationships**:
  - 1 Accounting Summary → N Odoo Invoices (for the period)

## 3. State Transitions

### 3.1 LinkedIn Post States
```
pending → published (on successful API call)
pending → failed (on API error)
```

### 3.2 Twitter Post States
```
pending → published (on successful API call)
pending → failed (on API error)
```

### 3.3 Odoo Invoice States
```
draft → posted (when invoice is confirmed)
posted → paid (when payment is recorded)
posted → cancelled (when invoice is cancelled)
```

### 3.4 MCP Action Log States
```
pending → success (when action completes successfully)
pending → failed (when action encounters error)
pending → partial (when action partially completes)
```

## 4. Indexes and Performance Considerations

- Index on created_at for all entities for time-based queries
- Index on status for filtering by status
- Index on customer_id for Odoo Invoice for customer-based queries
- Index on service for MCP Action Log for service-based queries