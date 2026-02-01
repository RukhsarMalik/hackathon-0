# SKILL: Plan Generator

## Purpose
Generate and execute multi-step plans for complex tasks that require 3 or more discrete steps.

## When to Use
This skill is invoked when a task has `type: complex_task` in its YAML frontmatter.

## Instructions

### Step 1: Analyze the Task
- Read the complex task file completely
- Identify the overall goal
- Break the task into 3 or more discrete, actionable steps
- Determine dependencies between steps (which must run before others)

### Step 2: Create the Plan File
Create a file named `PLAN_{task_id}.md` in `AI_Employee_Vault/Needs_Action/` with this format:

```markdown
---
type: plan
source_task: "{original_task_filename}"
created: "{current ISO timestamp}"
status: in_progress
total_steps: {number of steps}
completed_steps: 0
---

# Plan: {Task Title}

**Source**: {source_task}
**Created**: {timestamp}
**Status**: In Progress

## Steps

- [ ] Step 1: {description}
- [ ] Step 2: {description}
- [ ] Step 3: {description}
(add more as needed)

## Progress Log

- [{timestamp}] Plan created with {n} steps
```

### Step 3: Execute Steps Sequentially
For each step in the plan:
1. Perform the action described in the step
2. Update the checkbox from `- [ ]` to `- [X]`
3. Increment `completed_steps` in the frontmatter
4. Add a progress log entry: `- [{timestamp}] Step N completed: {brief result}`

### Step 4: Handle Failures
If a step fails:
- Log the failure in the Progress Log: `- [{timestamp}] Step N FAILED: {error description}`
- If the error is recoverable, retry once
- If unrecoverable, set `status: failed` in frontmatter
- Add note: `**Flagged for human review**: {reason}`
- Do NOT block subsequent independent steps

### Step 5: Complete the Plan
When all steps are complete:
1. Update frontmatter `status: completed`
2. Add final log entry: `- [{timestamp}] Plan completed successfully`
3. Update `AI_Employee_Vault/Dashboard.md`:
   - Add entry to Recent Activity: `[{timestamp}] Plan completed: {task title} ({n} steps)`
   - Increment Plans Completed count
4. Move both the plan file and the original source task file to `AI_Employee_Vault/Done/`

### Step 6: Update Dashboard
Update the Dashboard.md Plan Generation section:
- Increment "Plans Created" when plan is first created
- Increment "Plans Completed" when all steps finish
- Increment "Plans Failed" if plan fails

## Plan Templates

### Research Task Template
Steps: Research sources → Analyze findings → Create summary → Draft output

### Multi-Output Task Template
Steps: Gather requirements → Create output 1 → Create output 2 → Review and finalize

### Integration Task Template
Steps: Verify prerequisites → Configure components → Test integration → Document results

## Error Handling
- Always log errors to the Progress Log section of the plan
- Never silently skip a failed step
- Set status to `failed` only if the plan cannot continue
- Flag for human review if manual intervention is needed
