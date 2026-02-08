# Research Findings: Gold Module 1 Implementation

## 1. LinkedIn API vs Playwright Automation

**Decision**: Both approaches should be supported, with API preferred when available
**Rationale**: LinkedIn API is more reliable and efficient, but requires approval process. Playwright provides fallback automation option.
**Alternatives considered**:
- API only (requires LinkedIn developer account approval, can take time)
- Playwright only (more fragile, subject to UI changes)

**Details**:
- LinkedIn API requires creating a LinkedIn App with w_member_social permission
- Developer account approval can take 3-7 days
- Playwright automation requires initial manual login to persistent session
- API approach provides better error handling and post URL return

## 2. Twitter API Authentication Setup

**Decision**: Use Twitter API v2 with OAuth 2.0 Bearer Token
**Rationale**: Twitter API v2 provides comprehensive posting and analytics capabilities
**Alternatives considered**:
- Twitter API v1.1 (deprecated features)
- Browser automation (fragile, against ToS)

**Details**:
- Need Twitter Developer Account with Elevated access
- Requires API Key, API Secret, Access Token, Access Secret
- Rate limits: 300 tweets per 3-hour window for posting
- Thread posting requires sequential API calls with delays

## 3. Odoo 19 Community Installation

**Decision**: Use Docker Compose for local installation
**Rationale**: Provides isolated, reproducible environment with easy setup
**Alternatives considered**:
- Manual installation (complex, environment-dependent)
- Cloud-hosted Odoo (violates local-first principle)

**Details**:
- Docker Compose with PostgreSQL dependency
- Port 8069 for Odoo web interface
- XML-RPC API for integration (standard in Community edition)
- Initial setup requires manual configuration of accounting module

## 4. MCP Server Integration Patterns

**Decision**: Follow Claude Code MCP server pattern with tool-based architecture
**Rationale**: Leverages existing Claude Code infrastructure and patterns
**Alternatives considered**:
- Direct API calls from Claude (tight coupling, less reusable)
- Separate microservices (over-engineering for this scope)

**Details**:
- Each MCP server exports tools using @anthropic/mcp Server
- Tools follow consistent parameter and response patterns
- Error handling with proper status codes and messages
- Logging integration with existing vault structure

## 5. Security Best Practices for API Credentials

**Decision**: Store credentials in environment variables with .env files
**Rationale**: Follows security best practices while maintaining local-first principle
**Alternatives considered**:
- Hardcoded in source (major security risk)
- Encrypted files in vault (unnecessary complexity)

**Details**:
- .env files added to .gitignore
- Environment variables loaded via dotenv
- Documentation for required credentials
- Secure credential management in MCP configuration

## 6. Error Handling Patterns for External Services

**Decision**: Implement retry logic with exponential backoff and proper error categorization
**Rationale**: Ensures resilience against transient failures while providing clear error reporting
**Alternatives considered**:
- Fail immediately (poor user experience)
- Infinite retries (could cause blocking)

**Details**:
- Transient errors (network, rate limits): Retry with exponential backoff
- Permanent errors (auth, invalid data): Immediate failure with clear message
- Queue for retry mechanism for critical operations
- Circuit breaker pattern for service availability

## 7. Rate Limiting Strategies for Social Media APIs

**Decision**: Implement queue-based rate limiting with scheduling
**Rationale**: Prevents API violations while maintaining functionality
**Alternatives considered**:
- Ignore rate limits (violates terms of service)
- Simple delays (inefficient, doesn't handle bursts)

**Details**:
- Queue posts for retry when rate limit encountered
- Schedule posts during off-peak times when possible
- Monitor API response headers for rate limit status
- Batch operations where APIs support it