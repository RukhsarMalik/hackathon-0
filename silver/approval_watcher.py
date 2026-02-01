#!/usr/bin/env python3
"""
Approval Watcher - Monitors Approved/ and Rejected/ folders for processed approval requests.
Creates tasks in Needs_Action/ for approved items, logs rejections.
"""
import os
import re
import shutil
import time
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
APPROVED = VAULT_PATH / "Approved"
REJECTED = VAULT_PATH / "Rejected"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"
AUDIT_LOG = LOGS / "approval_audit.log"
POLL_INTERVAL = 10  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(AUDIT_LOG),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def log_audit(action, filename, to=None, reason=None):
    """
    Append a structured entry to the approval audit log.

    Args:
        action: approved, rejected, sent, send_failed
        filename: Name of the approval file
        to: Recipient email (if applicable)
        reason: Rejection reason (if applicable)
    """
    try:
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] action={action} file={filename}"
        if to:
            entry += f" to={to}"
        if reason:
            entry += f" reason=\"{reason}\""
        entry += "\n"

        with open(AUDIT_LOG, 'a') as f:
            f.write(entry)
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


def extract_frontmatter_field(content, field):
    """Extract a field value from YAML frontmatter."""
    match = re.search(rf'^{field}:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"')
    return None


def process_approved_files():
    """
    Scan Approved/ for .md files.
    For each, create an APPROVED_EMAIL_*.md task in Needs_Action/ for the orchestrator.
    """
    if not APPROVED.exists():
        return

    for f in sorted(APPROVED.glob('*.md')):
        try:
            content = f.read_text(encoding='utf-8')
            to = extract_frontmatter_field(content, 'to') or 'unknown'
            subject = extract_frontmatter_field(content, 'subject') or 'No Subject'

            logger.info(f"Approved email detected: {f.name} → {to}")
            log_audit('approved', f.name, to=to)

            # Create task file in Needs_Action/ for orchestrator
            task_filename = f"APPROVED_EMAIL_{f.stem}.md"
            task_path = NEEDS_ACTION / task_filename

            # Build task content with approval file reference
            task_content = f"""---
type: email_approval
to: {to}
subject: {subject}
approval_file: {f.name}
status: approved
created_date: {datetime.now().isoformat()}
---

## Approved Email — Send via MCP

This email has been approved by a human. Process using SKILL_ApprovalHandler.

**Approval File**: {f.name}
**Recipient**: {to}
**Subject**: {subject}

## Original Content

{content}
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            # Move approved file to Needs_Action/ alongside the task (for MCP to find)
            # Keep it in Approved/ so MCP can validate it
            # (MCP send_email checks Approved/ folder)

        except Exception as e:
            logger.error(f"Error processing approved file {f.name}: {e}")


def process_rejected_files():
    """
    Scan Rejected/ for .md files.
    Log the rejection and move to Done/.
    """
    if not REJECTED.exists():
        return

    for f in sorted(REJECTED.glob('*.md')):
        try:
            content = f.read_text(encoding='utf-8')
            to = extract_frontmatter_field(content, 'to') or 'unknown'
            subject = extract_frontmatter_field(content, 'subject') or 'No Subject'

            logger.info(f"Rejected email: {f.name} → {to}")
            log_audit('rejected', f.name, to=to, reason='Human rejected')

            # Append rejection note to file
            rejection_note = f"\n\n---\n**REJECTED** on {datetime.now().isoformat()} by human review.\n"
            with open(f, 'a') as fh:
                fh.write(rejection_note)

            # Move to Done/
            DONE.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(DONE / f.name))
            logger.info(f"Rejected file moved to Done/: {f.name}")

        except Exception as e:
            logger.error(f"Error processing rejected file {f.name}: {e}")


def main():
    """Main approval watcher loop."""
    logger.info("Starting Approval Watcher...")
    logger.info(f"Monitoring: {APPROVED} and {REJECTED}")
    logger.info(f"Poll interval: {POLL_INTERVAL}s")

    # Ensure directories exist
    APPROVED.mkdir(parents=True, exist_ok=True)
    REJECTED.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            process_approved_files()
            process_rejected_files()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down approval watcher...")

    logger.info("Approval watcher stopped.")


if __name__ == "__main__":
    main()
