# Quickstart Guide: Business Intelligence & Production System

## Prerequisites

Before running the Business Intelligence & Production System, ensure your environment meets these requirements:

### System Requirements
- **Operating System**: Linux or Windows Subsystem for Linux (WSL2)
- **Python**: Version 3.13 or higher
- **Node.js**: Version 18 or higher for MCP servers
- **Disk Space**: 500MB free space for logs and data
- **Memory**: 2GB RAM minimum

### Required Tools
- **Claude Code CLI**: Installed and accessible in PATH
- **Git**: Version control for updates
- **pip**: Python package installer

## Installation

### 1. Verify Claude Code Installation
```bash
claude --version
# Should return Claude Code version information
```

If Claude Code is not installed, install it first as the orchestrator depends on it entirely.

### 2. Install Python Dependencies
```bash
cd gold/
pip install -r requirements.txt  # if requirements file exists
# Otherwise install from the packages in your codebase:
pip install python-dotenv google-api-python-client facebook-sdk watchdog odoo-client-python
```

### 3. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
vim .env  # Or use your preferred editor
```

Required environment variables for Business Intelligence:
```
VAULT_PATH=./AI_Employee_Vault
CLAUDE_API_KEY=your_claude_api_key_here
GMAIL_CREDENTIALS_PATH=./credentials.json
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
FACEBOOK_PAGE_ID=your_facebook_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
ODOO_URL=https://your-instance.odoo.com
ODOO_DB_NAME=your_database_name
ODOO_USER=your_username
ODOO_PASSWORD=your_password
```

## Configuration

### 1. Set Up Business Goals
Create or update your `AI_Employee_Vault/Business_Goals.md` with your targets:

```yaml
---
type: business_goals_config
last_updated: 2026-02-06
version: 1.0
---

monthly_revenue_target: 50000
current_month: 2026-02

project_deadlines:
  - name: "Q1 Product Launch"
    due_date: 2026-03-15
    priority: high
    status: in_progress

subscriptions:
  - name: "Cloud Service Pro"
    monthly_cost: 199.99
    renewal_date: 2026-03-01
    category: "Infrastructure"
```

### 2. Configure Weekly Briefing Schedule
The system will automatically generate CEO briefings every Sunday at 11 PM. You can adjust this in `dashboard_server.py` or by modifying the cron job.

## Running the System

### 1. Start All Services
```bash
cd gold/
./start_all.sh
```

This will start:
- Orchestrator (Ralph Wiggum loop)
- Gmail Watcher
- LinkedIn Watcher
- Facebook Watcher
- Approval Watcher
- MCP Servers (Email, LinkedIn, Facebook, Odoo)
- Watchdog processes

### 2. Monitor System Health
Check the Dashboard: `AI_Employee_Vault/Dashboard.md` for real-time status.

View logs: `AI_Employee_Vault/Logs/` directory contains system logs.

### 3. Weekly CEO Briefing Generation
The system automatically generates briefings:
- **Schedule**: Sundays at 11 PM
- **Location**: `AI_Employee_Vault/Briefings/`
- **Format**: YYYY-MM-DD_CEO_Briefing.md

## Key Directories

```
gold/
├── AI_Employee_Vault/          # Main workspace
│   ├── Needs_Action/          # Tasks awaiting processing
│   ├── Pending_Approval/      # Human approval required
│   ├── Approved/              # Approved for execution
│   ├── Done/                  # Completed tasks
│   ├── Briefings/             # Weekly CEO reports
│   ├── Dashboard.md          # System status overview
│   └── Logs/                 # System logs
├── orchestrator.py            # Main processing loop
├── start_all.sh              # Service launcher
└── mcp-servers/              # External service connectors
    ├── linkedin-mcp/
    ├── facebook-mcp/
    └── odoo-mcp/
```

## Troubleshooting

### Common Issues

**Issue**: Orchestrator fails to start
**Solution**: Verify Claude Code CLI is installed and in PATH:
```bash
which claude
claude --help
```

**Issue**: MCP servers not connecting
**Solution**: Check credentials in `.env` and ensure services are properly configured.

**Issue**: Weekly briefings not generating
**Solution**: Verify system clock and cron scheduling, check Dashboard.md for any errors.

### Health Checks

Monitor these key indicators in Dashboard.md:
- Service uptime (should be 99%+)
- Task completion rate (should be consistently positive)
- MCP call success rate (should be >95%)
- Error log entries (should be minimal)

## Stopping the System

Use Ctrl+C in the terminal where `start_all.sh` is running to stop all services gracefully.

The system will save current state and clean up resources automatically.