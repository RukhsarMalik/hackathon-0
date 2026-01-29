# Research: Gmail Watcher

**Created**: 2026-01-29
**Status**: Complete
**Source**: Feature specification research and technology investigation

## R0.1: OAuth 2.0 Implementation Research

### Decision: Use Application Default Credentials with OAuth 2.0 flow
**Rationale**: The Google API Client Library for Python provides a secure and standardized way to handle OAuth 2.0 authentication for Gmail API. The approach involves downloading credentials.json from Google Cloud Console and running the OAuth flow to generate token.json.

**Alternatives considered**:
- Service Account Authentication: More complex setup, requires domain-wide delegation for Gmail access
- Direct HTTP API calls: Reinventing authentication mechanisms unnecessarily
- Stored username/password: Violates Gmail security policies (less secure apps disabled)

**Chosen approach**: Use `google_auth_oauthlib.flow.InstalledAppFlow` for the initial authentication and `google.oauth2.credentials.Credentials` for ongoing API access.

## R0.2: Rate Limiting Strategy Research

### Decision: Implement exponential backoff with jitter for Gmail API rate limits
**Rationale**: Gmail API has both usage quotas (requests per day, per 100 seconds) and rate limits. Exponential backoff with jitter prevents overwhelming the API during peak processing times.

**Gmail API Quotas**:
- Daily usage limit: 1,000,000,000 queries per day
- Per-user rate limit: 2500 requests per 100 seconds per user
- Polling interval of 120 seconds stays well within safe limits

**Implementation approach**: Use a base delay of 1 second with exponential increase (multiply by 2) up to a maximum of 60 seconds, with random jitter to avoid thundering herd problems.

**Alternatives considered**:
- Fixed delays: Could lead to inefficient resource usage
- No backoff: Would cause API errors and potential blocking
- Aggressive polling: Would exceed rate limits and waste resources

## R0.3: Email Parsing Best Practices

### Decision: Use Gmail API payload parsing with proper MIME handling
**Rationale**: Gmail API returns emails in a structured format with headers and payload parts. Extracting the email body from the payload parts provides the content needed for action files while preserving metadata in headers.

**Parsing approach**:
- Extract headers (From, Subject, Date) from message payload
- Parse body content from text/plain or text/html parts
- Limit content preview to 500 characters to avoid overly large action files
- Handle base64 encoded content properly

**Alternatives considered**:
- Raw IMAP parsing: More complex and not necessary since Gmail API provides structured data
- Third-party email parsing libraries: Unnecessary complexity when API provides structured data
- Full content retrieval: Would create unnecessarily large action files

## Additional Research: Security Best Practices

### Decision: Secure credential storage and access patterns
**Rationale**: OAuth 2.0 credentials must be protected to prevent unauthorized access to user's Gmail account.

**Security measures**:
- Store credentials.json and token.json in .gitignore
- Use environment variables for configuration
- Implement proper file permissions (600) for credential files
- Add clear warnings about credential security in documentation

## Priority Detection Algorithm Research

### Decision: Rule-based classification with keyword matching
**Rationale**: A simple rule-based approach using keyword matching is effective for email priority detection while remaining transparent and configurable.

**Classification rules**:
- High priority: urgent, asap, critical, emergency, invoice, payment, deadline, today, tomorrow
- Medium priority: request, question, meeting, reminder, follow-up
- Low priority: newsletter, notification, promotional, unsubscribe

**Alternatives considered**:
- Machine Learning classification: Overkill for this use case and requires training data
- Natural Language Processing: Too complex for simple triage needs
- Sender-based classification only: Doesn't account for content importance

## Duplicate Detection Research

### Decision: Message ID tracking with persistent storage
**Rationale**: Gmail provides unique message IDs that can be used to identify and prevent duplicate processing. Storing these in a simple text file provides persistence across application restarts.

**Implementation approach**:
- Store processed message IDs in Logs/processed_emails.txt
- Use set data structure for O(1) lookup performance
- Implement file rotation when the file grows too large (>10k entries)
- Add cleanup mechanism to remove old entries periodically

**Alternatives considered**:
- Database storage: Overkill for this simple use case
- In-memory tracking only: Would lose track after application restart
- Hash-based detection: Less reliable than using Gmail's unique IDs