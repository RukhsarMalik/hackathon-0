# Quickstart: Silver Module 2 — Email MCP Server + Approval Workflow

## Prerequisites

- Silver Module 1 complete (orchestrator, watchers running)
- Gmail API credentials with send scope
- Python packages: `mcp`, `google-api-python-client`, `google-auth`, `google-auth-oauthlib`

## Setup

```bash
cd silver/

# 1. Install MCP SDK
pip install mcp

# 2. Re-authenticate Gmail with send scope
# Delete old token to force re-auth with new scopes
rm -f token.pickle
python gmail_watcher.py  # Will prompt for auth with expanded scopes
# Ctrl+C after successful auth

# 3. Create required directories
mkdir -p AI_Employee_Vault/Approved AI_Employee_Vault/Rejected

# 4. Configure MCP for Claude Code
# Copy mcp.json to your Claude Code config, or add to existing config
```

## Testing the Full Workflow

### Test 1: Draft Email (no approval needed)

```bash
# Start the MCP server manually for testing
python email_mcp_server.py
```

In Claude Code, the `draft_email` tool should be available. Use it to preview an email without sending.

### Test 2: Full Approval Workflow

1. **Create a test approval request**:
   ```bash
   cat > AI_Employee_Vault/Pending_Approval/APPROVAL_REPLY_test.md << 'EOF'
   ---
   type: email_approval
   to: your-email@gmail.com
   subject: Test Email from AI Employee
   original_gmail_id: test123
   original_subject: Test
   created_date: 2026-01-30T12:00:00
   priority: medium
   status: awaiting_approval
   ---

   ## Email Body

   Hello,

   This is a test email sent from the AI Employee system.

   Best regards,
   AI Employee
   EOF
   ```

2. **Approve** — move the file to Approved/:
   ```bash
   mv AI_Employee_Vault/Pending_Approval/APPROVAL_REPLY_test.md AI_Employee_Vault/Approved/
   ```

3. **Verify** — the approval watcher should detect it, create a task, orchestrator processes it, MCP sends the email.

4. **Check logs**:
   ```bash
   cat AI_Employee_Vault/Logs/mcp_actions.log
   cat AI_Employee_Vault/Logs/approval_audit.log
   ```

### Test 3: Rejection Workflow

1. Create another test approval request in Pending_Approval/
2. Move it to Rejected/
3. Verify it's logged and moved to Done/ without sending

## Running

```bash
# Start all services (including MCP server and approval watcher)
./start_all.sh
```
