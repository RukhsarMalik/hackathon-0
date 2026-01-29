# Implementation Plan: Foundation Setup

**Branch**: `001-foundation-setup` | **Date**: 2026-01-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/bronze/001-foundation-setup/spec.md`

## Summary

Set up the Obsidian vault directory structure, core markdown files (Dashboard.md, Company_Handbook.md, SKILLS.md), and validate end-to-end file operations (read, write, move) via Claude Code. This is a file-system-only module with no external APIs or Python scripts.

## Technical Context

**Language/Version**: Bash (setup scripts), Markdown (vault files)
**Primary Dependencies**: None (filesystem operations only)
**Storage**: Local filesystem — Obsidian vault as flat directory structure
**Testing**: Manual verification via Claude Code file operations
**Target Platform**: Local workstation (Linux/WSL/macOS/Windows)
**Project Type**: Single project — local-first automation foundation
**Performance Goals**: N/A (human-speed operations, no latency requirements)
**Constraints**: No external APIs, no Python, no Obsidian plugins, no credentials in version control
**Scale/Scope**: Single user, single vault, ~10 files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | All data stays in local vault directory |
| II. Human-in-the-Loop | PASS | No autonomous actions in Module 1; user triggers all operations |
| III. Autonomous Monitoring | N/A | Watchers deferred to Module 2/3 |
| IV. Spec-Driven Development | PASS | Following SDD methodology (spec → plan → tasks) |
| V. Security-First | PASS | No credentials stored; .gitignore for vault |
| VI. Ethical Automation | PASS | Transparent file operations with logging |
| VII. Tiered Development | PASS | Bronze tier foundation — no scope creep into Silver/Gold |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/bronze/001-foundation-setup/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── vault-file-ops.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── Inbox/                    # Drop zone for new files
├── Needs_Action/
│   ├── SKILLS.md            # Agent skill documentation
│   └── TEST_Task.md         # Test file (moves to Done/)
├── Done/                     # Completed tasks
├── Logs/
│   └── malformed/           # Files that failed parsing
├── Dashboard.md             # Status dashboard
└── Company_Handbook.md      # AI behavior rules
```

**Structure Decision**: Flat vault directory at project root. No `src/` or `tests/` needed — Module 1 is entirely markdown files and manual verification. The vault itself is the deliverable.

## Implementation Phases

### Phase 1: Vault Structure (US-1, FR-001)

Create the directory tree:
- `AI_Employee_Vault/` with 4 subdirectories + `Logs/malformed/`
- Add `.gitkeep` files in empty directories so git tracks them
- Add `AI_Employee_Vault/` to `.gitignore` at repo root

### Phase 2: Dashboard.md (US-2, FR-002, FR-005, FR-007)

Create `AI_Employee_Vault/Dashboard.md` with:
- YAML frontmatter: `last_updated` field
- Sections: System Status, Recent Activity, Pending Actions, Quick Stats
- All counters initialized to 0
- Template from spec US-2

### Phase 3: Company_Handbook.md (US-3, FR-003)

Create `AI_Employee_Vault/Company_Handbook.md` with:
- YAML frontmatter: `version`, `created`
- 7 rule categories from spec US-3 template
- All rules actionable and unambiguous

### Phase 4: SKILLS.md (US-5, FR-008)

Create `AI_Employee_Vault/Needs_Action/SKILLS.md` with:
- Basic Task Processor v1.0 skill
- All sections: name, purpose, trigger, process flow, input format, output, error handling

### Phase 5: Test Workflow (US-4, FR-004, FR-006, FR-009)

1. Create `AI_Employee_Vault/Needs_Action/TEST_Task.md` with frontmatter and action items
2. Read the file via Claude Code
3. Update Dashboard.md (increment counters, add activity entry, update timestamp)
4. Move file to `AI_Employee_Vault/Done/TEST_Task.md`
5. Verify Dashboard reflects the change

### Phase 6: Documentation

- Create README-Module1.md with setup instructions
- Create `.env.example` (empty template for future modules)
- Verify all deliverables complete

## Complexity Tracking

No constitution violations — no complexity justifications needed.

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | Vault is local-only |
| V. Security-First | PASS | Vault in .gitignore, no secrets |
| VII. Tiered Development | PASS | Strictly Bronze scope |

**Final gate**: PASS
