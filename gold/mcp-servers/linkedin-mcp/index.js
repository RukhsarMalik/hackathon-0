// index.js - LinkedIn MCP Server
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load .env from the same directory as this script
dotenv.config({ path: path.join(__dirname, '.env') });
const VAULT_LOGS = path.resolve(__dirname, '..', '..', 'AI_Employee_Vault', 'Logs');
const LOG_FILE = path.join(VAULT_LOGS, 'linkedin_actions.log');

// Ensure log directory exists
if (!fs.existsSync(VAULT_LOGS)) {
  fs.mkdirSync(VAULT_LOGS, { recursive: true });
}

// LinkedIn API credentials
const LINKEDIN_ACCESS_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN;
const LINKEDIN_PERSON_URN = process.env.LINKEDIN_PERSON_URN;

// Logging
function logAction(action, details, status) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${status} - ${action}: ${JSON.stringify(details)}\n`;
  fs.appendFileSync(LOG_FILE, logEntry);
  console.error(logEntry.trim());
}

// Initialize MCP server
const server = new McpServer({
  name: 'linkedin-mcp',
  version: '1.0.0',
});

// Tool: post_to_linkedin
server.tool(
  'post_to_linkedin',
  {
    content: z.string().describe('Post content (text)'),
    approval_file: z.string().describe('Path to approval file that authorized this post'),
  },
  async ({ content, approval_file }) => {
    try {
      // Verify approval - accept files from Approved/, Done/, or task files with APPROVED_ prefix
      const isApproved = approval_file.includes('/Approved/') ||
        approval_file.includes('/Done/') ||
        approval_file.includes('APPROVED_') ||
        approval_file.includes('approved');

      if (!isApproved) {
        logAction('post_to_linkedin', { content: content.substring(0, 50), approval_file }, 'REJECTED - Not approved');
        return {
          content: [{ type: 'text', text: JSON.stringify({
            success: false,
            error: 'Post not approved - approval file must indicate approval status',
          })}],
        };
      }

      logAction('post_to_linkedin', { content: content.substring(0, 100) }, 'ATTEMPTING');

      // LinkedIn v2 UGC Posts API (works with w_member_social scope)
      const response = await axios.post(
        'https://api.linkedin.com/v2/ugcPosts',
        {
          author: LINKEDIN_PERSON_URN,
          lifecycleState: 'PUBLISHED',
          specificContent: {
            'com.linkedin.ugc.ShareContent': {
              shareCommentary: {
                text: content,
              },
              shareMediaCategory: 'NONE',
            },
          },
          visibility: {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
          },
        },
        {
          headers: {
            'Authorization': `Bearer ${LINKEDIN_ACCESS_TOKEN}`,
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
          },
        }
      );

      const postId = response.data?.id || 'unknown';
      const postUrl = `https://www.linkedin.com/feed/update/${postId}`;

      logAction('post_to_linkedin', { postId, postUrl, content: content.substring(0, 50) }, 'SUCCESS');

      // Move approval file to Done
      try {
        const doneFile = approval_file.replace('/Approved/', '/Done/');
        const doneDir = path.dirname(doneFile);
        if (!fs.existsSync(doneDir)) fs.mkdirSync(doneDir, { recursive: true });
        fs.renameSync(approval_file, doneFile);
      } catch (moveErr) {
        logAction('post_to_linkedin', { error: moveErr.message }, 'WARN - Failed to move approval file');
      }

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          postId,
          postUrl,
          message: 'Post published to LinkedIn successfully',
        })}],
      };
    } catch (error) {
      const status = error.response?.status || 'unknown';
      const apiError = error.response?.data || {};
      const apiHeaders = error.response?.headers || {};
      const errorMsg = error.message || 'Unknown error';
      const fullError = `HTTP ${status}: ${errorMsg} | API: ${JSON.stringify(apiError)}`;

      logAction('post_to_linkedin', {
        error: fullError,
        status,
        apiResponse: apiError,
        responseHeaders: apiHeaders['x-restli-error-response'] || apiHeaders['x-linkedin-error'] || null,
      }, 'FAILED');

      if (status === 401 || status === 403) {
        return {
          content: [{ type: 'text', text: JSON.stringify({
            success: false,
            error: `LinkedIn token expired or insufficient permissions (HTTP ${status}). Please refresh your access token.`,
            details: apiError,
          })}],
        };
      }

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: false,
          error: fullError,
          details: apiError,
        })}],
      };
    }
  }
);

// Tool: get_post_stats
server.tool(
  'get_post_stats',
  {
    days: z.number().optional().default(7).describe('Number of days to look back'),
  },
  async ({ days }) => {
    try {
      const response = await axios.get(
        `https://api.linkedin.com/v2/ugcPosts?q=authors&authors=${encodeURIComponent(LINKEDIN_PERSON_URN)}&count=10`,
        {
          headers: {
            'Authorization': `Bearer ${LINKEDIN_ACCESS_TOKEN}`,
            'X-Restli-Protocol-Version': '2.0.0',
          },
        }
      );

      const posts = response.data.elements || [];

      const stats = {
        total_posts: posts.length,
        total_likes: 0,
        total_comments: 0,
        total_shares: 0,
      };

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          stats,
          posts: posts.length,
        })}],
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: false,
          error: error.message,
        })}],
      };
    }
  }
);

// Start server
async function main() {
  console.error('Starting LinkedIn MCP Server...');
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('LinkedIn MCP Server running');
}

main().catch(console.error);
