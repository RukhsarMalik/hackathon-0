#!/usr/bin/env python3
"""
Weekly Audit Script - Gathers data from various sources for CEO briefings.
"""
import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from business_goals_utils import load_business_goals, get_monthly_revenue_target, get_project_deadlines, get_subscriptions
from ceo_briefing_utils import create_ceo_briefing_template, generate_ceo_briefing_filename, save_ceo_briefing


def get_done_tasks_from_week(week_start: datetime, week_end: datetime, vault_path: str = "./AI_Employee_Vault") -> List[Dict[str, Any]]:
    """
    Extract task completion metrics from the /Done/ folder for the specified week.

    Args:
        week_start: Start date of the week
        week_end: End date of the week
        vault_path: Path to the AI Employee Vault directory

    Returns:
        List of task dictionaries with details
    """
    vault = Path(vault_path)
    done_folder = vault / "Done"

    tasks = []

    # Check if Done folder exists
    if not done_folder.exists():
        print(f"Warning: Done folder does not exist at {done_folder}")
        return []

    for file_path in done_folder.glob("*.md"):
        # Skip system files
        if file_path.name == '.gitkeep':
            continue

        # Try to extract timestamp from filename or content
        try:
            # Check if filename contains a recognizable date pattern (e.g., YYYYMMDD or YYYY-MM-DD)
            match = re.search(r'(\d{4}-?\d{2}-?\d{2})', file_path.stem)
            if match:
                # Normalize the date string to YYYY-MM-DD format
                date_part = match.group(1)
                # Remove any dashes for consistent processing
                date_part_clean = date_part.replace('-', '')

                if len(date_part_clean) == 8:  # YYYYMMDD format
                    file_date = datetime.strptime(date_part_clean, '%Y%m%d')
                elif len(date_part) == 10:  # YYYY-MM-DD format
                    file_date = datetime.strptime(date_part, '%Y-%m-%d')
                else:
                    # If format doesn't match expected patterns, use file modification time
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    file_date = mod_time
            else:
                # Use file modification time if no date in filename
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                file_date = mod_time

            # Check if the task falls within the week
            if week_start.date() <= file_date.date() <= week_end.date():
                content = file_path.read_text(encoding='utf-8')

                # Extract task type from YAML frontmatter if available
                task_type = "unknown"
                lines = content.split('\n')
                in_frontmatter = False
                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter and line.startswith('type:'):
                        task_type = line.split(':', 1)[1].strip()
                        break

                # Extract more detailed information from the content
                title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                title = title_match.group(1) if title_match else file_path.stem

                # Calculate estimated processing time if timestamps are available
                estimated_duration = None
                # Look for created_date or similar timestamps in the content
                created_match = re.search(r'created_date:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', content)
                if created_match:
                    try:
                        created_time = datetime.fromisoformat(created_match.group(1).replace('Z', '+00:00'))
                        duration_hours = (file_date - created_time).total_seconds() / 3600
                        estimated_duration = round(duration_hours, 2)
                    except:
                        pass  # If parsing fails, just skip duration calculation

                tasks.append({
                    'filename': file_path.name,
                    'type': task_type,
                    'title': title,
                    'description': content[:200] if len(content) < 200 else content[:200] + "...",
                    'completion_date': file_date.isoformat(),
                    'estimated_duration_hours': estimated_duration
                })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    # Sort tasks by completion date
    tasks.sort(key=lambda x: x['completion_date'])
    return tasks


def get_tasks_over_duration(tasks: List[Dict[str, Any]], hours_threshold: int = 48) -> List[str]:
    """
    Identify tasks that took longer than the specified threshold to complete.

    Args:
        tasks: List of task dictionaries
        hours_threshold: Threshold in hours (default: 48)

    Returns:
        List of bottleneck descriptions
    """
    bottlenecks = []

    for task in tasks:
        try:
            duration_hours = task.get('estimated_duration_hours')

            if duration_hours and duration_hours > hours_threshold:
                bottlenecks.append(f"{task['filename']} - Type: {task['type']} - Duration: {duration_hours} hours")
            elif duration_hours is None:
                # If we couldn't calculate duration but want to flag tasks with certain characteristics
                # For example, if the task was in the system for a long time without knowing exact start time
                completion_date = datetime.fromisoformat(task['completion_date'])
                # If it's an old task (could indicate processing delay), flag it
                if (datetime.now() - completion_date).days > 7:  # More than a week in the system
                    bottlenecks.append(f"{task['filename']} - Type: {task['type']} - Long processing time (estimate > week)")

        except Exception as e:
            print(f"Error evaluating task duration for {task.get('filename', 'unknown')}: {e}")
            continue

    return bottlenecks


