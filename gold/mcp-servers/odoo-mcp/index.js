// index.js - Odoo MCP Server
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import xmlrpc from 'xmlrpc';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load .env from the same directory as this script
dotenv.config({ path: path.join(__dirname, '.env') });
const VAULT_LOGS = path.resolve(__dirname, '..', '..', 'AI_Employee_Vault', 'Logs');
const LOG_FILE = path.join(VAULT_LOGS, 'odoo_actions.log');

// Ensure log directory exists
if (!fs.existsSync(VAULT_LOGS)) {
  fs.mkdirSync(VAULT_LOGS, { recursive: true });
}

// Odoo configuration
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || 'ai_employee_accounting';
const ODOO_USERNAME = process.env.ODOO_USERNAME || 'admin@example.com';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

// Odoo clients
let common, models, uid;

// Logging
function logAction(action, details, status) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${status} - ${action}: ${JSON.stringify(details)}\n`;
  fs.appendFileSync(LOG_FILE, logEntry);
  console.error(logEntry.trim());
}

// Initialize Odoo connection
async function initOdoo() {
  return new Promise((resolve, reject) => {
    common = xmlrpc.createClient({ url: `${ODOO_URL}/xmlrpc/2/common` });
    models = xmlrpc.createClient({ url: `${ODOO_URL}/xmlrpc/2/object` });

    common.methodCall('authenticate', [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}], (error, value) => {
      if (error) {
        console.error('Odoo authentication failed:', error);
        reject(error);
      } else {
        uid = value;
        console.error(`Connected to Odoo as user ID: ${uid}`);
        resolve(uid);
      }
    });
  });
}

// Helper: Execute Odoo method
function executeKw(model, method, args, kwargs = {}) {
  return new Promise((resolve, reject) => {
    models.methodCall('execute_kw', [
      ODOO_DB, uid, ODOO_PASSWORD,
      model, method, args, kwargs
    ], (error, value) => {
      if (error) reject(error);
      else resolve(value);
    });
  });
}

// Initialize MCP server
const server = new McpServer({
  name: 'odoo-mcp',
  version: '1.0.0',
});

// Tool: create_invoice
server.tool(
  'create_invoice',
  {
    customer_name: z.string().describe('Customer name'),
    product_name: z.string().describe('Product/service name'),
    quantity: z.number().optional().default(1).describe('Quantity'),
    price_unit: z.number().describe('Unit price'),
    approval_file: z.string().optional().describe('Approval file path (if required)'),
  },
  async ({ customer_name, product_name, quantity, price_unit, approval_file }) => {
    try {
      logAction('create_invoice', { customer_name, product_name, quantity, price_unit }, 'ATTEMPTING');

      // Find customer
      const partners = await executeKw('res.partner', 'search_read', [
        [['name', '=', customer_name]]
      ], { fields: ['id', 'name'], limit: 1 });

      if (partners.length === 0) {
        return {
          content: [{ type: 'text', text: JSON.stringify({
            success: false,
            error: `Customer '${customer_name}' not found`,
          })}],
        };
      }

      const customerId = partners[0].id;

      // Find product
      const products = await executeKw('product.product', 'search_read', [
        [['name', '=', product_name]]
      ], { fields: ['id', 'name'], limit: 1 });

      if (products.length === 0) {
        return {
          content: [{ type: 'text', text: JSON.stringify({
            success: false,
            error: `Product '${product_name}' not found`,
          })}],
        };
      }

      const productId = products[0].id;

      // Create invoice
      const invoiceId = await executeKw('account.move', 'create', [[{
        partner_id: customerId,
        move_type: 'out_invoice',
        invoice_date: new Date().toISOString().split('T')[0],
        invoice_line_ids: [[0, 0, {
          product_id: productId,
          quantity: quantity,
          price_unit: price_unit,
        }]],
      }]]);

      // Get invoice number - handle both single ID and array returns
      const actualId = Array.isArray(invoiceId) ? invoiceId[0] : invoiceId;
      const invoice = await executeKw('account.move', 'search_read', [
        [['id', '=', actualId]]
      ], { fields: ['name', 'amount_total'], limit: 1 });

      const invoiceNumber = invoice[0].name;
      const totalAmount = invoice[0].amount_total;

      logAction('create_invoice', {
        invoiceId,
        invoiceNumber,
        customer: customer_name,
        amount: totalAmount,
      }, 'SUCCESS');

      // Move approval file if provided
      if (approval_file && approval_file.includes('/Approved/')) {
        try {
          const doneFile = approval_file.replace('/Approved/', '/Done/');
          const doneDir = path.dirname(doneFile);
          if (!fs.existsSync(doneDir)) fs.mkdirSync(doneDir, { recursive: true });
          fs.renameSync(approval_file, doneFile);
        } catch (moveErr) {
          logAction('create_invoice', { error: moveErr.message }, 'WARN - Failed to move approval file');
        }
      }

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          invoiceId,
          invoiceNumber,
          totalAmount,
          message: `Invoice ${invoiceNumber} created for ${customer_name}`,
        })}],
      };
    } catch (error) {
      logAction('create_invoice', { customer_name, product_name }, `FAILED - ${error.message}`);
      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: false,
          error: error.message,
        })}],
      };
    }
  }
);

// Tool: mark_invoice_paid
server.tool(
  'mark_invoice_paid',
  {
    invoice_number: z.string().describe('Invoice number (e.g., INV/2026/00001)'),
    payment_amount: z.number().describe('Payment amount'),
    payment_date: z.string().optional().describe('Payment date (YYYY-MM-DD)'),
  },
  async ({ invoice_number, payment_amount, payment_date }) => {
    try {
      logAction('mark_invoice_paid', { invoice_number, payment_amount }, 'ATTEMPTING');

      // Find invoice
      const invoices = await executeKw('account.move', 'search_read', [
        [['name', '=', invoice_number], ['move_type', '=', 'out_invoice']]
      ], { fields: ['id', 'name', 'amount_total', 'payment_state', 'state'], limit: 1 });

      if (invoices.length === 0) {
        return {
          content: [{ type: 'text', text: JSON.stringify({
            success: false,
            error: `Invoice '${invoice_number}' not found`,
          })}],
        };
      }

      const invoice = invoices[0];

      if (invoice.payment_state === 'paid') {
        return {
          content: [{ type: 'text', text: JSON.stringify({
            success: false,
            error: `Invoice ${invoice_number} is already marked as paid`,
          })}],
        };
      }

      // Confirm invoice if still draft
      if (invoice.state === 'draft') {
        await executeKw('account.move', 'action_post', [[invoice.id]]);
      }

      // Register payment using the payment register wizard
      const paymentDate = payment_date || new Date().toISOString().split('T')[0];
      const paymentWizard = await executeKw('account.payment.register', 'create', [[{
        payment_date: paymentDate,
        amount: payment_amount,
      }]], { context: { active_model: 'account.move', active_ids: [invoice.id] } });

      await executeKw('account.payment.register', 'action_create_payments', [[paymentWizard]], {
        context: { active_model: 'account.move', active_ids: [invoice.id] },
      });

      logAction('mark_invoice_paid', {
        invoiceNumber: invoice_number,
        amount: payment_amount,
      }, 'SUCCESS');

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          invoiceNumber: invoice_number,
          message: `Invoice ${invoice_number} marked as paid`,
        })}],
      };
    } catch (error) {
      logAction('mark_invoice_paid', { invoice_number }, `FAILED - ${error.message}`);
      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: false,
          error: error.message,
        })}],
      };
    }
  }
);

// Tool: get_revenue
server.tool(
  'get_revenue',
  {
    start_date: z.string().describe('Start date (YYYY-MM-DD)'),
    end_date: z.string().describe('End date (YYYY-MM-DD)'),
  },
  async ({ start_date, end_date }) => {
    try {
      const invoices = await executeKw('account.move', 'search_read', [
        [
          ['invoice_date', '>=', start_date],
          ['invoice_date', '<=', end_date],
          ['move_type', '=', 'out_invoice'],
          ['state', '=', 'posted'],
        ]
      ], { fields: ['amount_total', 'payment_state'] });

      let totalRevenue = 0;
      let paidRevenue = 0;
      let unpaidRevenue = 0;

      invoices.forEach(inv => {
        totalRevenue += inv.amount_total;
        if (inv.payment_state === 'paid') {
          paidRevenue += inv.amount_total;
        } else {
          unpaidRevenue += inv.amount_total;
        }
      });

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          period: `${start_date} to ${end_date}`,
          totalRevenue,
          paidRevenue,
          unpaidRevenue,
          invoiceCount: invoices.length,
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

// Tool: list_customers
server.tool(
  'list_customers',
  {
    limit: z.number().optional().default(10).describe('Maximum number of customers to return'),
  },
  async ({ limit }) => {
    try {
      const customers = await executeKw('res.partner', 'search_read', [
        [['customer_rank', '>', 0]]
      ], {
        fields: ['name', 'email', 'phone'],
        limit,
      });

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          customers,
          count: customers.length,
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

// Tool: create_customer
server.tool(
  'create_customer',
  {
    name: z.string().describe('Customer name'),
    email: z.string().optional().describe('Customer email'),
    phone: z.string().optional().describe('Customer phone'),
  },
  async ({ name, email, phone }) => {
    try {
      const customerId = await executeKw('res.partner', 'create', [[{
        name,
        email: email || false,
        phone: phone || false,
        customer_rank: 1,
      }]]);

      logAction('create_customer', { customerId, name }, 'SUCCESS');

      return {
        content: [{ type: 'text', text: JSON.stringify({
          success: true,
          customerId,
          message: `Customer '${name}' created`,
        })}],
      };
    } catch (error) {
      logAction('create_customer', { name }, `FAILED - ${error.message}`);
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
  console.error('Initializing Odoo connection...');
  await initOdoo();

  console.error('Starting Odoo MCP Server...');
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Odoo MCP Server running');
}

main().catch(console.error);
