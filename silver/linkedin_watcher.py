#!/usr/bin/env python3
"""
LinkedIn Watcher - Creates scheduled LinkedIn post requests on Mon/Wed/Fri.
"""
import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
LOGS = VAULT_PATH / "Logs"
POST_HISTORY_FILE = LOGS / "linkedin_posts.json"
POST_TIME = os.getenv('LINKEDIN_POST_TIME', '18:50')

# Schedule: day of week (0=Monday) → post type
SCHEDULE = {
    0: 'weekly_update',       # Monday
    1: 'industry_insight',    # Tuesday
    2: 'tip_of_day',          # Wednesday
    3: 'thought_leadership',  # Thursday
    4: 'success_story',       # Friday
    5: 'weekend_reflection',  # Saturday
    6: 'weekly_preview',      # Sunday
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "linkedin_watcher.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def load_post_history():
    """
    Load post history from linkedin_posts.json.

    Returns:
        List of post history entries
    """
    if not POST_HISTORY_FILE.exists():
        return []
    try:
        with open(POST_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error loading post history: {e}")
        return []


def save_post_entry(date_str, post_type, filename):
    """
    Append a new entry to the post history file.

    Args:
        date_str: Date string (YYYY-MM-DD)
        post_type: Type of post (weekly_update, tip_of_day, success_story)
        filename: Name of the created action file
    """
    history = load_post_history()
    history.append({
        'date': date_str,
        'type': post_type,
        'file': filename,
        'created_at': datetime.now().isoformat(),
    })
    try:
        with open(POST_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving post history: {e}")


def has_posted_today(post_type):
    """
    Check if a post of the given type has already been created today.

    Args:
        post_type: Type of post to check

    Returns:
        True if already posted today, False otherwise
    """
    today = datetime.now().strftime('%Y-%m-%d')
    history = load_post_history()
    return any(
        entry.get('date') == today and entry.get('type') == post_type
        for entry in history
    )


def create_post_request(post_type):
    """
    Create a LinkedIn post request file in Needs_Action/.

    Args:
        post_type: Type of post (weekly_update, tip_of_day, success_story)

    Returns:
        Filename of the created file, or None on failure
    """
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"LINKEDIN_POST_{today.replace('-', '')}_{post_type}.md"
    file_path = NEEDS_ACTION / filename

    content = f"""---
type: linkedin_post
topic: {post_type}
scheduled_date: {today}
status: pending
---

## LinkedIn Post Request

Generate a **{post_type.replace('_', ' ')}** post for LinkedIn.

**Post Type**: {post_type}
**Scheduled Date**: {today}

### Instructions
- Follow the SKILL_LinkedInPoster.md guidelines
- Generate engaging, value-driven content
- Place the generated post in Pending_Approval/ folder
- Move this file to Done/ after processing
"""

    try:
        NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        logger.info(f"Created LinkedIn post request: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error creating post request: {e}")
        return None


def check_schedule():
    """
    Check if it's time to create a LinkedIn post based on the schedule.
    Creates a post request if the current day/time matches and no post exists for today.
    """
    now = datetime.now()
    weekday = now.weekday()  # 0=Monday, 6=Sunday

    if weekday not in SCHEDULE:
        return

    post_type = SCHEDULE[weekday]

    # Check if we're within the posting time window (within 1 hour of POST_TIME)
    try:
        post_hour, post_minute = map(int, POST_TIME.split(':'))
    except ValueError:
        post_hour, post_minute = 9, 0

    current_minutes = now.hour * 60 + now.minute
    target_minutes = post_hour * 60 + post_minute

    # Only create post within a 60-minute window after the scheduled time
    if current_minutes < target_minutes or current_minutes > target_minutes + 60:
        return

    # Check if already posted today
    if has_posted_today(post_type):
        logger.debug(f"Already posted {post_type} today, skipping")
        return

    # Create the post request
    filename = create_post_request(post_type)
    if filename:
        save_post_entry(now.strftime('%Y-%m-%d'), post_type, filename)
        logger.info(f"Scheduled {post_type} post created successfully")


def main():
    """Main LinkedIn watcher loop."""
    logger.info("Starting LinkedIn Watcher...")
    logger.info(f"Schedule: Mon=weekly_update, Tue=industry_insight, Wed=tip_of_day, Thu=thought_leadership, Fri=success_story, Sat=weekend_reflection, Sun=weekly_preview")
    logger.info(f"Post time: {POST_TIME}")

    LOGS.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            check_schedule()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down LinkedIn watcher...")

    logger.info("LinkedIn watcher stopped.")


if __name__ == "__main__":
    main()