def analyze_subscription_usage(subscriptions: List[Dict[str, Any]], days_threshold: int = 30) -> List[Dict[str, Any]]:
    """
    Analyze subscription usage to identify unused subscriptions.

    Args:
        subscriptions: List of subscription dictionaries from Business_Goals.md
        days_threshold: Days threshold for considering a subscription unused

    Returns:
        List of unused subscription dictionaries
    """
    unused = []

    for sub in subscriptions:
        try:
            last_used_raw = sub.get('last_used', '')
            if last_used_raw:
                last_used_str = str(last_used_raw)
                last_used = datetime.strptime(last_used_str, '%Y-%m-%d')
                days_since_use = (datetime.now() - last_used).days

                if days_since_use > days_threshold:
                    unused.append({
                        'name': sub.get('name', 'Unknown'),
                        'monthly_cost': sub.get('monthly_cost', 0),
                        'renewal_date': sub.get('renewal_date', ''),
                        'category': sub.get('category', 'Uncategorized'),
                        'last_used': last_used_str,
                        'days_unused': days_since_use
                    })
        except ValueError:
            # If date parsing fails, skip this subscription
            continue

    return unused


def get_revenue_from_odoo_mcp() -> Dict[str, float]:
    """
    Extract revenue data from Odoo MCP server.

    Note: This is a placeholder implementation. In a real system, this would
    make an actual call to the Odoo MCP server to get revenue data.
    Implements graceful handling when Odoo is unreachable.

    Returns:
        Dictionary with revenue information
    """
    import subprocess
    import json

    # Attempt to call the Odoo MCP server to get revenue data
    try:
        # In a real implementation, this would make an actual call to the Odoo MCP
        # For now, we'll simulate the call and potential errors
        print("Attempting to connect to Odoo MCP server...")

        # This is a placeholder for the actual MCP call
        # In a real implementation, we would use the MCP client to make a call like:
        # result = await mcp_client.call_tool("get_revenue_data", {...})

        # Simulate checking if the Odoo server is reachable
        # For this simulation, we'll assume it's reachable and return mock data
        # but in reality, we'd make an actual call that could fail

        return {
            'actual': 45230.50,
            'breakdown': {
                'LinkedIn Posts': 12500.00,
                'Email Campaigns': 18730.50,
                'Accounting': 14000.00
            }
        }

    except subprocess.TimeoutExpired:
        print("Warning: Odoo MCP call timed out. Using partial data for briefing.")
        # Return partial data indicating that Odoo data is unavailable
        return {
            'actual': 0.0,
            'breakdown': {},
            'note': 'Odoo data unavailable - connection timed out'
        }
    except subprocess.CalledProcessError as e:
        print(f"Warning: Odoo MCP server call failed ({e}). Using partial data for briefing.")
        # Return partial data indicating that Odoo data is unavailable
        return {
            'actual': 0.0,
            'breakdown': {},
            'note': 'Odoo data unavailable - service error'
        }
    except Exception as e:
        print(f"Warning: Unable to reach Odoo MCP server ({e}). Generating briefing with available data only.")
        # Return default values if MCP call fails, but still generate briefing
        return {
            'actual': 0.0,
            'breakdown': {},
            'note': 'Odoo data unavailable - connection error'
        }


def get_approaching_deadlines(deadlines: List[Dict[str, Any]], days_ahead: int = 7) -> List[Dict[str, Any]]:
    """
    Get project deadlines approaching within the specified number of days.

    Args:
        deadlines: List of deadline dictionaries from Business_Goals.md
        days_ahead: Number of days ahead to consider (default: 7)

    Returns:
        List of approaching deadline dictionaries
    """
    approaching = []
    now = datetime.now()

    for deadline in deadlines:
        try:
            due_date_raw = deadline.get('due_date', '')
            if due_date_raw:
                due_date_str = str(due_date_raw)
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                days_until_deadline = (due_date - now).days

                if 0 <= days_until_deadline <= days_ahead:
                    approaching.append({
                        'name': deadline.get('name', 'Unknown'),
                        'due_date': due_date_str,
                        'description': deadline.get('description', ''),
                        'priority': deadline.get('priority', 'Unknown'),
                        'days_remaining': days_until_deadline
                    })
        except ValueError:
            # If date parsing fails, skip this deadline
            continue

    return approaching


