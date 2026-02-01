# Implementation Plan: Silver Module 3 — Plan Generation + Integration

**Branch**: `main` | **Date**: 2026-01-30 | **Spec**: `specs/silver/module-3/spec.md`
**Input**: Feature specification from `specs/silver/module-3/spec.md`

## Summary

Add plan generation capabilities for complex multi-step tasks (SKILL_PlanGenerator + orchestrator integration), verify end-to-end Silver tier integration, update documentation, and create a demo script.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Existing Silver infrastructure (orchestrator, watchers, MCP server)
**Storage**: File-based (Obsidian vault Markdown files)
**Testing**: Manual end-to-end verification
**Target Platform**: Linux/WSL, macOS
**Project Type**: Extension of existing Silver tier
**Constraints**: Must integrate with existing orchestrator SKILL_MAP; file-based workflow only; no Bronze modifications

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Privacy | PASS | All processing local |
| II. Human-in-the-Loop | PASS | Plans visible in vault for human review |
| III. Autonomous Operation | PASS | Plan generation extends orchestrator capabilities |
| IV. Spec-Driven Development | PASS | Following SDD lifecycle |
| V. Security-First | PASS | No new credentials or external APIs |
| VI. Ethical Automation | PASS | Plans are transparent Markdown files |
| VII. Tiered Development | PASS | Silver Modules 1 & 2 complete; building Module 3 |

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/silver/module-3/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code

```text
silver/
├── AI_Employee_Vault/
│   └── Needs_Action/
│       └── SKILL_PlanGenerator.md   # NEW: Plan generation skill instructions
├── orchestrator.py                   # UPDATE: Add complex_task type → SKILL_PlanGenerator mapping
└── (all existing files unchanged)
```

## Design Decisions

### D1: Plan generation as a skill file (not code)

Plan generation is implemented as a SKILL_PlanGenerator.md instruction file, not as Python code. The orchestrator already invokes Claude Code CLI with skill instructions — Claude Code itself handles the reasoning about what steps are needed and creates the plan. This keeps the architecture consistent with existing skills (EmailProcessor, FileProcessor, etc.).

**Rationale**: Claude Code is the reasoning engine. The skill file provides instructions; Claude generates the actual plan content. No new Python code needed for plan logic.

### D2: Complex task detection via frontmatter type

Tasks with `type: complex_task` in their YAML frontmatter are routed to SKILL_PlanGenerator. The orchestrator already reads frontmatter type fields — this is a single mapping addition.

Alternatively, SKILL_PlanGenerator could be invoked for ANY task type when the content appears complex (3+ steps). However, explicit typing is simpler and consistent with existing patterns.

**Decision**: Use explicit `type: complex_task` frontmatter field.

### D3: Plan files stored in Needs_Action/ as PLAN_*.md

Generated plans are written as `PLAN_{task_id}.md` files in Needs_Action/. The plan contains checkboxes that Claude Code checks off as it processes each step. When all steps are complete, the plan moves to Done/.

The orchestrator already skips SKILL_* files. We add PLAN_* to the skip patterns so plans aren't re-processed as new tasks. Instead, the SKILL_PlanGenerator instructions tell Claude to execute the plan steps directly.

### D4: Documentation updates consolidate existing README

The Silver README already exists and covers Modules 1 & 2. Module 3 adds plan generation documentation to the existing README rather than creating a new file. The demo script is a separate Markdown file with step-by-step instructions.

## Component Specifications

### SKILL_PlanGenerator.md

```
Instructions for Claude Code:
  1. Read the complex task file
  2. Analyze requirements and break into discrete steps (3+)
  3. Create PLAN_{task_id}.md with:
     - YAML frontmatter (type: plan, source_task, created date)
     - Numbered checkboxes for each step
     - Dependencies between steps noted
  4. Execute each step sequentially
  5. After completing each step, update the checkbox to [X]
  6. Update Dashboard with plan progress
  7. When all steps complete, move plan and source task to Done/
```

### Orchestrator Updates

```
Add to SKILL_MAP:
  'complex_task': 'SKILL_PlanGenerator.md'

Add to SKILL_PATTERNS:
  'SKILL_PlanGenerator.md'

Skip pattern addition:
  Files starting with 'PLAN_' are skipped (they're plans being executed, not new tasks)
```

### Demo Script (silver/DEMO_SCRIPT.md)

```
Step-by-step demo walkthrough:
  1. Show architecture diagram
  2. Start all services (./start_all.sh)
  3. Run health check
  4. Send test email → show Gmail watcher detection
  5. Show orchestrator processing
  6. Demonstrate approval workflow (approve + reject)
  7. Show LinkedIn post generation
  8. Create complex task → show plan generation
  9. Show Dashboard with all activity
```

## Complexity Tracking

No constitution violations. No complexity justification needed. This module is primarily a skill file addition + minor orchestrator update + documentation.
