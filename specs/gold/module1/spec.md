# Feature Specification: Gold Module 1 - External Integrations & Automation

**Feature Branch**: `001-external-integrations-automation`
**Created**: 2026-02-05
**Updated**: 2026-02-05
**Status**: Draft
**Input**: User description: "Gold Module 1: External Integrations & Automation - LinkedIn MCP (auto-posting), Facebook MCP (auto-posting), Odoo 19 installation, Odoo MCP server, Social media summary generation, Cross-domain integration (Email → Accounting), Updated Agent Skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - LinkedIn MCP Server (Priority: P1)

As a business owner, I want LinkedIn posts to auto-publish when approved so that I don't manually copy-paste to LinkedIn.

**Why this priority**: This transforms LinkedIn posting from a manual task to automated workflow, providing immediate value by eliminating the copy-paste bottleneck.

**Independent Test**: Create LinkedIn MCP server with post_to_linkedin tool, then approve a post draft and verify it publishes automatically to LinkedIn with URL returned.

**Acceptance Scenarios**:

1. **Given** LinkedIn MCP server is running and configured with API credentials, **When** an approved post is moved to /Approved/ folder, **Then** the post_to_linkedin tool executes and publishes content to LinkedIn with URL returned
2. **Given** a post draft exists in /Needs_Action/, **When** user moves it to /Approved/, **Then** LinkedIn MCP automatically posts the content and moves the file to /Done/
3. **Given** LinkedIn token is expired, **When** post_to_linkedin tool is called, **Then** appropriate error message is returned and human is alerted to refresh token
4. **Given** LinkedIn API is unavailable, **When** Playwright automation is configured, **Then** post is published via browser automation with success confirmed
5. **Given** get_post_stats tool is called with days parameter, **When** LinkedIn API responds, **Then** engagement metrics (likes, comments, shares) are returned for the specified period

---

### User Story 2 - Facebook MCP Server (Priority: P1)

As a business owner, I want to auto-post to Facebook when approved so that I maintain consistent social media presence without manual intervention.

**Why this priority**: Facebook is a high-engagement platform that benefits from consistent posting, and automation ensures regular presence without manual effort.

**Implementation choice**: Facebook MCP using the Facebook Graph API.

**Independent Test**: Create Facebook MCP server with post_to_facebook tool, then approve a post draft and verify it publishes automatically to Facebook with URL returned.

**Acceptance Scenarios**:

1. **Given** Facebook MCP server is running with valid Page Access Token, **When** an approved post is processed, **Then** the post_to_facebook tool enforces 63,206 character limit and publishes to the configured Facebook Page with post URL returned
2. **Given** Facebook API rate limit is reached, **When** additional posts are attempted, **Then** system queues posts for retry in 1 hour
3. **Given** get_page_insights tool is called with days parameter, **When** Facebook Graph API responds, **Then** engagement metrics (likes, comments, shares, reach) are returned for the specified period of recent posts
4. **Given** an approved post is processed, **When** the post_to_facebook tool publishes to the configured Facebook Page, **Then** post URL is returned and the approval file is moved to /Done/

---

### User Story 3 - Social Media Agent Skills (Priority: P1)

As a developer, I want updated agent skills for social media automation so that the AI Employee can generate, approve, and auto-post content via MCPs.

**Why this priority**: Agent skills are the instruction set for the orchestrator. Without updated skills, MCP servers cannot be triggered properly.

**Independent Test**: Verify SKILL_LinkedInPoster has MCP integration section, SKILL_FacebookPoster exists with post formatting, SKILL_SocialSummaryGenerator exists with weekly report format.

**Acceptance Scenarios**:

1. **Given** SKILL_LinkedInPoster.md is updated, **When** an approved LinkedIn post is processed, **Then** it calls post_to_linkedin MCP tool and handles success/failure responses
2. **Given** SKILL_FacebookPoster.md exists, **When** a Facebook post is generated, **Then** it enforces character limits (63,206 chars), formats content appropriately, and creates proper approval files
3. **Given** SKILL_SocialSummaryGenerator.md exists, **When** weekly summary is triggered, **Then** it collects data from logs and MCP tools to produce engagement report for CEO briefing
4. **Given** SKILL_ApprovalHandler.md is updated, **When** any social media approval is processed, **Then** it routes to the correct MCP tool (LinkedIn, Facebook, or email) based on approval type

---

### User Story 4 - Odoo 19 Installation & Setup (Priority: P1)

As a developer, I want Odoo 19 accounting system running locally so that I can track business finances via API.

