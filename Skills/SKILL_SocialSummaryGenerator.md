# Agent Skill: Social Media Summary Generator

## Skill Name
Social Summary Generator v1.0

## Purpose
Generate weekly summary of social media activity for CEO briefing.

## Trigger
- Part of weekly_audit.py (Sunday 11 PM)
- Can be called manually for monthly reports

## Process Flow

### Step 1: Collect Posted Content

Scan logs for past 7 days:
```
1. Read /Logs/linkedin_actions.log
2. Read /Logs/twitter_actions.log (or facebook_actions.log)
3. Extract all SUCCESS entries
4. Count posts by platform
```

### Step 2: Get Engagement Stats

Call MCP tools:
```
1. LinkedIn MCP: get_post_stats(days=7)
2. Twitter MCP: get_tweet_stats(count=10)
3. Aggregate metrics:
   - Total posts
   - Total likes/reactions
   - Total comments/replies
   - Total shares/retweets
```

### Step 3: Analyze Performance
```
Calculate:
- Posts per platform
- Avg engagement per post
- Best performing post (highest engagement)
- Posting consistency (did we hit 3x/week target?)
```

### Step 4: Generate Summary
Output format for CEO briefing:
```markdown
## Social Media Activity (Past 7 Days)

### Posts Published
- LinkedIn: 3 posts
- Twitter: 4 tweets (1 thread)
- **Total**: 7 pieces of content

### Engagement
- **Likes/Reactions**: 156 (avg 22/post)
- **Comments/Replies**: 31 (avg 4/post)
- **Shares/Retweets**: 12 (avg 2/post)

### Top Performer
**LinkedIn post** (Jan 28): "Business automation isn't optional..."
- 45 likes, 12 comments, 5 shares
- Engagement rate: 3.2%

### Consistency
✅ Hit 3x/week target
- Mon: LinkedIn post
- Wed: Twitter thread
- Fri: LinkedIn + Twitter

### Recommendations
- LinkedIn posts getting 2x engagement vs Twitter
- Consider increasing LinkedIn to 4x/week
- Friday posts perform best (end-of-week reflection)
```

### Step 5: Add to CEO Briefing

Append to briefing file:
```
/Briefings/YYYY-MM-DD_CEO_Briefing.md
```

## Data Sources
- /Logs/linkedin_actions.log
- /Logs/twitter_actions.log
- /Logs/facebook_actions.log
- LinkedIn MCP: get_post_stats
- Twitter MCP: get_tweet_stats

## Error Handling
- If MCP unavailable: Use log data only
- If logs missing: Note "No data available"
- If no posts this week: Flag as "No social activity"

## Version History
- v1.0: Initial social summary generation