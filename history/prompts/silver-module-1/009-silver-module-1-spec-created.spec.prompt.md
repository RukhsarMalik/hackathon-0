---
id: 9
title: Silver Module 1 Spec Created
stage: spec
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: silver-module-1
branch: silver-module-1
user: unknown
command: manual
labels:
  - specification
  - silver-tier
  - orchestrator
  - linkedin-automation
links:
  spec: specs/silver/module-1/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/silver/module-1/spec.md
  - specs/silver/module-1/checklists/requirements.md
tests: []
---

# Silver Module 1 Spec Created

## Prompt Text
```
# Silver Module 1: Orchestrator + LinkedIn Automation

## Overview
- **Module**: Automated Processing + Social Media
- **Purpose**: Remove manual triggers + add business promotion
- **Time**: 8-10 hours
- **Dependencies**: Bronze tier complete

## Scope - ALL INCLUDED:
- ✅ Orchestrator that auto-processes tasks
- ✅ LinkedIn watcher for scheduled posting
- ✅ LinkedIn auto-post content generation
- ✅ Health monitoring script
- ✅ Startup script for all services
- ✅ Scheduled posting capability

## NOT INCLUDED:
- ❌ Multiple social platforms (Gold tier)
- ❌ Advanced analytics
- ❌ A/B testing posts
- ❌ Paid promotion management

## User Stories

### US-1: Create Orchestrator Script
**As a** user
**I want** automatic task processing
**So that** I don't need to manually trigger Claude Code

**Requirements:**
- Watch /Needs_Action/ folder for new .md files
- Debounce (wait 10 seconds after last file)
- Auto-trigger Claude Code with appropriate prompt
- Log all processing attempts
- Handle errors without stopping
- Cooldown period (30 seconds between runs)

**File**: orchestrator.py
```pythonorchestrator.py
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandlerConfiguration
VAULT_PATH = Path.home() / "AI_Employee_Vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
LOGS = VAULT_PATH / "Logs"Setup logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler(LOGS / "orchestrator.log"),
logging.StreamHandler()
]
)
logger = logging.getLogger(name)class TaskOrchestrator(FileSystemEventHandler):
def init(self):
self.processing = False
self.last_event_time = None
self.debounce_seconds = 10def on_created(self, event):
    if event.is_directory or not event.src_path.endswith('.md'):
        return    # Ignore SKILL files
    if 'SKILL' in event.src_path:
        return    self.last_event_time = time.time()
    logger.info(f"New task detected: {Path(event.src_path).name}")    # Wait for debounce period
    time.sleep(self.debounce_seconds)    # Check if more files arrived during debounce
    if time.time() - self.last_event_time < self.debounce_seconds:
        logger.info("More files arriving, extending debounce...")
        return    # Process tasks
    self.process_tasks()def process_tasks(self):
    if self.processing:
        logger.info("Already processing, skipping...")
        return    self.processing = True
    logger.info("=" * 60)
    logger.info(f"PROCESSING CYCLE STARTED - {datetime.now()}")
    logger.info("=" * 60)    try:
        # Count pending tasks
        task_files = list(NEEDS_ACTION.glob("*.md"))
        # Exclude SKILL files
        task_files = [f for f in task_files if 'SKILL' not in f.name]        if not task_files:
            logger.info("No tasks to process")
            return        logger.info(f"Found {len(task_files)} task(s) to process")        # Trigger Claude Code
        prompt = """
Process all tasks in the Needs_Action folder following this workflow:
Scan Tasks: List all .md files (excluding SKILL files)

Read Each Task:

Extract type from frontmatter
Identify priority level
Check task dependencies



Follow Appropriate SKILL:

file_drop → SKILL_FileProcessor.md
email → SKILL_EmailProcessor.md
linkedin_post → SKILL_LinkedInPoster.md
Custom types → Create new skill if needed



Task Complexity Check:

Simple task (1-2 steps) → Execute directly
Complex task (3+ steps) → Create Plan.md in /Plans/ folder
Sensitive action → Create approval request in /Pending_Approval/



Execute or Request Approval:

Non-sensitive: Complete task, move to /Done/
Sensitive: Create approval file, wait for human



Update Dashboard:

Log activity with timestamp
Update task counts
Note any pending approvals



Clean Up:

Move processed tasks to /Done/
Archive old logs if needed


Work systematically and provide a summary at the end.
"""        result = subprocess.run(
            ['claude', 'code', prompt],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=str(VAULT_PATH)
        )        if result.returncode == 0:
            logger.info("✓ Tasks processed successfully")
            # Log first 300 chars of output
            output_preview = result.stdout[:300]
            logger.info(f"Claude output: {output_preview}...")
        else:
            logger.error(f"✗ Claude Code error (exit code {result.returncode})")
            logger.error(f"Error: {result.stderr[:500]}")    except subprocess.TimeoutExpired:
        logger.error("✗ Claude Code timed out (10 minutes)")
    except FileNotFoundError:
        logger.error("✗ Claude Code not found - is it installed?")
        logger.error("Install: npm install -g @anthropic/claude-code")
    except Exception as e:
        logger.error(f"✗ Unexpected error: {type(e).__name__}: {e}")
    finally:
        self.processing = False
        logger.info("=" * 60)
        logger.info(f"PROCESSING CYCLE COMPLETE - {datetime.now()}")
        logger.info("=" * 60)        # Cooldown period
        logger.info("Cooldown: 30 seconds...")
        time.sleep(30)def main():
