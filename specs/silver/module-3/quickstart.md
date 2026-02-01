# Quickstart: Silver Module 3 — Plan Generation + Integration

## Prerequisites

- Silver Modules 1 & 2 fully operational
- All 6 services running via `./start_all.sh`
- Claude Code CLI available in PATH

## Test 1: Plan Generation

### Setup
Create a complex task file in Needs_Action/:

```bash
cat > silver/AI_Employee_Vault/Needs_Action/TEST_ComplexTask.md << 'EOF'
---
type: complex_task
priority: medium
title: "Research and summarize AI trends"
created: "2026-01-30T12:00:00Z"
---

# Research and Summarize AI Trends

Research the latest AI trends for Q1 2026, create a summary document, and draft a LinkedIn post about the findings.

## Requirements
- Research at least 3 AI trend sources
- Create a summary with key findings
- Draft a LinkedIn post highlighting top trends
- Update the Dashboard with research results
EOF
```

### Expected Result
1. Orchestrator detects TEST_ComplexTask.md (type: complex_task)
2. SKILL_PlanGenerator creates PLAN_research_and_summarize.md with 4+ steps
3. Steps are executed sequentially with checkboxes updated
4. Dashboard updated with plan progress
5. Plan and task moved to Done/ on completion

### Verification
```bash
# Check for plan file
ls silver/AI_Employee_Vault/Needs_Action/PLAN_*.md

# Check Dashboard for plan activity
grep -i "plan" silver/AI_Employee_Vault/Dashboard.md
```

## Test 2: Integration Verification

### Run Health Check
```bash
cd silver/
python health_check.py
```

Expected: All 6 services UP, Dashboard FRESH, no stuck tasks.

### End-to-End Email Workflow
1. Send test email to linked Gmail account
2. Verify Gmail watcher creates task in Needs_Action/
3. Verify orchestrator processes with SKILL_EmailProcessor
4. If reply generated, verify approval file in Pending_Approval/
5. Move to Approved/, verify email sent via MCP

## Test 3: Demo Walkthrough

Follow `silver/DEMO_SCRIPT.md` for complete Silver tier demonstration.
