<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (added Bronze/Silver/Gold tier structure)
- Added principles: Tiered Development Approach with progressive complexity
- Templates requiring updates: ✅ plan-template.md, spec-template.md, tasks-template.md updated to reflect tiered approach
- Added sections: Bronze/Silver/Gold Tier Requirements, Progressive Development Path
- Follow-up TODOs: None
-->
# Personal AI Employee Hackathon Constitution

## Core Principles

### I. Local-First Privacy and Data Sovereignty
All personal and business data must remain under the user's direct control. Obsidian vault serves as the primary knowledge base stored locally. No sensitive data (emails, banking credentials, personal communications) may be transmitted to external services without explicit encryption and user approval. External APIs should be accessed through secure, local MCP servers rather than cloud-based intermediaries.

### II. Human-in-the-Loop Safety and Approval Systems
Critical actions requiring human judgment must never be performed autonomously. Payment processing, legal communications, emotionally sensitive responses, and irreversible actions require explicit human approval through the file-based approval system. The AI employee must create approval request files in /Pending_Approval/ and await human movement to /Approved/ before executing sensitive operations.

### III. Autonomous Operation and Continuous Monitoring
The AI employee must operate continuously using Watcher scripts that monitor external inputs (Gmail, WhatsApp, banking APIs) and trigger appropriate responses. The Ralph Wiggum loop pattern ensures persistent operation until multi-step tasks are complete. System uptime and reliability are paramount for effective 24/7 operation.

### IV. Spec-Driven Development and Agent Engineering
All AI employee functionality must be implemented through Spec-Driven Development methodology. Features begin with clear specifications in spec.md, followed by architectural planning in plan.md, and executable tasks in tasks.md. Claude Code serves as the primary reasoning engine, with all AI functionality implemented as Agent Skills for modularity and reusability.

### V. Security-First Design and Credential Management
Security is non-negotiable in autonomous systems. All credentials must be managed through secure environment variables or dedicated secrets managers, never stored in plain text or the Obsidian vault. All actions must be logged for audit purposes, and the system must implement proper authentication, authorization, and rate limiting. Development vs production environments must be clearly separated.

### VI. Ethical Automation and Human Accountability
The AI employee must operate transparently with clear audit trails and human oversight mechanisms. The system must respect user privacy, avoid making decisions in emotionally sensitive contexts, and maintain clear boundaries about what can be automated versus requiring human judgment. Users remain accountable for all actions taken by their AI employee.

### VII. Tiered Development Approach and Progressive Complexity
Development must follow a structured progression from Bronze (Foundation) to Silver (Functional Assistant) to Gold (Autonomous Employee) levels. Each tier builds upon the previous one, with clear deliverables, acceptance criteria, and complexity levels. This ensures manageable development pace and achievable milestones.

## Bronze Tier: Foundation Requirements

### Core Infrastructure
- Obsidian vault with Dashboard.md and Company_Handbook.md
- Claude Code successfully reading from and writing to the vault
- Basic folder structure: /Inbox, /Needs_Action, /Done
- One working Watcher script (Gmail OR file system monitoring)
- All AI functionality implemented as Agent Skills

### Minimum Viable Deliverable
- Basic file system operations using Claude Code
- Simple monitoring and file creation capabilities
- Initial integration with Obsidian as knowledge base
- Demonstration of basic automation workflow

## Silver Tier: Functional Assistant Requirements

### Enhanced Automation
- Two or more Watcher scripts (e.g., Gmail + WhatsApp + LinkedIn)
- Claude reasoning loop that creates Plan.md files
- One working MCP server for external action (e.g., sending emails)
- Human-in-the-loop approval workflow for sensitive actions
- Basic scheduling via cron or Task Scheduler
- Automatically post on LinkedIn about business to generate sales

### Intermediate Capabilities
- Cross-platform monitoring and response
- Automated decision-making with approval gates
- Integration with external services via MCP
- Social media automation capabilities

## Gold Tier: Autonomous Employee Requirements

### Advanced Integration
- Full cross-domain integration (Personal + Business)
- Accounting system integration with Odoo Community via MCP server
- Multiple MCP servers for different action types (Facebook, Instagram, Twitter)
- Weekly Business and Accounting Audit with CEO Briefing generation
- Ralph Wiggum loop for autonomous multi-step task completion
- Comprehensive audit logging and error recovery

### Production-Ready Features
- Multi-platform social media management
- Financial auditing and reporting
- Advanced error recovery and graceful degradation
- Self-monitoring and autonomous operation
- Business intelligence and proactive suggestions

## Security & Privacy Architecture

All implementations must follow strict security protocols regardless of tier:
- Never store credentials in plain text or commit them to version control
- Use environment variables and .env files (with .gitignore) for sensitive data
- Implement proper audit logging with timestamped records of all actions
- Apply rate limiting to prevent abuse and accidental spam
- Maintain separate development and production configurations
- Encrypt sensitive data at rest when possible
- Follow the principle of least privilege for all system permissions

## Autonomous Systems Governance

The AI employee operates as an autonomous system with the following governance requirements:
- Implement graceful degradation when external services are unavailable
- Use exponential backoff for retry logic on transient failures
- Maintain health monitoring through Watchdog processes that restart failed components
- Queue operations during downtime for processing when services are restored
- Provide clear visibility into system state through the Obsidian dashboard
- Enable immediate human intervention when needed
- Progressive monitoring and oversight based on tier level

## Development Workflow

All development follows the Spec-Driven Development lifecycle with tiered progression:
- Start with Bronze tier requirements as foundation
- Progress to Silver tier for enhanced functionality
- Advance to Gold tier for full autonomous capabilities
- Specifications (spec.md) define requirements and acceptance criteria per tier
- Architectural plans (plan.md) detail implementation approaches per tier
- Executable tasks (tasks.md) break work into testable units per tier
- Agent Skills encapsulate reusable functionality across tiers
- MCP servers provide secure interfaces to external systems with increasing complexity

## Ethics & Responsibility

The AI employee must operate ethically with increasing sophistication as tiers advance:
- Clear disclosure when AI is involved in communications
- Respect for recipient preferences regarding AI interaction
- Regular human oversight through scheduled reviews (daily, weekly, monthly)
- Transparency in decision-making processes
- Prevention of automated discrimination or bias
- Compliance with applicable laws and regulations in all jurisdictions
- Tier-appropriate level of autonomy with corresponding oversight

## Progressive Development Path

Teams must follow a structured progression approach:
- **Start with Bronze**: Establish foundational elements before advancing
- **Validate each tier**: Demonstrate complete functionality before moving forward
- **Build incrementally**: Each tier adds capabilities to previous foundation
- **Maintain quality**: Higher tiers require robust lower-tier implementations
- **Document progress**: Track advancement and lessons learned at each tier

## Governance

This constitution governs all aspects of the Personal AI Employee development and operation across all tiers. All implementations must comply with these principles. Tier advancement requires demonstration of previous tier completion. Amendments require documentation of the change rationale and impact assessment. All team members must review and acknowledge these principles before contributing to the project. Code reviews must verify constitutional compliance before merging.

**Version**: 1.1.0 | **Ratified**: 2026-01-28 | **Last Amended**: 2026-01-28