logger.info("=" * 60)
logger.info("AI EMPLOYEE ORCHESTRATOR v1.0")
logger.info("=" * 60)
logger.info(f"Vault path: {VAULT_PATH}")
logger.info(f"Watching: {NEEDS_ACTION}")
logger.info(f"Debounce: {10} seconds")
logger.info(f"Cooldown: {30} seconds")
logger.info("=" * 60)# Setup file system observer
event_handler = TaskOrchestrator()
observer = Observer()
observer.schedule(event_handler, str(NEEDS_ACTION), recursive=False)
observer.start()logger.info("✓ Orchestrator active - waiting for tasks...")
logger.info("Press Ctrl+C to stop")try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("\nShutting down orchestrator...")
    observer.stop()observer.join()
logger.info("Orchestrator stopped.")if name == "main":
main()

**Acceptance Criteria:**
- ✅ Detects new tasks within 10 seconds
- ✅ Triggers Claude Code automatically
- ✅ Logs all processing attempts
- ✅ Handles errors without crashing
- ✅ Cooldown prevents rapid re-processing
- ✅ Works with all Bronze watchers

---

### US-2: LinkedIn Watcher with Scheduled Posting
**As a** business owner
**I want** automatic LinkedIn posts about my business
**So that** I maintain social presence without manual work

**Requirements:**
- Schedule posts (Monday, Wednesday, Friday)
- Generate business-relevant content
- Track post history to avoid duplicates
- Create post requests for Claude to handle
- Log all scheduled activities

