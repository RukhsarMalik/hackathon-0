# Implementation Plan: File System Watcher

**Branch**: `002-filesystem-watcher` | **Date**: 2026-01-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/bronze/002-filesystem-watcher/spec.md`

## Summary

Build a Python watcher script using the watchdog library to continuously monitor `bronze/AI_Employee_Vault/Inbox/` for new files. On detection, create structured action files in `Needs_Action/` with metadata. Handle errors gracefully (quarantine oversized files, log all errors). Include a File Processing Agent Skill for the AI Employee.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: watchdog (filesystem events), python-dotenv (config)
**Storage**: Local filesystem — Obsidian vault directories
**Testing**: Manual end-to-end testing (drop files, verify action files)
**Target Platform**: Local workstation (Linux/WSL/macOS/Windows)
**Project Type**: Single script + agent skill document
**Performance Goals**: Action file created within 5 seconds of file detection
**Constraints**: Single instance, no concurrent processing, files assumed complete on arrival
**Scale/Scope**: Single user, single directory, ~10-50 files/day

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | All processing local; no data leaves the machine |
| II. Human-in-the-Loop | PASS | Watcher only creates action files; human/AI processes them separately |
| III. Autonomous Monitoring | PASS | Continuous watcher is a Bronze tier requirement |
| IV. Spec-Driven Development | PASS | Following SDD (spec → plan → tasks) |
| V. Security-First | PASS | Vault path from .env; no credentials in script; error logging |
| VI. Ethical Automation | PASS | Transparent logging; action files are auditable |
| VII. Tiered Development | PASS | Bronze scope only; no PM2, no MCP |

**Gate result**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/bronze/002-filesystem-watcher/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── watcher-events.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Created by /sp.tasks
```

### Source Code

```text
bronze/
├── filesystem_watcher.py             # Watcher script
├── AI_Employee_Vault/
│   ├── Inbox/                        # Monitored directory
│   ├── Needs_Action/
│   │   ├── SKILLS.md                 # Module 1 skill
│   │   ├── SKILL_FileProcessor.md    # Module 2 skill
│   │   └── FILE_*.md                 # Auto-generated action files
│   ├── Done/
│   ├── Logs/
│   │   ├── watcher_errors.log
│   │   └── quarantine/
│   ├── Dashboard.md
│   └── Company_Handbook.md
└── README-Module2.md
```

**Structure Decision**: Watcher script lives at `bronze/` root alongside the vault. Single-file script — no package structure needed for Bronze tier.

## Implementation Phases

### Phase 1: Dependencies & Configuration

- Install watchdog and python-dotenv
- Update .env.example with VAULT_PATH
- Configure logging (dual output: console + file)

### Phase 2: Core Watcher Script (US-1, US-2, FR-001 to FR-004, FR-010)

- Create `InboxHandler` class extending `FileSystemEventHandler`
- Implement `on_created` to detect new files (ignore directories)
- Generate action files with YAML frontmatter and suggested actions
- Sanitize filenames for action file naming (FR-007)
- Main loop with `Observer` watching Inbox/

### Phase 3: Error Handling (US-3, FR-005 to FR-008)

- File size check: >10MB → move to Logs/quarantine/
- Permission error handling with logging
- Filename sanitization for special characters
- Missing directory recovery
- Catch-all exception handler per file event
- Dual logging: console + Logs/watcher_errors.log

### Phase 4: Lifecycle Management (US-5, FR-009)

- Startup logging with directory path
- KeyboardInterrupt handler for clean shutdown
- Verify monitored directory exists before starting
- Observer stop and join on shutdown

### Phase 5: Agent Skill (US-4, FR-012)

- Create SKILL_FileProcessor.md with processing rules for:
  - .txt/.md: Read preview, keyword detection, priority flagging
  - .pdf: Metadata extraction, manual review flag
  - .csv: Row/column count, header analysis, financial keyword detection
  - Unknown: Manual review flag, extension logging

### Phase 6: Testing & Documentation

- Create test files (test.txt, urgent_note.md, sample.pdf, data.csv)
- Run end-to-end workflow
- Create README-Module2.md
- Update .env.example

## Complexity Tracking

No constitution violations — no complexity justifications needed.

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | All local filesystem operations |
| III. Autonomous Monitoring | PASS | Continuous watcher implemented |
| V. Security-First | PASS | Config via .env, logging to file, quarantine for bad files |
| VII. Tiered Development | PASS | No Silver/Gold features |

**Final gate**: PASS
