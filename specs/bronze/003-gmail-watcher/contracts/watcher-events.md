# Contract: Gmail Watcher Events

**Created**: 2026-01-29
**Status**: Draft
**Version**: 1.0

## Purpose
Defines the interface and contract between the Gmail watcher and the rest of the system, particularly how email events are processed and converted to action files.

## Event Types

### EmailDetectedEvent
Triggered when a new important email is detected in Gmail

**Schema**:
```json
{
  "type": "email_detected",
  "timestamp": "2026-01-29T10:30:00Z",
  "gmail_id": "msg_abc123xyz",
  "subject": "Project Update - Review Needed",
  "from": "sender@example.com",
  "from_name": "John Doe",
  "received_time": "2026-01-29T10:25:00Z",
  "size_bytes": 1234,
  "is_important": true,
  "is_unread": true
}
```

**Producer**: Gmail Watcher Service
**Consumer**: Action File Generator

### ActionFileCreatedEvent
Triggered when an email action file is successfully created in the vault

**Schema**:
```json
{
  "type": "action_file_created",
  "timestamp": "2026-01-29T10:30:05Z",
  "gmail_id": "msg_abc123xyz",
  "action_file_path": "Needs_Action/EMAIL_abc123xy.md",
  "priority": "high",
  "processing_status": "pending"
}
```

**Producer**: Action File Generator
**Consumer**: Dashboard Updater, Logger

### DuplicateDetectedEvent
Triggered when an email is detected but has already been processed

**Schema**:
```json
{
  "type": "duplicate_detected",
  "timestamp": "2026-01-29T10:30:10Z",
  "gmail_id": "msg_abc123xyz",
  "subject": "Project Update - Review Needed",
  "from": "sender@example.com"
}
```

**Producer**: Duplicate Detector
**Consumer**: Logger

### ApiRateLimitEvent
Triggered when Gmail API rate limits are encountered

**Schema**:
```json
{
  "type": "api_rate_limit",
  "timestamp": "2026-01-29T10:30:15Z",
  "retry_after_seconds": 30,
  "error_code": 429,
  "attempt_number": 1
}
```

**Producer**: Gmail API Client
**Consumer**: Backoff Handler

## Interface Contracts

### GmailServiceInterface
Methods that interact with the Gmail API

#### get_important_emails()
**Purpose**: Retrieve important unread emails from Gmail
**Input**: None
**Output**: Array of email objects with id, subject, from, received_time, size, snippet
**Errors**: API connection failures, authentication errors
**Timeout**: 30 seconds per request
**Rate Limit**: Respect Gmail API quotas (2500 requests per 100 seconds)

#### authenticate()
**Purpose**: Authenticate with Gmail API using OAuth 2.0
**Input**: Path to credentials.json
**Output**: Authenticated service object or error
**Errors**: Invalid credentials, network issues, expired tokens
**Retry Policy**: Exponential backoff with max 5 attempts

### ActionFileGeneratorInterface
Methods for creating action files in the vault

#### create_action_file(email_data)
**Purpose**: Create a structured action file from email data
**Input**: Email data object with id, subject, from, content, etc.
**Output**: Path to created action file or error
**Validation**: Ensure all required fields are present
**File Format**: Markdown with YAML frontmatter

#### email_already_processed(gmail_id)
**Purpose**: Check if an email has already been processed
**Input**: Gmail message ID
**Output**: Boolean indicating if email was previously processed
**Storage**: Check Logs/processed_emails.txt

### DuplicateDetectorInterface
Methods for tracking processed emails

#### mark_as_processed(gmail_id)
**Purpose**: Record that an email has been processed
**Input**: Gmail message ID
**Output**: Success or error
**Persistence**: Append to Logs/processed_emails.txt

#### load_processed_ids()
**Purpose**: Load all previously processed email IDs
**Input**: None
**Output**: Set of processed email IDs
**Storage**: Read from Logs/processed_emails.txt

## Error Handling Contract

### Retry Mechanism
- **Transient Errors**: Connection timeouts, temporary API failures
- **Backoff Strategy**: Exponential backoff starting at 1 second, doubling each attempt, max 60 seconds
- **Max Attempts**: 5 before escalating error
- **Jitter**: Random component added to backoff time to prevent thundering herd

### Failure Boundaries
- **Authentication Failures**: Immediate halt with clear error message
- **API Quota Exceeded**: Backoff and retry, log warning
- **File System Errors**: Attempt recovery, log error, continue watching
- **Network Errors**: Backoff and retry, continue watching

## Performance Contract

### Latency Requirements
- **Email Detection**: Within 2 minutes of email arrival (due to polling interval)
- **Action File Creation**: Within 5 seconds of detection
- **Duplicate Check**: Within 100ms for 10k+ processed emails

### Throughput Requirements
- **Email Processing**: At least 10 emails per minute during burst periods
- **API Requests**: Stay within Gmail's rate limits (2500/100s user limit)

### Resource Usage
- **Memory**: Less than 100MB during normal operation
- **CPU**: Minimal usage during idle periods
- **Disk**: Log files should rotate when exceeding 100MB

## Security Contract

### Credential Handling
- **Storage**: Credentials stored in secure files excluded from version control
- **Access**: Credentials accessed only during authentication
- **Permissions**: Credential files have restricted permissions (600)

### Data Protection
- **Email Content**: Only necessary content stored in action files
- **PII**: No personally identifiable information stored unnecessarily
- **Retention**: Processed email IDs retained for 30 days maximum