**File**: watchers/linkedin_watcher.py
```pythonwatchers/linkedin_watcher.py
import time
import logging
from pathlib import Path
from datetime import datetime, timedeltaVAULT_PATH = Path.home() / "AI_Employee_Vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
LOGS = VAULT_PATH / "Logs"
POSTED_HISTORY = LOGS / "linkedin_posted.txt"logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler(LOGS / "linkedin.log"),
logging.StreamHandler()
]
)
logger = logging.getLogger(name)Posting schedule
POST_SCHEDULE = {
'monday': {
'time': '09:00',
'topic': 'weekly_update',
'description': 'Share weekly accomplishments or goals'
},
'wednesday': {
'time': '14:00',
'topic': 'tip_of_day',
'description': 'Share helpful industry tip or advice'
},
'friday': {
'time': '10:00',
'topic': 'success_story',
'description': 'Share client success or case study'
}
}def should_post_today():
"""Check if we should create a post request today"""
today = datetime.now().strftime('%A').lower()if today not in POST_SCHEDULE:
    return False, Noneschedule = POST_SCHEDULE[today]
target_time = datetime.strptime(schedule['time'], '%H:%M').time()
current_time = datetime.now().time()# Calculate time difference in seconds
time_diff = abs(
    (datetime.combine(datetime.today(), current_time) -
     datetime.combine(datetime.today(), target_time)).total_seconds()
)# Post if within 1 hour window of scheduled time
if time_diff > 3600:  # More than 1 hour away
    return False, None# Check if already posted today
if POSTED_HISTORY.exists():
    lines = POSTED_HISTORY.read_text().strip().split('\n')
    if lines and lines[-1]:
        last_post_date_str = lines[-1].split('|')[0]
        try:
            last_post_date = datetime.fromisoformat(last_post_date_str).date()
            if last_post_date == datetime.now().date():
                logger.info(f"Already posted today ({today})")
                return False, None
        except:
            passreturn True, scheduledef create_post_request(schedule):
"""Create a LinkedIn post request file for Claude to process"""
topic = schedule['topic']
description = schedule['description']content = f"""---
type: linkedin_post
topic: {topic}
scheduled_for: {datetime.now().isoformat()}
status: pending
auto_post: true
priority: mediumLinkedIn Post RequestTopic: {topic.replace('_', ' ').title()}
Description: {description}Instructions for ClaudeUse the SKILL_LinkedInPoster.md skill to generate this post.Content Requirements:

Research Context:

Review Company_Handbook.md for business description
Check /Done/ folder for recent accomplishments
Look for relevant achievements this week



Post Structure:

Opening hook (1 compelling sentence)
Main content (3-4 sentences with value)
Call-to-action (1 sentence ending with question)
Hashtags (3-5 relevant tags)



Tone Guidelines:

Professional but approachable
Enthusiastic about the topic
Value-focused (help audience, not just promote)
Include 1-2 emojis naturally



Length: 150-200 words total
Topic-Specific Guidance:If weekly_update:

Highlight 1-2 specific accomplishments
Show progress or growth
Thank team/clients if relevant
If tip_of_day:

Share actionable advice
Back it with experience or data
Make it immediately useful
If success_story:

Tell a brief client story (anonymize if needed)
Show problem → solution → result
Emphasize customer value
Output Format:
After generating content, create approval file:

Location: /Pending_Approval/LINKEDIN_POST_[date].md
Include: Generated post text
Wait for: Human approval before posting
Example Structure:
[Hook: Surprising insight or accomplishment] 🚀

[Context: What we did and why it matters]

[Value: What others can learn from this]

[CTA: Question to engage audience] 👇

#RelevantTag #IndustryTag #BusinessTag"""filename = NEEDS_ACTION / f"LINKEDIN_POST_{topic}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
filename.write_text(content)
logger.info(f"✓ Created LinkedIn post request: {topic}")# Log to history
with open(POSTED_HISTORY, 'a') as f:
    f.write(f"{datetime.now().isoformat()}|{topic}|requested\n")return filenamedef main():
logger.info("=" * 60)
logger.info("LinkedIn Watcher Started")
logger.info("=" * 60)
logger.info("Post Schedule:")
for day, schedule in POST_SCHEDULE.items():
logger.info(f"  {day.title()}: {schedule['time']} - {schedule['topic']}")
logger.info("=" * 60)# Ensure history file exists
if not POSTED_HISTORY.exists():
    POSTED_HISTORY.touch()# Check every 10 minutes
CHECK_INTERVAL = 600try:
    while True:
        should_post, schedule = should_post_today()        if should_post:
            logger.info(f"⏰ Time to post! Creating request for: {schedule['topic']}")
            create_post_request(schedule)
            logger.info("✓ Post request created - waiting for orchestrator to process")            # Sleep longer after creating post to avoid duplicates
            time.sleep(3600)  # Sleep 1 hour
        else:
            current_day = datetime.now().strftime('%A')
            current_time = datetime.now().strftime('%H:%M')
            logger.info(f"⏳ No post needed now ({current_day} {current_time})")        time.sleep(CHECK_INTERVAL)except KeyboardInterrupt:
    logger.info("\nShutting down LinkedIn watcher...")if name == "main":
main()

**Acceptance Criteria:**
- ✅ Runs continuously without crashes
- ✅ Creates post requests at scheduled times
- ✅ Tracks history to avoid duplicates
- ✅ Logs all activities clearly
- ✅ Integrates with orchestrator

---

### US-3: LinkedIn Poster Agent Skill
**As a** AI Employee
**I want** instructions for generating LinkedIn posts
**So that** I can create engaging business content

**File**: AI_Employee_Vault/Needs_Action/SKILL_LinkedInPoster.md
```markdownAgent Skill: LinkedIn Post GeneratorSkill Name
LinkedIn Post Generator v1.0Purpose
Generate engaging, business-relevant LinkedIn posts that maintain consistent brand voice and drive audience engagement.Trigger

