# Quickstart Guide: Gold Module 1 - External Integrations & Automation

## Overview
This guide will help you set up the Gold Module 1 features: LinkedIn and Twitter MCP servers for auto-posting, and Odoo MCP server for accounting integration.

## Prerequisites
- Node.js LTS (v18 or higher)
- Docker and Docker Compose
- Claude Code installed and configured
- Access to LinkedIn Developer Account (optional - for API approach)
- Access to Twitter Developer Account (for API access)
- Access to Odoo Community Edition

## 1. Setting Up MCP Servers

### 1.1 LinkedIn MCP Server

**Option A: LinkedIn API (Recommended)**
1. Create LinkedIn Developer Account at https://www.linkedin.com/developers
2. Create a new application and get credentials:
   - Client ID
   - Client Secret
3. Get your LinkedIn Person URN (format: `urn:li:person:YOUR_ID`)
4. Navigate to the LinkedIn MCP directory:
   ```bash
   cd mcp-servers/linkedin-mcp
   ```
5. Install dependencies:
   ```bash
   npm install
   ```
6. Create `.env` file with credentials:
   ```env
   LINKEDIN_ACCESS_TOKEN=your_access_token
   LINKEDIN_PERSON_URN=urn:li:person:YOUR_ID
   ```
7. Start the server:
   ```bash
   node index.js
   ```

**Option B: Playwright Automation (No API required)**
1. Navigate to the LinkedIn MCP directory:
   ```bash
   cd mcp-servers/linkedin-mcp
   ```
2. Install dependencies including Playwright:
   ```bash
   npm install
   npx playwright install
   ```
3. First-time setup - login manually:
   ```bash
   npx playwright open --user-data-dir=$HOME/.linkedin_session https://www.linkedin.com
   ```
4. Login with your credentials, then close the browser
5. Start the server:
   ```bash
   node playwright-index.js
   ```

### 1.2 Twitter MCP Server
1. Create Twitter Developer Account at https://developer.twitter.com
2. Apply for Elevated access and create an app
3. Get credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
4. Navigate to the Twitter MCP directory:
   ```bash
   cd mcp-servers/twitter-mcp
   ```
5. Install dependencies:
   ```bash
   npm install
   ```
6. Create `.env` file with credentials:
   ```env
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   ```
7. Start the server:
   ```bash
   node index.js
   ```

### 1.3 Odoo MCP Server
1. Set up Odoo 19 Community using Docker:
   ```bash
   # Create docker-compose.yml
   version: '3.8'

   services:
     postgres:
       image: postgres:15
       environment:
         - POSTGRES_DB=postgres
         - POSTGRES_USER=odoo
         - POSTGRES_PASSWORD=odoo
       volumes:
         - odoo-db-data:/var/lib/postgresql/data
       networks:
         - odoo-network

     odoo:
       image: odoo:19.0
       depends_on:
         - postgres
       ports:
         - "8069:8069"
       environment:
         - HOST=postgres
         - USER=odoo
         - PASSWORD=odoo
       volumes:
         - odoo-web-data:/var/lib/odoo
       networks:
         - odoo-network

   volumes:
     odoo-db-data:
     odoo-web-data:

   networks:
     odoo-network:
       driver: bridge
   ```
2. Start Odoo:
   ```bash
   docker-compose up -d
   ```
3. Navigate to http://localhost:8069 and create database:
   - Database name: ai_employee_accounting
   - Email: admin@example.com
   - Password: admin (change later!)
4. Install Accounting module:
   - Go to Apps → Search "Accounting" → Install
5. Navigate to the Odoo MCP directory:
   ```bash
   cd mcp-servers/odoo-mcp
   ```
6. Install dependencies:
   ```bash
   npm install
   ```
7. Create `.env` file with credentials:
   ```env
   ODOO_URL=http://localhost:8069
   ODOO_DB=ai_employee_accounting
   ODOO_USERNAME=admin@example.com
   ODOO_PASSWORD=admin
   ```
8. Start the server:
   ```bash
   node index.js
   ```

## 2. Configuring Claude Code MCP

Add the MCP servers to Claude Code configuration in `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": ["/full/path/to/mcp-servers/linkedin-mcp/index.js"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token_here",
        "LINKEDIN_PERSON_URN": "urn:li:person:YOUR_ID"
      }
    },
    "twitter": {
      "command": "node",
      "args": ["/full/path/to/mcp-servers/twitter-mcp/index.js"],
      "env": {
        "TWITTER_API_KEY": "your_key",
        "TWITTER_API_SECRET": "your_secret",
        "TWITTER_ACCESS_TOKEN": "your_token",
        "TWITTER_ACCESS_SECRET": "your_token_secret"
      }
    },
    "odoo": {
      "command": "node",
      "args": ["/full/path/to/mcp-servers/odoo-mcp/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "ai_employee_accounting",
        "ODOO_USERNAME": "admin@example.com",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

## 3. Setting Up Agent Skills

### 3.1 Update LinkedIn Poster Skill
Update `AI_Employee_Vault/Needs_Action/SKILL_LinkedInPoster.md` to include MCP integration.

### 3.2 Create Twitter Poster Skill
Create `Skills/SKILL_TwitterPoster.md` with Twitter posting logic.

### 3.3 Create Accounting Manager Skill
Create `Skills/SKILL_AccountingManager.md` for handling invoices and payments.

### 3.4 Create Social Summary Generator Skill
Create `Skills/SKILL_SocialSummaryGenerator.md` for weekly reports.

## 4. Testing the Setup

### 4.1 Test LinkedIn MCP
```bash
claude code "Call post_to_linkedin tool with sample content"
```

### 4.2 Test Twitter MCP
```bash
claude code "Call post_tweet tool with sample content"
```

### 4.3 Test Odoo MCP
```bash
claude code "Call list_customers tool"
```

## 5. Running the System

1. Start all MCP servers:
   ```bash
   # In separate terminals
   cd mcp-servers/linkedin-mcp && node index.js
   cd mcp-servers/twitter-mcp && node index.js
   cd mcp-servers/odoo-mcp && node index.js
   ```
2. Ensure Claude Code can access all MCP servers
3. Place approval files in `/Approved/` folder to trigger automated posting
4. Monitor logs in `AI_Employee_Vault/Logs/` for activity

## Troubleshooting

- **LinkedIn API errors**: Check access token validity and permissions
- **Twitter rate limits**: Check credentials and rate limit status
- **Odoo connection errors**: Verify Odoo server is running and credentials are correct
- **MCP server not accessible**: Check Claude Code configuration and server startup logs

## Next Steps

1. Set up the orchestrator to automatically process files in `/Needs_Action/`
2. Configure the approval workflow system
3. Set up the weekly audit process for social media and accounting summaries
4. Configure the dashboard updates for real-time metrics