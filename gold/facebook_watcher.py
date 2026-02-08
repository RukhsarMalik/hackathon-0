#!/usr/bin/env python3
"""
Facebook Watcher - Creates scheduled Facebook post requests on a daily schedule.
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
POST_HISTORY_FILE = LOGS / "facebook_posts.json"
POST_TIME = os.getenv('FACEBOOK_POST_TIME', '07:20')

# Schedule: day of week (0=Monday) → post type
SCHEDULE = {
    0: 'monday_motivation',     # Monday
    1: 'tech_tip',              # Tuesday
    2: 'midweek_insight',       # Wednesday
    3: 'throwback_thursday',    # Thursday
    4: 'friday_wins',           # Friday
    5: 'weekend_thought',       # Saturday
    6: 'sunday_reflection',     # Sunday
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "facebook_watcher.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def load_post_history():
    """
    Load post history from facebook_posts.json.

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
        post_type: Type of post
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
    Create a Facebook post request file in Needs_Action/.

    Args:
        post_type: Type of post (monday_motivation, tech_tip, etc.)

    Returns:
        Filename of the created file, or None on failure
    """
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"FACEBOOK_POST_{today.replace('-', '')}_{post_type}.md"
    file_path = NEEDS_ACTION / filename

    content = f"""---
type: facebook_post
topic: {post_type}
scheduled_date: {today}
status: pending
---

## Facebook Post Request

Generate a **{post_type.replace('_', ' ')}** post for our Facebook Page.

**Post Type**: {post_type}
**Scheduled Date**: {today}

### Instructions
- Follow the SKILL_FacebookPoster.md guidelines
- Keep content engaging and readable
- Use line breaks for readability
- Generate engaging content with relevant hashtags (1-3)
- End with a question or call-to-action
- Place the generated post in Pending_Approval/ folder
- Move this file to Done/ after processing
"""

    try:
        NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        logger.info(f"Created Facebook post request: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error creating post request: {e}")
        return None


def check_schedule():
    """
    Check if it's time to create a Facebook post based on the schedule.
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
        post_hour, post_minute = 10, 0

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
        logger.info(f"Scheduled {post_type} Facebook post created successfully")


def main():
    """Main Facebook watcher loop."""
    logger.info("Starting Facebook Watcher...")
    logger.info(f"Schedule: Mon=monday_motivation, Tue=tech_tip, Wed=midweek_insight, Thu=throwback_thursday, Fri=friday_wins, Sat=weekend_thought, Sun=sunday_reflection")
    logger.info(f"Post time: {POST_TIME}")

    LOGS.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            check_schedule()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down Facebook watcher...")

    logger.info("Facebook watcher stopped.")


if __name__ == "__main__":
    main()