Files in /Needs_Action/ with type: linkedin_post
Auto-triggered by linkedin_watcher.py on schedule
Prerequisites

Company_Handbook.md exists (for business context)
Recent activities in /Done/ folder
Understanding of target audience
Process FlowStep 1: Gather Context
1. Read Company_Handbook.md
   - Extract business description
   - Note target audience
   - Identify key value propositions

2. Scan /Done/ folder (past 7 days)
   - Look for completed projects
   - Note client interactions
   - Find measurable achievements

3. Review topic from request file
   - weekly_update → Find accomplishments
   - tip_of_day → Identify actionable advice
   - success_story → Look for client winsStep 2: Generate ContentTemplate Structure:
[HOOK] - One compelling sentence with emoji
↓
[CONTEXT] - 2-3 sentences explaining what/why
↓
[VALUE] - 1-2 sentences on audience benefit
↓
[CTA] - Engaging question for comments
↓
[HASHTAGS] - 3-5 relevant tagsContent Rules:

Total length: 150-200 words
Paragraphs: 1-2 sentences each
Emojis: 1-2 (naturally placed)
Tone: Professional + enthusiastic
Focus: Value to audience (not just promotion)
Step 3: Topic-Specific GenerationFor weekly_update:
markdownHook: Share specific metric or achievement
Context: What was accomplished and by whom
Value: What this means for clients/industry
CTA: Ask about their week's wins
Hashtags: #BusinessGrowth #MondayMotivation #[Industry]For tip_of_day:
markdownHook: Counter-intuitive insight or common mistake
Context: Explain the tip with example
Value: How to implement immediately
CTA: Ask for their experience with this
Hashtags: #ProTip #BusinessAdvice #[Skill]For success_story:
markdownHook: Client's challenge in one sentence
Context: Your solution approach
Value: Results achieved (numbers if possible)
CTA: Ask if they face similar challenges
Hashtags: #CaseStudy #ClientSuccess #[Industry]Step 4: Create Approval RequestFile Location: /Pending_Approval/LINKEDIN_POST_[date].mdApproval File Format:
markdown---
type: linkedin_approval
platform: linkedin
action: post_content
created: [ISO timestamp]
status: awaiting_approval
priority: medium
---

## Proposed LinkedIn Post

[Generated post content here - exactly as it will appear]

## Post Metadata
- **Topic**: [weekly_update/tip_of_day/success_story]
- **Word Count**: [count]
- **Hashtags**: [list]
- **Emojis**: [list]

## Approval Instructions

**To Approve:**
1. Review post content above
2. Make any edits directly in this file if needed
3. Move this file to `/Approved/` folder
4. Post will be published via MCP (Module 2)

**To Reject:**
1. Move this file to `/Rejected/` folder
2. Add rejection reason in comments below

**To Request Changes:**
1. Add specific feedback below
2. Move to `/Needs_Action/` with prefix REVISE_
3. AI will regenerate with your feedback

