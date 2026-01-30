# Module 3: Gmail Watcher

## Overview
Module 3 implements email monitoring and task creation functionality. It monitors Gmail for important emails and automatically creates action files in the AI Employee vault for processing.

## Prerequisites
- Python 3.13+
- Google Cloud account with Gmail API enabled
- Gmail API OAuth 2.0 credentials (credentials.json)
- Existing vault structure from Module 1 (AI_Employee_Vault/)

## Setup Steps

### 1. Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API" and click on it
5. Click "Enable" to enable the API for your project

### 2. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Select "Desktop application" as the application type
4. Download the credentials JSON file
5. Rename the downloaded file to `credentials.json`
6. Place `credentials.json` in your project root directory

### 3. Install Dependencies
```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 python-dotenv
```

### 4. Configure Environment
1. Copy `.env.example` to `.env`
2. Update the `VAULT_PATH` in `.env` to point to your AI_Employee_Vault directory
3. Ensure `GMAIL_CHECK_INTERVAL=120` (or desired polling interval in seconds)

### 5. Run Initial Authentication
1. Run the Gmail watcher script (it will guide you through OAuth flow):
```bash
python gmail_watcher.py
```
2. Follow the browser prompts to authorize the application
3. The script will create `token.json` for future authentication

## How the Watcher Works
- Polls Gmail every 2 minutes (configurable via GMAIL_CHECK_INTERVAL)
- Queries for "is:unread is:important" emails
- Creates action files in `Needs_Action/` with `EMAIL_*.md` naming convention
- Tracks processed email IDs to prevent duplicates
- Logs all activity to console and `Logs/gmail_errors.log`

## File Structure
```
AI_Employee_Vault/
├── Inbox/                           # File drops (Module 1)
├── Needs_Action/
│   ├── SKILLS.md                    # Basic Task Processor (Module 1)
│   ├── SKILL_FileProcessor.md       # File Drop Processor (Module 2)
│   ├── SKILL_EmailProcessor.md      # Email Processor (Module 3)
│   ├── EMAIL_*.md                   # Auto-generated email actions
│   └── REPLY_*.md                   # Draft replies (if any)
├── Done/                            # Processed items
├── Logs/
│   ├── watcher_errors.log           # File System Watcher logs
│   ├── gmail_errors.log             # Gmail Watcher logs
│   ├── processed_emails.txt         # Duplicate detection
│   └── malformed/
├── Dashboard.md
└── Company_Handbook.md

Project Root/
├── filesystem_watcher.py            # Module 2
├── gmail_watcher.py                 # Module 3
├── credentials.json                 # Gmail OAuth (DO NOT COMMIT)
├── token.json                       # Gmail token (DO NOT COMMIT)
├── .env                             # Config
└── .gitignore                       # Excludes credentials
```

## Testing Guide
1. Start the watcher: `python gmail_watcher.py`
2. Send yourself an email marked as "Important"
3. Wait up to 2 minutes for polling interval
4. Verify an EMAIL_*.md file appears in `AI_Employee_Vault/Needs_Action/`
5. Process the email using the AI Employee with the Email Processing Skill

## Troubleshooting
- **Authentication Issues**: Delete `token.pickle` and rerun the script to reauthenticate
- **No Emails Detected**: Ensure the email is marked as "Important" and "Unread" in Gmail
- **Rate Limit Errors**: The system implements exponential backoff automatically
- **File Permission Errors**: Verify the AI_Employee_Vault directory has write permissions

## Next Steps
- Silver tier features (email sending capability with MCP)
- Additional watcher types (WhatsApp, LinkedIn, etc.)
- Enhanced email processing with AI