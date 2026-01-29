# Data Model: File System Watcher

**Feature**: 002-filesystem-watcher
**Date**: 2026-01-29

## Entities

### Watched File (Input)

A file appearing in the Inbox/ directory that triggers the watcher.

**Attributes**:
| Field     | Type    | Description                  | Source         |
|-----------|---------|------------------------------|----------------|
| name      | string  | Original filename with ext   | filesystem     |
| stem      | string  | Filename without extension   | derived        |
| suffix    | string  | File extension (e.g., .txt)  | derived        |
| size      | integer | File size in bytes           | filesystem     |
| path      | Path    | Absolute path to file        | filesystem     |
| detected  | ISO dt  | When the watcher detected it | runtime        |

**Validation**:
- size <= 10MB (10,485,760 bytes) — otherwise quarantine
- name must be sanitizable to valid filesystem characters

---

### Action File (Output)

A markdown file created in Needs_Action/ representing a detected file drop.

**Naming**: `FILE_[sanitized_stem].md`

**YAML Frontmatter**:
| Field         | Type   | Description                     | Example                    |
|---------------|--------|---------------------------------|----------------------------|
| type          | string | Always "file_drop"              | file_drop                  |
| original_name | string | Original filename (unsanitized) | my report (final).txt      |
| size          | int    | File size in bytes              | 1024                       |
| detected      | ISO dt | Detection timestamp             | 2026-01-29T10:30:00        |
| status        | string | Always "pending" on creation    | pending                    |

**Body sections**: File Details, Suggested Actions (checkboxes)

---

### Quarantined File

A file exceeding 10MB, moved from Inbox/ to Logs/quarantine/.

**Attributes**: Same as Watched File, plus error log entry with reason.

---

### Agent Skill: File Processor

Processing rules document at `Needs_Action/SKILL_FileProcessor.md`.

**File Type Rules**:
| Extension   | Processing                                     | Priority Check |
|-------------|-------------------------------------------------|----------------|
| .txt, .md   | Read first 500 chars, keyword scan             | Yes            |
| .pdf        | Note metadata, flag for manual review          | No             |
| .csv        | Count rows/cols, read headers, financial check | Yes            |
| Other       | Flag for manual review, log extension          | No             |

**Priority Keywords**: urgent, invoice, payment, todo

## State Transitions

```
Inbox/ file detected
    │
    ├── size > 10MB ──→ Logs/quarantine/ (error logged)
    │
    └── size <= 10MB ──→ Action file in Needs_Action/
                              │
                              ├── AI processes ──→ Done/ (both files)
                              └── Error ──→ Logs/ (error logged)
```

## Relationships

```
Watched File (Inbox/) ──(triggers)──→ Action File (Needs_Action/)
Action File ──(processed by)──→ SKILL_FileProcessor.md
SKILL_FileProcessor.md ──(references)──→ Company_Handbook.md
Processing ──(updates)──→ Dashboard.md
Completed ──(moves to)──→ Done/
Oversized ──(quarantined to)──→ Logs/quarantine/
```
