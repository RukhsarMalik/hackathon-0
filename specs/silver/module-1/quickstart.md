# Quickstart: Silver Module 1

## Prerequisites

- Python 3.13+
- Claude Code CLI installed and authenticated
- Bronze tier complete (vault structure, gmail_watcher, filesystem_watcher)
- pip packages: `watchdog`, `python-dotenv`

## Setup

```bash
cd silver/

# 1. Copy environment config
cp .env.example .env
# Edit .env with your VAULT_PATH

# 2. Copy credentials from bronze (if using Gmail watcher)
cp ../bronze/credentials.json .
cp ../bronze/token.pickle .

# 3. Make startup script executable
chmod +x start_all.sh
```

## Running

### Start all services
```bash
cd silver/
./start_all.sh
```

This launches:
- Gmail Watcher (background)
- File System Watcher (background)
- LinkedIn Watcher (background)
- Orchestrator (foreground)

### Stop all services
Press `Ctrl+C` — the startup script handles graceful shutdown of all processes.

### Run health check
```bash
python health_check.py
```

## Testing the Orchestrator

1. Create a test task file:
   ```bash
   cat > AI_Employee_Vault/Needs_Action/TEST_task.md << 'EOF'
   ---
   type: task
   priority: medium
   status: pending
   ---
   ## Test Task
   This is a test to verify the orchestrator processes tasks automatically.
   EOF
   ```

2. Wait ~10 seconds (debounce) — the orchestrator should detect and process it.

3. Check `AI_Employee_Vault/Done/` for the processed file and `Dashboard.md` for updated activity.

## Testing LinkedIn Watcher

The LinkedIn watcher creates posts on Mon/Wed/Fri at 09:00. To test immediately, temporarily modify the schedule in `linkedin_watcher.py` or create a manual post request:

```bash
cat > AI_Employee_Vault/Needs_Action/LINKEDIN_POST_test.md << 'EOF'
---
type: linkedin_post
topic: tip_of_day
scheduled_date: 2026-01-30
status: pending
---
## LinkedIn Post Request
Generate a tip_of_day post for LinkedIn.
EOF
```

The orchestrator will pick it up and generate content in `Pending_Approval/`.

## Directory Structure

```
silver/
├── orchestrator.py
├── linkedin_watcher.py
├── start_all.sh
├── health_check.py
├── gmail_watcher.py
├── filesystem_watcher.py
├── .env.example
├── .pids/                    # PID files (auto-created)
└── AI_Employee_Vault/
    ├── Inbox/
    ├── Needs_Action/
    ├── Pending_Approval/     # LinkedIn posts awaiting human review
    ├── Done/
    ├── Logs/
    ├── Dashboard.md
    └── Company_Handbook.md
```
