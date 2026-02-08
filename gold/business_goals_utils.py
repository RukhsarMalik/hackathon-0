"""
Utility functions for reading Business_Goals.md configuration.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_business_goals(vault_path: str = "./AI_Employee_Vault") -> Optional[Dict[str, Any]]:
    """
    Load the Business_Goals.md configuration file.

    Args:
        vault_path: Path to the AI Employee Vault directory

    Returns:
        Dictionary with parsed business goals configuration or None if file not found
    """
    vault = Path(vault_path)
    goals_file = vault / "Business_Goals.md"

    if not goals_file.exists():
        print(f"Business_Goals.md not found at {goals_file}")
        return None

    try:
        content = goals_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Parse YAML frontmatter between --- delimiters
        config = {}
        start_idx = -1
        end_idx = -1

        for i, line in enumerate(lines):
            if line.strip() == '---':
                if start_idx == -1:
                    start_idx = i
                elif end_idx == -1:
                    end_idx = i
                    break

        if start_idx != -1 and end_idx != -1:
            yaml_content = '\n'.join(lines[start_idx + 1:end_idx])
            config = yaml.safe_load(yaml_content) or {}

        # Also parse YAML from ```yaml code blocks in the body
        import re
        yaml_blocks = re.findall(r'```yaml\s*\n(.*?)```', content, re.DOTALL)
        for block in yaml_blocks:
            try:
                parsed = yaml.safe_load(block)
                if isinstance(parsed, dict):
                    config.update(parsed)
            except yaml.YAMLError:
                continue

        return config if config else None

    except Exception as e:
        print(f"Error parsing Business_Goals.md: {e}")
        return None


def get_monthly_revenue_target(month: str, goals_config: Dict[str, Any]) -> float:
    """
    Get the monthly revenue target for a specific month.

    Args:
        month: Month in YYYY-MM format (e.g., "2026-02")
        goals_config: Parsed business goals configuration

    Returns:
        Revenue target as float or 0.0 if not found
    """
    if not goals_config:
        return 0.0

    # First try to find in revenue_targets array
    if 'revenue_targets' in goals_config:
        for target in goals_config['revenue_targets']:
            if target.get('month') == month:
                return float(target.get('target', 0.0))

    # Fallback to monthly_revenue_target if month doesn't match
    return float(goals_config.get('monthly_revenue_target', 0.0))


def get_project_deadlines(goals_config: Dict[str, Any]) -> list:
    """
    Get all project deadlines from the configuration.

    Args:
        goals_config: Parsed business goals configuration

    Returns:
        List of project deadline dictionaries
    """
    if not goals_config:
        return []

    return goals_config.get('project_deadlines', [])


def get_subscriptions(goals_config: Dict[str, Any]) -> list:
    """
    Get all subscriptions from the configuration.

    Args:
        goals_config: Parsed business goals configuration

    Returns:
        List of subscription dictionaries
    """
    if not goals_config:
        return []

    return goals_config.get('subscriptions', [])


def get_kpis(goals_config: Dict[str, Any]) -> list:
    """
    Get all KPIs from the configuration.

    Args:
        goals_config: Parsed business goals configuration

    Returns:
        List of KPI dictionaries
    """
    if not goals_config:
        return []

    return goals_config.get('kpis', [])


def get_subscription_by_name(subscription_name: str, goals_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get a specific subscription by name.

    Args:
        subscription_name: Name of the subscription to find
        goals_config: Parsed business goals configuration

    Returns:
        Subscription dictionary or None if not found
    """
    if not goals_config:
        return None

    subscriptions = goals_config.get('subscriptions', [])
    for sub in subscriptions:
        if sub.get('name') == subscription_name:
            return sub

    return None


def is_deadline_approaching(deadline_date: str, days_ahead: int = 7) -> bool:
    """
    Check if a deadline is approaching within the specified number of days.

    Args:
        deadline_date: Deadline date in YYYY-MM-DD format
        days_ahead: Number of days ahead to consider as 'approaching' (default: 7)

    Returns:
        True if deadline is approaching, False otherwise
    """
    from datetime import datetime, timedelta

    try:
        deadline = datetime.strptime(deadline_date, '%Y-%m-%d')
        today = datetime.now()
        days_until_deadline = (deadline - today).days

        return 0 <= days_until_deadline <= days_ahead
    except ValueError:
        # Invalid date format
        return False


def check_kpi_deviation(kpi_name: str, current_value: float, goals_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if a KPI is deviating from its target.

    Args:
        kpi_name: Name of the KPI to check
        current_value: Current value of the KPI
        goals_config: Parsed business goals configuration

    Returns:
        Dictionary with deviation information or None if KPI not found
    """
    if not goals_config:
        return None

    kpis = goals_config.get('kpis', [])
    for kpi in kpis:
        if kpi.get('name') == kpi_name:
            target = kpi.get('target', 0)

            # Calculate deviation percentage
            deviation_pct = 0
            if target != 0:
                deviation_pct = ((current_value - target) / target) * 100

            # Determine severity based on deviation magnitude
            severity = "normal"
            if abs(deviation_pct) > 20:  # More than 20% off target
                severity = "high"
            elif abs(deviation_pct) > 10:  # More than 10% off target
                severity = "medium"

            return {
                'kpi_name': kpi_name,
                'current_value': current_value,
                'target_value': target,
                'unit': kpi.get('unit', ''),
                'description': kpi.get('description', ''),
                'deviation_percentage': round(deviation_pct, 2),
                'severity': severity,
                'on_track': deviation_pct >= 0 if kpi.get('higher_is_better', True) else deviation_pct <= 0
            }

    return None


def get_all_kpi_status(goals_config: Dict[str, Any], current_values: Dict[str, float] = None) -> Dict[str, Dict[str, Any]]:
    """
    Get status for all KPIs in the configuration.

    Args:
        goals_config: Parsed business goals configuration
        current_values: Dictionary of current KPI values (name: value)

    Returns:
        Dictionary mapping KPI names to their status information
    """
    if current_values is None:
        current_values = {}

    if not goals_config:
        return {}

    kpi_statuses = {}
    kpis = goals_config.get('kpis', [])

    for kpi in kpis:
        kpi_name = kpi.get('name')
        current_value = current_values.get(kpi_name, 0)

        status = check_kpi_deviation(kpi_name, current_value, goals_config)
        if status:
            kpi_statuses[kpi_name] = status

    return kpi_statuses