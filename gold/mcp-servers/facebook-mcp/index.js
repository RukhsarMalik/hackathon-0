// index.js - Facebook MCP Server
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load .env from the same directory as this script
dotenv.config({ path: path.join(__dirname, '.env') });
const VAULT_LOGS = path.resolve(
  __dirname,
  "..",
  "..",
  "AI_Employee_Vault",
  "Logs",
);
const LOG_FILE = path.join(VAULT_LOGS, "facebook_actions.log");

// Ensure log directory exists
if (!fs.existsSync(VAULT_LOGS)) {
  fs.mkdirSync(VAULT_LOGS, { recursive: true });
}

// Facebook Graph API configuration
const FACEBOOK_PAGE_ID = process.env.FACEBOOK_PAGE_ID;
const FACEBOOK_PAGE_ACCESS_TOKEN = process.env.FACEBOOK_PAGE_ACCESS_TOKEN;
const GRAPH_API_VERSION = process.env.FACEBOOK_GRAPH_API_VERSION || "v19.0";
const GRAPH_API_BASE = `https://graph.facebook.com/${GRAPH_API_VERSION}`;

// Logging
function logAction(action, details, status) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${status} - ${action}: ${JSON.stringify(details)}\n`;
  fs.appendFileSync(LOG_FILE, logEntry);
  console.error(logEntry.trim());
}

// Helper: Make Facebook Graph API request
async function graphApiRequest(endpoint, method = "GET", body = null) {
  const url = `${GRAPH_API_BASE}${endpoint}`;
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  const data = await response.json();

  if (data.error) {
    throw new Error(`Facebook API Error: ${data.error.message} (code: ${data.error.code})`);
  }

  return data;
}

// Initialize MCP server
const server = new McpServer({
  name: "facebook-mcp",
  version: "1.0.0",
});

// Tool: post_to_facebook
server.tool(
  "post_to_facebook",
  {
    message: z.string().describe("Post content for the Facebook Page"),
    approval_file: z.string().describe("Path to approval file"),
    link: z.string().optional().describe("Optional URL to attach to the post"),
  },
  async ({ message, approval_file, link }) => {
    try {
      // Verify approval - accept files from Approved/, Done/, or task files with APPROVED_ prefix
      const isApproved = approval_file.includes("/Approved/") ||
        approval_file.includes("/Done/") ||
        approval_file.includes("APPROVED_") ||
        approval_file.includes("approved");

      if (!isApproved) {
        logAction(
          "post_to_facebook",
          { message: message.substring(0, 50), approval_file },
          "REJECTED - Not approved",
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: false,
                error: "Post not approved - approval file must indicate approval status",
              }),
            },
          ],
        };
      }

      logAction("post_to_facebook", { message: message.substring(0, 100) }, "ATTEMPTING");

      // Post to Facebook Page via Graph API
      const postBody = {
        message,
        access_token: FACEBOOK_PAGE_ACCESS_TOKEN,
      };

      if (link) {
        postBody.link = link;
      }

      const result = await graphApiRequest(
        `/${FACEBOOK_PAGE_ID}/feed`,
        "POST",
        postBody,
      );

      const postId = result.id;
      const postUrl = `https://www.facebook.com/${postId}`;

      logAction(
        "post_to_facebook",
        { postId, postUrl, message: message.substring(0, 50) },
        "SUCCESS",
      );

      // Move approval to Done
      try {
        const doneFile = approval_file.replace("/Approved/", "/Done/");
        const doneDir = path.dirname(doneFile);
        if (!fs.existsSync(doneDir)) fs.mkdirSync(doneDir, { recursive: true });
        fs.renameSync(approval_file, doneFile);
      } catch (moveErr) {
        logAction(
          "post_to_facebook",
          { error: moveErr.message },
          "WARN - Failed to move approval file",
        );
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              postId,
              postUrl,
              message: "Facebook post published successfully",
            }),
          },
        ],
      };
    } catch (error) {
      logAction("post_to_facebook", { error: error.message }, "FAILED");
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: false,
              error: error.message,
            }),
          },
        ],
      };
    }
  },
);

// Tool: get_page_insights
server.tool(
  "get_page_insights",
  {
    metric: z
      .string()
      .optional()
      .default("page_impressions")
      .describe("Metric to retrieve (e.g. page_impressions, page_engaged_users, page_post_engagements)"),
    period: z
      .string()
      .optional()
      .default("day")
      .describe("Period for the metric (day, week, days_28)"),
  },
  async ({ metric, period }) => {
    try {
      const data = await graphApiRequest(
        `/${FACEBOOK_PAGE_ID}/insights/${metric}?period=${period}&access_token=${FACEBOOK_PAGE_ACCESS_TOKEN}`,
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              metric,
              period,
              data: data.data,
            }),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: false,
              error: error.message,
            }),
          },
        ],
      };
    }
  },
);

// Tool: get_recent_posts
server.tool(
  "get_recent_posts",
  {
    count: z
      .number()
      .optional()
      .default(10)
      .describe("Number of recent posts to retrieve"),
  },
  async ({ count }) => {
    try {
      const data = await graphApiRequest(
        `/${FACEBOOK_PAGE_ID}/posts?limit=${Math.min(count, 100)}&fields=id,message,created_time,likes.summary(true),comments.summary(true),shares&access_token=${FACEBOOK_PAGE_ACCESS_TOKEN}`,
      );

      const stats = {
        total_posts: 0,
        total_likes: 0,
        total_comments: 0,
        total_shares: 0,
      };

      for (const post of data.data || []) {
        stats.total_posts++;
        stats.total_likes += post.likes?.summary?.total_count || 0;
        stats.total_comments += post.comments?.summary?.total_count || 0;
        stats.total_shares += post.shares?.count || 0;
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              stats,
              posts: data.data,
              period: `Last ${count} posts`,
            }),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: false,
              error: error.message,
            }),
          },
        ],
      };
    }
  },
);

// Start server
async function main() {
  console.error("Starting Facebook MCP Server...");
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Facebook MCP Server running");
}

main().catch(console.error);
