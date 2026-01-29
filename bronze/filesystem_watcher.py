#!/usr/bin/env python3
"""File System Watcher - Monitors Inbox/ for new files and creates action files in Needs_Action/."""

import os
import re
import sys
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv("VAULT_PATH", "./AI_Employee_Vault"))
INBOX = VAULT_PATH / "Inbox"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
LOGS = VAULT_PATH / "Logs"
QUARANTINE = LOGS / "quarantine"

# Max file size: 10MB
MAX_FILE_SIZE = 10_485_760

# Setup dual logging: console + file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS / "watcher_errors.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Replace special characters with underscores for safe filesystem naming."""
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name)


class InboxHandler(FileSystemEventHandler):
    """Handles file creation events in the Inbox directory."""

    def on_created(self, event):
        if event.is_directory:
            return

        try:
            source = Path(event.src_path)

            # Brief delay to allow file write to complete
            time.sleep(0.5)

            logger.info(f"File detected: {source.name}")

            # Check file size
            size = source.stat().st_size
            if size > MAX_FILE_SIZE:
                logger.error(
                    f"File too large: {source.name} ({size} bytes) — quarantined"
                )
                QUARANTINE.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(QUARANTINE / source.name))
                return

            # Create action file
            sanitized_stem = sanitize_filename(source.stem)
            detected_time = datetime.now().isoformat()

            action_content = f"""---
type: file_drop
original_name: {source.name}
size: {size}
detected: {detected_time}
status: pending
---

## New File Dropped

A new file has been detected in Inbox folder.

**File Details:**
- Name: {source.name}
- Size: {size} bytes
- Type: {source.suffix}

## Suggested Actions
- [ ] Review file content
- [ ] Determine appropriate handling
- [ ] Process according to file type
- [ ] Move to Done when complete
"""

            action_file = NEEDS_ACTION / f"FILE_{sanitized_stem}.md"
            action_file.write_text(action_content)
            logger.info(f"Action file created: FILE_{sanitized_stem}.md")

        except FileNotFoundError:
            logger.warning(f"File vanished before processing: {event.src_path}")
        except PermissionError:
            logger.error(f"Permission denied: {event.src_path}")
        except OSError as e:
            logger.error(f"OS error processing {event.src_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {event.src_path}: {e}")


def main():
    """Start the file system watcher."""
    # Validate inbox directory exists
    if not INBOX.exists():
        logger.error(f"Inbox directory not found: {INBOX}")
        sys.exit(1)

    logger.info("Starting File System Watcher...")
    logger.info(f"Monitoring: {INBOX}")

    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down watcher...")
        observer.stop()

    observer.join()
    logger.info("Watcher stopped.")


if __name__ == "__main__":
    main()
