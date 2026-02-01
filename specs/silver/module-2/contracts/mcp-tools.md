# MCP Tool Contracts: Email Server

## Tool: send_email

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "to": {
      "type": "string",
      "description": "Recipient email address"
    },
    "subject": {
      "type": "string",
      "description": "Email subject line"
    },
    "body": {
      "type": "string",
      "description": "Email body content (plain text)"
    },
    "approval_file": {
      "type": "string",
      "description": "Filename of the approval file in Approved/ folder"
    }
  },
  "required": ["to", "subject", "body", "approval_file"]
}
```

### Success Response
```json
{
  "success": true,
  "message_id": "19c0edf916e0e43d",
  "message": "Email sent successfully to user@example.com"
}
```

### Error Responses
```json
{
  "success": false,
  "error": "Approval file not found in Approved/ folder"
}
```
```json
{
  "success": false,
  "error": "Invalid email address format"
}
```
```json
{
  "success": false,
  "error": "Gmail API error: <details>"
}
```

---

## Tool: draft_email

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "to": {
      "type": "string",
      "description": "Recipient email address"
    },
    "subject": {
      "type": "string",
      "description": "Email subject line"
    },
    "body": {
      "type": "string",
      "description": "Email body content (plain text)"
    }
  },
  "required": ["to", "subject", "body"]
}
```

### Success Response
```json
{
  "preview": "To: user@example.com\nSubject: Re: Meeting Tomorrow\n\nHi,\n\nThank you for your email..."
}
```
