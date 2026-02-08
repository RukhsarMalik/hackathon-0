# Implementation Plan: Gold Module 1 - External Integrations & Automation

**Branch**: `001-external-integrations-automation` | **Date**: 2026-02-05 | **Spec**: [specs/gold/module1/spec.md](specs/gold/module1/spec.md)
**Input**: Feature specification from `specs/gold/module1/spec.md`

**Note**: This plan implements the Gold Module 1 specification with MCP servers for LinkedIn, Facebook, and Odoo integration.

## Summary

Implementation of Gold Module 1 featuring multiple MCP servers for LinkedIn and Facebook auto-posting, Odoo accounting integration, and cross-domain email-accounting workflows. This extends the Silver tier foundation with advanced automation capabilities including social media posting and financial management.

## Technical Context

**Language/Version**: Node.js LTS (v18+), Python 3.11
**Primary Dependencies**: @modelcontextprotocol/sdk, axios, xmlrpc, playwright, facebook-sdk, docker
**Storage**: File-based (Obsidian vault) with Odoo ERP database (PostgreSQL via Docker)
**Testing**: Manual testing with Claude Code integration + test scripts
**Target Platform**: Local development environment with Docker for Odoo
**Project Type**: Multi-service integration with MCP servers
**Performance Goals**: <10 second response times for MCP tool calls, 99% uptime for MCP servers
**Constraints**: <5 seconds for invoice creation, <3 seconds for social media posting, rate limiting compliance
**Scale/Scope**: Support 10+ concurrent MCP requests, handle growing customer base in Odoo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Local-First Privacy: MCP servers run locally, data stays in user's control
- Human-in-the-Loop: Approval workflows maintained for sensitive operations
- Autonomous Operation: Watcher scripts will monitor and trigger MCP actions
- Security-First: Credentials stored in environment variables, not in vault
- Ethical Automation: Clear audit trails and human oversight maintained

## Project Structure

### Documentation (this feature)

```text
specs/gold/module1/
├── spec.md              # Feature specification (8 user stories)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Setup guide
├── contracts/           # API contracts per MCP server
│   ├── linkedin-mcp-contract.md
│   ├── facebook-mcp-contract.md
│   └── odoo-mcp-contract.md
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
gold/
├── mcp-servers/
│   ├── base-template.js         # Shared MCP server template
│   ├── logging-framework.js     # Shared logging utilities
│   ├── .env.example             # Template for MCP env vars
│   ├── linkedin-mcp/            # LinkedIn MCP server
│   │   ├── package.json
│   │   ├── index.js             # API-based implementation
│   │   ├── playwright-index.js  # Playwright fallback (optional)
│   │   └── .env
│   ├── facebook-mcp/            # Facebook MCP server
│   │   ├── package.json
│   │   ├── index.js
│   │   └── .env
│   └── odoo-mcp/                # Odoo MCP server
│       ├── package.json
│       ├── index.js
│       └── .env
├── docker-compose.yml           # Odoo 19 + PostgreSQL
├── config/
│   └── odoo.conf                # Odoo configuration
├── orchestrator.py              # Task orchestrator (UPDATED)
├── mcp.json                     # Claude Code MCP config
├── start_all.sh                 # Service startup script (UPDATED)
├── test-linkedin-mcp.js         # LinkedIn MCP tests
├── run-tests.js                 # Test runner
└── AI_Employee_Vault/
    ├── Dashboard.md             # UPDATED with accounting metrics
    └── Logs/
        ├── linkedin_actions.log # NEW
        ├── facebook_actions.log # NEW
        └── odoo_actions.log     # NEW

Skills/
├── SKILL_LinkedInPoster.md      # UPDATED with MCP integration
├── SKILL_FacebookPoster.md      # NEW
├── SKILL_AccountingManager.md   # NEW
├── SKILL_SocialSummaryGenerator.md # NEW
├── SKILL_EmailProcessor.md      # UPDATED with accounting handoff
└── SKILL_ApprovalHandler.md     # UPDATED with multi-MCP routing
```

**Structure Decision**: Multi-service architecture with separate MCP servers for each integration point, maintaining separation of concerns while enabling cross-domain workflows.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple MCP servers | Required for different API integrations | Single server would create tight coupling between different services |
| External dependencies (Docker, Odoo) | Needed for accounting functionality | Building accounting system from scratch would be excessive scope |

## Phase 0: Research Requirements

The following unknowns were resolved (see research.md):

1. LinkedIn API access requirements vs Playwright automation approach
2. Facebook Graph API authentication setup and rate limits
3. Odoo 19 Community installation and configuration requirements
4. MCP server integration patterns with Claude Code
5. Security best practices for storing API credentials
6. Error handling patterns for external service failures
7. Rate limiting strategies for social media APIs

