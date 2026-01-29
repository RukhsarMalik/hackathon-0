# Data Model: Foundation Setup

**Feature**: 001-foundation-setup
**Date**: 2026-01-29

## Entities

### Task File

A markdown file representing a unit of work that flows through the vault lifecycle.

**Fields (YAML frontmatter, all optional)**:
| Field      | Type     | Description                          | Default       |
|------------|----------|--------------------------------------|---------------|
| type       | string   | Task category (e.g., "task", "email")| "task"        |
| priority   | string   | Urgency level: low, medium, high     | "medium"      |
| created    | ISO date | When the task was created            | file creation |
| status     | string   | Processing state                     | "pending"     |

**Body**: Free-form markdown. Action items use `- [ ]` checkbox syntax.

**Lifecycle**: `Inbox/` → `Needs_Action/` → `Done/`
**Error path**: `Needs_Action/` → `Logs/malformed/` (if unparseable)

---

### Dashboard (Dashboard.md)

Single file at vault root tracking system state.

**Frontmatter**:
| Field         | Type     | Description                    |
|---------------|----------|--------------------------------|
| last_updated  | ISO datetime | Last modification timestamp |

**Sections**:
| Section          | Content                                      |
|------------------|----------------------------------------------|
| System Status    | Operational state, active/completed counts   |
| Recent Activity  | List of last N processed tasks with timestamps|
| Pending Actions  | Items currently in Needs_Action/             |
| Quick Stats      | Aggregate counters (total, success rate, avg)|

---

### Company Handbook (Company_Handbook.md)

Single file at vault root defining AI behavior rules.

**Frontmatter**:
| Field    | Type     | Description          |
|----------|----------|----------------------|
| version  | string   | Handbook version     |
| created  | ISO date | Creation date        |

**Rule Categories** (7 required):
1. Core Principles
2. Communication Guidelines
3. Financial Rules
4. File Management
5. Privacy & Security
6. Work Hours
7. Error Handling

---

### Agent Skill (SKILLS.md)

Documentation file defining reusable AI capabilities.

**Sections per skill**:
| Section        | Description                                   |
|----------------|-----------------------------------------------|
| Skill Name     | Name and version                              |
| Purpose        | What the skill does                           |
| Trigger        | When/how the skill is invoked                 |
| Process Flow   | Step-by-step execution instructions           |
| Input Format   | Expected file structure                       |
| Output         | What the skill produces                       |
| Error Handling | How failures are managed                      |

## Relationships

```
Inbox/ ──(manual drop)──→ Needs_Action/ ──(process)──→ Done/
                                │                         │
                                └──(malformed)──→ Logs/malformed/
                                │
                                └──(updates)──→ Dashboard.md

Company_Handbook.md ──(rules referenced by)──→ Task Processing
SKILLS.md ──(instructions for)──→ Task Processing
```

## State Transitions

```
Task States:
  [created] → pending (in Needs_Action/)
  pending → completed (moved to Done/)
  pending → malformed (moved to Logs/malformed/)
  pending → needs_review (renamed to REVIEW_* in Needs_Action/)
```