**Why this priority**: Odoo is the infrastructure prerequisite for all accounting automation. Without it, US-5, US-6, and US-7 cannot function.

**Independent Test**: Start Odoo via Docker, create database, install accounting module, add test customers/products, create manual invoice, verify API access via XML-RPC.

**Acceptance Scenarios**:

1. **Given** Docker Compose file is configured, **When** `docker-compose up -d` is run, **Then** Odoo 19 Community is accessible at localhost:8069 with PostgreSQL backend
2. **Given** Odoo is running, **When** database `ai_employee_accounting` is created with accounting module installed, **Then** chart of accounts is auto-configured and accounting features are available
3. **Given** accounting module is installed, **When** 3+ customers and 3+ products/services are added, **Then** they are queryable via XML-RPC API with correct fields
4. **Given** customers and products exist, **When** a test invoice is created and payment registered manually, **Then** invoice lifecycle (draft → posted → paid) works correctly
5. **Given** Odoo is running, **When** XML-RPC authentication is attempted with correct credentials, **Then** user ID is returned and `execute_kw` calls succeed

---

### User Story 5 - Odoo MCP Server (Priority: P1)

As a developer, I want an MCP server for Odoo integration so that Claude can manage accounting automatically.

**Why this priority**: The MCP server is the bridge between Claude Code and Odoo, enabling all accounting automation workflows.

**Independent Test**: Start Odoo MCP server, verify it connects to Odoo, test create_invoice, mark_invoice_paid, get_revenue, list_customers, and create_customer tools.

**Acceptance Scenarios**:

1. **Given** Odoo MCP server is started, **When** it initializes, **Then** it authenticates with Odoo via XML-RPC and logs "Connected to Odoo as user ID: X"
2. **Given** create_invoice tool is called with customer_name, product_name, and price_unit, **When** customer and product exist in Odoo, **Then** invoice is created and invoice number + total amount are returned
3. **Given** mark_invoice_paid tool is called with invoice_number and payment_amount, **When** invoice exists and is not already paid, **Then** invoice payment status is updated and success is returned
4. **Given** get_revenue tool is called with start_date and end_date, **When** invoices exist in the period, **Then** total revenue, paid revenue, unpaid revenue, and invoice count are returned
5. **Given** list_customers tool is called, **When** customers exist in Odoo, **Then** customer list with name, email, phone is returned up to the specified limit
6. **Given** create_customer tool is called with name, **When** customer doesn't already exist, **Then** new customer is created in Odoo and customer ID is returned
7. **Given** Odoo connection fails, **When** any tool is called, **Then** appropriate error is returned and logged without crashing the MCP server

---

### User Story 6 - Accounting Agent Skill (Priority: P1)

As an AI Employee, I want an Accounting Manager skill so that invoices are created and payments tracked automatically when triggered by emails.

**Why this priority**: The skill file defines the business logic for accounting automation, mapping email triggers to Odoo MCP operations.

**Independent Test**: Create SKILL_AccountingManager.md with 4 workflows (Create Invoice from Email, Mark Invoice Paid, Monthly Revenue Report, Add New Customer), verify each workflow documents complete process flow.

**Acceptance Scenarios**:

1. **Given** SKILL_AccountingManager.md exists with Workflow 1, **When** email contains "invoice" keyword, **Then** skill instructions guide parsing customer/product/amount, calling create_invoice MCP tool, drafting reply, and updating dashboard
2. **Given** SKILL_AccountingManager.md exists with Workflow 2, **When** email contains "payment received" keyword, **Then** skill instructions guide parsing invoice number/amount, calling mark_invoice_paid MCP tool, and updating revenue in dashboard
3. **Given** SKILL_AccountingManager.md exists with Workflow 3, **When** monthly revenue report is requested, **Then** skill instructions guide calling get_revenue MCP tool and generating formatted report in /Briefings/
4. **Given** SKILL_AccountingManager.md exists with Workflow 4, **When** email from unknown customer arrives, **Then** skill instructions guide calling create_customer MCP tool before proceeding with invoice creation
5. **Given** Odoo MCP is unavailable, **When** accounting task is triggered, **Then** skill instructions guide creating pending task file, retrying 3 times, and alerting human if all retries fail

---

### User Story 7 - Cross-Domain Email to Accounting Integration (Priority: P2)

As a system, I want email and accounting to work together so that invoice workflows are fully automated without manual handoffs.

**Why this priority**: Creates seamless integration between communication and financial systems, eliminating manual transfer of information between systems.

