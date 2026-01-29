# Quickstart: Gmail Watcher

**Created**: 2026-01-29
**Status**: Draft
**Target Audience**: Developers implementing the Gmail Watcher

## Prerequisites

- Python 3.13+ installed
- Google Cloud account with billing enabled
- Access to Google Cloud Console
- Existing vault structure from Module 1 (AI_Employee_Vault/)
- Completed Module 1 (Foundation Setup) and Module 2 (File System Watcher)

## Setup Steps

### Step 1: Google Cloud Project Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API" and click on it
5. Click "Enable" to enable the API for your project

### Step 2: OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Select "Desktop application" as the application type
4. Download the credentials JSON file
5. Rename the downloaded file to `credentials.json`
6. Place `credentials.json` in your project root directory

### Step 3: Install Dependencies
```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 python-dotenv
```

### Step 4: Configure Environment
1. Copy `.env.example` to `.env`
2. Update the `VAULT_PATH` in `.env` to point to your AI_Employee_Vault directory
3. Ensure `GMAIL_CHECK_INTERVAL=120` (or desired polling interval in seconds)

### Step 5: Run Initial Authentication
1. Run the Gmail watcher script (it will guide you through OAuth flow):
```bash
python gmail_watcher.py
```
2. Follow the browser prompts to authorize the application
3. The script will create `token.json` for future authentication

## Running the Gmail Watcher

### Starting the Service
```bash
python gmail_watcher.py
```

The service will:
- Authenticate with Gmail API
- Load previously processed email IDs
- Begin monitoring for important unread emails
- Log activity to console and `Logs/gmail_errors.log`

### Expected Output
```
2026-01-29 10:30:00 - INFO - Starting Gmail Watcher...
2026-01-29 10:30:05 - INFO - Monitoring Gmail (check every 120 seconds)
2026-01-29 10:30:05 - INFO - Previously processed: 5 emails
```

## Verification

### Test Email Detection
1. Send an email to your monitored Gmail account
2. Mark the email as "Important" in Gmail
3. Wait up to 2 minutes for the polling interval
4. Verify an action file appears in `AI_Employee_Vault/Needs_Action/` with name like `EMAIL_abc123xy.md`

### Check Action File Format
Verify the created action file contains:
- YAML frontmatter with `type: email`, `subject`, `from`, `received`, `priority`, `gmail_id`
- Email content preview in the body
- Suggested action checkboxes

### Verify Duplicate Prevention
1. Send the same email again (or another test email)
2. Confirm no duplicate action file is created for the same message
3. Check `Logs/processed_emails.txt` to see recorded message IDs

## Troubleshooting

### Authentication Issues
- **Problem**: "Invalid Grant" or authentication errors
- **Solution**: Delete `token.json` and rerun the script to reauthenticate

### No Emails Detected
- **Problem**: Watcher runs but no action files created
- **Solution**: Verify the email is marked as "Important" and "Unread" in Gmail

### Rate Limit Errors
- **Problem**: API errors related to rate limits
- **Solution**: The system implements exponential backoff automatically; this is normal during bursts

### File Permission Errors
- **Problem**: Errors writing action files or logs
- **Solution**: Verify the AI_Employee_Vault directory has write permissions

## Stopping the Service

Press `Ctrl+C` to gracefully stop the service:
```
^C2026-01-29 10:45:30 - INFO - Shutting down Gmail watcher...
2026-01-29 10:45:30 - INFO - Watcher stopped.
```

## Integration with AI Employee

Once action files are created in `Needs_Action/`:
1. The AI Employee can process these using the Email Processing Skill
2. Completed emails are moved to `Done/`
3. Dashboard statistics are updated automatically
4. Processed email IDs prevent re-processing

## Next Steps

After successful setup:
1. Customize the email priority detection rules in the agent skill
2. Configure additional email filters if needed
3. Integrate with your existing workflow processes
4. Monitor the logs for any unusual activity