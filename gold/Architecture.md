# Business Intelligence & Production System Architecture

## Overview

The Business Intelligence & Production System (Gold Module 2) transforms the AI Employee from a functional assistant into a true business intelligence agent with weekly CEO briefings, continuous task processing, and advanced monitoring.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                           │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│    LinkedIn     │    Facebook     │     Gmail       │  Odoo   │
│   MCP Server    │  MCP Server     │  MCP Server     │ MCP     │
│                 │                 │                 │ Server  │
└─────────────────┴─────────────────┴─────────────────┴─────────┘
                    │                   │
                    ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Model Context Protocol Layer                  │
│              (Secure External Service Interface)               │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Services                              │
│  │ Orchestrator │ │ Watchdog │ │ Dashboard │ │ Weekly Audit │ │
│  │    (Ralph   │ │  Server  │ │  Server   │ │    Script   │ │
│  │   Loop)     │ │          │ │           │ │             │ │
└─────────────────┴─────────────┴─────────────┴───────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Data Storage Layer                           │
│  │ Business Goals │ │ Audit Logs │ │ CEO Briefings │ │ Tasks │ │
│  │    Config      │ │            │               │ │ Queue │ │
└────────────────────┴──────────────┴───────────────┴─────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                File-Based Task Queue                          │
│  │ Needs Action │ │ Pending App │ │  Approved   │ │  Done   │ │
│  │     (Task)   │ │   roval     │ │   (Task)    │ │ (Task)  │ │
└──────────────────┴───────────────┴───────────────┴───────────┘
```

## Core Components

### 1. Orchestrator (Ralph Wiggum Loop)
- **File**: `orchestrator.py`
- **Function**: Continuously processes tasks from `/Needs_Action/` until empty
- **Features**:
  - Task processing with retry logic (max 3 attempts)
  - Audit logging for all operations
  - Performance metrics tracking
  - Integration with Claude Code for AI processing

### 2. Watchdog Process Monitor
- **File**: `watchdog.py`
- **Function**: Monitors system processes and automatically restarts crashed services
- **Features**:
  - Health checks every minute
  - Automatic restart with rate limiting (max 5/hour)
  - PID file management
  - Dashboard status updates

### 3. Weekly Audit System
- **File**: `weekly_audit.py`
- **Function**: Generates CEO briefings every Sunday at 11 PM
- **Features**:
  - Revenue data extraction from Odoo MCP
  - Task completion metrics from `/Done/` folder
  - Subscription usage analysis (>30 days unused)
  - Project deadline monitoring

### 4. Dashboard Server
- **File**: `dashboard_server.py`
- **Function**: Serves HTML dashboard and provides JSON API
- **Features**:
  - Real-time service status monitoring
  - System metrics visualization
  - REST API for frontend consumption

### 5. Audit Logging System
- **File**: `audit_logging.py`
- **Function**: Structured JSON logging for all system operations
- **Features**:
  - Daily log rotation (YYYY-MM-DD_audit.json)
  - 90-day retention policy
  - Tamper-evident integrity checking
  - Log analysis and viewing tools

## Data Flow

### Weekly CEO Briefing Generation
```
Business_Goals.md → weekly_audit.py → Data Aggregation →
CEO Briefing Template → Output to /Briefings/ → Dashboard Update
```

### Continuous Task Processing (Ralph Loop)
```
/Needs_Action/ → orchestrator.py → Claude Code →
Skill Application → /Done/ → Dashboard Update → Loop Back to /Needs_Action/
```

### Error Recovery & Graceful Degradation
```
Service Failure → watchdog.py → Health Check →
Automatic Restart (with limits) → /Needs_Action_Fallback/ → Retry Queue →
Service Restoration → Process Queued Actions
```

### Cross-Domain Intelligence Workflow
```
Email Received → EmailProcessor → Payment Keywords →
AccountingManager → Odoo MCP Update → Milestone Logging →
LinkedIn Post Draft (if significant) → Dashboard Update
```

## Security & Compliance

### Authentication & Authorization
- MCP servers handle external service authentication
- Environment variables for credentials (.env)
- No sensitive data stored in file system

### Audit Trail
- All operations logged in structured JSON format
- Integrity hashes for tamper detection
- 90-day retention with archiving capability

### Data Sovereignty
- All data stored in local Obsidian vault structure
- No external transmission of sensitive business data
- Complete audit trail maintained locally

## Deployment Architecture

### File Structure
```
gold/
├── AI_Employee_Vault/              # Primary knowledge base
│   ├── Inbox/                     # Incoming raw data
│   ├── Needs_Action/              # Tasks requiring processing
│   ├── Pending_Approval/          # Human approval required
│   ├── Approved/                  # Approved for execution
│   ├── Done/                      # Completed tasks
│   ├── Rejected/                  # Rejected tasks
│   ├── Logs/                      # Processing logs
│   │   └── Audit/                 # Structured audit logs
│   ├── Briefings/                 # Weekly CEO briefings
│   ├── Dashboard.md              # Central status overview
│   └── Business_Goals.md         # Business rules and targets
├── orchestrator.py                 # Main task processing loop
├── watchdog.py                     # Process monitoring
├── weekly_audit.py                 # Weekly briefing generation
├── dashboard_server.py             # Dashboard web interface
├── audit_logging.py               # Structured logging system
├── business_goals_utils.py        # Business goals parsing
├── ceo_briefing_utils.py          # Briefing generation tools
├── mcp-servers/                   # MCP server implementations
│   ├── linkedin-mcp/
│   ├── facebook-mcp/
│   └── odoo-mcp/
└── start_all.sh                   # Service startup script
```

### Process Management
- All services run as background Python processes
- PID files in `/.pids/` directory for monitoring
- Graceful shutdown handling with SIGINT
- Automatic restart on failure (rate limited)

## Performance Characteristics

### Processing Speed
- Real-time task processing (< 30 seconds)
- Weekly briefings generated within 5 minutes
- Health checks every minute

### Reliability
- 99% uptime target with watchdog monitoring
- Automatic error recovery with retry mechanisms
- Graceful degradation when external services unavailable

### Scalability
- Single-user business automation system
- File-based architecture scales to thousands of tasks
- Linear performance degradation under heavy load