**Independent Test**: Send email requesting invoice, verify it triggers accounting workflow, creates invoice in Odoo, drafts reply, and updates dashboard - all without manual intervention.

**Acceptance Scenarios**:

1. **Given** email contains invoice-related keywords ("invoice", "send invoice", "billing"), **When** EmailProcessor detects them, **Then** it hands off to AccountingManager for processing
2. **Given** AccountingManager processes invoice request, **When** it completes, **Then** reply is drafted in /Pending_Approval/ and original email moved to /Done/
3. **Given** customer doesn't exist in Odoo, **When** invoice request is processed, **Then** system creates customer first then proceeds with invoice creation
4. **Given** orchestrator.py receives email task with accounting keywords, **When** it processes the task, **Then** it creates an accounting subtask using `contains_accounting_keywords()` and routes to SKILL_AccountingManager
5. **Given** email contains "payment received" for existing invoice, **When** processed end-to-end, **Then** invoice is marked paid in Odoo, reply drafted, dashboard revenue updated, and business goals checked

---

### User Story 8 - Social Media Summary Generation (Priority: P2)

As a CEO, I want weekly social media activity summaries so that I can quickly understand engagement and performance metrics.

**Why this priority**: Provides executive-level visibility into social media performance, supporting strategic decision-making about marketing efforts.

**Independent Test**: Generate weekly summary using data from social media logs and MCP tools, verify it contains engagement metrics and performance insights.

**Acceptance Scenarios**:

1. **Given** 7 days of social media activity exists, **When** summary generator runs (triggered by weekly_audit.py Sunday 11 PM), **Then** it produces weekly report with post counts, engagement metrics, and top performers
2. **Given** MCP tools are unavailable, **When** summary is generated, **Then** it uses log data as fallback and notes "MCP unavailable" in report
3. **Given** no posts occurred in the week, **When** summary is generated, **Then** it flags "No social activity" and suggests action
4. **Given** summary is generated, **When** appended to CEO briefing, **Then** file is created at /Briefings/YYYY-MM-DD_CEO_Briefing.md with correct format

---

### Edge Cases

- What happens when LinkedIn/MCP servers are temporarily down during approval? (System queues for retry, alerts dashboard)
- What happens when Odoo API returns unexpected error during invoice creation? (Logs error, creates manual task for human)
- What happens when Facebook character limit changes from 63,206 to different value? (System uses configured limit, not hardcoded)
- What happens when email contains both invoice and social media keywords? (Handles both workflows separately)
- What happens when multiple approvals happen simultaneously? (Processes concurrently with proper rate limiting)
- What happens when Playwright session expires for LinkedIn? (Returns error "Not logged in", prompts human to re-login)
- What happens when Odoo Docker container is stopped? (Odoo MCP returns connection error, tasks queued for retry)
- What happens when customer name in email doesn't exactly match Odoo? (Fuzzy match attempted, then approval requested for new customer creation)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide `post_to_linkedin` tool accessible to Claude Code that verifies approval before posting and returns post URL
- **FR-002**: System MUST provide `post_to_facebook` tool that enforces 63,206 character limit and publishes posts to the configured Facebook Page with post URL returned
- **FR-004**: System MUST provide `get_post_stats` tool for LinkedIn that returns engagement metrics (likes, comments, shares) for a configurable lookback period
- **FR-005**: System MUST provide `get_page_insights` tool for Facebook that returns engagement metrics (likes, comments, shares, reach) for recent posts
- **FR-006**: System MUST provide `create_invoice` tool that validates customer exists in Odoo before creating invoice and returns invoice number + total amount
- **FR-007**: System MUST provide `mark_invoice_paid` tool that verifies invoice exists and is not already paid before updating payment status
- **FR-008**: System MUST provide `get_revenue` tool that aggregates total, paid, and unpaid revenue for specified date ranges
- **FR-009**: System MUST provide `list_customers` and `create_customer` tools for customer management in Odoo
- **FR-010**: System MUST update Dashboard.md with real-time accounting and social media metrics
- **FR-011**: System MUST detect accounting keywords ("invoice", "send invoice", "billing", "payment received", "paid invoice") in emails and route to AccountingManager via updated SKILL_EmailProcessor and orchestrator
- **FR-012**: System MUST generate weekly social media summaries with engagement metrics from MCP tools, triggered by weekly_audit.py
- **FR-013**: System MUST handle LinkedIn token expiration with appropriate error messages and human alerting
- **FR-014**: System MUST queue accounting tasks when Odoo MCP is unavailable and retry automatically (max 3 attempts)
- **FR-015**: System MUST log all MCP server actions with timestamps, status, and detailed information to respective log files
- **FR-016**: System MUST move approval files from /Approved/ to /Done/ after successful processing
- **FR-017**: System MUST handle Facebook rate limiting by queuing posts for later retry per Graph API rate limits
- **FR-018**: System MUST support both LinkedIn API and Playwright automation implementations
- **FR-019**: System MUST update orchestrator.py SKILL_MAP with new task types (facebook_post, accounting, social_summary)
- **FR-020**: System MUST update SKILL_ApprovalHandler to route approvals to correct MCP tool based on approval type (email, linkedin, facebook, accounting)
- **FR-021**: System MUST provide Docker Compose configuration for local Odoo 19 Community installation with PostgreSQL

