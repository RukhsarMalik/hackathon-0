# Contract: Vault File Operations

**Feature**: 001-foundation-setup
**Date**: 2026-01-29

## Operations

This module uses filesystem operations only. No REST APIs or programmatic interfaces. The "contract" defines the expected file operation behaviors Claude Code must support.

### OP-001: Read File

**Input**: Absolute path to a markdown file in any vault subdirectory
**Output**: File contents as string (including YAML frontmatter)
**Errors**: File not found, permission denied

### OP-002: Write File

**Input**: Absolute path + content string
**Output**: File written/overwritten at path
**Errors**: Permission denied, directory does not exist
**Constraint**: Must preserve YAML frontmatter structure

### OP-003: Move File

**Input**: Source path, destination directory
**Output**: File moved to destination
**Errors**: Source not found, destination not found, name collision
**Collision handling**: If destination file exists, append `_YYYY-MM-DDTHHMMSS` before extension

### OP-004: Update Dashboard

**Input**: Dashboard.md path, event data (task name, timestamp, status)
**Output**: Updated Dashboard.md with:
- `last_updated` frontmatter set to current ISO datetime
- `Active Tasks` / `Completed Today` counters incremented
- New entry in Recent Activity section
- `Last Activity` field updated

### OP-005: List Directory

**Input**: Absolute path to vault subdirectory
**Output**: List of filenames in directory
**Errors**: Directory not found, permission denied
**Filter**: Only `.md` files for task processing
