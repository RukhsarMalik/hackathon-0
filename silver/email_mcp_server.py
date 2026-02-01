#!/usr/bin/env python3
"""
Email MCP Server - Exposes send_email and draft_email tools via Gmail API.
Requires human approval (file in Approved/ folder) before sending.
"""
import os
import re
import base64
import logging
import shutil
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import asyncio
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

import pickle

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"
MCP_LOG = LOGS / "mcp_actions.log"

# Gmail API scopes (includes send)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def get_gmail_service():
    """Authenticate and return Gmail service."""
    creds = None

    if Path('token.pickle').exists():
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None

        if not creds:
            if not Path('credentials.json').exists():
                logger.error("credentials.json not found.")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Error during OAuth flow: {e}")
                return None

            try:
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                logger.error(f"Error saving credentials: {e}")

    return build('gmail', 'v1', credentials=creds)


def validate_email(address):
    """Check if an email address has valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, address))


def log_mcp_action(action, to, subject, status, message_id=None, error=None):
    """Append an action entry to mcp_actions.log."""
    try:
        LOGS.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] action={action} to={to} subject=\"{subject}\" status={status}"
        if message_id:
            entry += f" message_id={message_id}"
        if error:
            entry += f" error=\"{error}\""
        entry += "\n"

        with open(MCP_LOG, 'a') as f:
            f.write(entry)
    except Exception as e:
        logger.error(f"Failed to log MCP action: {e}")


def send_email_via_gmail(service, to, subject, body):
    """
    Send an email via Gmail API.

    Returns:
        Tuple of (success, message_id_or_error)
    """
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_body = {'raw': raw}

        result = service.users().messages().send(userId='me', body=send_body).execute()
        return True, result.get('id', 'unknown')
    except Exception as e:
        return False, str(e)


def format_email_preview(to, subject, body):
    """Format an email for preview display."""
    return f"""To: {to}
Subject: {subject}

{body}"""


# === MCP Server Setup ===

if MCP_AVAILABLE:
    server = Server("email-mcp-server")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="send_email",
                description="Send an email via Gmail API. Requires an approval file in the Approved/ folder.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject line"},
                        "body": {"type": "string", "description": "Email body content (plain text)"},
                        "approval_file": {"type": "string", "description": "Filename of approval file in Approved/ folder"},
                    },
                    "required": ["to", "subject", "body", "approval_file"],
                },
            ),
            Tool(
                name="draft_email",
                description="Preview an email without sending. No approval required.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject line"},
                        "body": {"type": "string", "description": "Email body content (plain text)"},
                    },
                    "required": ["to", "subject", "body"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name, arguments):
        if name == "draft_email":
            to = arguments.get("to", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "")

            if not validate_email(to):
                return [TextContent(type="text", text=f'{{"success": false, "error": "Invalid email address format: {to}"}}')]

            preview = format_email_preview(to, subject, body)
            return [TextContent(type="text", text=f'{{"preview": "{preview}"}}')]

        elif name == "send_email":
            to = arguments.get("to", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "")
            approval_file = arguments.get("approval_file", "")

            # Validate email
            if not validate_email(to):
                log_mcp_action("send_email", to, subject, "failed", error="Invalid email format")
                return [TextContent(type="text", text='{"success": false, "error": "Invalid email address format"}')]

            # Validate subject and body
            if not subject.strip():
                log_mcp_action("send_email", to, subject, "failed", error="Empty subject")
                return [TextContent(type="text", text='{"success": false, "error": "Subject cannot be empty"}')]
            if not body.strip():
                log_mcp_action("send_email", to, subject, "failed", error="Empty body")
                return [TextContent(type="text", text='{"success": false, "error": "Body cannot be empty"}')]

            # Validate approval file exists in Approved/
            approval_path = APPROVED / approval_file
            if not approval_path.exists():
                log_mcp_action("send_email", to, subject, "failed", error="Approval file not found in Approved/")
                return [TextContent(type="text", text='{"success": false, "error": "Approval file not found in Approved/ folder"}')]

            # Get Gmail service
            service = get_gmail_service()
            if not service:
                log_mcp_action("send_email", to, subject, "failed", error="Gmail authentication failed")
                return [TextContent(type="text", text='{"success": false, "error": "Gmail authentication failed"}')]

            # Send email
            success, result = send_email_via_gmail(service, to, subject, body)

            if success:
                # Move approval file to Done/
                DONE.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(approval_path), str(DONE / approval_file))
                except Exception as e:
                    logger.warning(f"Failed to move approval file to Done: {e}")

                log_mcp_action("send_email", to, subject, "success", message_id=result)
                return [TextContent(type="text", text=f'{{"success": true, "message_id": "{result}", "message": "Email sent successfully to {to}"}}')]
            else:
                log_mcp_action("send_email", to, subject, "failed", error=result)
                return [TextContent(type="text", text=f'{{"success": false, "error": "Gmail API error: {result}"}}')]

        return [TextContent(type="text", text='{"error": "Unknown tool"}')]


def main():
    """Start the MCP server."""
    if not MCP_AVAILABLE:
        logger.error("MCP SDK not installed. Run: pip install mcp")
        logger.error("Falling back to standalone mode for testing.")
        # Test Gmail auth
        service = get_gmail_service()
        if service:
            logger.info("Gmail authentication successful")
            profile = service.users().getProfile(userId='me').execute()
            logger.info(f"Authenticated as: {profile.get('emailAddress')}")
        return

    logger.info("Starting Email MCP Server...")
    logger.info(f"Approved folder: {APPROVED}")
    logger.info(f"Log file: {MCP_LOG}")

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