### Key Entities

- **LinkedIn Post**: Content published to LinkedIn platform via MCP automation with associated URL and engagement metrics
- **Facebook Post**: Content published to a Facebook Page via MCP automation with 63,206-character limit and associated URL and engagement metrics
- **Odoo Invoice**: Financial document in accounting system with customer, product, amount, and payment status lifecycle (draft → posted → paid)
- **Odoo Customer**: Contact record in Odoo with name, email, phone, and customer rank
- **Accounting Task**: Workflow triggered by email keywords to create invoices, process payments, or manage customers
- **Social Media Summary**: Weekly report aggregating platform activity, engagement metrics, and performance insights for CEO briefing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: LinkedIn MCP posts achieve 95%+ success rate when approved and moved to /Approved/ folder
- **SC-002**: Facebook MCP posts achieve 95%+ success rate with proper character limit enforcement
- **SC-003**: Odoo invoice creation from email requests achieves 90%+ success rate with proper customer validation
- **SC-004**: All 4 MCP servers (email, LinkedIn, Facebook, Odoo) are accessible and functional in Claude Code mcp.json
- **SC-005**: Weekly social media summaries are generated automatically with engagement metrics accuracy >85%
- **SC-006**: Email → Accounting workflow processes 95%+ of invoice requests without manual intervention
- **SC-007**: All MCP server actions are logged with 99%+ completion rate for audit purposes
- **SC-008**: Dashboard updates in real-time with both social media and accounting metrics
- **SC-009**: Cross-domain integration handles 10+ concurrent workflows without conflicts
- **SC-010**: System maintains 99%+ uptime for MCP servers with graceful error handling
- **SC-011**: Odoo 19 running locally via Docker with accounting module, 3+ customers, 3+ products configured
- **SC-012**: All agent skills (LinkedInPoster, FacebookPoster, AccountingManager, SocialSummaryGenerator) are created/updated and integrated with orchestrator

## Assumptions

- LinkedIn API access can be obtained for posting automation (alternative: Playwright browser automation)
- Facebook developer account can be established with Page Access Token for Graph API usage
- Odoo 19 Community edition provides necessary accounting functionality via XML-RPC API
- Current email processing infrastructure (SKILL_EmailProcessor, orchestrator.py) can be extended to support accounting keyword detection and routing
- User has administrative access to install Docker for local Odoo installation
- Network connectivity remains stable for external API calls to social media platforms
- Existing dashboard system can accommodate new accounting and social media metrics
- Existing approval workflow (SKILL_ApprovalHandler) can be extended to new MCP server integrations
- weekly_audit.py exists or will be created to trigger social summary generation

## Constraints

- LinkedIn posts limited to text-only content (images optional but not required for MVP)
- Facebook character limit of 63,206 characters per post must be enforced
- Odoo installation requires Docker with PostgreSQL 15 for community edition
- MCP server tools must be compatible with Claude Code MCP integration (stdio transport)
- Approval workflow must maintain current security model (files moved to /Approved/ folder)
- Rate limits on social media APIs must be respected to avoid account suspension
- All financial data must be transmitted securely with proper authentication
- All automation must provide clear audit trails for compliance and debugging
- No secrets or tokens hardcoded - all credentials via .env files and environment variables

## Dependencies

- Silver tier 100% complete (email MCP server foundation)
- LinkedIn developer account with w_member_social permission (OR Playwright setup)
- Facebook developer account with Page Access Token for Graph API
- Docker and Docker Compose installed for Odoo local installation
- Claude Code MCP configuration support (mcp.json)
- Node.js LTS (v18+) for MCP server implementations
- Python 3.11 for orchestrator and watcher scripts
- Stable internet connection for external API calls
