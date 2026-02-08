#!/usr/bin/env python3
"""
Orchestrator - Monitors Needs_Action/ and triggers Claude Code for automatic task processing.
"""
import os
import re
import sys
import time
import json
import shutil
import signal
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"
SKILLS_DIR = Path(os.getenv('SKILLS_PATH', str(Path(__file__).parent.parent / 'Skills')))
DEBOUNCE_SECONDS = int(os.getenv('ORCHESTRATOR_DEBOUNCE', '10'))
COOLDOWN_SECONDS = int(os.getenv('ORCHESTRATOR_COOLDOWN', '30'))
MAX_PARALLEL_TASKS = int(os.getenv('MAX_PARALLEL_TASKS', '3'))

# Thread-safe locks for shared resources
_dashboard_lock = threading.Lock()
_audit_lock = threading.Lock()

# Skill file exclusion pattern
SKILL_PATTERNS = {
    'SKILLS.md', 'SKILL_FileProcessor.md', 'SKILL_EmailProcessor.md',
    'SKILL_LinkedInPoster.md', 'SKILL_ApprovalHandler.md', 'SKILL_PlanGenerator.md',
    'SKILL_FacebookPoster.md', 'SKILL_AccountingManager.md', 'SKILL_SocialSummaryGenerator.md',
}

# Task type to skill file mapping
SKILL_MAP = {
    'email': 'SKILL_EmailProcessor.md',
    'file_drop': 'SKILL_FileProcessor.md',
    'linkedin_post': 'SKILL_LinkedInPoster.md',
    'facebook_post': 'SKILL_FacebookPoster.md',
    'email_approval': 'SKILL_ApprovalHandler.md',
    'facebook_approval': 'SKILL_ApprovalHandler.md',
    'linkedin_approval': 'SKILL_ApprovalHandler.md',
    'complex_task': 'SKILL_PlanGenerator.md',
    'accounting': 'SKILL_AccountingManager.md',
    'invoice_request': 'SKILL_AccountingManager.md',
    'social_summary': 'SKILL_SocialSummaryGenerator.md',
    'task_check': 'SKILL_FileProcessor.md',
    'business_goals_test': 'SKILL_FileProcessor.md',
    'error_recovery_test': 'SKILL_FileProcessor.md',
}

# Keywords that indicate an email needs accounting processing
ACCOUNTING_KEYWORDS = [
    'invoice', 'send invoice', 'billing',
    'payment received', 'paid invoice', 'payment confirmation',
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "orchestrator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def parse_frontmatter(file_path):
    """
    Extract YAML frontmatter from a markdown file and return the 'type' field.

    Args:
        file_path: Path to the markdown file

    Returns:
        The value of the 'type' field, or None if not found
    """
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        # Match YAML frontmatter between --- delimiters
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        frontmatter = match.group(1)
        for line in frontmatter.splitlines():
            line = line.strip()
            if line.startswith('type:'):
                return line.split(':', 1)[1].strip()
        return None
    except Exception as e:
        logger.error(f"Error parsing frontmatter from {file_path}: {e}")
        return None


def get_skill_for_type(task_type):
    """
    Map a task type to its corresponding skill file.

    Args:
        task_type: The type field from the task's YAML frontmatter

    Returns:
        Skill filename or None if no mapping exists
    """
    return SKILL_MAP.get(task_type)


def contains_accounting_keywords(content):
    """
    Check if email content contains accounting-related keywords.

    Args:
        content: Full text content of the email/task file

    Returns:
        True if accounting keywords are found, False otherwise
    """
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in ACCOUNTING_KEYWORDS)


def has_existing_accounting_subtask(source_file):
    """
    Check if an accounting subtask already exists for the given source email.

    Args:
        source_file: Path to the original email task file

    Returns:
        True if a subtask already exists, False otherwise
    """
    if not NEEDS_ACTION.exists():
        return False

    for f in NEEDS_ACTION.glob('ACCOUNTING_*'):
        if source_file.stem in f.name:
            return True

    # Also check Done/ folder
    if DONE.exists():
        for f in DONE.glob('ACCOUNTING_*'):
            if source_file.stem in f.name:
                return True

    return False


