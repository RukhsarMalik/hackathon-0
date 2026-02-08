# Silver Tier Demo Script

## 1. System Overview
- Show the `silver/` directory structure
- Highlight key components: orchestrator, watchers, MCP server, approval workflow
- Show `AI_Employee_Vault/` folder structure in Obsidian

## 2. Start All Services
```bash
cd silver/
./start_all.sh
```
- Point out the 6 services starting: gmail, filesystem, linkedin, orchestrator, approval, mcp_email

## 3. Health Check
```bash
python health_check.py
```
- Show all 6 services reporting UP
- Show Dashboard freshness status

## 4. Email Detection Demo
- Send a test email to the linked Gmail account
- Wait for Gmail watcher to detect it (check console output)
- Show the created task file in `Needs_Action/`
- Watch orchestrator pick it up and process with SKILL_EmailProcessor
- Show the processed file in `Done/`
- Show Dashboard updated with email activity

## 5. Approval Workflow Demo

### 5a. Approve an Email
- Show an approval request in `Pending_Approval/`
- Move it to `Approved/` (drag in Obsidian or `mv` command)
- Watch approval_watcher detect it
- Show orchestrator process via SKILL_ApprovalHandler
- Verify email sent (check mcp_actions.log)
- Show file moved to `Done/`

### 5b. Reject an Email
- Show an approval request in `Pending_Approval/`
- Move it to `Rejected/`
- Watch approval_watcher log the rejection
- Show approval_audit.log entry
- Show file moved to `Done/` with rejection note

## 6. LinkedIn Post Demo
- Show linkedin_watcher schedule (Mon/Wed/Fri)
- Show a generated post request in `Pending_Approval/`
- Show the post content and format

## 7. Plan Generation Demo
```bash
# Create a complex task
cat > AI_Employee_Vault/Needs_Action/DEMO_ComplexTask.md << 'EOF'
---
type: complex_task
priority: medium
title: "Prepare weekly business summary"
created: "2026-01-30T18:00:00Z"
---

# Prepare Weekly Business Summary

Create a comprehensive weekly business summary including email activity, task completion stats, and recommendations.

## Requirements
- Summarize email processing activity from Dashboard
- Compile task completion statistics
- Generate 3 actionable recommendations
- Update Dashboard with summary results
EOF
```
- Watch orchestrator detect and route to SKILL_PlanGenerator
- Show the generated PLAN_*.md file with checkboxes
- Watch steps being executed and checkboxes updating
- Show completed plan in `Done/`

## 8. Dashboard Review
- Open `AI_Employee_Vault/Dashboard.md` in Obsidian
- Show all sections: System Status, Plan Generation Stats, Email Approval Stats, Recent Activity
- Highlight the comprehensive activity log

## 9. Wrap Up
- Stop all services: `Ctrl+C`
- Run final health check to show services stopped
- Summarize Silver tier capabilities:
  - Automated email monitoring and processing
  - Human-in-the-loop approval workflow
  - LinkedIn post scheduling
  - Multi-step plan generation
  - Unified dashboard and health monitoring
