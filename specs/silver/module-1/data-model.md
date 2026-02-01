# Data Model: Silver Module 1

## Entities

### TaskFile (Needs_Action/*.md)

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| type | string | YAML frontmatter | Required. One of: `email`, `file_drop`, `linkedin_post` |
| priority | string | YAML frontmatter | Optional. One of: `high`, `medium`, `low` |
| status | string | YAML frontmatter | Required. One of: `pending`, `processing`, `completed` |
| from | string | YAML frontmatter | Email-type only |
| subject | string | YAML frontmatter | Email-type only |
| gmail_id | string | YAML frontmatter | Email-type only |
| original_name | string | YAML frontmatter | File-drop-type only |
| topic | string | YAML frontmatter | LinkedIn-type only |
| content | markdown | Body | Free-form task content |

**State transitions**: `pending` → `processing` (orchestrator picks up) → `completed` (moved to Done/)

### LinkedInPostRequest (Needs_Action/LINKEDIN_POST_*.md)

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| type | string | YAML frontmatter | Always `linkedin_post` |
| topic | string | YAML frontmatter | One of: `weekly_update`, `tip_of_day`, `success_story` |
| scheduled_date | ISO date | YAML frontmatter | Date the post was scheduled for |
| status | string | YAML frontmatter | `pending` |

### LinkedInPostReady (Pending_Approval/LINKEDIN_READY_*.md)

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| type | string | YAML frontmatter | Always `linkedin_post_ready` |
| topic | string | YAML frontmatter | Inherited from request |
| generated_date | ISO datetime | YAML frontmatter | When content was generated |
| word_count | int | YAML frontmatter | Post word count |
| hashtag_count | int | YAML frontmatter | Number of hashtags |
| status | string | YAML frontmatter | `awaiting_approval` |
| content | markdown | Body | Generated post content |

### PostHistory (Logs/linkedin_posts.json)

```json
[
  {
    "date": "2026-01-30",
    "type": "weekly_update",
    "file": "LINKEDIN_POST_20260130_weekly_update.md",
    "created_at": "2026-01-30T09:00:00"
  }
]
```

### PIDFile (.pids/*.pid)

Plain text file containing a single integer (process ID).

Files: `gmail.pid`, `filesystem.pid`, `linkedin.pid`, `orchestrator.pid`

### SkillMapping (orchestrator internal)

| Task Type | Skill File | Description |
|-----------|-----------|-------------|
| email | SKILL_EmailProcessor.md | Process email action files |
| file_drop | SKILL_FileProcessor.md | Process file drop action files |
| linkedin_post | SKILL_LinkedInPoster.md | Generate LinkedIn post content |

## Relationships

```
LinkedInWatcher --creates--> LinkedInPostRequest (in Needs_Action/)
Orchestrator --reads--> TaskFile (from Needs_Action/)
Orchestrator --reads--> SkillFile (from Needs_Action/SKILL_*.md)
Orchestrator --invokes--> Claude Code (via subprocess)
Claude Code --creates--> LinkedInPostReady (in Pending_Approval/)
Claude Code --moves--> TaskFile (to Done/)
HealthCheck --reads--> PIDFile, Dashboard.md, Needs_Action/
```
