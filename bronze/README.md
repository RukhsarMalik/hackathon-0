# AI Employee - Bronze Tier

A personal AI Employee system built with Obsidian, Python watchers, and Claude Code. It monitors your file system and Gmail, creates actionable tasks, and processes them through a structured vault workflow.

## Architecture

```
bronze/
├── AI_Employee_Vault/
│   ├── Inbox/                    # Drop zone for new files (monitored)
│   ├── Needs_Action/             # Pending tasks and action files
│   │   ├── SKILLS.md             # Basic Task Processor skill
│   │   ├── SKILL_FileProcessor.md # File Drop Processor skill
│   │   └── SKILL_EmailProcessor.md # Email Processor skill
│   ├── Done/                     # Completed tasks
│   ├── Logs/
│   │   ├── watcher_errors.log    # File System Watcher logs
│   │   ├── gmail_errors.log      # Gmail Watcher logs
│   │   ├── processed_emails.txt  # Email duplicate detection
│   │   ├── malformed/            # Files that failed parsing
│   │   └── quarantine/           # Oversized files (>10MB)
│   ├── Dashboard.md              # Real-time status dashboard
│   └── Company_Handbook.md       # AI behavior rules
├── filesystem_watcher.py         # File System Watcher (Module 2)
├── gmail_watcher.py              # Gmail Watcher (Module 3)
├── .env.example                  # Environment config template
└── .gitignore
```

## Prerequisites

- Python 3.13+
- Obsidian v1.10.6+
- Google Cloud account with Gmail API enabled (for Module 3)

## Setup

### 1. Install Dependencies

```bash
pip install watchdog python-dotenv google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Update `VAULT_PATH` and other values as needed.

### 3. Open Vault in Obsidian

1. Open Obsidian
2. "Open folder as vault" → select `bronze/AI_Employee_Vault/`
3. All folders and files should appear in the sidebar

## Modules

### Module 1: Foundation Setup

The vault structure with task processing workflow.

**Key files:**

| File | Purpose |
|------|---------|
| Dashboard.md | Real-time status of the AI Employee |
| Company_Handbook.md | Behavior rules (communication, financial, privacy, etc.) |
| SKILLS.md | Agent skill definitions |

**Test it:**

1. Create a task file in `Needs_Action/` with YAML frontmatter (`type: task`, `priority`, `created`)
2. Use Claude Code to process it — update Dashboard, move to `Done/`
3. Verify the file moved and Dashboard updated

### Module 2: File System Watcher

Monitors `Inbox/` for new files and creates action files in `Needs_Action/`.

```bash
cd bronze
python filesystem_watcher.py
```

**How it works:**
- Uses `watchdog` (PollingObserver) to monitor `AI_Employee_Vault/Inbox/`
- Creates `FILE_[name].md` action files in `Needs_Action/` with YAML frontmatter
- Files >10MB are quarantined to `Logs/quarantine/`
- Supports .txt, .md, .pdf, .csv with type-specific processing rules

**Test it:**
```bash
echo "Test content" > AI_Employee_Vault/Inbox/test.txt
```

### Module 3: Gmail Watcher

Monitors Gmail for important unread emails and creates action files.

#### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project → enable Gmail API
3. Go to "APIs & Services" → "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
4. Select "Desktop application", download the JSON file
5. Rename to `credentials.json` and place in the `bronze/` directory

#### Run the Watcher

```bash
cd bronze
python gmail_watcher.py
```

On first run, a browser window opens for OAuth authentication. Select the Gmail account you want to monitor.

**How it works:**
- Polls Gmail every 2 minutes for `is:unread is:important` emails
- Creates `EMAIL_*.md` action files in `Needs_Action/`
- Tracks processed IDs in `processed_emails.txt` to prevent duplicates
- Implements exponential backoff for rate limits

**To switch Gmail accounts:** Delete `token.pickle` and rerun the script.

## Processing Tasks

Use Claude Code to process action files in `Needs_Action/`:

1. Read the action file
2. Apply rules from `Company_Handbook.md`
3. Follow the relevant SKILL file for processing logic
4. Update `Dashboard.md` with activity
5. Move processed file to `Done/`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install` for the missing package |
| Watcher doesn't detect files | Check `VAULT_PATH` in `.env`, ensure directories exist |
| Gmail auth fails | Delete `token.pickle`, rerun script, select correct account |
| No emails detected | Ensure emails are marked "Important" and "Unread" |
| Rate limit errors | Exponential backoff handles this automatically |
| Permission denied | Check folder permissions, stop cloud sync during tests |

## Next Steps

- Silver tier: email sending capability with MCP
- Additional watchers (WhatsApp, LinkedIn, etc.)
- Enhanced email processing with AI
