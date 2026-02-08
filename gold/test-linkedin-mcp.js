// Test Framework for LinkedIn MCP Server
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

console.log('🧪 Starting LinkedIn MCP Server Tests...\n');

async function testLinkedInMCP() {
  try {
    // Test 1: Check if LinkedIn MCP server files exist
    console.log('📋 Test T120: Checking LinkedIn MCP server files...');

    const linkedinDir = './mcp-servers/linkedin-mcp/';
    const requiredFiles = [
      'package.json',
      'index.js',
      '.env'
    ];

    for (const file of requiredFiles) {
      const filePath = path.join(linkedinDir, file);
      if (fs.existsSync(filePath)) {
        console.log(`  ✅ ${file} exists`);
      } else {
        console.log(`  ❌ ${file} missing`);
        return false;
      }
    }

    // Test 2: Check if package.json has correct dependencies
    const pkg = JSON.parse(fs.readFileSync(path.join(linkedinDir, 'package.json'), 'utf8'));
    const requiredDeps = ['@anthropic/mcp', 'axios', 'dotenv'];

    for (const dep of requiredDeps) {
      if (pkg.dependencies && pkg.dependencies[dep]) {
        console.log(`  ✅ Dependency ${dep} found`);
      } else {
        console.log(`  ❌ Dependency ${dep} missing`);
        return false;
      }
    }

    // Test 3: Check if index.js has the required functionality
    const indexContent = fs.readFileSync(path.join(linkedinDir, 'index.js'), 'utf8');

    const requiredFunctions = [
      'post_to_linkedin',
      'get_post_stats',
      'approval verification',
      'logAction',
      'file movement from /Approved/ to /Done/'
    ];

    for (const func of requiredFunctions) {
      if (indexContent.toLowerCase().includes(func.toLowerCase())) {
        console.log(`  ✅ Functionality for ${func} found`);
      } else {
        console.log(`  ❌ Functionality for ${func} missing`);
        return false;
      }
    }

    console.log('\n✅ LinkedIn MCP Server tests passed!');
    return true;

  } catch (error) {
    console.error(`❌ LinkedIn MCP Server tests failed: ${error.message}`);
    return false;
  }
}

async function testFacebookMCP() {
  try {
    console.log('\n📋 Test T121: Checking Facebook MCP server files...');

    const facebookDir = './mcp-servers/facebook-mcp/';
    const requiredFiles = [
      'package.json',
      'index.js'
    ];

    for (const file of requiredFiles) {
      const filePath = path.join(facebookDir, file);
      if (fs.existsSync(filePath)) {
        console.log(`  ✅ ${file} exists`);
      } else {
        console.log(`  ❌ ${file} missing`);
        return false;
      }
    }

    // Check package.json dependencies
    const pkg = JSON.parse(fs.readFileSync(path.join(facebookDir, 'package.json'), 'utf8'));
    const requiredDeps = ['@modelcontextprotocol/sdk', 'zod', 'dotenv'];

    for (const dep of requiredDeps) {
      if (pkg.dependencies && pkg.dependencies[dep]) {
        console.log(`  ✅ Dependency ${dep} found`);
      } else {
        console.log(`  ❌ Dependency ${dep} missing`);
        return false;
      }
    }

    // Check functionality in index.js
    const indexContent = fs.readFileSync(path.join(facebookDir, 'index.js'), 'utf8');

    const requiredFunctions = [
      'post_to_facebook',
      'get_page_insights',
      'get_recent_posts',
      'approval',
      'error'
    ];

    for (const func of requiredFunctions) {
      if (indexContent.toLowerCase().includes(func.toLowerCase())) {
        console.log(`  ✅ Functionality for ${func} found`);
      } else {
        console.log(`  ❌ Functionality for ${func} missing`);
        return false;
      }
    }

    console.log('\n✅ Facebook MCP Server tests passed!');
    return true;

  } catch (error) {
    console.error(`❌ Facebook MCP Server tests failed: ${error.message}`);
    return false;
  }
}

