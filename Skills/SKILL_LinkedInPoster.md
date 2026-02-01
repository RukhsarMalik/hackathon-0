---
name: LinkedIn Poster v1.0
purpose: Generate LinkedIn post content for business promotion
trigger: LINKEDIN_POST_*.md action file in Needs_Action/
created: 2026-01-30
version: 1.0
---

# LinkedIn Poster Agent Skill

## Purpose
Generate engaging LinkedIn post content based on the requested post type. All generated content goes to Pending_Approval/ for human review before publishing.

## Trigger Conditions
- An action file with `type: linkedin_post` exists in Needs_Action/
- File follows naming convention: LINKEDIN_POST_*.md

## Post Types

### weekly_update (Monday)
**Purpose**: Share weekly business highlights and achievements
**Structure**:
1. **Hook** (1-2 lines): Start with an attention-grabbing statement about the week
2. **Context** (2-3 lines): What happened this week in the business
3. **Value** (3-4 lines): Key takeaways, lessons learned, or milestones reached
4. **CTA** (1-2 lines): Ask a question or invite engagement
5. **Hashtags** (3-5): Relevant industry and business hashtags

### tip_of_day (Wednesday)
**Purpose**: Share a practical business or industry tip
**Structure**:
1. **Hook** (1-2 lines): Bold statement or surprising fact
2. **Context** (1-2 lines): Why this tip matters
3. **Value** (3-5 lines): The actual tip with actionable steps
4. **CTA** (1-2 lines): Ask readers to share their own tips
5. **Hashtags** (3-5): Relevant hashtags

### success_story (Friday)
**Purpose**: Share a client success story or business win
**Structure**:
1. **Hook** (1-2 lines): Compelling result or transformation
2. **Context** (2-3 lines): The challenge or starting point
3. **Value** (3-4 lines): How the solution was implemented
4. **CTA** (1-2 lines): Invite similar conversations or inquiries
5. **Hashtags** (3-5): Relevant hashtags

## Quality Standards
- Posts should be 150-300 words
- Professional but authentic tone
- Include 1-2 relevant emojis per section (not excessive)
- No hard selling — focus on providing value
- Each post should educate, inspire, or entertain
- Use line breaks for readability

## Output Format

Create the output file in `Pending_Approval/` with this naming convention:
`LINKEDIN_READY_{date}_{topic}.md`

Output file must include:
```yaml
---
type: linkedin_post_ready
topic: [weekly_update|tip_of_day|success_story]
generated_date: [ISO datetime]
word_count: [number]
hashtag_count: [number]
status: awaiting_approval
---
```

Followed by the generated post content.

## Processing Steps
1. Read the LINKEDIN_POST_*.md action file
2. Determine post type from `topic` field
3. Generate content following the appropriate template above
4. Create LINKEDIN_READY_*.md in Pending_Approval/
5. Update Dashboard.md with activity
6. Move original action file to Done/
