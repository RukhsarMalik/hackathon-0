# Agent Skill: Basic Task Processing

## Skill Name
Basic Task Processor v1.0

## Purpose
Process simple task files from /Needs_Action/ folder

## Trigger
Manual invocation or scheduled check

## Process Flow
1. List all .md files in /Needs_Action/
2. For each file:
   - Read content
   - Extract action items (lines starting with "- [ ]")
   - Determine task type from frontmatter
   - Execute according to Company_Handbook rules
   - Update Dashboard with activity
   - Move file to /Done/ with timestamp

## Input Format
Markdown file with optional YAML frontmatter:

```yaml
---
type: task
priority: medium
created: 2026-01-29
---
```

### Task Description
[What needs to be done]

### Actions
- [ ] Step 1
- [ ] Step 2

## Output
- Updated Dashboard.md
- File moved to /Done/[FILENAME]
- Activity logged

## Error Handling
- If file malformed: Move to /Logs/malformed/
- If task unclear: Move to /Needs_Action/REVIEW_[FILENAME]
- If critical error: Log and alert human

## Testing
Place a test file in /Needs_Action/ and verify it moves to /Done/ with Dashboard updated.