## Quality Checklist
- [ ] Engaging hook that stops scrolling
- [ ] Clear value proposition for audience
- [ ] Professional but approachable tone
- [ ] Strong call-to-action
- [ ] Appropriate hashtags
- [ ] No typos or errors
- [ ] Aligns with brand voiceStep 5: Update DashboardAdd entry to Dashboard.md:
markdown## Recent Activity
- [TIMESTAMP] LinkedIn post generated - Topic: [topic] - Status: Awaiting approvalMove original request file to /Done/Example OutputsExample 1: Weekly Update
Proud to share we helped 5 new clients automate their workflows this week! 🚀

Each is saving an average of 12 hours per week on repetitive tasks. That's 60 hours returned to focus on growth, creativity, and what they do best.

Automation isn't about replacing people—it's about amplifying human potential. When the robots handle the boring stuff, humans get to do the brilliant stuff.

What's one task you wish took zero time? Drop it in the comments! 👇

#Automation #SmallBusiness #Productivity #BusinessGrowth #AIExample 2: Tip of Day
Stop checking email first thing in the morning. ☕

Here's why: Your morning energy is your most valuable asset. Spending it on reactive tasks (email) instead of proactive work (strategy, creation) is like using premium fuel for idling.

Try this instead: First 90 minutes = deep work only. Email after 10am. Watch your productivity double.

Do you protect your morning energy? What's your routine? 👇

#ProductivityTip #TimeManagement #BusinessAdvice #WorkSmart #DeepWorkExample 3: Success Story
A client came to us drowning in spreadsheets—tracking 200+ projects manually. 😰

We built them a simple automation that syncs data from 3 different tools into one dashboard. Setup took 2 days.

Result: 15 hours saved per week + zero human errors + real-time visibility for the whole team.

The best part? Their PM said, "I actually have time to think now."

Are you spending time ON your business or IN your business? 🤔

#CaseStudy #ProcessAutomation #ClientSuccess #BusinessEfficiency #ProjectManagementError HandlingIf Company_Handbook.md missing:
- Create generic post acknowledging the work done
- Flag for human to add business context later
- Note in approval file: "Generic content - needs personalization"If no recent Done/ activities:
- Focus on evergreen industry insight
- Share personal reflection on business journey
- Use theoretical example or case studyIf topic unclear:
- Default to "business update" theme
- Include note in approval requesting topic clarification
- Continue with best judgmentQuality StandardsMust Have:

✅ Clear value for reader (not just self-promotion)
✅ Conversational tone (avoid corporate speak)
✅ Specific examples or numbers
✅ Engaging question for comments
Must Avoid:

❌ Jargon or technical terms (unless B2B tech)
❌ All caps or excessive punctuation
❌ More than 2 emojis
❌ Controversial topics (politics, religion)
❌ Negative or complaint-focused content
❌ Overly salesy language
TestingTest Case 1: Weekly Update

Input: Monday, recent client project completed
Expected: Post highlighting project outcome with metrics
Validation: Positive, specific, includes CTA
Test Case 2: Tip with No Recent Work

Input: Wednesday, /Done/ folder empty
Expected: Evergreen industry advice post
Validation: Still valuable, well-structured
Test Case 3: Success Story

Input: Friday, multiple Done/ items
Expected: Best/most impactful story selected
Validation: Clear problem-solution-result flow
Version History

v1.0 (2026-01-30): Initial skill creation


**Acceptance Criteria:**
- ✅ Skill clearly documented
- ✅ Claude can follow instructions
- ✅ Generates quality post content
- ✅ Creates proper approval files
- ✅ Handles edge cases gracefully

---

### US-4: System Startup Script
**As a** user
**I want** one command to start all services
**So that** I don't manually start each watcher