## Phase 1: Design Decisions & Architecture

### 1.1 MCP Server Architecture

**Decision**: Each external service gets its own MCP server process.

```
Claude Code ─── stdio ──→ LinkedIn MCP ──→ LinkedIn API
            ─── stdio ──→ Facebook MCP ──→ Facebook Graph API
            ─── stdio ──→ Odoo MCP     ──→ Odoo XML-RPC (localhost:8069)
            ─── stdio ──→ Email MCP    ──→ Gmail API (existing)
```

**Rationale**: Isolation means one server failure doesn't affect others. Each server manages its own credentials, rate limiting, and error handling independently.

### 1.2 LinkedIn Implementation Strategy

**Decision**: Support both API and Playwright approaches.

| Approach | Pros | Cons |
|----------|------|------|
| LinkedIn API (primary) | Reliable, returns post URL, proper error codes | Requires developer app approval (3-7 days) |
| Playwright (fallback) | No API approval needed | Fragile, no post URL, needs manual login |

**Implementation**: `index.js` for API, `playwright-index.js` for Playwright. User configures which to use via mcp.json `args` field.

### 1.3 Facebook Graph API Version

**Decision**: Use Facebook Graph API with `facebook-sdk` npm package.

- Page Access Token for posting to Facebook Pages
- Rate limit: Per Graph API rate limiting (200 calls/user/hour)
- Posting: `POST /{page-id}/feed` with message parameter
- Insights: `GET /{page-id}/insights` for engagement metrics (likes, comments, shares, reach)

### 1.4 Odoo Integration Architecture

**Decision**: Docker Compose for Odoo 19 + PostgreSQL, XML-RPC for integration.

```
Docker Network (odoo-network):
  ┌─────────┐     ┌──────────┐
  │ Odoo 19 │────→│ Postgres │
  │ :8069   │     │ :5432    │
  └────┬────┘     └──────────┘
       │
  XML-RPC API
       │
  ┌────┴────┐
  │ Odoo MCP│
  │ Server  │
  └─────────┘
```

**XML-RPC endpoints**:
- `{url}/xmlrpc/2/common` - Authentication
- `{url}/xmlrpc/2/object` - CRUD operations via `execute_kw`

### 1.5 Orchestrator Update Design

**Decision**: Extend existing orchestrator.py SKILL_MAP and add cross-domain routing.

**Current SKILL_MAP**:
```python
SKILL_MAP = {
    'email': 'SKILL_EmailProcessor.md',
    'file_drop': 'SKILL_FileProcessor.md',
    'linkedin_post': 'SKILL_LinkedInPoster.md',
    'email_approval': 'SKILL_ApprovalHandler.md',
    'complex_task': 'SKILL_PlanGenerator.md',
}
```

**Updated SKILL_MAP**:
```python
SKILL_MAP = {
    'email': 'SKILL_EmailProcessor.md',
    'file_drop': 'SKILL_FileProcessor.md',
    'linkedin_post': 'SKILL_LinkedInPoster.md',
    'facebook_post': 'SKILL_FacebookPoster.md',
    'email_approval': 'SKILL_ApprovalHandler.md',
    'complex_task': 'SKILL_PlanGenerator.md',
    'accounting': 'SKILL_AccountingManager.md',
    'invoice_request': 'SKILL_AccountingManager.md',
    'social_summary': 'SKILL_SocialSummaryGenerator.md',
}
```

**New function**: `contains_accounting_keywords(content)` checks email content for accounting-related terms and returns True if detected.

**New function**: `create_accounting_task(email_content, task_file)` creates a subtask file with `type: accounting` in Needs_Action/ for the AccountingManager to process.

**Cross-domain routing in `process_task()`**:
```python
# After determining task_type == 'email':
if contains_accounting_keywords(task_content):
    create_accounting_task(task_content, file_path)
```

### 1.6 Approval Handler Multi-MCP Routing

**Decision**: Extend SKILL_ApprovalHandler to detect approval type and route to correct MCP.

**Routing logic** (based on frontmatter `type` or file naming):
```
type: email_approval     → Email MCP: send_email
type: linkedin_post_ready → LinkedIn MCP: post_to_linkedin
type: facebook_post_ready → Facebook MCP: post_to_facebook
type: invoice_approval    → Odoo MCP: create_invoice
```

### 1.7 SKILL_EmailProcessor Accounting Handoff

**Decision**: Add accounting keyword detection section to SKILL_EmailProcessor.md.

