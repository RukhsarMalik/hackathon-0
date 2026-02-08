# Facebook MCP Server API Contract

## Overview
This document defines the API contract for the Facebook MCP server that enables automated posting to a Facebook Page via the Facebook Graph API.

## Base URL
The Facebook MCP server is accessed through Claude Code's MCP interface. The server is typically started with:
```bash
node /path/to/mcp-servers/facebook-mcp/index.js
```

## Authentication
Authentication is handled through environment variables:
- `FACEBOOK_PAGE_ID`: Facebook Page ID to post to
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Long-lived Page Access Token with `pages_manage_posts` and `pages_read_engagement` permissions

## Tools

### 1. post_to_facebook
**Description**: Posts content to a Facebook Page.

**Method**: Tool call through Claude Code MCP interface

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "Post content (max 63,206 characters)",
      "maxLength": 63206
    },
    "approval_file": {
      "type": "string",
      "description": "Path to approval file"
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
      "description": "Facebook-generated post ID"
    },
    "postUrl": {
      "type": "string",
      "description": "URL of the published Facebook post"
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
- Enforces 63,206 character limit
- Posts to the configured Facebook Page via Graph API (`POST /{page-id}/feed`)
- Returns post URL upon successful publication
- Moves approval file to Done folder after successful posting
- Logs all Facebook actions with timestamps and status

### 2. get_page_insights
**Description**: Gets engagement insights for recent Facebook Page posts.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "days": {
      "type": "number",
      "description": "Number of days to look back for insights",
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
        "total_shares": {"type": "number"},
        "total_reach": {"type": "number"}
      }
    },
    "period": {
      "type": "string",
      "description": "Description of time period analyzed"
    }
  },
  "required": ["success", "stats", "period"]
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

### 3. get_recent_posts
**Description**: Gets a list of recent posts from the Facebook Page with engagement data.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "count": {
      "type": "number",
      "description": "Number of recent posts to retrieve",
      "default": 10
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
    "posts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "message": {"type": "string"},
          "created_time": {"type": "string"},
          "likes": {"type": "number"},
          "comments": {"type": "number"},
          "shares": {"type": "number"}
        }
      }
    },
    "message": {
      "type": "string",
      "description": "Success message"
    }
  },
  "required": ["success", "posts", "message"]
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
- `190`: Invalid or expired access token - regenerate Page Access Token
- `200`: Insufficient permissions - check `pages_manage_posts` and `pages_read_engagement` permissions
- `4`: Application rate limit reached - retry after delay per Graph API rate limits
- `100`: Invalid parameter - check post content or request parameters
- `500`: Internal server error - check server logs

## Security Considerations
- Page Access Token must be stored in environment variables
- Approval verification prevents unauthorized posting
- All actions are logged for audit purposes
- Rate limiting is enforced to comply with Facebook Graph API terms
- Use long-lived Page Access Tokens (60-day expiry) and implement token refresh logic

## Rate Limits
- Facebook Graph API allows 200 calls per user per hour
- Server implements appropriate delays between consecutive posts
- Excessive requests will be queued for later processing
- Rate limit status is monitored to prevent violations
- Page-level rate limits: 4800 calls per 24 hours for page-specific endpoints