**File**: start_system.sh (Mac/Linux)
```bash#!/bin/bashstart_system.sh - AI Employee System Launcherecho "=========================================="
echo "   AI EMPLOYEE SYSTEM STARTUP v1.0"
echo "=========================================="
echo ""Change to script directory
cd "$(dirname "$0")"Check prerequisites
echo "Checking prerequisites..."Check Python
if ! command -v python3 &> /dev/null; then
echo "❌ Python 3 not found"
exit 1
fi
echo "✓ Python 3: $(python3 --version)"Check Claude Code
if ! command -v claude &> /dev/null; then
echo "❌ Claude Code not installed"
echo "Install: npm install -g @anthropic/claude-code"
exit 1
fi
echo "✓ Claude Code: $(claude --version)"Check vault exists
VAULT_PATH="$HOME/AI_Employee_Vault"
if [ ! -d "$VAULT_PATH" ]; then
echo "❌ Vault not found at: $VAULT_PATH"
exit 1
fi
echo "✓ Vault found: $VAULT_PATH"echo ""
echo "=========================================="
echo "Starting services..."
echo "=========================================="Create PIDs directory
mkdir -p .pidsStart Gmail Watcher
echo "Starting Gmail Watcher..."
python3 watchers/gmail_watcher.py > /dev/null 2>&1 &
GMAIL_PID=$!
echo $GMAIL_PID > .pids/gmail.pid
echo "  └─ PID: $GMAIL_PID"sleep 1Start File System Watcher
echo "Starting File System Watcher..."
python3 watchers/filesystem_watcher.py > /dev/null 2>&1 &
FILE_PID=$!
echo $FILE_PID > .pids/filesystem.pid
echo "  └─ PID: $FILE_PID"sleep 1Start LinkedIn Watcher
echo "Starting LinkedIn Watcher..."
python3 watchers/linkedin_watcher.py > /dev/null 2>&1 &
LINKEDIN_PID=$!
echo $LINKEDIN_PID > .pids/linkedin.pid
echo "  └─ PID: $LINKEDIN_PID"sleep 2echo ""
echo "=========================================="
echo "✓ All watchers started successfully"
echo "=========================================="
echo ""
echo "Starting Orchestrator (foreground)..."
echo "Press Ctrl+C to stop all services"
echo "=========================================="
echo ""Trap Ctrl+C to kill all background processes
trap "echo ''; echo 'Stopping all services...'; kill $GMAIL_PID $FILE_PID $LINKEDIN_PID 2>/dev/null; rm -rf .pids; echo '✓ All services stopped'; exit" INT TERMStart orchestrator in foreground
python3 orchestrator.pyCleanup on exit
kill $GMAIL_PID $FILE_PID $LINKEDIN_PID 2>/dev/null
rm -rf .pids
echo "✓ All services stopped"

**File**: start_system.ps1 (Windows)
```powershellstart_system.ps1 - AI Employee System LauncherWrite-Host "=========================================="
Write-Host "   AI EMPLOYEE SYSTEM STARTUP v1.0"
Write-Host "=========================================="
Write-Host ""Check prerequisites
Write-Host "Checking prerequisites..."Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found"
    exit 1
}
Write-Host "✓ Python: ((
(python.Version)"
Check Claude Code
$claude = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claude) {
Write-Error "Claude Code not installed"
Write-Host "Install: npm install -g @anthropic/claude-code"
exit 1
}
Write-Host "✓ Claude Code installed"Check vault
vaultPath="vaultPath = "
vaultPath="env
:USERPROFILE\AI_Employee_Vault"
if (-not (Test-Path $vaultPath)) {
Write-Error "Vault not found at: $vaultPath"
exit 1
}
Write-Host "✓ Vault found: $vaultPath"Write-Host ""
Write-Host "=========================================="
Write-Host "Starting services..."
Write-Host "=========================================="Start watchers in background
Write-Host "Starting Gmail Watcher..."
Start-Process python -ArgumentList "watchers\gmail_watcher.py" -WindowStyle HiddenWrite-Host "Starting File System Watcher..."
Start-Process python -ArgumentList "watchers\filesystem_watcher.py" -WindowStyle HiddenWrite-Host "Starting LinkedIn Watcher..."
Start-Process python -ArgumentList "watchers\linkedin_watcher.py" -WindowStyle HiddenStart-Sleep -Seconds 3Write-Host ""
Write-Host "=========================================="
Write-Host "✓ All watchers started"
Write-Host "=========================================="
Write-Host ""
Write-Host "Starting Orchestrator..."
Write-Host "Press Ctrl+C to stop"
Write-Host "=========================================="
Write-Host ""Start orchestrator in foreground
python orchestrator.py