**Keywords**: "invoice", "send invoice", "billing", "payment received", "paid invoice", "payment confirmation"

**Handoff flow**:
```
Email arrives with "invoice" keyword
  ↓
EmailProcessor detects accounting keyword
  ↓
Extracts: customer name, service, amount, invoice number
  ↓
Hands off to SKILL_AccountingManager
  ↓
AccountingManager calls Odoo MCP
  ↓
AccountingManager drafts reply
  ↓
EmailProcessor moves original email to /Done/
```

### 1.8 Dashboard Update Schema

**New sections in Dashboard.md**:
```markdown
## Accounting Activity
- **Revenue MTD**: $X,XXX (XX% of $XX,XXX target)
- **Invoices Created**: X
- **Invoices Paid**: X
- **Outstanding**: $X,XXX

## Social Media Activity
- **LinkedIn Posts This Week**: X
- **Facebook Posts This Week**: X
- **Total Engagement**: X (likes + comments + shares)
```

## Phase 2: Implementation Sequence

### Dependency Graph

```
US-1 (LinkedIn MCP) ──┐
                       ├──→ US-3 (Agent Skills) ──→ US-8 (Social Summary)
US-2 (Facebook MCP) ──┘          │
                                  │
US-4 (Odoo Install) ──→ US-5 (Odoo MCP) ──→ US-6 (Accounting Skill) ──→ US-7 (Cross-Domain)
                                                      │
                                                      └──→ Orchestrator Update
                                                      └──→ EmailProcessor Update
                                                      └──→ ApprovalHandler Update
```

### Implementation Order

1. **US-1**: LinkedIn MCP Server (independent, can start immediately)
2. **US-2**: Facebook MCP Server (independent, can parallel with US-1)
3. **US-4**: Odoo Installation (independent, can parallel with US-1/US-2)
4. **US-5**: Odoo MCP Server (depends on US-4)
5. **US-3**: Agent Skills - Update all skill files (depends on US-1, US-2 patterns)
6. **US-6**: Accounting Agent Skill (depends on US-5)
7. **US-7**: Cross-Domain Integration - orchestrator.py, EmailProcessor, ApprovalHandler updates (depends on US-6)
8. **US-8**: Social Media Summary (depends on US-3)

### Parallel Execution Opportunities

- US-1 + US-2 + US-4 can all start in parallel
- US-3 skill file creation can partially overlap with US-5
- US-8 can start once US-3 is done, independent of US-6/US-7

## Phase 3: Interface Definitions

See contract files for full API specifications:
- [LinkedIn MCP Contract](contracts/linkedin-mcp-contract.md)
- [Facebook MCP Contract](contracts/facebook-mcp-contract.md)
- [Odoo MCP Contract](contracts/odoo-mcp-contract.md)

### Common Response Pattern (all MCP tools)

**Success**:
```json
{ "success": true, "message": "...", ...tool-specific-fields }
```

**Failure**:
```json
{ "success": false, "error": "Human-readable error message" }
```

### Approval File Format (standardized)

```yaml
---
type: [email_approval|linkedin_post_ready|facebook_post_ready|invoice_approval]
platform: [email|linkedin|facebook|odoo]
action: [send_email|post_to_linkedin|post_to_facebook|create_invoice]
created: [ISO timestamp]
status: awaiting_approval
---
[Content to be posted/sent]
```

## Phase 4: Error Handling Strategy

### Retry Matrix

| Service | Transient Error | Auth Error | Rate Limit |
|---------|----------------|------------|------------|
| LinkedIn API | Retry 3x, 5s backoff | Alert human, pause | Queue 1 hour |
| Facebook Graph API | Retry 3x, 5s backoff | Alert human, pause | Queue 1 hour |
| Odoo XML-RPC | Retry 3x, 5m backoff | Alert human | N/A |
| Email MCP | Retry 3x, 10s backoff | Alert human | Queue 5 min |

### Failure Recovery

1. **MCP server crash**: Orchestrator logs error, task stays in Needs_Action/ for next cycle
2. **Odoo Docker down**: Odoo MCP returns connection error, task file created with PENDING_ODOO_ prefix
3. **Rate limit hit**: Post queued with timestamp, retried on next orchestrator cycle after cooldown
4. **Token expired**: Error logged to dashboard, human alerted, all posting paused for that platform

## Phase 5: Security Considerations

- All API credentials in `.env` files (gitignored)
- MCP server credentials in Claude Code mcp.json `env` section
- No credentials in vault markdown files
- Approval verification: all posting tools check approval_file path contains `/Approved/`
- Audit trail: every MCP action logged with timestamp, parameters, result
- Odoo credentials: admin password changed from default in production