def create_accounting_task(email_content, source_file):
    """
    Create an accounting subtask from an email that contains accounting keywords.

    Checks for existing subtasks to prevent duplicates.
    Extracts relevant details and creates a new task file with type: accounting
    in Needs_Action/ for the AccountingManager skill to process.

    Args:
        email_content: Full content of the email task file
        source_file: Path to the original email task file
    """
    # Prevent duplicate subtask creation
    if has_existing_accounting_subtask(source_file):
        logger.info(f"Accounting subtask already exists for {source_file.name}, skipping creation")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    task_filename = f"ACCOUNTING_{timestamp}_{source_file.stem}.md"
    task_path = NEEDS_ACTION / task_filename

    task_content = f"""---
type: accounting
source_email: {source_file.name}
created: {datetime.now().isoformat()}
status: pending
---

## Accounting Task (auto-generated from email)

**Source**: {source_file.name}

### Original Email Content

{email_content}

### Instructions

Process this email using SKILL_AccountingManager:
1. Detect if this is an invoice request or payment confirmation
2. Extract customer, service, amount details
3. Call appropriate Odoo MCP tool
4. Draft reply email
5. Update Dashboard with accounting activity
"""

    try:
        task_path.write_text(task_content, encoding='utf-8')
        logger.info(f"Created accounting subtask: {task_filename}")
    except Exception as e:
        logger.error(f"Failed to create accounting subtask: {e}")


def get_actionable_files():
    """
    List .md files in Needs_Action/ that are ready for processing.

    Excludes SKILL_* and SKILLS.md files.
    Only returns files whose mtime is older than DEBOUNCE_SECONDS (debounce).

    Returns:
        List of Path objects for actionable files
    """
    if not NEEDS_ACTION.exists():
        return []

    now = time.time()
    actionable = []

    for f in sorted(NEEDS_ACTION.glob('*.md')):
        if f.name in SKILL_PATTERNS or f.name.startswith('SKILL_') or f.name.startswith('PLAN_'):
            continue

        # Debounce: only process files older than DEBOUNCE_SECONDS
        age = now - f.stat().st_mtime
        if age < DEBOUNCE_SECONDS:
            logger.debug(f"Skipping {f.name} (age: {age:.1f}s < {DEBOUNCE_SECONDS}s debounce)")
            continue

        actionable.append(f)

    return actionable


def build_claude_prompt(task_content, skill_content, task_filename):
    """
    Construct the processing prompt for Claude Code.

    Args:
        task_content: Full content of the task file
        skill_content: Full content of the skill file
        task_filename: Name of the task file being processed

    Returns:
        Formatted prompt string
    """
    return f"""You are processing a task from the AI Employee's Needs_Action folder.

## Skill Instructions

{skill_content}

## Task File: {task_filename}

{task_content}

## Instructions

1. Process this task following the skill instructions above.
2. Update the Dashboard.md in AI_Employee_Vault/ with the processing activity.
3. Move the processed task file from Needs_Action/ to Done/.
4. Log the activity appropriately.

Working directory context: You are in the gold/ directory. The vault is at AI_Employee_Vault/.
"""


def _resolve_claude_path():
    """
    Resolve the full path to the Claude Code CLI binary.
    Uses shutil.which() first, then checks common install locations.

    Returns:
        Full path to claude binary, or 'claude' as fallback
    """
    # Try shutil.which first (respects PATH)
    found = shutil.which("claude")
    if found:
        return found

    # Check common install locations
    common_paths = [
        Path.home() / ".npm-global" / "bin" / "claude",
        Path("/usr/local/bin/claude"),
        Path("/usr/bin/claude"),
    ]

    # Windows/WSL npm global path
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        common_paths.append(Path(appdata) / "npm" / "claude")
        common_paths.append(Path(appdata) / "npm" / "claude.cmd")

    for p in common_paths:
        if p.exists():
            return str(p)

    return "claude"  # fallback, let subprocess try


# Resolve claude path once at startup
CLAUDE_CLI_PATH = _resolve_claude_path()


