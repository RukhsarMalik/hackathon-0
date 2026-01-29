# Research: File System Watcher

**Feature**: 002-filesystem-watcher
**Date**: 2026-01-29

## R1: Filesystem Event Library

**Decision**: Use `watchdog` library for filesystem monitoring
**Rationale**: Mature, cross-platform (Linux inotify, macOS FSEvents, Windows ReadDirectoryChanges), well-documented, pip-installable. Used by tools like Django's auto-reloader.
**Alternatives considered**:
- `inotify` (Linux-only — not cross-platform)
- Polling with `os.listdir` (high CPU, slow detection, no event-driven architecture)
- `asyncio` + `aiofiles` (unnecessary complexity for single-directory monitoring)

## R2: Configuration Management

**Decision**: Use `python-dotenv` with `.env` file for vault path configuration
**Rationale**: Standard pattern for Python apps. Separates config from code. Fallback to sensible default (`./AI_Employee_Vault`) when .env is absent.
**Alternatives considered**:
- Hardcoded paths (not portable)
- Command-line arguments (less convenient for repeated runs)
- YAML config file (overkill for 1-2 settings)

## R3: Logging Strategy

**Decision**: Dual-output logging — console (StreamHandler) + file (FileHandler at `Logs/watcher_errors.log`)
**Rationale**: Console output provides real-time feedback during development. File logging creates audit trail per constitution requirement. Both use same format for consistency.
**Alternatives considered**:
- File-only logging (no real-time visibility)
- Console-only logging (no persistence, violates audit requirements)
- Structured JSON logging (overkill for Bronze tier)

## R4: Filename Sanitization

**Decision**: Replace non-alphanumeric characters (except hyphens, underscores, dots) with underscores in action file names. Preserve original filename in frontmatter.
**Rationale**: Prevents filesystem errors from special characters while maintaining traceability through frontmatter `original_name` field.
**Alternatives considered**:
- URL encoding (produces unreadable filenames like `FILE_%20test.md`)
- Rejecting files with special characters (too restrictive)

## R5: Large File Handling

**Decision**: Files >10MB are moved to `Logs/quarantine/` with error log entry. No action file created.
**Rationale**: Obsidian and Claude Code work best with text-based files. Very large files likely aren't task-relevant markdown. Quarantine preserves the file for manual review.
**Alternatives considered**:
- Creating action file anyway (could overwhelm processing)
- Deleting large files (data loss, violates handbook "never delete without approval")
- Configurable size limit (premature; 10MB is reasonable default)
