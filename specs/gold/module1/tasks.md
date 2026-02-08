# Implementation Tasks: Gold Module 1 - External Integrations & Automation

**Feature**: Gold Module 1 - External Integrations & Automation
**Date**: 2026-02-05
**Status**: In progress

## Summary

Implementation of Gold Module 1 featuring MCP servers for LinkedIn, Facebook, and Odoo integration to enable automated social media posting and accounting management. This extends the Silver tier with advanced automation capabilities.

## Dependencies

- Silver tier 100% complete (email MCP server foundation)
- Node.js LTS (v18+) installed
- Docker and Docker Compose installed
- Claude Code configured with MCP support

## Implementation Strategy

### MVP First Approach
Start with LinkedIn MCP server implementation as the first deliverable (User Story 1), which provides immediate value with automated LinkedIn posting. Subsequently implement Facebook MCP (User Story 2), Odoo integration (User Stories 4-5), social summaries (User Story 8), and cross-domain integration (User Story 7).

### Incremental Delivery
Each user story is designed to be independently testable and deliverable, building upon the previous ones to gradually expand the AI employee's automation capabilities.

## Phase 1: Setup (Project Initialization)

Goal: Prepare the development environment and initialize project structure.

- [x] T001 Create mcp-servers directory structure
- [x] T002 Initialize git repository with proper .gitignore for MCP servers
- [x] T003 Set up Docker environment for Odoo installation (Odoo 19 + PostgreSQL running)

## Phase 2: Foundational Tasks

Goal: Establish foundational components required for all user stories.

- [x] T010 Create base MCP server template files
- [x] T011 Set up environment variable configuration for all MCP servers
- [x] T012 Configure Claude Code MCP integration for new servers
- [x] T013 Create logging framework for MCP actions

## Phase 3: LinkedIn MCP Server (User Story 1 - P1)

Goal: Implement LinkedIn MCP server for auto-posting approved content.

**Independent Test**: Create LinkedIn MCP server with post_to_linkedin tool, then approve a post draft and verify it publishes automatically to LinkedIn with URL returned.

- [x] T020 [P] [US1] Create mcp-servers/linkedin-mcp/package.json with MCP dependencies
- [x] T021 [P] [US1] Create mcp-servers/linkedin-mcp/index.js with post_to_linkedin tool
- [x] T022 [US1] Create mcp-servers/linkedin-mcp/.env for LinkedIn credentials
- [x] T023 [US1] Implement approval verification in LinkedIn MCP
- [x] T024 [US1] Implement post URL return functionality
- [x] T025 [US1] Implement file movement from /Approved/ to /Done/
- [x] T026 [US1] Add error handling for LinkedIn token expiration
- [x] T027 [US1] Add logging for LinkedIn actions
- [x] T028 [US1] Test LinkedIn MCP with sample post
- [x] T029 [US1] Implement get_post_stats tool for engagement tracking

## Phase 4: Facebook MCP Server (User Story 2 - P1)

Goal: Implement Facebook MCP server for auto-posting approved content.

**Independent Test**: Create Facebook MCP server with post_to_facebook tool, then approve a post draft and verify it publishes automatically to the Facebook Page with URL returned.

- [x] T040 [P] [US2] Create mcp-servers/facebook-mcp/package.json with Facebook Graph API dependencies
- [x] T041 [P] [US2] Create mcp-servers/facebook-mcp/index.js with post_to_facebook tool
- [x] T042 [P] [US2] Create mcp-servers/facebook-mcp/.env for Facebook credentials (FACEBOOK_PAGE_ID, FACEBOOK_PAGE_ACCESS_TOKEN)
- [x] T043 [US2] Implement character limit enforcement (63,206 chars)
- [x] T044 [US2] Implement approval verification in Facebook MCP
- [x] T045 [US2] Implement file movement from /Approved/ to /Done/
- [x] T046 [US2] Add rate limiting with queue for retries per Graph API limits
- [x] T047 [US2] Add logging for Facebook actions
- [x] T048 [US2] Implement get_page_insights tool for engagement metrics
- [x] T049 [US2] Test Facebook MCP with sample post

## Phase 5: Social Media Agent Skills (User Story 3 - P1)

Goal: Create and update agent skill files for social media automation.

**Independent Test**: Verify SKILL_LinkedInPoster has MCP integration section, SKILL_FacebookPoster exists with post formatting, SKILL_SocialSummaryGenerator exists with weekly report format.