def generate_weekly_audit_report(week_start: datetime = None, week_end: datetime = None, vault_path: str = "./AI_Employee_Vault"):
    """
    Generate the weekly audit report with data from various sources.

    Args:
        week_start: Start date of the week (defaults to last Sunday)
        week_end: End date of the week (defaults to following Saturday)
        vault_path: Path to the AI Employee Vault directory
    """
    if week_start is None:
        # Find the most recent Sunday
        today = datetime.now()
        days_since_sunday = today.weekday() + 1  # Monday is 0, so Sunday is 6+1=7, Saturday is 5+1=6
        if today.weekday() == 6:  # If today is Sunday
            week_start = today
        else:
            week_start = today - timedelta(days=today.weekday() + 1)

    if week_end is None:
        week_end = week_start + timedelta(days=6)  # Following Saturday

    print(f"Generating weekly audit report for {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

    # Load business goals
    goals_config = load_business_goals(vault_path)

    # Get done tasks for the week
    done_tasks = get_done_tasks_from_week(week_start, week_end, vault_path)
    print(f"Found {len(done_tasks)} tasks completed during the week")

    # Identify bottlenecks (tasks > 48 hours)
    bottlenecks = get_tasks_over_duration(done_tasks)
    print(f"Identified {len(bottlenecks)} potential bottlenecks")

    # Get subscriptions and analyze usage
    subscriptions = get_subscriptions(goals_config) if goals_config else []
    unused_subscriptions = analyze_subscription_usage(subscriptions)
    print(f"Found {len(unused_subscriptions)} unused subscriptions")

    # Get revenue data from Odoo MCP
    revenue_data = get_revenue_from_odoo_mcp()

    # Update revenue data with target if available
    if goals_config:
        current_month = goals_config.get('current_month', datetime.now().strftime('%Y-%m'))
        target = get_monthly_revenue_target(current_month, goals_config)
        revenue_data['target'] = target

        # Calculate variance if we have both actual and target
        if 'actual' in revenue_data:
            actual = revenue_data['actual']
            variance = ((actual - target) / target) * 100 if target != 0 else 0
            revenue_data['variance'] = variance

    # Get approaching project deadlines
    deadlines = get_project_deadlines(goals_config) if goals_config else []
    approaching_deadlines = get_approaching_deadlines(deadlines)
    print(f"Found {len(approaching_deadlines)} approaching deadlines")

    # Generate cross-domain insights (placeholder)
    cross_domain_insights = [
        "Placeholder: Cross-domain insights would be generated from system logs",
        "Placeholder: Payment confirmation emails triggering Odoo invoice updates",
        "Placeholder: LinkedIn engagement correlating with email response rates"
    ]

    # Generate recommendations (placeholder)
    recommendations = [
        "Placeholder: Recommendations based on audit findings",
        f"Review {len(unused_subscriptions)} unused subscriptions for potential cancellation",
        f"Address {len(bottlenecks)} identified bottlenecks in task processing workflows"
    ]

    # Create CEO briefing
    briefing_content = create_ceo_briefing_template(
        week_start=week_start,
        week_end=week_end,
        revenue_data=revenue_data,
        task_metrics=done_tasks,
        bottlenecks=bottlenecks,
        unused_subscriptions=unused_subscriptions,
        cross_domain_insights=cross_domain_insights,
        recommendations=recommendations
    )

    # Save the briefing
    filename = generate_ceo_briefing_filename(week_start)
    filepath = save_ceo_briefing(briefing_content, filename)

    print(f"CEO Weekly Briefing generated: {filepath}")

    return {
        'briefing_file': str(filepath),
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'summary': {
            'tasks_completed': len(done_tasks),
            'bottlenecks_found': len(bottlenecks),
            'unused_subscriptions': len(unused_subscriptions),
            'approaching_deadlines': len(approaching_deadlines)
        }
    }


def schedule_weekly_audit():
    """
    Schedule the weekly audit to run automatically every Sunday at 11 PM.

    Note: This would typically integrate with cron or Windows Task Scheduler
    depending on the platform. For now, this is a placeholder.
    """
    print("Setting up weekly audit scheduling...")
    print("In a real implementation, this would add a cron job or Windows Task Scheduler entry")
    print("to run the weekly audit every Sunday at 11 PM.")


if __name__ == "__main__":
    # Generate a sample weekly audit report
    result = generate_weekly_audit_report()
    print(f"\nWeekly audit completed. Report saved to: {result['briefing_file']}")
    print(f"Summary: {result['summary']}")