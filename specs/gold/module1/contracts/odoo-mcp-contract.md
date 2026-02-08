# Odoo MCP Server API Contract

## Overview
This document defines the API contract for the Odoo MCP server that enables automated accounting operations through Odoo ERP.

## Base URL
The Odoo MCP server is accessed through Claude Code's MCP interface. The server is typically started with:
```bash
node /path/to/mcp-servers/odoo-mcp/index.js
```

## Authentication
Authentication is handled through environment variables:
- `ODOO_URL`: URL of the Odoo instance (default: http://localhost:8069)
- `ODOO_DB`: Database name (default: ai_employee_accounting)
- `ODOO_USERNAME`: Username for authentication (default: admin@example.com)
- `ODOO_PASSWORD`: Password for authentication (default: admin)

## Tools

### 1. create_invoice
**Description**: Creates an invoice in Odoo.

**Method**: Tool call through Claude Code MCP interface

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "customer_name": {
      "type": "string",
      "description": "Customer name"
    },
    "product_name": {
      "type": "string",
      "description": "Product/service name"
    },
    "quantity": {
      "type": "number",
      "description": "Quantity",
      "default": 1
    },
    "price_unit": {
      "type": "number",
      "description": "Unit price"
    },
    "approval_file": {
      "type": "string",
      "description": "Approval file path (if required)"
    }
  },
  "required": ["customer_name", "product_name", "price_unit"]
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
    "invoiceId": {
      "type": "string",
      "description": "Odoo-generated invoice ID"
    },
    "invoiceNumber": {
      "type": "string",
      "description": "Formatted invoice number"
    },
    "totalAmount": {
      "type": "number",
      "description": "Calculated total amount"
    },
    "message": {
      "type": "string",
      "description": "Success message"
    }
  },
  "required": ["success", "invoiceId", "invoiceNumber", "totalAmount", "message"]
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
- Finds customer by name in Odoo
- Returns error if customer not found
- Finds product by name in Odoo
- Returns error if product not found
- Creates invoice with specified details
- Returns invoice number and total amount
- Moves approval file to Done folder if provided
- Logs all actions with timestamps and status

### 2. mark_invoice_paid
**Description**: Marks an invoice as paid in Odoo.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "invoice_number": {
      "type": "string",
      "description": "Invoice number (e.g., INV/2026/00001)"
    },
    "payment_amount": {
      "type": "number",
      "description": "Payment amount"
    },
    "payment_date": {
      "type": "string",
      "description": "Payment date (YYYY-MM-DD)",
      "default": "current date"
    }
  },
  "required": ["invoice_number", "payment_amount"]
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
    "invoiceNumber": {
      "type": "string",
      "description": "Invoice number that was marked as paid"
    },
    "message": {
      "type": "string",
      "description": "Success message"
    }
  },
  "required": ["success", "invoiceNumber", "message"]
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
- Finds invoice by invoice number in Odoo
- Returns error if invoice not found
- Checks if invoice is already marked as paid
- Returns error if already paid
- Updates invoice payment status
- Logs all actions with timestamps and status

### 3. get_revenue
**Description**: Gets total revenue for a specified period.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "start_date": {
      "type": "string",
      "description": "Start date (YYYY-MM-DD)"
    },
    "end_date": {
      "type": "string",
      "description": "End date (YYYY-MM-DD)"
    }
  },
  "required": ["start_date", "end_date"]
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
    "period": {
      "type": "string",
      "description": "Description of the date range"
    },
    "totalRevenue": {
      "type": "number",
      "description": "Total revenue in the period"
    },
    "paidRevenue": {
      "type": "number",
      "description": "Paid revenue in the period"
    },
    "unpaidRevenue": {
      "type": "number",
      "description": "Unpaid revenue in the period"
    },
    "invoiceCount": {
      "type": "number",
      "description": "Number of invoices in the period"
    }
  },
  "required": ["success", "period", "totalRevenue", "paidRevenue", "unpaidRevenue", "invoiceCount"]
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

### 4. list_customers
**Description**: Gets a list of customers.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "limit": {
      "type": "number",
      "description": "Maximum number of customers to return",
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
    "customers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "email": {"type": "string"},
          "phone": {"type": "string"}
        },
        "required": ["name"]
      },
      "description": "List of customers"
    },
    "count": {
      "type": "number",
      "description": "Number of customers returned"
    }
  },
  "required": ["success", "customers", "count"]
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

### 5. create_customer
**Description**: Adds a new customer to Odoo.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Customer name"
    },
    "email": {
      "type": "string",
      "description": "Customer email"
    },
    "phone": {
      "type": "string",
      "description": "Customer phone"
    }
  },
  "required": ["name"]
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
    "customerId": {
      "type": "string",
      "description": "Odoo-generated customer ID"
    },
    "message": {
      "type": "string",
      "description": "Success message"
    }
  },
  "required": ["success", "customerId", "message"]
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
- `401`: Authentication failed - check credentials
- `403`: Insufficient permissions - check user role
- `500`: Internal server error - check Odoo server and logs
- `ConnectionError`: Unable to connect to Odoo server

## Security Considerations
- API credentials must be stored in environment variables
- All actions are logged for audit purposes
- Connection to Odoo server is secured with authentication
- Sensitive financial data is transmitted securely

## Performance Considerations
- XML-RPC calls may have latency depending on server load
- Connection pooling is used to optimize performance
- Server implements retry logic for transient failures