- [x] T055 [P] [US3] Update SKILL_LinkedInPoster.md with LinkedIn MCP integration section
- [x] T056 [US3] Create SKILL_FacebookPoster.md with post formatting and character limit enforcement
- [x] T057 [US3] Create SKILL_SocialSummaryGenerator.md with weekly report format
- [x] T058 [US3] Update SKILL_ApprovalHandler.md for multi-MCP routing (email, linkedin, facebook, accounting)
- [ ] T059 [US3] Verify all skill files integrate with orchestrator SKILL_MAP

## Phase 6: Odoo 19 Installation & Setup (User Story 4 - P1)

Goal: Set up Odoo 19 locally via Docker with accounting module configured.

**Independent Test**: Start Odoo via Docker, create database, install accounting module, add test customers/products, create manual invoice, verify API access.

- [x] T060 [P] [US4] Create docker-compose.yml for Odoo 19 Community + PostgreSQL 15
- [x] T061 [US4] Create config/odoo.conf for Odoo configuration
- [x] T062 [US4] Start Odoo Docker containers and verify localhost:8069 accessible
- [x] T063 [US4] Create database `ai_employee_accounting` with accounting module installed
- [x] T064 [US4] Add 3+ customers to Odoo (Client A - TechCorp, Client B - StartupXYZ, Client C - DesignStudio)
- [x] T065 [US4] Add 3+ products/services to Odoo (Web Development $100/hr, Automation Setup $150/hr, Consulting $200/hr)
- [x] T066 [US4] Create test invoice and verify lifecycle (draft → posted → paid) - INV/2026/00001 paid, INV/2026/00002 posted
- [x] T067 [US4] Verify XML-RPC API access with test Python script

## Phase 7: Odoo MCP Server (User Story 5 - P1)

Goal: Implement Odoo MCP server for automated accounting operations.

**Independent Test**: Start Odoo MCP server, verify connection, test all 6 tools.

- [x] T070 [P] [US5] Create mcp-servers/odoo-mcp/package.json with XML-RPC dependencies
- [x] T071 [P] [US5] Create mcp-servers/odoo-mcp/index.js with Odoo authentication
- [x] T072 [US5] Create mcp-servers/odoo-mcp/.env for Odoo credentials
- [x] T073 [US5] Implement create_invoice tool with customer/product validation
- [x] T074 [US5] Implement mark_invoice_paid tool with status checking
- [x] T075 [US5] Implement get_revenue tool for date-range reporting
- [x] T076 [US5] Implement list_customers and create_customer tools
- [x] T077 [US5] Add connection error handling with retry logic
- [x] T078 [US5] Add comprehensive logging for all Odoo interactions
- [x] T079 [US5] Test Odoo MCP with live Odoo instance (API verified, invoice lifecycle tested)

## Phase 8: Accounting Agent Skill (User Story 6 - P1)

Goal: Create SKILL_AccountingManager.md with all 4 accounting workflows.

**Independent Test**: Verify skill file contains complete process flows for invoice creation, payment processing, revenue reports, and customer management.

- [x] T080 [P] [US6] Create SKILL_AccountingManager.md with Workflow 1 (Create Invoice from Email)
- [x] T081 [US6] Add Workflow 2 (Mark Invoice Paid) to AccountingManager
- [x] T082 [US6] Add Workflow 3 (Monthly Revenue Report) to AccountingManager
- [x] T083 [US6] Add Workflow 4 (Add New Customer) to AccountingManager
- [x] T084 [US6] Add error handling section (Odoo offline, customer not found, creation failure)
- [x] T085 [US6] Add quality checks and dashboard update format
- [x] T086 [US6] Add integration with other skills section (EmailProcessor, Business Goals)

## Phase 9: Cross-Domain Integration (User Story 7 - P2)

Goal: Integrate email processing with accounting workflows and update orchestrator.

**Independent Test**: Send email requesting invoice, verify end-to-end flow through email → accounting → Odoo → reply.

- [x] T090 [P] [US7] Update SKILL_EmailProcessor.md with accounting keyword detection and handoff logic
- [x] T091 [P] [US7] Update orchestrator.py SKILL_MAP with new task types (facebook_post, accounting, invoice_request, social_summary)
- [x] T092 [US7] Add contains_accounting_keywords() function to orchestrator.py
- [x] T093 [US7] Add create_accounting_task() function to orchestrator.py
- [x] T094 [US7] Update orchestrator.py SKILL_PATTERNS with new skill file exclusions
- [x] T095 [US7] Add cross-domain routing in process_task() for email→accounting handoff
- [ ] T096 [US7] Test email with "invoice" keyword triggers accounting workflow
- [ ] T097 [US7] Test email with "payment received" triggers payment processing
- [ ] T098 [US7] Test full end-to-end: email → Odoo invoice → reply drafted → dashboard updated

