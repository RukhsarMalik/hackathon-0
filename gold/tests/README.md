# AI Employee - Test Suite

## How to Test

Each test file tests ONE specific feature. Copy files into `AI_Employee_Vault/Needs_Action/` **one at a time** to see each feature working.

### Quick Start
```bash
# Make sure services are running
cd /mnt/d/hackathon-0/gold
bash start_all.sh

# Copy a test file (example: Test 01)
cp tests/TEST_01_simple_email.md AI_Employee_Vault/Needs_Action/EMAIL_test_simple_01.md

# Watch the orchestrator log
tail -f AI_Employee_Vault/Logs/orchestrator.log
```

### Test Order (Recommended)

| # | File | Feature Tested | Expected Result |
|---|------|---------------|-----------------|
| 01 | `TEST_01_simple_email.md` | Email Processing | Reply draft in Pending_Approval/ |
| 02 | `TEST_02_invoice_request.md` | Odoo Invoice Creation | Customer found + Invoice created in Odoo + Reply draft |
| 03 | `TEST_03_payment_received.md` | Odoo Payment Recording | Invoice marked paid in Odoo + Confirmation reply draft |
| 04 | `TEST_04_new_client.md` | Odoo Customer + Invoice | New customer created + Invoice created + Reply draft |
| 05 | `TEST_05_revenue_report.md` | Odoo Revenue Report | Revenue data fetched + Report reply draft |
| 06 | `TEST_06_linkedin_post.md` | LinkedIn Post Generation | Post content generated in Pending_Approval/ |
| 07 | `TEST_07_facebook_post.md` | Facebook Post Generation | Post content generated in Pending_Approval/ |

### Copy Commands (one at a time)
```bash
# Test 01 - Simple Email
cp tests/TEST_01_simple_email.md AI_Employee_Vault/Needs_Action/EMAIL_test_simple_01.md

# Test 02 - Invoice Request
cp tests/TEST_02_invoice_request.md AI_Employee_Vault/Needs_Action/EMAIL_test_invoice_02.md

# Test 03 - Payment Received
cp tests/TEST_03_payment_received.md AI_Employee_Vault/Needs_Action/EMAIL_test_payment_03.md

# Test 04 - New Client
cp tests/TEST_04_new_client.md AI_Employee_Vault/Needs_Action/EMAIL_test_newclient_04.md

# Test 05 - Revenue Report
cp tests/TEST_05_revenue_report.md AI_Employee_Vault/Needs_Action/EMAIL_test_revenue_05.md

# Test 06 - LinkedIn Post
cp tests/TEST_06_linkedin_post.md AI_Employee_Vault/Needs_Action/LINKEDIN_POST_test_06.md

# Test 07 - Facebook Post
cp tests/TEST_07_facebook_post.md AI_Employee_Vault/Needs_Action/FACEBOOK_POST_test_07.md
```

### After Each Test - Verify
```bash
# Check what moved to Done/
ls AI_Employee_Vault/Done/ | tail -5

# Check drafts awaiting approval
ls AI_Employee_Vault/Pending_Approval/

# Check Odoo logs (for tests 02-05)
tail -5 AI_Employee_Vault/Logs/odoo_actions.log

# Check Dashboard
cat AI_Employee_Vault/Dashboard.md | head -20
```

### Clean Between Tests
```bash
# Move processed files out of the way
mv AI_Employee_Vault/Pending_Approval/APPROVAL_* AI_Employee_Vault/Done/ 2>/dev/null
```
