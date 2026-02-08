# LinkedIn MCP Server API Contract

## Overview
This document defines the API contract for the LinkedIn MCP server that enables automated posting to LinkedIn.

## Base URL
The LinkedIn MCP server is accessed through Claude Code's MCP interface. The server is typically started with:
```bash
node /path/to/mcp-servers/linkedin-mcp/index.js
```

## Authentication
Authentication is handled through environment variables:
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn API access token
- `LINKEDIN_PERSON_URN`: LinkedIn person URN (format: urn:li:person:YOUR_ID)

## Tools

### 1. post_to_linkedin
**Description**: Posts content to LinkedIn using either API or Playwright automation.

**Method**: Tool call through Claude Code MCP interface

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "Post content (text)",
      "maxLength": 1300
    },
    "approval_file": {
      "type": "string",
      "description": "Path to approval file that authorized this post"
    }
  },
  "required": ["content", "approval_file"]
}
```

**Successful Response**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "const": true
    },
    "postId": {
      "type": "string",
      "description": "LinkedIn-generated post ID"
    },
    "postUrl": {
      "type": "string",
      "description": "URL of the published post"
    },
    "message": {
      "type": "string",
      "description": "Success message"
    }
  },
  "required": ["success", "postId", "postUrl", "message"]
}
```

**Error Response**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "const": false
    },
    "error": {
      "type": "string",
      "description": "Error message"
    }
  },
  "required": ["success", "error"]
}
```

**Business Logic**:
- Verifies approval_file is in /Approved/ directory
- Validates approval_file exists
- Posts content to LinkedIn
- Returns post URL upon successful publication
- Moves approval file to Done folder after successful posting
- Logs all actions with timestamps and status
- Handles LinkedIn token expiration with appropriate error messages

### 2. get_post_stats
**Description**: Gets engagement stats for recent posts.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "days": {
      "type": "number",
      "description": "Number of days to look back",
      "default": 7
    }
  }
}
```

**Successful Response**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "const": true
    },
    "stats": {
      "type": "object",
      "properties": {
        "total_posts": {"type": "number"},
        "total_likes": {"type": "number"},
        "total_comments": {"type": "number"},
        "total_shares": {"type": "number"}
      }
    },
    "posts": {
      "type": "number",
      "description": "Number of posts analyzed"
    }
  },
  "required": ["success", "stats", "posts"]
}
```

**Error Response**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "const": false
    },
    "error": {
      "type": "string",
      "description": "Error message"
    }
  },
  "required": ["success", "error"]
}
```

## Error Codes
- `401`: LinkedIn token expired - user needs to refresh token
- `403`: Insufficient permissions - check LinkedIn app permissions
- `429`: Rate limit exceeded - retry after delay
- `500`: Internal server error - check server logs

## Security Considerations
- API credentials must be stored in environment variables
- Approval verification prevents unauthorized posting
- All actions are logged for audit purposes
- Token expiration is handled gracefully with user notification

## Rate Limits
- LinkedIn API has rate limits that vary by endpoint
- Server implements appropriate delays and retry logic
- Excessive requests will be queued for later processing