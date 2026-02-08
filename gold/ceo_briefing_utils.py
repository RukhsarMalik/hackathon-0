"""
Utility functions for generating CEO briefing markdown files.
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import yaml


def generate_ceo_briefing_filename(week_start_date: datetime = None) -> str:
    """
    Generate a filename for the CEO briefing based on the week's start date.

    Args:
        week_start_date: Date when the week starts (defaults to last Sunday)

    Returns:
        String filename in the format YYYY-MM-DD_CEO_Briefing.md
    """
    if week_start_date is None:
        # Find the most recent Sunday
        today = datetime.now()
        days_since_sunday = today.weekday() + 1  # Monday is 0, so Sunday is 6+1=7, Saturday is 5+1=6
        if today.weekday() == 6:  # If today is Sunday
            week_start_date = today
        else:
            week_start_date = today - timedelta(days=today.weekday() + 1)

    return f"{week_start_date.strftime('%Y-%m-%d')}_CEO_Briefing.md"


def create_ceo_briefing_template(
    week_start: datetime,
    week_end: datetime,
    revenue_data: Dict[str, Any] = None,
    task_metrics: List[Dict[str, Any]] = None,
    bottlenecks: List[str] = None,
    unused_subscriptions: List[Dict[str, Any]] = None,
    cross_domain_insights: List[str] = None,
    recommendations: List[str] = None
) -> str:
    """
    Create a CEO briefing markdown file with all required sections.

    Args:
        week_start: Start date of the week being reported
        week_end: End date of the week being reported
        revenue_data: Revenue information (actual vs. target)
        task_metrics: Task completion metrics
        bottlenecks: Bottleneck identifications
        unused_subscriptions: Unused subscriptions (>30 days)
        cross_domain_insights: Cross-domain insights
        recommendations: Recommendations for human review

    Returns:
        String content for the CEO briefing markdown file
    """
    if revenue_data is None:
        revenue_data = {}
    if task_metrics is None:
        task_metrics = []
    if bottlenecks is None:
        bottlenecks = []
    if unused_subscriptions is None:
        unused_subscriptions = []
    if cross_domain_insights is None:
        cross_domain_insights = []
    if recommendations is None:
        recommendations = []

    # Calculate period
    period = f"Week of {week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}"

    # Start building the content
    content = f"""---
type: ceo_briefing
generation_date: {datetime.now().isoformat()}
week_start: {week_start.date().isoformat()}
week_end: {week_end.date().isoformat()}
period: "{period}"
generated_by: "Business_Intelligence_Agent_v1.0"
status: "completed"
---

# CEO Weekly Business Briefing
**Period**: {period}

## Executive Summary
This report consolidates business performance data for the week of {week_start.strftime('%B %d')} through {week_end.strftime('%B %d, %Y')}. Key highlights include:

"""

    # Add revenue summary if available
    if revenue_data:
        content += f"\n### Revenue Analysis\n"
        actual = revenue_data.get('actual', 0)
        target = revenue_data.get('target', 0)
        variance = revenue_data.get('variance', 0)
        content += f"- **Actual Revenue**: ${actual:,.2f}\n"
        content += f"- **Target Revenue**: ${target:,.2f}\n"
        content += f"- **Variance**: {variance:+.2f}%\n"

        if variance >= 0:
            content += f"- **Performance**: Ahead of target by ${abs(actual-target):,.2f}\n"
        else:
            content += f"- **Performance**: Below target by ${abs(actual-target):,.2f}\n"

        if 'breakdown' in revenue_data:
            content += "\n**Revenue Breakdown**:\n"
            for source, amount in revenue_data['breakdown'].items():
                content += f"  - {source}: ${amount:,.2f}\n"

    # Add task completion metrics
    if task_metrics:
        content += f"\n### Task Completion Metrics\n"
        content += f"- **Total Tasks Completed**: {len(task_metrics)}\n"

        # Count different types of tasks
        email_tasks = sum(1 for t in task_metrics if t.get('type') == 'email')
        linkedin_tasks = sum(1 for t in task_metrics if t.get('type') == 'linkedin')
        other_tasks = len(task_metrics) - email_tasks - linkedin_tasks

        content += f"- **Email Tasks**: {email_tasks}\n"
        content += f"- **LinkedIn Tasks**: {linkedin_tasks}\n"
        content += f"- **Other Tasks**: {other_tasks}\n"

        if task_metrics:
            content += "\n**Recent Task Highlights**:\n"
            for i, task in enumerate(task_metrics[:5]):  # Show first 5 tasks
                content += f"  - {task.get('description', 'Task completed')}\n"

    # Add bottleneck identification
    if bottlenecks:
        content += f"\n### Bottleneck Identification\n"
        content += f"- **Tasks >48 hours**: {len(bottlenecks)} items detected\n"
        content += "\n**Identified Bottlenecks**:\n"
        for bottleneck in bottlenecks:
            content += f"  - {bottleneck}\n"

    # Add subscription utilization
    if unused_subscriptions:
        content += f"\n### Subscription Utilization\n"
        content += f"- **Unused >30 days**: {len(unused_subscriptions)} subscriptions flagged\n"
        content += "\n**Underutilized Subscriptions**:\n"
        for sub in unused_subscriptions:
            name = sub.get('name', 'Unknown')
            cost = sub.get('monthly_cost', 0)
            last_used = sub.get('last_used', 'Unknown')
            content += f"  - **{name}** (${cost}/mo) - Last used: {last_used}\n"

    # Add cross-domain insights
    if cross_domain_insights:
        content += f"\n### Cross-Domain Insights\n"
        content += f"- **Connected Workflows**: {len(cross_domain_insights)} insights\n"
        content += "\n**Cross-Domain Activities**:\n"
        for insight in cross_domain_insights:
            content += f"  - {insight}\n"

    # Add project deadline monitoring
    content += f"\n### Project Deadline Monitoring\n"
    # This would typically be populated with actual deadline data

    # Add recommendations
    if recommendations:
        content += f"\n### Recommendations\n"
        content += f"- **Action Items**: {len(recommendations)} recommendations for review\n"
        content += "\n**Recommended Actions**:\n"
        for recommendation in recommendations:
            content += f"  - {recommendation}\n"

    content += f"""

