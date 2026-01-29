# Quickstart: Foundation Setup

## Prerequisites

- Obsidian v1.10.6+ installed
- Claude Code installed and authenticated
- Terminal access
- Git installed

## Setup Steps

### 1. Create Vault Structure

Create the vault directory and all subfolders:

```bash
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done,Logs,Logs/malformed}
```

### 2. Create Dashboard.md

Create `AI_Employee_Vault/Dashboard.md` with the status template containing YAML frontmatter (`last_updated`) and sections: System Status, Recent Activity, Pending Actions, Quick Stats.

### 3. Create Company_Handbook.md

Create `AI_Employee_Vault/Company_Handbook.md` with versioned frontmatter and 7 rule categories: Core Principles, Communication, Financial, File Management, Privacy & Security, Work Hours, Error Handling.

### 4. Create SKILLS.md

Create `AI_Employee_Vault/Needs_Action/SKILLS.md` documenting the Basic Task Processor v1.0 skill with all required sections.

### 5. Test the Workflow

```bash
# Create a test task
# Place TEST_Task.md in AI_Employee_Vault/Needs_Action/

# Use Claude Code to process:
# 1. Read the test file
# 2. Update Dashboard.md
# 3. Move file to Done/
```

### 6. Add to .gitignore

```
AI_Employee_Vault/
```

### 7. Verify

- Open vault in Obsidian — all folders visible
- Dashboard.md renders correctly
- Company_Handbook.md has all 7 rule sections
- Test file moved from Needs_Action/ to Done/
- Dashboard shows updated activity

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Claude Code can't find vault | Run from vault directory or use absolute paths |
| Permission denied | Check folder permissions, stop cloud sync during tests |
| Dashboard doesn't update | Verify write permissions, close file in Obsidian |