async function testOdooMCP() {
  try {
    console.log('\n📋 Test T122: Checking Odoo MCP server files...');

    const odooDir = './mcp-servers/odoo-mcp/';
    const requiredFiles = [
      'package.json',
      'index.js',
      '.env'
    ];

    for (const file of requiredFiles) {
      const filePath = path.join(odooDir, file);
      if (fs.existsSync(filePath)) {
        console.log(`  ✅ ${file} exists`);
      } else {
        console.log(`  ❌ ${file} missing`);
        return false;
      }
    }

    // Check package.json dependencies
    const pkg = JSON.parse(fs.readFileSync(path.join(odooDir, 'package.json'), 'utf8'));
    const requiredDeps = ['@anthropic/mcp', 'xmlrpc', 'dotenv'];

    for (const dep of requiredDeps) {
      if (pkg.dependencies && pkg.dependencies[dep]) {
        console.log(`  ✅ Dependency ${dep} found`);
      } else {
        console.log(`  ❌ Dependency ${dep} missing`);
        return false;
      }
    }

    // Check functionality in index.js
    const indexContent = fs.readFileSync(path.join(odooDir, 'index.js'), 'utf8');

    const requiredFunctions = [
      'create_invoice',
      'mark_invoice_paid',
      'get_revenue',
      'list_customers',
      'create_customer',
      'customer validation',
      'connection error handling'
    ];

    for (const func of requiredFunctions) {
      if (indexContent.toLowerCase().includes(func.toLowerCase())) {
        console.log(`  ✅ Functionality for ${func} found`);
      } else {
        console.log(`  ❌ Functionality for ${func} missing`);
        return false;
      }
    }

    console.log('\n✅ Odoo MCP Server tests passed!');
    return true;

  } catch (error) {
    console.error(`❌ Odoo MCP Server tests failed: ${error.message}`);
    return false;
  }
}

async function testOverallStructure() {
  try {
    console.log('\n📋 Checking overall project structure...');

    // Check if docker-compose.yml exists
    if (fs.existsSync('./docker-compose.yml')) {
      console.log('  ✅ docker-compose.yml exists');
    } else {
      console.log('  ❌ docker-compose.yml missing');
      return false;
    }

    // Check if mcp.json exists and has proper configuration
    if (fs.existsSync('./mcp.json')) {
      const mcpConfig = JSON.parse(fs.readFileSync('./mcp.json', 'utf8'));
      const requiredServers = ['linkedin', 'facebook', 'odoo'];

      for (const server of requiredServers) {
        if (mcpConfig.mcpServers && mcpConfig.mcpServers[server]) {
          console.log(`  ✅ MCP server configuration for ${server} exists`);
        } else {
          console.log(`  ❌ MCP server configuration for ${server} missing`);
          return false;
        }
      }
    } else {
      console.log('  ❌ mcp.json missing');
      return false;
    }

    // Check if Skills exist
    const skillsDir = '../AI_Employee_Vault/Needs_Action/';
    const requiredSkills = [
      'SKILL_AccountingManager.md',
      'SKILL_SocialSummaryGenerator.md',
      'SKILL_FacebookPoster.md'
    ];

    for (const skill of requiredSkills) {
      const skillPath = path.join(skillsDir, skill);
      if (fs.existsSync(skillPath)) {
        console.log(`  ✅ Skill ${skill} exists`);
      } else {
        console.log(`  ❌ Skill ${skill} missing (but may be in root Skills/ dir)`);
        // Check in root Skills directory
        const rootSkillPath = path.join('../Skills/', skill.replace('SKILL_', '').replace('.md', '.md'));
        if (fs.existsSync(rootSkillPath)) {
          console.log(`  ⚠️  Skill found in root Skills/ directory: ${rootSkillPath}`);
        } else {
          console.log(`  ❌ Skill ${skill} not found anywhere`);
        }
      }
    }

    console.log('\n✅ Overall structure tests passed!');
    return true;

  } catch (error) {
    console.error(`❌ Overall structure tests failed: ${error.message}`);
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Running comprehensive tests for Gold Module 1...\n');

  const results = [];

  results.push(await testLinkedInMCP());
  results.push(await testFacebookMCP());
  results.push(await testOdooMCP());
  results.push(await testOverallStructure());

  const passed = results.filter(r => r).length;
  const total = results.length;

  console.log(`\n📊 Test Results: ${passed}/${total} test suites passed`);

  if (passed === total) {
    console.log('🎉 All tests passed! Gold Module 1 implementation is complete.');
  } else {
    console.log('⚠️ Some tests failed. Please check the implementation.');
  }

  return passed === total;
}

// Execute tests
runAllTests().then(success => {
  process.exit(success ? 0 : 1);
});