# Research: Foundation Setup

**Feature**: 001-foundation-setup
**Date**: 2026-01-29

## R1: Vault Directory Structure Convention

**Decision**: Use flat 4-folder structure at vault root: `Inbox/`, `Needs_Action/`, `Done/`, `Logs/`
**Rationale**: Obsidian works best with shallow folder hierarchies. Flat structure keeps sidebar navigation simple and avoids nested path complexity for file move operations.
**Alternatives considered**:
- Nested structure (e.g., `Tasks/Active/`, `Tasks/Completed/`) — adds unnecessary depth for Bronze tier
- Date-based subfolders (e.g., `Done/2026-01/`) — premature optimization, can be added in Silver tier

## R2: Dashboard Update Mechanism

**Decision**: Direct file write with YAML frontmatter parsing. Claude Code reads Dashboard.md, parses frontmatter, updates fields, and writes back the entire file.
**Rationale**: No external dependencies needed. Markdown + YAML frontmatter is native to Obsidian. Simple read-modify-write cycle is sufficient for single-user, single-agent operation.
**Alternatives considered**:
- Obsidian plugin API — requires plugin development, out of scope for Bronze
- Dataview plugin queries — adds plugin dependency, constitution says no custom plugins required

## R3: File Conflict Resolution in Done/

**Decision**: Append ISO timestamp suffix before extension when filename collision occurs (e.g., `TEST_Task_2026-01-29T143022.md`)
**Rationale**: Preserves original filename for readability, timestamp ensures uniqueness, and lexicographic sorting by name groups related files together.
**Alternatives considered**:
- Overwrite existing — data loss risk, violates Company Handbook "never delete without approval"
- Sequential numbering (e.g., `_v2`) — less informative than timestamps, doesn't indicate when processed

## R4: Task File Format

**Decision**: Optional YAML frontmatter with `type`, `priority`, `created` fields. Body contains markdown with action items as `- [ ]` checkboxes.
**Rationale**: Frontmatter is optional to support both structured tasks (from watchers in Modules 2/3) and ad-hoc tasks (manually dropped files). Checkbox format is Obsidian-native.
**Alternatives considered**:
- Mandatory frontmatter — too rigid for manual file drops
- JSON task files — not Obsidian-friendly, breaks markdown rendering

## R5: Obsidian Compatibility

**Decision**: Use only standard Obsidian features (YAML frontmatter, markdown, folder structure). No community plugins required.
**Rationale**: Constitution constraint. Standard Obsidian ensures portability and reduces failure modes.
**Alternatives considered**:
- Templater plugin for auto-updating Dashboard — adds dependency
- Dataview for dynamic queries — adds dependency
