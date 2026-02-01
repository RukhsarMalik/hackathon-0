# Implementation Plan: Silver Module 1 — Orchestrator + LinkedIn Automation

**Branch**: `main` | **Date**: 2026-01-30 | **Spec**: `specs/silver/module-1/spec.md`
**Input**: Feature specification from `specs/silver/module-1/spec.md`

## Summary

Implement an automated orchestrator that monitors `Needs_Action/` and triggers Claude Code for task processing without manual intervention, a LinkedIn watcher that creates scheduled post requests (Mon/Wed/Fri), a LinkedIn poster skill, a unified startup script, and a health monitor. All components build on the existing bronze tier file-based workflow.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: watchdog, python-dotenv, subprocess (stdlib)
**Storage**: File-based (Obsidian vault Markdown files)
**Testing**: pytest with unittest.mock
**Target Platform**: Linux/WSL (Windows via WSL), macOS
**Project Type**: Single project — CLI scripts
**Performance Goals**: Task processing within 10 seconds of file creation; 24h+ continuous operation
**Constraints**: No external database; no actual LinkedIn API (content generation only); must preserve bronze tier functionality
**Scale/Scope**: Single user, local system, 5 concurrent services max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | All data stays in local vault; no external transmissions |
| II. Human-in-the-Loop | PASS | LinkedIn posts go to Pending_Approval; orchestrator only processes existing skills |
| III. Autonomous Operation | PASS | Orchestrator + watchers provide continuous monitoring |
| IV. Spec-Driven Development | PASS | Following SDD lifecycle |
| V. Security-First | PASS | No credentials in code; .env for config; audit logging |
| VI. Ethical Automation | PASS | LinkedIn posts require human approval before publishing |
| VII. Tiered Development | PASS | Bronze complete; building Silver capabilities |

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/silver/module-1/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
silver/
├── orchestrator.py              # FR-1: Monitors Needs_Action, triggers Claude Code
├── linkedin_watcher.py          # FR-2: Schedules LinkedIn post requests
├── start_all.sh                 # FR-4: Unified startup script (bash)
├── health_check.py              # FR-5: Health monitoring
├── AI_Employee_Vault/
│   ├── Inbox/
│   ├── Needs_Action/
│   │   ├── SKILLS.md
│   │   ├── SKILL_FileProcessor.md
│   │   ├── SKILL_EmailProcessor.md
│   │   └── SKILL_LinkedInPoster.md   # FR-3: New skill file
│   ├── Pending_Approval/             # New: LinkedIn posts awaiting approval
│   ├── Done/
│   ├── Logs/
│   │   ├── orchestrator.log
│   │   ├── linkedin_watcher.log
│   │   ├── gmail_errors.log
│   │   ├── watcher_errors.log
│   │   ├── processed_emails.txt
│   │   └── linkedin_posts.json       # Post history tracking
│   ├── Dashboard.md
│   └── Company_Handbook.md
├── filesystem_watcher.py        # Copied from bronze
├── gmail_watcher.py             # Copied from bronze
├── .env.example
└── .gitignore

tests/
├── test_orchestrator.py
├── test_linkedin_watcher.py
├── test_health_check.py
└── test_linkedin_poster_skill.py
```

**Structure Decision**: Single project layout under `silver/` directory, mirroring bronze structure. Tests in a sibling `tests/` directory at the same level or under `specs/`.

## Design Decisions

### D1: Orchestrator triggers Claude Code via subprocess

The orchestrator will invoke `claude` CLI via `subprocess.run()` with a constructed prompt that includes the task file content and skill instructions. This keeps the orchestrator simple — it's a file watcher + dispatcher, not an AI engine itself.

**Flow**:
1. Detect new `.md` file in `Needs_Action/` (exclude `SKILL_*`, `SKILLS.md`)
2. Wait 10s debounce
3. Read file, determine type from YAML frontmatter
4. Build prompt: "Process this task using {skill}. File content: {content}. Move to Done when complete."
5. Run `claude --print --dangerously-skip-permissions "{prompt}"` (or interactive mode)
6. 30s cooldown before next cycle

### D2: LinkedIn Watcher uses schedule-based file creation

No LinkedIn API needed. The watcher checks current day/time, creates a `LINKEDIN_POST_*.md` file in `Needs_Action/` with the post type. The orchestrator picks it up and uses the LinkedIn Poster skill to generate content in `Pending_Approval/`.

**Post history** tracked in `Logs/linkedin_posts.json` to prevent duplicates on the same day.

### D3: Startup script manages PIDs

`start_all.sh` launches each watcher as a background process, writes PIDs to `.pids/`, and runs orchestrator in foreground. `trap` on SIGINT kills all background PIDs for graceful shutdown.

### D4: Health check reads PID files + Dashboard

`health_check.py` checks:
- PID files exist and processes are running (`os.kill(pid, 0)`)
- Dashboard.md `last_updated` is within 24 hours
- No files in `Needs_Action/` older than 2 hours (stuck tasks)

## Component Specifications

### Orchestrator (orchestrator.py)

```
Loop:
  1. List *.md in Needs_Action/ (exclude SKILL_*, SKILLS.md)
  2. For each file not yet processing:
     a. Wait 10s after file mtime (debounce)
     b. Read YAML frontmatter → extract type
     c. Map type → skill file (email→SKILL_EmailProcessor, file_drop→SKILL_FileProcessor, linkedin_post→SKILL_LinkedInPoster)
     d. Read skill file content
     e. Build Claude prompt
     f. subprocess.run(["claude", "--print", "-p", prompt])
     g. Log result
  3. Sleep 30s (cooldown)
```

### LinkedIn Watcher (linkedin_watcher.py)

```
Schedule:
  Monday    09:00 → weekly_update
  Wednesday 09:00 → tip_of_day
  Friday    09:00 → success_story

Loop:
  1. Check current day/time
  2. If scheduled day and within time window:
     a. Check linkedin_posts.json for today's entry
     b. If not posted today, create LINKEDIN_POST_*.md in Needs_Action/
     c. Log to linkedin_posts.json
  3. Sleep 60s
```

### LinkedIn Poster Skill (SKILL_LinkedInPoster.md)

Skill file with instructions for generating LinkedIn content:
- Post structure: Hook → Context → Value → CTA → Hashtags
- Three templates: weekly_update, tip_of_day, success_story
- Output goes to `Pending_Approval/LINKEDIN_READY_*.md`

### Startup Script (start_all.sh)

```bash
1. Check prerequisites (python3, claude, vault dir)
2. mkdir -p .pids
3. Start gmail_watcher.py → .pids/gmail.pid
4. Start filesystem_watcher.py → .pids/filesystem.pid
5. Start linkedin_watcher.py → .pids/linkedin.pid
6. trap cleanup SIGINT SIGTERM
7. Start orchestrator.py (foreground)
```

### Health Check (health_check.py)

```
1. Check each PID file in .pids/ → process alive?
2. Read Dashboard.md last_updated → within 24h?
3. List Needs_Action/ files → any older than 2h?
4. Print status table
5. Exit 0 (healthy) or 1 (issues)
```

## Complexity Tracking

No constitution violations. No complexity justification needed.
