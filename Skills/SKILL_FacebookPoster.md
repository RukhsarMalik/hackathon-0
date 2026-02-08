# Agent Skill: Facebook Poster

## Skill Name
Facebook Content Generator & Poster v1.0

## Purpose
Generate Facebook posts for the business Page, handle approval, and auto-post via MCP.

## Trigger
- Files in /Needs_Action/ with `type: facebook_post`
- Scheduled by facebook_watcher.py (3x per week)

## Process Flow

### Step 1: Analyze Content Type

**Short Update (< 500 chars)**:
- Single post
- Direct and engaging
- Include hashtag (max 3)

**Long Form (500+ chars)**:
- Full post (Facebook supports up to 63,206 characters)
- Use line breaks for readability
- Add a call-to-action at the end

### Step 2: Generate Post Content

**Tone Guidelines**:
- Casual but professional
- Use conversational language
- Can use emojis (2-3)
- NO corporate jargon
- Direct and engaging

**Topics by Day**:
- Monday: Quick win or tip
- Wednesday: Industry insight
- Friday: Behind-the-scenes or reflection

**Formatting Tips**:
- Use line breaks for readability
- Keep paragraphs short (2-3 sentences)
- Use emojis as bullet points if appropriate
- End with a question or call-to-action to drive engagement

### Step 3: Create Approval Request
```markdown
---
type: facebook_approval
platform: facebook
action: post_to_facebook
created: [timestamp]
status: awaiting_approval
character_count: [count]
---

## Proposed Facebook Post

[Generated post content here]

**Character count**: 450/63206

## Hashtags
#BusinessTips #Productivity #SmallBusiness

## Approval Instructions
- Move to /Approved/ to post
- Move to /Rejected/ to cancel
- Edit content directly if needed
```

### Step 4: Handle Approval (via SKILL_ApprovalHandler)

When approved:
````
1. Call Facebook MCP: post_to_facebook
2. Parameters:
   - message: [post text]
   - approval_file: [path]
3. Log result
4. Update Dashboard
````

## Quality Checklist
- [ ] Content is engaging and readable
- [ ] Clear value or insight
- [ ] Appropriate hashtags (1-3)
- [ ] No typos or errors
- [ ] On-brand tone
- [ ] Ends with engagement hook (question/CTA)

## Error Handling

**If post fails**:
- Facebook API error: Log, retry once after 5 min
- Rate limit: Queue for 1 hour later
- Auth error: Alert human, pause Facebook posting
- Token expired: Refresh Page Access Token

## Testing
- Test Case 1: 200 char post -> Posts as single post
- Test Case 2: 1000 char content -> Posts as full post
- Test Case 3: Post with image URL -> Posts with link preview

## Version History
- v1.0: Initial Facebook posting automation (migrated from Twitter)
