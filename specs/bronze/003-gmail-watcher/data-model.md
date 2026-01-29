# Data Model: Gmail Watcher

**Created**: 2026-01-29
**Status**: Complete
**Source**: Feature specification and implementation requirements

## Entities

### GmailMessage
Represents a raw message from the Gmail API

**Fields**:
- `id` (string): Unique Gmail message identifier
- `threadId` (string): Thread identifier for conversation grouping
- `labelIds` (array[string]): List of labels applied to the message
- `snippet` (string): Plain text snippet of the message
- `payload` (object): Message payload with headers and body parts
- `sizeEstimate` (integer): Size of the message in bytes
- `historyId` (string): History ID for change tracking
- `internalDate` (string): Internal date of the message (RFC3339 format)

**Relationships**:
- Zero-to-one EmailActionFile (via message ID reference)

### EmailActionFile
Represents the action file created in the vault for AI processing

**Fields**:
- `type` (string): Fixed value "email" for email action files
- `from` (string): Sender email address
- `from_name` (string): Sender display name (optional)
- `subject` (string): Email subject line
- `received` (string): ISO timestamp of email receipt
- `priority` (string): Priority level (high, medium, low)
- `status` (string): Processing status (pending, in_progress, completed)
- `gmail_id` (string): Original Gmail message ID
- `size` (integer): Original email size in bytes
- `content_preview` (string): First 500 characters of email content
- `suggested_actions` (array[object]): List of suggested action items

**Validation Rules**:
- `type` must equal "email"
- `gmail_id` must match the pattern of a Gmail message ID
- `priority` must be one of: "high", "medium", "low"
- `status` must be one of: "pending", "in_progress", "completed"
- `received` must be a valid ISO 8601 timestamp

### ProcessedEmailId
Represents a record of a processed email to prevent duplicates

**Fields**:
- `gmail_message_id` (string): Unique Gmail message identifier
- `processed_at` (string): ISO timestamp when email was processed
- `action_file_path` (string): Path to the created action file (optional)

**Validation Rules**:
- `gmail_message_id` must be unique in the collection
- `processed_at` must be a valid ISO 8601 timestamp

### GmailServiceConfig
Configuration for the Gmail API service

**Fields**:
- `client_secret_file` (string): Path to credentials.json
- `token_file` (string): Path to token.json for authentication persistence
- `scopes` (array[string]): OAuth scopes required for the application
- `poll_interval_seconds` (integer): Interval between Gmail checks (default: 120)
- `max_retries` (integer): Maximum retry attempts for failed API calls
- `backoff_base_delay` (integer): Base delay for exponential backoff (seconds)
- `backoff_max_delay` (integer): Maximum delay for exponential backoff (seconds)

## State Transitions

### EmailActionFile States
```
PENDING -> IN_PROGRESS -> COMPLETED
   |              |
   V              V
COMPLETED <- IN_PROGRESS
```

- **PENDING**: Action file created, waiting for AI processing
- **IN_PROGRESS**: AI Employee has started processing the email
- **COMPLETED**: AI Employee has finished processing the email

### ProcessedEmailId Lifecycle
- **CREATED**: When an email is first processed and its ID is recorded
- **RETAINED**: Until cleanup process removes old entries (retention policy: 30 days)
- **DELETED**: During cleanup of old entries

## Relationships

```
GmailMessage --[1:1]--> EmailActionFile
GmailMessage --[1:1]--> ProcessedEmailId
EmailActionFile --[1:1]--> ProcessedEmailId (via gmail_id)
```

## Constraints

1. **Uniqueness Constraint**: Each Gmail message ID can only appear once in ProcessedEmailId
2. **Referential Integrity**: Every EmailActionFile with a gmail_id must correspond to a GmailMessage that existed at processing time
3. **Temporal Constraint**: ProcessedEmailId.processed_at must be after the GmailMessage.internalDate
4. **Size Constraint**: EmailActionFile.content_preview must not exceed 500 characters