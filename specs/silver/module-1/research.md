# Research: Silver Module 1 — Orchestrator + LinkedIn Automation

## R1: Orchestrator — Invoking Claude Code via subprocess

**Decision**: Use `subprocess.run()` to call `claude` CLI with `--print` and `-p` flags.

**Rationale**: Claude Code CLI supports non-interactive mode via `--print -p "prompt"`. This is the simplest integration — no SDK, no API keys, just the CLI already installed on the system. The orchestrator stays a thin dispatcher.

**Alternatives considered**:
- Claude API directly (requires API key management, SDK dependency, more complex)
- MCP integration (overkill for task dispatch, planned for future modules)

**Key finding**: `claude --print -p "prompt"` runs non-interactively and returns output to stdout. Use `--dangerously-skip-permissions` only if needed for file operations, otherwise rely on allowed tools config.

## R2: File-based scheduling vs cron

**Decision**: Python-based scheduling loop inside `linkedin_watcher.py` rather than system cron.

**Rationale**: Keeps the system self-contained. Cron requires system-level configuration that varies across OS. A Python loop with day/time checks is portable and consistent with the existing watcher pattern (gmail_watcher, filesystem_watcher).

**Alternatives considered**:
- System cron/Task Scheduler (OS-dependent, harder to manage as a unit)
- APScheduler library (extra dependency for simple day-of-week check)
- schedule library (lightweight but unnecessary — stdlib datetime suffices)

## R3: Post duplicate prevention

**Decision**: JSON file (`linkedin_posts.json`) tracking date + post type.

**Rationale**: Simple, human-readable, consistent with file-based architecture. Each entry records `{"date": "2026-01-30", "type": "weekly_update", "file": "LINKEDIN_POST_xxx.md"}`. Check before creating.

**Alternatives considered**:
- SQLite (overkill for <1000 records)
- Text file with dates (less structured)

## R4: Process management in startup script

**Decision**: Bash script with PID files and trap-based cleanup.

**Rationale**: Standard Unix pattern. Each background process writes its PID to `.pids/`. The startup script traps SIGINT/SIGTERM and kills all PIDs. Simple, no dependencies.

**Alternatives considered**:
- supervisord (heavy dependency for 4 processes)
- systemd services (not portable, requires root)
- Python multiprocessing (mixes concerns — startup should be thin)

## R5: Health check approach

**Decision**: Python script that checks PID liveness + Dashboard freshness + stuck tasks.

**Rationale**: Can be run manually or via cron. Returns exit code 0/1 for scripting. Reads existing artifacts (PID files, Dashboard.md, Needs_Action/ directory) — no new infrastructure needed.
