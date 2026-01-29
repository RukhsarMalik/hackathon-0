# Quickstart: File System Watcher

## Prerequisites

- Module 1 complete (vault structure exists at `bronze/AI_Employee_Vault/`)
- Python 3.13+
- pip

## Setup

### 1. Install Dependencies

```bash
pip install watchdog python-dotenv
```

### 2. Configure Vault Path

Create or update `.env` at the project root:

```
VAULT_PATH=./bronze/AI_Employee_Vault
```

### 3. Ensure Quarantine Directory Exists

```bash
mkdir -p bronze/AI_Employee_Vault/Logs/quarantine
```

### 4. Start the Watcher

```bash
cd bronze
python filesystem_watcher.py
```

Expected output:
```
YYYY-MM-DD HH:MM:SS - INFO - Starting File System Watcher...
YYYY-MM-DD HH:MM:SS - INFO - Monitoring: /path/to/bronze/AI_Employee_Vault/Inbox
```

### 5. Test: Drop a File

In a separate terminal:

```bash
echo "Test content for watcher" > bronze/AI_Employee_Vault/Inbox/test.txt
```

Expected watcher output:
```
YYYY-MM-DD HH:MM:SS - INFO - File detected: test.txt
YYYY-MM-DD HH:MM:SS - INFO - Action file created: FILE_test.md
```

Verify action file exists: `bronze/AI_Employee_Vault/Needs_Action/FILE_test.md`

### 6. Stop the Watcher

Press `Ctrl+C` in the watcher terminal.

Expected output:
```
YYYY-MM-DD HH:MM:SS - INFO - Shutting down watcher...
YYYY-MM-DD HH:MM:SS - INFO - Watcher stopped.
```

## Full Test Suite

Drop these 4 files and verify action files are created:

| Test File | Content | Expected Action File |
|-----------|---------|---------------------|
| test.txt | "Test content" | FILE_test.md |
| urgent_note.md | "URGENT: Review immediately" | FILE_urgent_note.md |
| sample.pdf | Any PDF file | FILE_sample.md |
| data.csv | "name,amount\nJohn,150" | FILE_data.md |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: watchdog" | Run `pip install watchdog` |
| Watcher doesn't detect files | Check VAULT_PATH in .env matches actual vault location |
| Permission denied on action file | Check Needs_Action/ folder permissions |
| No log file created | Ensure Logs/ directory exists |