## Next Week's Priorities
- Review outstanding bottlenecks
- Address underutilized subscriptions
- Follow up on deadline approaching projects

---
*Generated by Business Intelligence Agent on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""

    return content


def save_ceo_briefing(content: str, filename: str, briefing_directory: str = "./AI_Employee_Vault/Briefings"):
    """
    Save the CEO briefing to a markdown file.

    Args:
        content: The content of the briefing
        filename: The name of the file to save
        briefing_directory: Directory where briefings are stored

    Returns:
        Path to the saved file
    """
    directory = Path(briefing_directory)
    directory.mkdir(parents=True, exist_ok=True)

    filepath = directory / filename
    filepath.write_text(content, encoding='utf-8')

    return filepath


def generate_sample_briefing():
    """
    Generate a sample CEO briefing for testing purposes.
    """
    from datetime import datetime, timedelta

    # Define a week (Sunday to Saturday)
    today = datetime.now()
    # Find the Sunday of the current week
    days_since_sunday = (today.weekday() + 1) % 7
    week_start = today - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=6)

    # Sample data
    revenue_data = {
        'actual': 45230.50,
        'target': 50000.00,
        'variance': -9.54,
        'breakdown': {
            'LinkedIn Posts': 12500.00,
            'Email Campaigns': 18730.50,
            'Accounting': 14000.00
        }
    }

    task_metrics = [
        {'type': 'email', 'description': 'Processed 15 email replies'},
        {'type': 'linkedin', 'description': 'Published 3 LinkedIn posts'},
        {'type': 'accounting', 'description': 'Processed 5 invoice requests'},
        {'type': 'facebook', 'description': 'Published 7 Facebook posts'},
        {'type': 'email', 'description': 'Handled 8 approval requests'}
    ]

    bottlenecks = [
        "Invoice processing workflow experiencing delays (>72h)",
        "LinkedIn post approval queue backed up"
    ]

    unused_subscriptions = [
        {
            'name': 'Marketing Analytics Pro',
            'monthly_cost': 299.00,
            'last_used': '2026-01-15'
        },
        {
            'name': 'Design Suite Premium',
            'monthly_cost': 49.99,
            'last_used': '2025-12-20'
        }
    ]

    cross_domain_insights = [
        "Payment confirmation emails triggering successful Odoo invoice updates",
        "Significant correlation between LinkedIn engagement and email response rates",
        "Facebook activity driving traffic to business website"
    ]

    recommendations = [
        "Review Marketing Analytics subscription usage - hasn't been used in 3+ weeks",
        "Investigate invoice processing delays - consider workflow optimization",
        "Evaluate LinkedIn post approval process - too many manual steps"
    ]

    briefing_content = create_ceo_briefing_template(
        week_start=week_start,
        week_end=week_end,
        revenue_data=revenue_data,
        task_metrics=task_metrics,
        bottlenecks=bottlenecks,
        unused_subscriptions=unused_subscriptions,
        cross_domain_insights=cross_domain_insights,
        recommendations=recommendations
    )

    filename = generate_ceo_briefing_filename(week_start)
    filepath = save_ceo_briefing(briefing_content, filename)

    print(f"Sample CEO briefing generated: {filepath}")
    return filepath


if __name__ == "__main__":
    # Generate a sample briefing when running as main
    generate_sample_briefing()