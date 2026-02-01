# Research: Silver Module 2 — Email MCP Server + Approval Workflow

## R1: MCP SDK for Python

**Decision**: Use the `mcp` Python package (Model Context Protocol SDK) with stdio transport.

**Rationale**: The official MCP Python SDK provides a standard way to expose tools to Claude Code. The stdio transport is simplest — Claude Code spawns the MCP server as a subprocess and communicates via stdin/stdout. No HTTP server needed.

**Alternatives considered**:
- HTTP-based MCP server (adds complexity with port management, CORS)
- Custom JSON-RPC over pipes (reinventing the wheel)
- Direct Claude API integration (bypasses MCP, loses tool discoverability)

**Key finding**: Install via `pip install mcp`. Server uses `@server.tool()` decorator to register tools. Claude Code configures via `mcp.json` or `.claude/mcp.json`.

## R2: Gmail API — Sending emails

**Decision**: Use `googleapiclient` with existing OAuth credentials (token.pickle) to send emails via `users().messages().send()`.

**Rationale**: Already authenticated for reading in gmail_watcher.py. Sending requires the `gmail.send` scope added to SCOPES. Reuse the same credential flow.

**Alternatives considered**:
- SMTP via smtplib (requires app passwords, less secure)
- SendGrid/Mailgun (external service, violates local-first principle)

**Key finding**: Need to add `https://www.googleapis.com/auth/gmail.send` to SCOPES. Will need to re-authenticate (delete token.pickle) when scope changes. Email body constructed as base64-encoded MIME message.

## R3: Approval file format

**Decision**: YAML frontmatter markdown file with all email metadata in frontmatter and body content below.

**Rationale**: Consistent with existing task file format. Human-readable in Obsidian. YAML frontmatter parseable by code. Includes all data needed to send without external lookups.

**Alternatives considered**:
- JSON files (less human-readable in Obsidian)
- Separate metadata + content files (fragmented, harder to manage)

## R4: Approval watcher vs extending orchestrator

**Decision**: Dedicated `approval_watcher.py` that creates tasks for orchestrator rather than extending orchestrator directly.

**Rationale**: Separation of concerns. The orchestrator processes Needs_Action/. The approval watcher translates Approved/Rejected folder events into Needs_Action/ tasks. This keeps both components simple and testable independently.

**Alternatives considered**:
- Extend orchestrator to also watch Approved/Rejected (mixes concerns, more complex)
- Use filesystem_watcher for Approved/ (doesn't handle the specific approval logic)

## R5: MCP server credential sharing

**Decision**: MCP server reuses the same `token.pickle` and `credentials.json` from the silver/ directory.

**Rationale**: Single set of credentials for all Gmail operations. The MCP server runs in the same working directory as other services. No credential duplication.

**Key finding**: The MCP server needs `gmail.send` scope in addition to `gmail.readonly` and `gmail.modify`. Token must be regenerated with expanded scopes.
