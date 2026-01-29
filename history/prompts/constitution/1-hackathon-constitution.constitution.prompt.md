---
id: 1
title: Hackathon Constitution
stage: constitution
date: 2026-01-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: sp.constitution
labels: [constitution, hackathon, ai-employee]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 -
---

## Prompt

```text
Personal AI Employee Hackathon 0: Building Autonomous FTEs (Full-Time Equivalent) in 2026

Tagline: Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This document serves as a comprehensive architectural blueprint and hackathon guide for building a "Digital FTE" (Full-Time Equivalent). It proposes a futuristic, local-first approach to automation where an AI agent—powered by Claude Code and Obsidian—proactively manages personal and business affairs 24/7. You can also think of it as a "Smart Consultant" (General Agents). The focus is on high-level reasoning, autonomy, and flexibility. Think of it as hiring a senior employee who figures out how to solve the problems.

This hackathon takes the concept of a "Personal AI Employee" to its logical extreme. It doesn't just wait for you to type; it proactively manages your "Personal Affairs" (Gmail, WhatsApp, Bank) and your "Business" (Social Media, Payments, Project Tasks) using Claude Code as the executor and Obsidian as the management dashboard.

All our faculty members and students will build this Personal AI Employee using Claude Code.

Standout Idea: The "Monday Morning CEO Briefing," where the AI autonomously audits bank transactions and tasks to report revenue and bottlenecks, transforms the AI from a chatbot into a proactive business partner.

Architecture & Tech Stack:

The proposed stack is robust, privacy-focused, and clever:

The Brain: Claude Code acts as the reasoning engine. We add the Ralph Wiggum Stop hook to let the agent continuously iterate until the assigned task is complete.

The Memory/GUI: Obsidian (local Markdown) is used as the dashboard, keeping data local and accessible.

The Senses (Watchers): Lightweight Python scripts monitor Gmail, WhatsApp, and filesystems to trigger the AI.

The Hands (MCP): Model Context Protocol (MCP) servers handle external actions like sending emails or clicking buttons.

This architecture solves the "lazy agent" problem by using "Watchers" to wake the agent up rather than waiting for user input and "Ralph Wiggum" (a Stop hook pattern) to keep it working until done.

This is an exceptional technical hackathon project. It moves beyond "prompt engineering" into "agent engineering." It provides a complete, viable path to building a functional autonomous agent using tools available in 2026 (or today).

[Rest of the hackathon requirements document...]
```

## Response snapshot

Created a comprehensive constitution file for the Personal AI Employee Hackathon project based on the provided requirements. The constitution includes seven core principles with detailed Bronze/Silver/Gold tier requirements:

1. Local-First Privacy and Data Sovereignty - Ensuring all data remains under user control
2. Human-in-the-Loop Safety and Approval Systems - Critical actions require human approval
3. Autonomous Operation and Continuous Monitoring - Continuous operation using Watcher scripts
4. Spec-Driven Development and Agent Engineering - Following SDD methodology
5. Security-First Design and Credential Management - Secure credential handling and audit logging
6. Ethical Automation and Human Accountability - Maintaining transparency and human oversight
7. Tiered Development Approach and Progressive Complexity - Structured progression from Bronze to Silver to Gold tiers

Added detailed requirements for each tier:
- Bronze Tier: Foundation requirements (Obsidian vault, basic Watcher, Agent Skills)
- Silver Tier: Functional Assistant requirements (Multiple Watchers, MCP server, social media)
- Gold Tier: Autonomous Employee requirements (Full integration, accounting, advanced features)

## Outcome

- ✅ Impact: Created foundational constitution for hackathon project with 7 core principles including tiered development approach
- 🧪 Tests: No tests created, as this is a documentation task
- 📁 Files: Updated 1 file (.specify/memory/constitution.md)
- 🔁 Next prompts: Ready for feature specification and planning
- 🧠 Reflection: Constitution provides clear governance framework for hackathon participants with Bronze/Silver/Gold tier structure

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): Standard constitution creation
- Next experiment (smallest change to try): Begin feature specification based on constitution