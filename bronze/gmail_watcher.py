#!/usr/bin/env python3
"""
Gmail Watcher - Monitors Gmail for important emails and creates action files
"""
import time
import logging
import os
from pathlib import Path
from datetime import datetime
import pickle

# Imports for Gmail API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Imports for environment/config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './bronze/AI_Employee_Vault'))
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
LOGS = VAULT_PATH / "Logs"
PROCESSED_FILE = LOGS / "processed_emails.txt"

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "gmail_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_gmail_service():
    """
    Authenticate and return Gmail service.
    """
    creds = None

    # The file token.pickle stores the user's access and refresh tokens.
    if Path('token.pickle').exists():
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None

        if not creds:
            # This will fail until credentials.json is provided by the user
            if not Path('credentials.json').exists():
                logger.error("credentials.json not found. Please follow Gmail API setup instructions.")
                logger.error("Visit https://developers.google.com/gmail/api/quickstart/python")
                logger.error("to set up your credentials.json file.")
                return None

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Error during OAuth flow: {e}")
                return None

        # Save the credentials for the next run
        try:
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return None

    return build('gmail', 'v1', credentials=creds)


def validate_authentication(service):
    """
    Validate that the Gmail service is properly authenticated by making a test API call.
    """
    try:
        # Test API call to get user profile
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"Successfully authenticated as: {profile.get('emailAddress', 'Unknown')}")
        return True
    except Exception as e:
        logger.error(f"Authentication validation failed: {e}")
        return False


def load_processed_ids():
    """
    Load already processed message IDs.
    """
    if not PROCESSED_FILE.exists():
        return set()
    try:
        with open(PROCESSED_FILE, 'r') as f:
            ids = {line.strip() for line in f if line.strip()}
        return ids
    except Exception as e:
        logger.error(f"Error loading processed IDs: {e}")
        return set()


def save_processed_id(msg_id):
    """
    Save processed message ID.
    """
    try:
        with open(PROCESSED_FILE, 'a') as f:
            f.write(f"{msg_id}\n")
    except Exception as e:
        logger.error(f"Error saving processed ID: {e}")


def check_emails(service, processed_ids):
    """
    Check for new important unread emails.
    """
    try:
        # Query for important unread emails using safe API call
        list_response = safe_api_call(
            service.users().messages().list,
            userId='me',
            q='is:unread is:important'
        )

        if list_response is None:
            logger.error("Failed to retrieve emails after retries")
            return

        messages = list_response.get('messages', [])
        new_count = 0

        for msg in messages:
            msg_id = msg['id']

            if msg_id in processed_ids:
                continue

            try:
                # Get full message using safe API call
                message = safe_api_call(
                    service.users().messages().get,
                    userId='me',
                    id=msg_id
                )

                if message is None:
                    logger.error(f"Failed to retrieve message {msg_id} after retries")
                    continue

                # Extract headers
                headers = {}
                if 'payload' in message and 'headers' in message['payload']:
                    for header in message['payload']['headers']:
                        headers[header['name']] = header['value']

                # Get snippet (preview)
                snippet = message.get('snippet', '')

                # Create action file
                action_content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
from_name: {headers.get('From', 'Unknown').split('<')[0].strip() if '<' in str(headers.get('From', '')) else headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
gmail_id: {msg_id}
---

## Email Content

{snippet[:500]}...

## Email Details
- **From**: {headers.get('From', 'Unknown')}
- **Date**: {headers.get('Date', 'Unknown')}
- **Labels**: IMPORTANT, UNREAD

## Suggested Actions
- [ ] Read full email content
- [ ] Determine if reply needed
- [ ] Check Company_Handbook for response rules
- [ ] Draft reply if required (human approval)
- [ ] Mark as read after handling
- [ ] Archive or move to appropriate folder
"""

                # Sanitize filename to handle special characters
                import re
                sanitized_subject = re.sub(r'[^a-zA-Z0-9._-]', '_', headers.get('Subject', 'no-subject')[:30])
                action_file = NEEDS_ACTION / f"EMAIL_{msg_id[:8]}_{sanitized_subject}.md"

                # Ensure the Needs_Action directory exists
                action_file.parent.mkdir(parents=True, exist_ok=True)

                action_file.write_text(action_content)

                save_processed_id(msg_id)
                processed_ids.add(msg_id)
                logger.info(f"Email detected: {headers.get('Subject', 'No Subject')}")
                new_count += 1

            except Exception as msg_error:
                logger.error(f"Error processing message {msg_id}: {msg_error}")
                continue

        if new_count > 0:
            logger.info(f"Created {new_count} new email tasks")

    except Exception as e:
        logger.error(f"Error checking emails: {e}")
        # Handle specific Gmail API errors
        if hasattr(e, 'resp') and e.resp.status == 429:  # Rate limit
            logger.warning("Rate limit exceeded, implementing backoff...")
            time.sleep(60)  # Wait 1 minute before continuing


def exponential_backoff(attempt_number, base_delay=1, max_delay=60):
    """
    Implement exponential backoff with jitter for API errors.

    Args:
        attempt_number: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds to wait before next attempt
    """
    import random

    # Calculate base delay with exponential growth
    delay = min(base_delay * (2 ** attempt_number), max_delay)

    # Add jitter to prevent thundering herd
    jitter = random.uniform(0, delay * 0.1)  # Up to 10% additional random delay
    total_delay = min(delay + jitter, max_delay)

    return total_delay


def safe_api_call(api_func, *args, max_retries=5, **kwargs):
    """
    Safely execute an API call with exponential backoff for rate limits.

    Args:
        api_func: The API function to call
        *args: Arguments to pass to the API function
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments to pass to the API function

    Returns:
        Result of the API call or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            return api_func(*args, **kwargs).execute()
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                logger.error(f"API call failed after {max_retries} attempts: {e}")
                return None

            # Check if it's a rate limit error
            if hasattr(e, 'resp') and e.resp.status == 429:
                delay = exponential_backoff(attempt)
                logger.warning(f"Rate limit hit, waiting {delay:.2f}s before retry {attempt + 1}/{max_retries}")
                time.sleep(delay)
            elif "invalid_grant" in str(e):
                logger.error(f"Invalid grant error (possibly expired token): {e}")
                return None
            else:
                delay = exponential_backoff(attempt)
                logger.warning(f"API error on attempt {attempt + 1}/{max_retries}, waiting {delay:.2f}s: {e}")
                time.sleep(delay)

    return None


def main():
    """
    Main function to run the Gmail watcher.
    """
    logger.info("Starting Gmail Watcher...")

    # Initialize Gmail service
    service = get_gmail_service()
    if not service:
        logger.error("Failed to initialize Gmail service. Exiting.")
        return

    # Validate authentication
    if not validate_authentication(service):
        logger.error("Authentication validation failed. Exiting.")
        return

    # Load processed email IDs
    processed_ids = load_processed_ids()
    logger.info(f"Monitoring Gmail (check every 120 seconds)")
    logger.info(f"Previously processed: {len(processed_ids)} emails")

    try:
        while True:
            check_emails(service, processed_ids)
            time.sleep(120)  # Check every 2 minutes
    except KeyboardInterrupt:
        logger.info("Shutting down Gmail watcher...")

    logger.info("Watcher stopped.")


if __name__ == "__main__":
    main()