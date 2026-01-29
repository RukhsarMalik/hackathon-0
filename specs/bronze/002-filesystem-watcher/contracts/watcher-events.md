# Contract: Watcher Events

**Feature**: 002-filesystem-watcher
**Date**: 2026-01-29

## Event: File Created in Inbox

**Trigger**: New file appears in `AI_Employee_Vault/Inbox/`
**Handler**: `InboxHandler.on_created(event)`

### Input
- `event.src_path`: Absolute path to the new file
- `event.is_directory`: Boolean (must be False to process)

### Processing Rules

1. **Ignore directories**: If `event.is_directory` is True, return immediately
2. **Size check**: If file size > 10,485,760 bytes (10MB):
   - Move file to `Logs/quarantine/`
   - Log error: "File too large: [name] ([size] bytes) — quarantined"
   - Return (no action file)
3. **Sanitize filename**: Replace `[^a-zA-Z0-9._-]` with `_`
4. **Create action file**: Write `FILE_[sanitized_stem].md` to `Needs_Action/`

### Output: Action File Format

```yaml
---
type: file_drop
original_name: [original filename]
size: [bytes]
detected: [ISO datetime]
status: pending
---
```

Body:
```markdown
## New File Dropped

A new file has been detected in Inbox folder.

**File Details:**
- Name: [original_name]
- Size: [size] bytes
- Type: [extension]

## Suggested Actions
- [ ] Review file content
- [ ] Determine appropriate handling
- [ ] Process according to file type
- [ ] Move to Done when complete
```

### Error Handling

| Error | Action | Log Level |
|-------|--------|-----------|
| File vanished before read | Skip, log warning | WARNING |
| Permission denied | Log error, continue | ERROR |
| Needs_Action/ missing | Log error, continue | ERROR |
| Disk full | Log error, continue | ERROR |
| Any other exception | Log error, continue | ERROR |

### Logging

All events logged to both:
- Console (StreamHandler)
- `Logs/watcher_errors.log` (FileHandler)

Format: `%(asctime)s - %(levelname)s - %(message)s`
