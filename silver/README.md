# AI Employee - Silver Tier

Orchestrator + LinkedIn Automation + Email MCP Server with human-in-the-loop approval workflow. Automates task processing via Claude Code, generates LinkedIn posts, and sends approved emails via Gmail API.

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Orchestrator | `orchestrator.py` | Auto-detects tasks in Needs_Action/, invokes Claude Code to process them |
| Email MCP Server | `email_mcp_server.py` | MCP server with send_email and draft_email tools via Gmail API |
| Approval Watcher | `approval_watcher.py` | Monitors Approved/ and Rejected/ folders for approval decisions |
| LinkedIn Watcher | `linkedin_watcher.py` | Creates LinkedIn post requests on Mon/Wed/Fri schedule |
| Gmail Watcher | `gmail_watcher.py` | Monitors Gmail for important emails (from Bronze) |
| File System Watcher | `filesystem_watcher.py` | Monitors Inbox/ for new files (from Bronze) |
| Health Check | `health_check.py` | Verifies all services are running and system is healthy |
| Startup Script | `start_all.sh` | Launches all services with graceful shutdown |

## Setup

```bash
cd silver/

# Install dependencies
pip install watchdog python-dotenv google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# Configure environment
cp .env.example .env

# Copy Gmail credentials from bronze (if using Gmail)
cp ../bronze/credentials.json .
cp ../bronze/token.pickle .
```

## Running

### Start all services
```bash
./start_all.sh
```

### Stop all services
Press `Ctrl+C`

### Run health check
```bash
python health_check.py
python health_check.py --json  # JSON output
```

## How It Works

### Orchestrator Flow
1. Scans `Needs_Action/` every 30 seconds
2. Skips SKILL_* files (they're instructions, not tasks)
3. Waits 10s after file creation (debounce)
4. Reads YAML frontmatter to determine task type
5. Maps type to skill file (email → SKILL_EmailProcessor, file_drop → SKILL_FileProcessor, linkedin_post → SKILL_LinkedInPoster)
6. Invokes Claude Code CLI with task content + skill instructions
7. Claude processes the task, updates Dashboard, moves file to Done/

### LinkedIn Schedule
| Day | Post Type | Description |
|-----|-----------|-------------|
| Monday | weekly_update | Business highlights and achievements |
| Wednesday | tip_of_day | Practical industry tips |
| Friday | success_story | Client success or business wins |

Posts are generated at 09:00 and placed in `Pending_Approval/` for human review.

### Email Approval Workflow
1. Gmail Watcher detects important email → creates task in Needs_Action/
2. Orchestrator processes with SKILL_EmailProcessor → if reply needed, creates approval request in Pending_Approval/
3. Human reviews in Obsidian → moves to Approved/ or Rejected/
4. Approval Watcher detects → creates task for orchestrator (approved) or logs rejection
5. Orchestrator processes with SKILL_ApprovalHandler → calls MCP send_email
6. Email sent via Gmail API → approval file moved to Done/

### Plan Generation Workflow
1. A task with `type: complex_task` is placed in Needs_Action/
2. Orchestrator routes to SKILL_PlanGenerator
3. Claude Code analyzes the task, creates `PLAN_{id}.md` with numbered checkboxes
4. Steps are executed sequentially; checkboxes updated as each completes
5. Dashboard updated with plan progress
6. Completed plan and source task moved to Done/

Plan files use YAML frontmatter with fields: `type: plan`, `source_task`, `status`, `total_steps`, `completed_steps`.

### MCP Configuration
Add to your Claude Code MCP config (`~/.claude/mcp.json`):
```json
{
  "mcpServers": {
    "email": {
      "command": "python3",
      "args": ["email_mcp_server.py"],
      "cwd": "/path/to/silver/"
    }
  }
}
```

## Directory Structure

```
silver/
├── orchestrator.py
├── linkedin_watcher.py
├── gmail_watcher.py
├── filesystem_watcher.py
├── health_check.py
├── start_all.sh
├── .env.example
├── .gitignore
├── .pids/                        # PID files (auto-created)
└── AI_Employee_Vault/
    ├── Inbox/                    # File drop zone
    ├── Needs_Action/             # Pending tasks
    │   ├── SKILLS.md
    │   ├── SKILL_FileProcessor.md
    │   ├── SKILL_EmailProcessor.md
    │   ├── SKILL_LinkedInPoster.md
    │   ├── SKILL_ApprovalHandler.md
    │   └── SKILL_PlanGenerator.md
    ├── Pending_Approval/         # Approval requests awaiting review
    ├── Approved/                 # Human-approved items (triggers send)
    ├── Rejected/                 # Human-rejected items (logged, archived)
    ├── Done/                     # Processed tasks
    ├── Logs/
    │   ├── orchestrator.log
    │   ├── linkedin_watcher.log
    │   ├── gmail_errors.log
    │   ├── watcher_errors.log
    │   ├── processed_emails.txt
    │   ├── linkedin_posts.json
    │   ├── mcp_actions.log
    │   └── approval_audit.log
    ├── Dashboard.md
    └── Company_Handbook.md
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Orchestrator not processing | Check `claude` CLI is in PATH, check orchestrator.log |
| LinkedIn posts not creating | Verify day/time matches schedule, check linkedin_posts.json for duplicates |
| Health check shows DOWN | Run `./start_all.sh` to restart all services |
| Tasks stuck in Needs_Action | Check orchestrator.log for errors, verify skill files exist |
| MCP server not starting | Run `pip install mcp`, check credentials.json exists |
| Emails not sending | Verify approval file is in Approved/, check mcp_actions.log |
| Approval not detected | Check approval_watcher is running, verify file is in Approved/ |
| Plan not created | Verify task has `type: complex_task` in frontmatter, check orchestrator.log |
| Plan steps stuck | Check orchestrator.log for Claude CLI errors, verify skill file exists |
| Plan not completing | Check PLAN_*.md progress log for failed steps, verify Dashboard access |
