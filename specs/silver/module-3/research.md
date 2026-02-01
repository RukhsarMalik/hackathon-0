# Research: Silver Module 3 — Plan Generation + Integration

## R1: Plan Generation Approach

**Decision**: Skill-based plan generation using Claude Code as the reasoning engine
**Rationale**: The orchestrator already invokes Claude Code CLI with skill instructions for all task types. Plan generation is a reasoning task — determining what steps are needed — which is exactly what Claude Code excels at. Adding a SKILL_PlanGenerator.md follows the established pattern without new dependencies.
**Alternatives considered**:
- Python-based plan generation with templates: Too rigid; can't handle arbitrary task types
- Separate planning service: Over-engineered for single-user system
- LangChain/LangGraph agents: Unnecessary dependency; Claude Code CLI already provides agent capabilities

## R2: Complex Task Detection

**Decision**: Explicit `type: complex_task` in YAML frontmatter
**Rationale**: Consistent with existing type-based routing (email, file_drop, linkedin_post, email_approval). Simple, predictable, no ambiguity.
**Alternatives considered**:
- Heuristic detection (word count, keyword analysis): Unreliable, false positives
- All tasks go through planner: Unnecessary overhead for simple tasks
- User-specified complexity flag: Extra burden on upstream components

## R3: Plan File Format

**Decision**: Markdown with YAML frontmatter and checkbox steps, stored as PLAN_*.md in Needs_Action/
**Rationale**: Human-readable in Obsidian, consistent with vault file patterns, easy for Claude Code to parse and update. Checkboxes provide clear progress tracking.
**Alternatives considered**:
- JSON plan files: Not human-readable in Obsidian
- Separate Plans/ directory: Adds complexity; Needs_Action/ is the processing queue
- Database tracking: Violates file-based constraint

## R4: Integration Testing Strategy

**Decision**: Manual end-to-end verification using demo script
**Rationale**: The system is file-based with multiple long-running processes. Automated integration tests would require complex process management. A structured demo script serves as both verification and demonstration.
**Alternatives considered**:
- pytest with subprocess management: Complex setup, brittle
- Docker-based testing: Over-engineered for hackathon
- Unit tests only: Don't verify integration

## R5: Documentation Approach

**Decision**: Update existing Silver README + create demo script as separate file
**Rationale**: Single README already covers Modules 1 & 2. Adding Module 3 content keeps documentation consolidated. Demo script is separate because it's a procedural walkthrough, not reference documentation.
**Alternatives considered**:
- Per-module READMEs: Fragmented, harder to maintain
- Wiki-style documentation: Not in vault
