# Module 1: Foundation Setup

## Prerequisites
- Obsidian v1.10.6+ installed
- Claude Code installed and authenticated
- Terminal access
- Git installed

## Setup

### 1. Vault Structure
The vault is located at `bronze/AI_Employee_Vault/` with this structure:

```
AI_Employee_Vault/
├── Inbox/                    # Drop zone for new files
├── Needs_Action/
│   └── SKILLS.md            # Agent skill documentation
├── Done/                     # Completed tasks
├── Logs/
│   └── malformed/           # Files that failed parsing
├── Dashboard.md             # Status dashboard
└── Company_Handbook.md      # AI behavior rules
```

### 2. Open in Obsidian
1. Open Obsidian
2. "Open folder as vault" → select `bronze/AI_Employee_Vault/`
3. All folders and files should appear in the sidebar

### 3. Environment Variables
Copy `.env.example` to `.env` at the project root and fill in values when needed for Modules 2 and 3.

## Test Workflow

To verify the system works end-to-end:

1. Create a task file in `Needs_Action/`:
   ```markdown
   ---
   type: task
   priority: medium
   created: 2026-01-29
   ---
   ## Task Description
   [Your task here]
   ## Actions
   - [ ] Step 1
   - [ ] Step 2
   ```

2. Use Claude Code to process the task:
   - Read the file from `Needs_Action/`
   - Update `Dashboard.md` with activity
   - Move the file to `Done/`

3. Verify:
   - File exists in `Done/`
   - File removed from `Needs_Action/`
   - Dashboard shows updated counters and activity

## Key Files

| File | Purpose |
|------|---------|
| Dashboard.md | Real-time status of the AI Employee |
| Company_Handbook.md | Behavior rules (7 categories) |
| SKILLS.md | Agent skill definitions |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Claude Code can't find vault | Use absolute path to `bronze/AI_Employee_Vault/` |
| Permission denied | Check folder permissions, stop cloud sync during tests |
| Dashboard doesn't update | Verify write permissions, close file in Obsidian first |

## Next Steps
- **Module 2**: File System Watcher (Python script monitoring Inbox/)
- **Module 3**: Gmail Watcher (Gmail API integration)
