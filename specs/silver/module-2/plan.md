# Implementation Plan: Silver Module 2 — Email MCP Server + Approval Workflow

**Branch**: `main` | **Date**: 2026-01-30 | **Spec**: `specs/silver/module-2/spec.md`
**Input**: Feature specification from `specs/silver/module-2/spec.md`

## Summary

Implement an MCP server exposing `send_email` and `draft_email` tools via Gmail API, a file-based human-in-the-loop approval workflow (Pending_Approval → Approved/Rejected), an approval handler skill, and enhanced email processing that drafts replies requiring approval before sending.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: mcp (Model Context Protocol SDK), google-api-python-client, google-auth, google-auth-oauthlib
**Storage**: File-based (Obsidian vault Markdown files)
**Testing**: pytest with unittest.mock
**Target Platform**: Linux/WSL, macOS
**Project Type**: Single project — MCP server + CLI scripts
**Performance Goals**: MCP server start < 10s; approved emails sent < 1 minute; approval processing < 30s
**Constraints**: All sends require approval file in /Approved/; Gmail API only; must integrate with existing orchestrator
**Scale/Scope**: Single user, local system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | Gmail API via local MCP server; no cloud intermediaries |
| II. Human-in-the-Loop | PASS | Core feature — all emails require approval before sending |
| III. Autonomous Operation | PASS | Approval handler integrates with orchestrator for auto-processing |
| IV. Spec-Driven Development | PASS | Following SDD lifecycle |
| V. Security-First | PASS | Approval validation before send; audit logging; credential management via .env |
| VI. Ethical Automation | PASS | No auto-sending; human reviews every outbound email |
| VII. Tiered Development | PASS | Silver Module 1 complete; building Module 2 |

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/silver/module-2/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (MCP tool schemas)
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code

```text
silver/
├── email_mcp_server.py          # FR-1: MCP server with send_email, draft_email tools
├── approval_watcher.py          # FR-3: Monitors Approved/ and Rejected/ folders
├── AI_Employee_Vault/
│   ├── Needs_Action/
│   │   ├── SKILL_ApprovalHandler.md   # FR-4: Approval processing skill
│   │   └── SKILL_EmailProcessor.md    # FR-5: Updated with reply drafting
│   ├── Pending_Approval/              # Approval requests placed here
│   ├── Approved/                      # NEW: Human moves files here to approve
│   ├── Rejected/                      # NEW: Human moves files here to reject
│   ├── Done/
│   └── Logs/
│       ├── mcp_actions.log            # MCP server audit log
│       └── approval_audit.log         # Approval workflow audit log
├── mcp.json                           # FR-2: MCP configuration for Claude Code
├── orchestrator.py                    # Updated: handle email_approval type
└── start_all.sh                       # Updated: start MCP server + approval watcher
```

**Structure Decision**: Extends existing silver/ directory. New files for MCP server and approval watcher. Updates to orchestrator and startup script.

## Design Decisions

### D1: MCP Server as standalone Python process

The MCP server runs as a separate process using the `mcp` Python SDK. It exposes two tools:
- `send_email(to, subject, body, approval_file)` — validates approval file exists in /Approved/, sends via Gmail API, moves to Done
- `draft_email(to, subject, body)` — returns preview without sending

The server communicates with Claude Code via stdio transport (standard MCP pattern).

### D2: Approval workflow via folder-based state machine

```
Pending_Approval/  →  Human reviews
                   →  Approved/   →  Orchestrator detects → MCP send_email → Done/
                   →  Rejected/   →  Approval watcher logs rejection → Done/
```

No database needed. File presence in a folder = state. Human moves files between folders in Obsidian.

### D3: Approval watcher as separate lightweight service

A dedicated `approval_watcher.py` monitors both `/Approved/` and `/Rejected/` folders:
- Approved files: Creates a task in Needs_Action/ for orchestrator to process via SKILL_ApprovalHandler
- Rejected files: Logs rejection and moves to Done/

This keeps the orchestrator focused on Needs_Action/ processing while the approval watcher handles the approval state transitions.

### D4: Enhanced EmailProcessor creates approval files

Updated SKILL_EmailProcessor instructs Claude to:
1. Analyze incoming email
2. If reply needed → draft reply content
3. Create approval request file in Pending_Approval/ (not send directly)
4. Include original email context in approval file for human review

### D5: MCP configuration via mcp.json

Standard Claude Code MCP config pointing to the email server:
```json
{
  "mcpServers": {
    "email": {
      "command": "python3",
      "args": ["email_mcp_server.py"],
      "cwd": "silver/"
    }
  }
}
```

## Component Specifications

### Email MCP Server (email_mcp_server.py)

```
Tools:
  send_email:
    params: to (str), subject (str), body (str), approval_file (str)
    validation:
      - approval_file must exist in Approved/
      - to must be valid email format
      - subject and body must be non-empty
    action:
      - Authenticate with Gmail API (reuse token.pickle)
      - Create MIME message
      - Send via Gmail API
      - Move approval file to Done/
      - Log to mcp_actions.log
    returns: {success: bool, message_id: str, error: str}

  draft_email:
    params: to (str), subject (str), body (str)
    validation:
      - to must be valid email format
    action:
      - Format email preview
      - Return formatted preview (no send)
    returns: {preview: str}
```

### Approval Watcher (approval_watcher.py)

```
Loop (every 10 seconds):
  1. Scan Approved/ for *.md files
     - For each: create processing task in Needs_Action/ with type: email_approval
     - Move original to Needs_Action/ as context
  2. Scan Rejected/ for *.md files
     - For each: log rejection to approval_audit.log
     - Move to Done/ with rejection note
```

### Approval Handler Skill (SKILL_ApprovalHandler.md)

```
Processing:
  1. Read approved email file
  2. Extract to, subject, body from YAML frontmatter
  3. Call MCP send_email tool with extracted parameters
  4. Handle success/failure
  5. Update Dashboard
  6. Move to Done/

Retry: Up to 3 attempts with 10s delay between
Error: Log to approval_audit.log, flag for human review
```

### Updated SKILL_EmailProcessor

```
Enhanced flow:
  1. Analyze incoming email (existing)
  2. Determine if reply needed (existing)
  3. NEW: If reply needed:
     a. Draft professional reply following Company_Handbook
     b. Create APPROVAL_REPLY_{gmail_id}.md in Pending_Approval/
     c. Include: to, subject, body, original_gmail_id, original_subject
  4. NEW: If no reply needed (newsletters, notifications):
     a. Log as "no reply needed"
     b. Move to Done/
```

## Complexity Tracking

No constitution violations. No complexity justification needed.