def invoke_claude(prompt):
    """
    Invoke Claude Code CLI with the given prompt.

    Args:
        prompt: The prompt to send to Claude

    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            [CLAUDE_CLI_PATH, "-p", prompt, "--dangerously-skip-permissions"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(Path(__file__).parent),
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Claude Code timed out after 300 seconds")
        return False, "Timeout"
    except FileNotFoundError:
        logger.error(f"Claude Code CLI not found at '{CLAUDE_CLI_PATH}'. Ensure 'claude' is in PATH.")
        return False, "Claude CLI not found"
    except Exception as e:
        logger.error(f"Error invoking Claude: {e}")
        return False, str(e)


def update_dashboard(task_filename, task_type):
    """
    Programmatically update Dashboard.md with task processing activity.
    This is a safety net in case the Claude CLI invocation doesn't update it.
    Thread-safe via _dashboard_lock.
    """
    dashboard_path = VAULT_PATH / "Dashboard.md"
    if not dashboard_path.exists():
        return

    with _dashboard_lock:
        try:
            content = dashboard_path.read_text(encoding='utf-8')
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            now_iso = datetime.now().isoformat()

            # Add recent activity entry
            activity_line = f"- [{now}] Processed {task_filename} (type: {task_type}) — moved to /Done/"
            content = content.replace(
                "## Recent Activity\n",
                f"## Recent Activity\n{activity_line}\n",
            )

            # Update last_updated
            content = re.sub(
                r'last_updated:.*',
                f'last_updated: {now_iso}',
                content,
            )

            # Update last activity
            content = re.sub(
                r'\*\*Last Activity\*\*:.*',
                f'**Last Activity**: Processed {task_filename}',
                content,
            )

            # Increment email approval stats if applicable
            if task_type == 'email_approval':
                content = re.sub(
                    r'\*\*Emails Sent\*\*: (\d+)',
                    lambda m: f'**Emails Sent**: {int(m.group(1)) + 1}',
                    content,
                )
                content = re.sub(
                    r'\*\*Emails Approved\*\*: (\d+)',
                    lambda m: f'**Emails Approved**: {int(m.group(1)) + 1}',
                    content,
                )

            # Increment total tasks
            content = re.sub(
                r'Total Tasks Processed: (\d+)',
                lambda m: f'Total Tasks Processed: {int(m.group(1)) + 1}',
                content,
            )

            dashboard_path.write_text(content, encoding='utf-8')
            logger.info(f"Dashboard updated for {task_filename}")
        except Exception as e:
            logger.warning(f"Failed to update dashboard: {e}")


def write_audit_log(event_type, service, action, correlation_id, status, duration_ms=None, result_summary="", error_details=None, tags=None, user_context=""):
    """
    Write structured JSON audit log entry.

    Args:
        event_type: Type of event (mcp_call, task_processed, service_monitor, error_event)
        service: Service name (orchestrator, gmail_watcher, etc.)
        action: Specific action taken
        correlation_id: Unique identifier for the task/session
        status: Result status (success, failure, partial_success)
        duration_ms: Duration in milliseconds (optional)
        result_summary: Brief description of the outcome
        error_details: Error information if status is failure (optional)
        tags: Additional tags for categorization (optional)
        user_context: Context of triggering event (optional)
    """
    if tags is None:
        tags = []

    audit_entry = {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "event_type": event_type,
        "service": service,
        "action": action,
        "correlation_id": correlation_id,
        "status": status,
        "duration_ms": duration_ms,
        "input_size_bytes": len(result_summary.encode('utf-8')) if result_summary else 0,
        "result_summary": result_summary,
        "user_context": user_context
    }

    if error_details:
        audit_entry["error_details"] = error_details

    if tags:
        audit_entry["tags"] = tags

    # Write to daily audit log file
    log_date = datetime.now().strftime('%Y-%m-%d')
    audit_log_dir = LOGS / "Audit"
    audit_log_dir.mkdir(exist_ok=True)
    audit_log_file = audit_log_dir / f"{log_date}_audit.json"

    with _audit_lock:
        try:
            # Append the log entry to the file
            with open(audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


# Dictionary to track retry attempts for each task (with lock for thread safety)
TASK_RETRY_COUNTS = {}
_retry_lock = threading.Lock()

def process_task(file_path):
    """
    Process a single task file: read it, find the skill, invoke Claude.

    Args:
        file_path: Path to the task file

    Returns:
        True if processing succeeded, False otherwise
    """
    start_time = time.time()
    correlation_id = f"task_{file_path.stem}_{int(start_time)}"

    # Track retry attempts for this task
    task_key = str(file_path)
    with _retry_lock:
        if task_key not in TASK_RETRY_COUNTS:
            TASK_RETRY_COUNTS[task_key] = 0
        attempt = TASK_RETRY_COUNTS[task_key] + 1

    logger.info(f"Processing task: {file_path.name} (attempt #{attempt})")

    # Log the task start
    write_audit_log(
        event_type="task_processing",
        service="orchestrator",
        action=f"start_process_{file_path.stem}",
        correlation_id=correlation_id,
        status="started",
        result_summary=f"Started processing task {file_path.name} (attempt #{attempt})",
        tags=["orchestrator", "task_processing", "started"]
    )

    # Read task content
    try:
        task_content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read task file {file_path}: {e}")

        # Log the error
        write_audit_log(
            event_type="task_processing",
            service="orchestrator",
            action=f"read_failure_{file_path.stem}",
            correlation_id=correlation_id,
            status="failure",
            result_summary=f"Failed to read task file {file_path.name}",
            error_details={
                "type": "FileReadError",
                "message": str(e),
                "file_path": str(file_path)
            },
            tags=["orchestrator", "task_processing", "error"]
        )
        return False

    # Determine task type
    task_type = parse_frontmatter(file_path)
    if not task_type:
        logger.warning(f"No type found in {file_path.name}, using generic processing")
        task_type = 'task'

    # Flag for cross-domain routing (subtask created after successful processing)
    needs_accounting_subtask = (task_type == 'email' and contains_accounting_keywords(task_content))
    if needs_accounting_subtask:
        logger.info(f"Accounting keywords detected in {file_path.name}, will create subtask after processing")

    # Get skill file
    skill_filename = get_skill_for_type(task_type)
    skill_content = ""
    if skill_filename:
        skill_path = SKILLS_DIR / skill_filename
        if skill_path.exists():
            try:
                skill_content = skill_path.read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Failed to read skill file {skill_filename}: {e}")
        else:
            logger.warning(f"Skill file not found: {skill_filename}")
    else:
        logger.info(f"No skill mapping for type '{task_type}', using basic processing")
        # Use SKILLS.md as fallback
        skills_path = SKILLS_DIR / "SKILLS.md"
        if skills_path.exists():
            try:
                skill_content = skills_path.read_text(encoding='utf-8')
            except Exception:
                pass

    # Build prompt and invoke Claude
    prompt = build_claude_prompt(task_content, skill_content, file_path.name)
    success, output = invoke_claude(prompt)

    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)

    if success:
        logger.info(f"Successfully processed: {file_path.name}")

        # Cross-domain: create accounting subtask only after successful processing
        if needs_accounting_subtask:
            create_accounting_task(task_content, file_path)

        # Reset retry counter on success
        with _retry_lock:
            if task_key in TASK_RETRY_COUNTS:
                del TASK_RETRY_COUNTS[task_key]

        # Log the successful processing
        write_audit_log(
            event_type="task_processed",
            service="orchestrator",
            action=f"process_success_{file_path.stem}",
            correlation_id=correlation_id,
            status="success",
            duration_ms=duration_ms,
            result_summary=f"Successfully processed task {file_path.name} (type: {task_type})",
            tags=["orchestrator", "task_processing", "success", task_type]
        )

        # Update dashboard with processing activity
        update_dashboard(file_path.name, task_type)
        # Safety net: move task to Done/ if Claude didn't already
        if file_path.exists():
            dest = DONE / file_path.name
            try:
                shutil.move(str(file_path), str(dest))
                logger.info(f"Moved {file_path.name} → Done/")

                # Log the move action
                write_audit_log(
                    event_type="file_operation",
                    service="orchestrator",
                    action="move_to_done",
                    correlation_id=correlation_id,
                    status="success",
                    duration_ms=10,  # approximate
                    result_summary=f"Moved {file_path.name} to Done/",
                    tags=["orchestrator", "file_operation", "success"]
                )
            except Exception as e:
                logger.warning(f"Failed to move {file_path.name} to Done/: {e}")

                # Log the move failure
                write_audit_log(
                    event_type="file_operation",
                    service="orchestrator",
                    action="move_failure",
                    correlation_id=correlation_id,
                    status="failure",
                    result_summary=f"Failed to move {file_path.name} to Done/",
                    error_details={
                        "type": "FileMoveError",
                        "message": str(e),
                        "source": str(file_path),
                        "destination": str(dest)
                    },
                    tags=["orchestrator", "file_operation", "error"]
                )
    else:
        # Increment retry counter
        with _retry_lock:
            TASK_RETRY_COUNTS[task_key] += 1
            current_retries = TASK_RETRY_COUNTS[task_key]

        # Check if we've exceeded max retries
        max_retries = 3
        if current_retries >= max_retries:
            logger.error(f"Task {file_path.name} failed after {max_retries} attempts, moving to review queue")

            # Move to review queue instead of keeping in Needs_Action
            stuck_tasks_dir = NEEDS_ACTION.parent / "Needs_Action_Review"
            stuck_tasks_dir.mkdir(exist_ok=True)

            stuck_dest = stuck_tasks_dir / f"STUCK_{file_path.name}"
            shutil.move(str(file_path), str(stuck_dest))

            logger.info(f"Moved stuck task to review: {stuck_dest}")

            # Log the failure and escalation
            write_audit_log(
                event_type="task_processed",
                service="orchestrator",
                action=f"process_failure_max_retries_{file_path.stem}",
                correlation_id=correlation_id,
                status="failure",
                duration_ms=duration_ms,
                result_summary=f"Task {file_path.name} failed after {max_retries} retries, escalated to review queue",
                error_details={
                    "type": "MaxRetriesExceeded",
                    "message": f"Task failed {max_retries} times, moved to review queue",
                    "file_path": str(file_path),
                    "retry_count": max_retries
                },
                tags=["orchestrator", "task_processing", "error", "escalation", task_type]
            )

            # Remove from retry tracking since it's escalated
            with _retry_lock:
                if task_key in TASK_RETRY_COUNTS:
                    del TASK_RETRY_COUNTS[task_key]
        else:
            logger.warning(f"Task {file_path.name} failed (attempt {current_retries}/{max_retries}), will retry")

            # Log the retry attempt
            write_audit_log(
                event_type="task_processed",
                service="orchestrator",
                action=f"process_retry_{file_path.stem}",
                correlation_id=correlation_id,
                status="retry_scheduled",
                duration_ms=duration_ms,
                result_summary=f"Task {file_path.name} failed, retry scheduled (attempt {current_retries}/{max_retries})",
                error_details={
                    "type": "RetryScheduled",
                    "message": f"Retrying task (attempt {current_retries}/{max_retries})",
                    "file_path": str(file_path),
                    "retry_count": current_retries
                },
                tags=["orchestrator", "task_processing", "retry", task_type]
            )

    return success


PID_FILE = Path(__file__).parent / ".pids" / "orchestrator.pid"


def acquire_pid_lock():
    """
    Acquire a PID file lock to prevent duplicate orchestrator instances.

    Returns:
        True if lock acquired, False if another instance is running
    """
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)

    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            # Check if the old process is still running
            os.kill(old_pid, 0)
            # Process is still alive
            logger.error(f"Another orchestrator instance is running (PID {old_pid}). Exiting.")
            return False
        except (ProcessLookupError, ValueError):
            # Process is dead or PID file is corrupt, safe to take over
            logger.info(f"Stale PID file found, taking over.")
        except PermissionError:
            # Process exists but we can't signal it (still alive)
            logger.error(f"Another orchestrator instance is running (PID file exists). Exiting.")
            return False

    PID_FILE.write_text(str(os.getpid()))
    return True


def release_pid_lock():
    """Remove the PID file on shutdown."""
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception as e:
        logger.warning(f"Failed to remove PID file: {e}")


def main():
    """Main orchestrator loop - Implements the Ralph Wiggum Loop for continuous task processing."""

    # Acquire PID lock to prevent duplicate instances
    if not acquire_pid_lock():
        sys.exit(1)

    # Initialize statistics tracking
    total_processed = 0
    total_successful = 0
    total_failed = 0

    logger.info("Starting Orchestrator...")
    logger.info(f"Claude CLI path: {CLAUDE_CLI_PATH}")
    logger.info(f"Monitoring: {NEEDS_ACTION}")
    logger.info(f"Debounce: {DEBOUNCE_SECONDS}s | Cooldown: {COOLDOWN_SECONDS}s | Parallel: {MAX_PARALLEL_TASKS}")

    # Ensure directories exist
    DONE.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    iteration_count = 0
    max_iterations = 10  # Prevent infinite loops

    try:
        while True:
            iteration_count += 1
            iteration_start_time = time.time()

            logger.info(f"Ralph Wiggum Loop iteration #{iteration_count}")

            # Process all actionable files in this iteration
            actionable = get_actionable_files()

            if actionable:
                logger.info(f"Found {len(actionable)} task(s) to process in iteration #{iteration_count} (parallel={MAX_PARALLEL_TASKS})")

                # Track results for this iteration
                successful_tasks = 0
                failed_tasks = 0

                # Process tasks in parallel using ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=MAX_PARALLEL_TASKS) as executor:
                    future_to_file = {executor.submit(process_task, task_file): task_file for task_file in actionable}

                    for future in as_completed(future_to_file):
                        task_file = future_to_file[future]
                        try:
                            success = future.result()
                            if success:
                                successful_tasks += 1
                                total_successful += 1
                            else:
                                failed_tasks += 1
                                total_failed += 1
                        except Exception as e:
                            logger.error(f"Task {task_file.name} raised exception: {e}")
                            failed_tasks += 1
                            total_failed += 1

                        total_processed += 1

                iteration_duration = int((time.time() - iteration_start_time) * 1000)

                logger.info(f"Iteration #{iteration_count} completed: {successful_tasks} succeeded, {failed_tasks} failed, duration: {iteration_duration}ms")

                # Log iteration metrics
                write_audit_log(
                    event_type="performance_metrics",
                    service="orchestrator",
                    action="iteration_complete",
                    correlation_id=f"iter_{iteration_count}_{int(time.time())}",
                    status="completed",
                    duration_ms=iteration_duration,
                    result_summary=f"Iteration #{iteration_count} processed {len(actionable)} tasks",
                    tags=["orchestrator", "performance", "metrics"]
                )

                # Check if new tasks appeared during processing of this batch
                additional_tasks = get_actionable_files()
                if additional_tasks:
                    logger.info(f"New tasks appeared during processing: {len(additional_tasks)} additional tasks found")
                    # Continue to next iteration without sleeping to process new tasks quickly
                    continue
            else:
                logger.debug(f"No actionable tasks found in iteration #{iteration_count}")

            # Periodically log overall statistics
            if iteration_count % 5 == 0:  # Every 5 iterations
                success_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0
                logger.info(f"Performance Stats: Total={total_processed}, Success={total_successful}, "
                           f"Failed={total_failed}, Success Rate={success_rate:.2f}%")

                # Log aggregate metrics
                write_audit_log(
                    event_type="aggregate_metrics",
                    service="orchestrator",
                    action="aggregate_stats",
                    correlation_id=f"agg_stats_{int(time.time())}",
                    status="reported",
                    result_summary=f"Overall stats: {total_processed} processed, {total_successful} successful, "
                                 f"{total_failed} failed, {success_rate:.2f}% success rate",
                    tags=["orchestrator", "aggregate", "performance", "stats"]
                )

            # Check if we've reached the max iterations
            if iteration_count >= max_iterations:
                logger.warning(f"Max iterations ({max_iterations}) reached. Pausing to prevent infinite loop.")

                # Log the max iterations warning
                write_audit_log(
                    event_type="service_monitor",
                    service="orchestrator",
                    action="max_iterations_reached",
                    correlation_id=f"max_iter_{int(time.time())}",
                    status="warning",
                    result_summary=f"Max iterations ({max_iterations}) reached, resetting counter",
                    tags=["orchestrator", "lifecycle", "warning"]
                )

                logger.info("Orchestrator will reset and continue normal operation.")
                iteration_count = 0  # Reset counter to continue operation

            # Sleep between iterations
            time.sleep(COOLDOWN_SECONDS)
    except KeyboardInterrupt:
        logger.info("Shutting down orchestrator...")

        # Final statistics report
        success_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0
        logger.info(f"Final Stats: Total={total_processed}, Success={total_successful}, "
                   f"Failed={total_failed}, Success Rate={success_rate:.2f}%")

        write_audit_log(
            event_type="service_monitor",
            service="orchestrator",
            action="shutdown",
            correlation_id=f"shutdown_{int(time.time())}",
            status="graceful",
            result_summary=f"Orchestrator shutdown by user interrupt. Final stats: "
                         f"{total_processed} processed, {total_successful} successful, {success_rate:.2f}% success rate",
            tags=["orchestrator", "lifecycle", "shutdown", "final_stats"]
        )
    finally:
        release_pid_lock()

    logger.info("Orchestrator stopped.")


if __name__ == "__main__":
    main()
