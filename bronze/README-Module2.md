# Module 2: File System Watcher

## Prerequisites
- Module 1 complete (vault structure exists)
- Python 3.13+
- pip

## Setup

### 1. Install Dependencies

```bash
pip install watchdog python-dotenv
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update if needed:

```
VAULT_PATH=./AI_Employee_Vault
```

### 3. Start the Watcher

```bash
cd bronze
python filesystem_watcher.py
```

Expected output:
```
YYYY-MM-DD HH:MM:SS - INFO - Starting File System Watcher...
YYYY-MM-DD HH:MM:SS - INFO - Monitoring: AI_Employee_Vault/Inbox
```

### 4. Drop Files

In a separate terminal, copy or create files in `bronze/AI_Employee_Vault/Inbox/`:

```bash
echo "Test content" > bronze/AI_Employee_Vault/Inbox/test.txt
```

The watcher will log detection and create an action file in `Needs_Action/`.

### 5. Stop the Watcher

Press `Ctrl+C`. The watcher shuts down cleanly.

## How It Works

1. **Monitoring**: Uses `watchdog` (PollingObserver) to watch `AI_Employee_Vault/Inbox/`
2. **Detection**: When a new file appears, creates a structured action file `FILE_[name].md` in `Needs_Action/`
3. **Action Files**: Contain YAML frontmatter (type, original_name, size, detected, status) and suggested actions
4. **Error Handling**: Files >10MB are quarantined to `Logs/quarantine/`. All errors logged, watcher continues.
5. **Processing**: Use `SKILL_FileProcessor.md` to process action files with Claude Code

## File Structure

```
bronze/
├── filesystem_watcher.py              # Watcher script
├── AI_Employee_Vault/
│   ├── Inbox/                         # Drop files here (monitored)
│   ├── Needs_Action/
│   │   ├── SKILL_FileProcessor.md     # Processing instructions
│   │   └── FILE_*.md                  # Auto-generated action files
│   ├── Done/
│   └── Logs/
│       ├── watcher_errors.log         # Watcher log
│       └── quarantine/                # Oversized files
├── .env.example
└── .gitignore
```

## Supported File Types

| Type | Processing |
|------|-----------|
| .txt, .md | Read preview, keyword scan (urgent, invoice, payment, todo) |
| .pdf | Flag for manual review |
| .csv | Row/column count, financial keyword check |
| Other | Flag for manual review |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: watchdog" | Run `pip install watchdog` |
| Watcher doesn't detect files | Check VAULT_PATH in .env, ensure Inbox/ exists |
| Permission denied | Check folder permissions |
| No log file | Ensure Logs/ directory exists |

## Next Steps
- **Module 3**: Gmail Watcher (Gmail API integration)
