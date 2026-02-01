# Agent Skill: File Drop Processor

## Skill Name
File Drop Processor v1.0

## Purpose
Process file_drop action files from /Needs_Action/ that were created by the File System Watcher.

## Trigger
Manual invocation after watcher creates action files, or scheduled check of Needs_Action/ for FILE_*.md files.

## Process Flow
1. List all `FILE_*.md` files in /Needs_Action/
2. For each file:
   - Read YAML frontmatter (type, original_name, size, detected, status)
   - Confirm type is "file_drop"
   - Determine file type from `original_name` extension
   - Apply type-specific processing rules (see below)
   - Update Dashboard.md with activity
   - Move action file to /Done/
   - Move original file from /Inbox/ to /Done/ (if still present)

## File Type Handling

### .txt / .md Files
1. Read first 500 characters of the original file
2. Check for priority keywords: **urgent**, **invoice**, **payment**, **todo**
3. If keywords found → flag for priority review, note in Dashboard
4. Log summary in Dashboard Recent Activity

### .pdf Files
1. Note file metadata (name, size)
2. Flag: "PDF requires manual review"
3. Move to Done with note about manual review needed

### .csv Files
1. Count rows and columns
2. Read header row
3. Check for financial keywords in headers: **amount**, **price**, **invoice**, **total**, **cost**
4. If financial data detected → flag for financial review per Company_Handbook rules
5. Log row/column count and financial flag status in Dashboard

### Unknown Types
1. Note file extension
2. Flag for manual review
3. Log: "Unknown file type: [ext] — requires manual review"

## Input Format
Action file with YAML frontmatter:

```yaml
---
type: file_drop
original_name: example.txt
size: 1024
detected: 2026-01-29T10:30:00
status: pending
---
```

## Output
- Updated Dashboard.md (last_updated, Completed Today increment, Recent Activity entry)
- Action file moved to /Done/
- Original file moved from /Inbox/ to /Done/ (if present)
- Activity logged

## Error Handling
- If action file has malformed frontmatter → move to /Logs/malformed/
- If original file missing from /Inbox/ → log warning, move action file to /Done/ with note
- If processing error → log error, continue with next file
- Always reference Company_Handbook.md rules before taking actions
