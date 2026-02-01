#!/usr/bin/env python3
"""
Orchestrator - Monitors Needs_Action/ and triggers Claude Code for automatic task processing.
"""
import os
import re
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime

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

# Skill file exclusion pattern
SKILL_PATTERNS = {'SKILLS.md', 'SKILL_FileProcessor.md', 'SKILL_EmailProcessor.md', 'SKILL_LinkedInPoster.md', 'SKILL_ApprovalHandler.md', 'SKILL_PlanGenerator.md'}

# Task type to skill file mapping
SKILL_MAP = {
    'email': 'SKILL_EmailProcessor.md',
    'file_drop': 'SKILL_FileProcessor.md',
    'linkedin_post': 'SKILL_LinkedInPoster.md',
    'email_approval': 'SKILL_ApprovalHandler.md',
    'complex_task': 'SKILL_PlanGenerator.md',
}

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

Working directory context: You are in the silver/ directory. The vault is at AI_Employee_Vault/.
"""


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
            ["claude", "-p", prompt, "--dangerously-skip-permissions"],
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
        logger.error("Claude Code CLI not found. Ensure 'claude' is in PATH.")
        return False, "Claude CLI not found"
    except Exception as e:
        logger.error(f"Error invoking Claude: {e}")
        return False, str(e)


def process_task(file_path):
    """
    Process a single task file: read it, find the skill, invoke Claude.

    Args:
        file_path: Path to the task file

    Returns:
        True if processing succeeded, False otherwise
    """
    logger.info(f"Processing task: {file_path.name}")

    # Read task content
    try:
        task_content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read task file {file_path}: {e}")
        return False

    # Determine task type
    task_type = parse_frontmatter(file_path)
    if not task_type:
        logger.warning(f"No type found in {file_path.name}, using generic processing")
        task_type = 'task'

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

    if success:
        logger.info(f"Successfully processed: {file_path.name}")
        # Safety net: move task to Done/ if Claude didn't already
        if file_path.exists():
            dest = DONE / file_path.name
            try:
                import shutil
                shutil.move(str(file_path), str(dest))
                logger.info(f"Moved {file_path.name} → Done/")
            except Exception as e:
                logger.warning(f"Failed to move {file_path.name} to Done/: {e}")
    else:
        logger.error(f"Failed to process {file_path.name}: {output[:200]}")

    return success


def main():
    """Main orchestrator loop."""
    logger.info("Starting Orchestrator...")
    logger.info(f"Monitoring: {NEEDS_ACTION}")
    logger.info(f"Debounce: {DEBOUNCE_SECONDS}s | Cooldown: {COOLDOWN_SECONDS}s")

    # Ensure directories exist
    DONE.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            actionable = get_actionable_files()

            if actionable:
                logger.info(f"Found {len(actionable)} task(s) to process")
                for task_file in actionable:
                    process_task(task_file)
            else:
                logger.debug("No actionable tasks found")

            time.sleep(COOLDOWN_SECONDS)
    except KeyboardInterrupt:
        logger.info("Shutting down orchestrator...")

    logger.info("Orchestrator stopped.")


if __name__ == "__main__":
    main()