**Make executable:**
```bashchmod +x start_system.sh

**Acceptance Criteria:**
- ✅ Single command starts all services
- ✅ Prerequisite checks before starting
- ✅ Clear status messages
- ✅ Graceful shutdown on Ctrl+C
- ✅ Works on target OS

---

### US-5: Health Monitoring
**As a** system administrator
**I want** health checks on all components
**So that** I know when something fails

**File**: health_check.py
```pythonhealth_check.py
import psutil
import logging
from pathlib import Path
from datetime import datetime, timedeltaVAULT_PATH = Path.home() / "AI_Employee_Vault"
LOGS = VAULT_PATH / "Logs"logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler(LOGS / "health.log"),
logging.StreamHandler()
]
)
logger = logging.getLogger(name)def check_processes():
"""Check if all required processes are running"""
required = {
'gmail_watcher.py': False,
'filesystem_watcher.py': False,
'linkedin_watcher.py': False,
'orchestrator.py': False
}for proc in psutil.process_iter(['cmdline']):
    try:
        cmdline = ' '.join(proc.info['cmdline'] or [])
        for script in required.keys():
            if script in cmdline:
                required[script] = True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        passall_running = all(required.values())logger.info("Process Status:")
for script, running in required.items():
    status = "✓" if running else "✗"
    logger.info(f"  {status} {script}")return all_runningdef check_dashboard_activity():
"""Check if Dashboard was updated recently"""
dashboard = VAULT_PATH / "Dashboard.md"if not dashboard.exists():
    logger.error("✗ Dashboard.md not found!")
    return Falsemtime = datetime.fromtimestamp(dashboard.stat().st_mtime)
age = datetime.now() - mtimeif age > timedelta(hours=24):
    logger.warning(f"⚠ Dashboard not updated in {age.total_seconds()/3600:.1f} hours")
    return False
else:
    logger.info(f"✓ Dashboard updated {age.total_seconds()/60:.0f} min ago")
    return Truedef check_pending_tasks():
"""Check for stuck tasks"""
needs_action = VAULT_PATH / "Needs_Action"
tasks = [f for f in needs_action.glob("*.md") if 'SKILL' not in f.name]old_tasks = []
for task in tasks:
    age = datetime.now() - datetime.fromtimestamp(task.stat().st_mtime)
    if age > timedelta(hours=2):
        old_tasks.append((task.name, age))if old_tasks:
    logger.warning(f"⚠ {len(old_tasks)} task(s) pending > 2 hours:")
    for name, age in old_tasks:
        logger.warning(f"    - {name} ({age.total_seconds()/3600:.1f}h old)")
    return False
else:
    logger.info(f"✓ {len(tasks)} pending task(s), all recent")
    return Truedef main():
logger.info("=" * 50)
logger.info(f"HEALTH CHECK - {datetime.now()}")
logger.info("=" * 50)checks = {
    "Processes Running": check_processes(),
    "Dashboard Active": check_dashboard_activity(),
    "No Stuck Tasks": check_pending_tasks()
}passed = sum(checks.values())
total = len(checks)logger.info("=" * 50)
logger.info(f"Result: {passed}/{total} checks passed")
logger.info("=" * 50)if passed == total:
    logger.info("✓ SYSTEM HEALTHY")
    return 0
else:
    logger.error("✗ SYSTEM NEEDS ATTENTION")
    return 1if name == "main":
exit(main())