## Phase 10: Social Media Summary Generation (User Story 8 - P2)

Goal: Implement automated generation of weekly social media summaries.

**Independent Test**: Generate weekly summary using data from social media logs and MCP tools, verify it contains engagement metrics.

- [x] T100 [P] [US8] SKILL_SocialSummaryGenerator.md created with log scanning steps
- [x] T101 [US8] Engagement statistics aggregation from MCP tools documented
- [x] T102 [US8] Weekly summary format for CEO briefings defined
- [x] T103 [US8] Top performer identification logic documented
- [x] T104 [US8] Posting frequency and consistency metrics included
- [x] T105 [US8] Fallback handling when MCPs unavailable documented
- [x] T106 [US8] CEO briefing append path defined (/Briefings/YYYY-MM-DD_CEO_Briefing.md)
- [ ] T107 [US8] Test weekly summary generation with mock log data

## Phase 11: Infrastructure & Integration Updates

Goal: Update startup scripts, MCP config, and supporting infrastructure.

- [x] T110 Update claude-code-mcp-config.json / mcp.json with all 4 MCP servers
- [ ] T111 Update start_all.sh to include new MCP server startup commands
- [ ] T112 Create/update .env.example files for each MCP server with required variables documented
- [ ] T113 Update Dashboard.md with accounting and social media sections
- [ ] T114 Ensure all new log files (linkedin_actions.log, facebook_actions.log, odoo_actions.log) are created on first run

## Phase 12: Testing & Validation

Goal: Ensure all components work together correctly.

- [ ] T120 Test full LinkedIn posting workflow: draft → approve → auto-post → URL logged → file moved to Done
- [ ] T121 Test full Facebook posting workflow: post to Page
- [ ] T122 Test Odoo MCP: create invoice → verify in Odoo UI
- [ ] T123 Test Odoo MCP: mark invoice paid → verify in Odoo UI
- [ ] T124 Test cross-domain: email with "invoice" keyword → Odoo invoice created → reply drafted
- [ ] T125 Test cross-domain: email with "payment received" → invoice marked paid → revenue updated
- [ ] T126 Test social media summary generation with real log data
- [ ] T127 Test error scenarios: MCP server down, Odoo offline, token expired
- [ ] T128 Test concurrent approvals (LinkedIn + Facebook + email simultaneously)
- [ ] T129 Verify dashboard shows correct metrics from all sources

## Task Dependencies

### User Story Completion Order
1. US-1 (LinkedIn MCP) + US-2 (Facebook MCP) + US-4 (Odoo Install) - can run in parallel
2. US-5 (Odoo MCP) - depends on US-4
3. US-3 (Agent Skills) - depends on US-1, US-2 patterns established
4. US-6 (Accounting Skill) - depends on US-5
5. US-7 (Cross-Domain) - depends on US-6, integrates with US-3
6. US-8 (Social Summary) - depends on US-3

### Critical Path
US-4 → US-5 → US-6 → US-7 (Odoo install is the bottleneck for accounting features)

### Parallel Execution Opportunities
- T020-T029 (LinkedIn MCP) can run in parallel with T040-T049 (Facebook MCP) and T060-T061 (Docker compose)
- T055-T057 (Skill files) can run in parallel with T070-T078 (Odoo MCP code)
- T100-T106 (Social Summary skill) can run in parallel with T080-T086 (Accounting skill)

## Success Criteria

- [ ] LinkedIn MCP server operational with 95%+ success rate for auto-posting
- [ ] Facebook MCP server operational with 95%+ success rate for auto-posting
- [ ] Odoo 19 running locally via Docker with accounting module configured
- [ ] Odoo MCP server connects to Odoo and all 6 tools functional
- [ ] All 4 MCP servers integrated and accessible to Claude Code (mcp.json)
- [ ] SKILL_EmailProcessor updated with accounting keyword handoff
- [ ] SKILL_ApprovalHandler updated for multi-MCP routing
- [ ] Orchestrator.py updated with new SKILL_MAP entries and accounting detection
- [ ] Social media summary generation documented and tested
- [ ] Cross-domain email → accounting workflow functional end-to-end
- [ ] Dashboard updated with real-time accounting and social media metrics
- [ ] All actions logged to respective log files
- [ ] End-to-end testing completed with 90%+ success rate for all workflows
