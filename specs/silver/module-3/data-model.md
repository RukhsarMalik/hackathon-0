# Data Model: Silver Module 3 — Plan Generation + Integration

## Entities

### Plan File (PLAN_{task_id}.md)

```yaml
# YAML Frontmatter
type: plan
source_task: "{original_task_filename}"
created: "{ISO timestamp}"
status: "in_progress"  # pending | in_progress | completed | failed
total_steps: 5
completed_steps: 0
```

```markdown
# Plan: {Task Title}

**Source**: {source_task}
**Created**: {timestamp}
**Status**: {status}

## Steps

- [ ] Step 1: {description}
- [ ] Step 2: {description}
- [ ] Step 3: {description}
- [ ] Step 4: {description}
- [ ] Step 5: {description}

## Progress Log

- [{timestamp}] Plan created with {n} steps
- [{timestamp}] Step 1 completed: {brief result}
```

### Complex Task File (trigger format)

```yaml
# YAML Frontmatter
type: complex_task
priority: medium
title: "{task title}"
created: "{ISO timestamp}"
```

```markdown
# {Task Title}

{Detailed description of what needs to be done}

## Requirements
- {requirement 1}
- {requirement 2}
- {requirement 3+}
```

## State Transitions

```
Complex Task Created → Orchestrator detects (type: complex_task)
  → SKILL_PlanGenerator invoked
  → PLAN_{id}.md created in Needs_Action/ (status: in_progress)
  → Steps executed sequentially
  → Each step: checkbox updated [ ] → [X]
  → All steps complete → status: completed → moved to Done/
  → Step failure → logged, status: failed if unrecoverable
```

## Relationships

- **Complex Task → Plan**: One-to-one. Each complex task generates exactly one plan.
- **Plan → Steps**: One-to-many. Plan contains ordered list of steps.
- **Plan → Dashboard**: Plan progress reflected in Dashboard activity log.

## File Naming Conventions

| Pattern | Purpose | Example |
|---------|---------|---------|
| PLAN_{id}.md | Generated plan | PLAN_research_competitors.md |
| SKILL_PlanGenerator.md | Skill instructions | (static, not generated) |