**Cron entry for hourly health checks:**
```bashRun health check every hour
0 * * * * cd ~/path/to/project && python3 health_check.py >> ~/AI_Employee_Vault/Logs/health.log 2>&1

**Acceptance Criteria:**
- ✅ Detects missing processes
- ✅ Checks dashboard freshness
- ✅ Identifies stuck tasks
- ✅ Logs all checks clearly
- ✅ Returns proper exit codes

## File Structure - Module 1[Project Root]/
├── watchers/
│   ├── gmail_watcher.py           # Bronze
│   ├── filesystem_watcher.py      # Bronze
│   └── linkedin_watcher.py        # NEW
├── orchestrator.py                # NEW
├── health_check.py                # NEW
├── start_system.sh                # NEW (or .ps1)
└── .pids/                         # NEW (created by startup script)AI_Employee_Vault/
├── Needs_Action/
│   ├── SKILL_LinkedInPoster.md   # NEW
│   └── LINKEDIN_POST_*.md        # Auto-generated
├── Logs/
│   ├── orchestrator.log          # NEW
│   ├── linkedin.log              # NEW
│   ├── linkedin_posted.txt       # NEW
│   └── health.log                # NEW
└── Dashboard.md

## Success Criteria - Module 1
- ✅ Orchestrator auto-processes tasks within 10 seconds
- ✅ LinkedIn watcher creates scheduled post requests
- ✅ SKILL_LinkedInPoster generates quality content
- ✅ Health checks detect failures
- ✅ Startup script works smoothly
- ✅ All services log activity
- ✅ System runs for 24+ hours without manual intervention

## Deliverables
- orchestrator.py (fully functional)
- watchers/linkedin_watcher.py
- SKILL_LinkedInPoster.md
- health_check.py
- start_system script (.sh or .ps1)
- Updated README-Silver-Module1.md
- Test results showing 24-hour autonomous operation

## Testing Checklist
```bashTest orchestrator
□ Start: python orchestrator.py
□ Drop test file in /Needs_Action/
□ Verify: Processed within 10 seconds
□ Verify: Logs show activityTest LinkedIn watcher
□ Set system time to Monday 9:00 AM (or wait for real schedule)
□ Start: python watchers/linkedin_watcher.py
□ Verify: Post request created in /Needs_Action/
□ Verify: Orchestrator processes it
□ Verify: Approval file created in /Pending_Approval/Test complete system
□ Run: ./start_system.sh
□ Verify: All watchers start
□ Verify: Orchestrator starts
□ Drop test file, send email, wait for LinkedIn schedule
□ Verify: All processed automatically
□ Press Ctrl+C
□ Verify: All processes stop cleanlyTest health monitoring
□ Run: python health_check.py
□ Verify: All checks pass
□ Stop orchestrator
□ Re-run health check
□ Verify: Missing process detected24-hour test
□ Start system with ./start_system.sh
□ Leave running overnight
□ Check logs next day
□ Verify: No crashes, all tasks processed

## Common Issues & Solutions

**Issue**: Orchestrator processes too frequently
**Solution**: Increase debounce_seconds or cooldown period

**Issue**: LinkedIn watcher creates duplicate posts
**Solution**: Check linkedin_posted.txt for proper logging

**Issue**: Claude Code timeout on complex tasks
**Solution**: Increase timeout in orchestrator.py (line ~120)

**Issue**: Startup script fails on Windows
**Solution**: Use .ps1 version, run with: `powershell -ExecutionPolicy Bypass -File start_system.ps1`

## Next Module
After completing Module 1, proceed to:
**Module 2: Email MCP Server + Approval Workflow**
for this spec you will work in specs/silver folder remember everything we will implement, we will implement in silver dir firstly go to the specs/silver dir then create a folder for module 1 then create a spec.md file then start creating specs
```

## Response Text
Created a comprehensive specification for Silver Module 1: Orchestrator + LinkedIn Automation, including functional requirements, user scenarios, success criteria, and a quality checklist.

## Outcome Impact
Successfully created the specification document for the Silver Module 1 which will enable automated task processing and scheduled LinkedIn business promotion posts. The specification covers all required components including orchestrator, LinkedIn watcher, poster skill, startup script, and health monitoring.

## Tests Summary
none

## Files Summary
- specs/silver/module-1/spec.md - Main specification document
- specs/silver/module-1/checklists/requirements.md - Quality checklist for the specification

## Next Prompts
none

## Reflection Note
The specification comprehensively covers all aspects of the Silver Module 1 including orchestrator functionality, LinkedIn automation, system management, and health monitoring.

## Failure Modes Observed
none

## Next Experiment to Improve Prompt Quality
none