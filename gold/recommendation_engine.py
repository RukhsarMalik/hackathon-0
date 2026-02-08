"""
Goal-Based Recommendation Engine for CEO Briefings.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from business_goals_utils import load_business_goals, get_monthly_revenue_target, get_project_deadlines, get_subscriptions, get_kpis
from historical_tracking import HistoricalTracker


class RecommendationEngine:
    """
    Generates business recommendations based on goal tracking, historical data, and current performance.
    """
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.tracker = HistoricalTracker(vault_path)

    def generate_recommendations(self, goals_config: Dict[str, Any], current_data: Dict[str, Any] = None) -> List[str]:
        """
        Generate business recommendations based on goals and current data.

        Args:
            goals_config: Loaded business goals configuration
            current_data: Current business data (revenue, tasks, etc.)

        Returns:
            List of recommendation strings
        """
        if current_data is None:
            current_data = {}

        recommendations = []

        # Analyze revenue performance
        revenue_rec = self._analyze_revenue_recommendations(goals_config, current_data)
        recommendations.extend(revenue_rec)

        # Analyze project deadlines
        deadline_rec = self._analyze_deadline_recommendations(goals_config, current_data)
        recommendations.extend(deadline_rec)

        # Analyze subscription usage
        subscription_rec = self._analyze_subscription_recommendations(goals_config, current_data)
        recommendations.extend(subscription_rec)

        # Analyze KPI performance
        kpi_rec = self._analyze_kpi_recommendations(goals_config, current_data)
        recommendations.extend(kpi_rec)

        return recommendations

    def _analyze_revenue_recommendations(self, goals_config: Dict[str, Any], current_data: Dict[str, Any]) -> List[str]:
        """
        Generate revenue-focused recommendations.
        """
        recommendations = []

        # Check monthly revenue target
        current_month = goals_config.get('current_month', datetime.now().strftime('%Y-%m'))
        target = get_monthly_revenue_target(current_month, goals_config)

        actual = current_data.get('actual_revenue', 0)
        if target > 0:
            achievement_pct = (actual / target) * 100
            days_remaining = self._days_remaining_in_month()

            if achievement_pct < 75:
                # Significantly behind target
                recommendations.append(
                    f"You are significantly behind on the monthly revenue target. "
                    f"Currently at {achievement_pct:.1f}% of ${target:,.2f} target with {days_remaining} days remaining. "
                    f"Consider intensifying sales efforts or adjusting expectations for the month."
                )
            elif achievement_pct < 90 and days_remaining < 10:
                # Behind and running out of time
                recommendations.append(
                    f"Monthly revenue target is lagging with {days_remaining} days remaining. "
                    f"At {achievement_pct:.1f}% of target (${actual:,.2f}/${target:,.2f}), "
                    f"consider focusing on high-value opportunities to close the gap."
                )
            elif achievement_pct > 110:
                # Ahead of target
                recommendations.append(
                    f"Excellent! Revenue is ahead of target at {achievement_pct:.1f}% of ${target:,.2f}. "
                    f"Consider setting stretch goals or planning for next month's targets."
                )

        # Analyze revenue trend
        try:
            revenue_trend = self.tracker.get_revenue_performance("monthly")
            if revenue_trend['trend'] == 'decreasing':
                recommendations.append(
                    "Revenue trend is declining compared to previous months. "
                    "Investigate factors affecting performance and consider strategic adjustments."
                )
            elif revenue_trend['trend'] == 'increasing':
                recommendations.append(
                    "Revenue trend is improving. Maintain current strategies that are driving growth."
                )
        except:
            pass  # Silently fail if trend analysis unavailable

        return recommendations

    def _analyze_deadline_recommendations(self, goals_config: Dict[str, Any], current_data: Dict[str, Any]) -> List[str]:
        """
        Generate deadline-focused recommendations.
        """
        recommendations = []

        # Get approaching deadlines
        deadlines = get_project_deadlines(goals_config) if goals_config else []

        approaching_deadlines = []
        for deadline in deadlines:
            due_date_str = deadline.get('due_date', '')
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                    days_until_deadline = (due_date - datetime.now()).days

                    if 0 <= days_until_deadline <= 7:  # Approaching within a week
                        approaching_deadlines.append({
                            'name': deadline.get('name', 'Unknown'),
                            'due_date': due_date_str,
                            'days_remaining': days_until_deadline,
                            'priority': deadline.get('priority', 'Unknown'),
                            'status': deadline.get('status', 'Unknown')
                        })
                except ValueError:
                    continue  # Skip invalid dates

        # Generate recommendations for approaching deadlines
        if approaching_deadlines:
            if len(approaching_deadlines) == 1:
                deadline = approaching_deadlines[0]
                recommendations.append(
                    f"The project '{deadline['name']}' is due in {deadline['days_remaining']} days. "
                    f"Ensure all deliverables are on track for completion."
                )
            else:
                deadline_names = [d['name'] for d in approaching_deadlines]
                recommendations.append(
                    f"Multiple projects are approaching deadlines: {', '.join(deadline_names)}. "
                    f"Prioritize these projects and allocate necessary resources to meet commitments."
                )

            # Check for overdue deadlines
            overdue = [d for d in deadlines if self._is_overdue(d.get('due_date', ''))]
            if overdue:
                overdue_names = [d.get('name', 'Unknown') for d in overdue]
                recommendations.append(
                    f"Attention needed: Projects may be overdue: {', '.join(overdue_names)}. "
                    f"Verify status and take corrective action if necessary."
                )

        return recommendations

    def _analyze_subscription_recommendations(self, goals_config: Dict[str, Any], current_data: Dict[str, Any]) -> List[str]:
        """
        Generate subscription-focused recommendations.
        """
        recommendations = []

        # Check subscription utilization
        subscriptions = get_subscriptions(goals_config) if goals_config else []

        unused_subscriptions = []
        for sub in subscriptions:
            last_used_str = sub.get('last_used', '')
            if last_used_str:
                try:
                    last_used = datetime.strptime(last_used_str, '%Y-%m-%d')
                    days_since_use = (datetime.now() - last_used).days

                    if days_since_use > 30:  # Unused for more than 30 days
                        unused_subscriptions.append({
                            'name': sub.get('name', 'Unknown'),
                            'cost': sub.get('monthly_cost', 0),
                            'days_unused': days_since_use
                        })
                except ValueError:
                    continue  # Skip invalid dates

        # Generate recommendations for unused subscriptions
        total_potential_savings = 0
        for sub in unused_subscriptions:
            total_potential_savings += sub['cost']
            recommendations.append(
                f"Subscription '{sub['name']}' hasn't been used for {sub['days_unused']} days "
                f"(${sub['cost']:.2f}/month). Consider reviewing necessity and potential cancellation."
            )

        if total_potential_savings > 0:
            recommendations.append(
                f"Potential savings of ${total_potential_savings:.2f}/month by reviewing unused subscriptions."
            )

        return recommendations

    def _analyze_kpi_recommendations(self, goals_config: Dict[str, Any], current_data: Dict[str, Any]) -> List[str]:
        """
        Generate KPI-focused recommendations.
        """
        recommendations = []

        # Get current KPI values from current_data or defaults
        kpi_current_values = {}
        if 'kpi_values' in current_data:
            kpi_current_values = current_data['kpi_values']
        else:
            # If not provided, try to infer from other data
            # This is a basic example - in practice, you'd have more sophisticated inference
            if 'actual_revenue' in current_data and 'target_revenue' in current_data:
                if current_data['target_revenue'] != 0:
                    kpi_current_values['Revenue Achievement Rate'] = (
                        current_data['actual_revenue'] / current_data['target_revenue'] * 100
                    )

        # Check KPIs against targets
        all_kpis = get_kpis(goals_config) if goals_config else []

        for kpi in all_kpis:
            kpi_name = kpi.get('name', '')
            current_value = kpi_current_values.get(kpi_name, 0)
            target_value = kpi.get('target', 0)

            if target_value != 0:
                achievement_pct = (current_value / target_value) * 100

                # Generate recommendations based on achievement
                if achievement_pct < 80:
                    recommendations.append(
                        f"The KPI '{kpi_name}' is significantly below target ({achievement_pct:.1f}% of {target_value}). "
                        f"Review processes and strategies to improve performance in this area."
                    )
                elif achievement_pct < 95:
                    recommendations.append(
                        f"The KPI '{kpi_name}' is below target ({achievement_pct:.1f}% of {target_value}). "
                        f"Consider implementing improvement measures to reach target levels."
                    )
                elif achievement_pct > 110:
                    recommendations.append(
                        f"Excellent performance! The KPI '{kpi_name}' is exceeding target ({achievement_pct:.1f}% of {target_value}). "
                        f"Document successful strategies for replication in other areas."
                    )

        # Analyze KPI trends
        try:
            kpi_trends = self.tracker.get_kpi_trends(days_back=30)

            for kpi_name, trend_data in kpi_trends.items():
                if trend_data.get('trend') == 'declining':
                    recommendations.append(
                        f"The KPI '{kpi_name}' is showing a declining trend. "
                        f"Investigate causes and implement corrective actions."
                    )
                elif trend_data.get('trend') == 'improving':
                    recommendations.append(
                        f"The KPI '{kpi_name}' is improving. Continue current strategies that are driving positive results."
                    )
        except:
            pass  # Silently fail if trend analysis unavailable

        return recommendations

    def _days_remaining_in_month(self) -> int:
        """
        Calculate the number of days remaining in the current month.
        """
        today = datetime.now()
        # Get the first day of next month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        # Calculate difference
        last_day_of_month = next_month - timedelta(days=1)
        return (last_day_of_month - today).days + 1

    def _is_overdue(self, due_date_str: str) -> bool:
        """
        Check if a date is overdue (past due).
        """
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            return due_date.date() < datetime.now().date()
        except ValueError:
            return False

    def generate_ceo_briefing_recommendations(self, week_start: datetime, week_end: datetime) -> List[str]:
        """
        Generate specific recommendations for the weekly CEO briefing.

        Args:
            week_start: Start date of the week being briefed
            week_end: End date of the week being briefed

        Returns:
            List of recommendations specifically for the CEO briefing
        """
        # Load goals configuration
        goals_config = load_business_goals(str(self.vault_path))

        # Get current business data (this would come from various sources in a real implementation)
        current_data = {
            'actual_revenue': 45230.50,  # Placeholder - in real implementation this would come from actual data
            'target_revenue': 50000.00,  # Placeholder
            'kpi_values': {
                'Task Completion Rate': 92,  # Placeholder
                'Customer Acquisition Rate': 8  # Placeholder
            }
        }

        # Generate recommendations based on goals and current data
        recommendations = self.generate_recommendations(goals_config, current_data)

        # Add week-specific recommendations
        additional_recommendations = []

        # Check if month is ending soon
        days_remaining = self._days_remaining_in_month()
        if days_remaining <= 7:
            current_month = datetime.now().strftime('%B %Y')
            additional_recommendations.append(
                f"Month end approaches: Focus on closing deals and achieving monthly targets in {current_month}. "
                f"There are {days_remaining} days remaining to reach goals."
            )

        # Combine all recommendations
        all_recommendations = recommendations + additional_recommendations

        # Limit to top 5 recommendations to avoid overwhelming the CEO
        return all_recommendations[:5]


def generate_sample_recommendations():
    """
    Generate sample recommendations for testing purposes.
    """
    vault_path = "./AI_Employee_Vault"

    # Ensure Business_Goals.md exists
    goals_file = Path(vault_path) / "Business_Goals.md"
    if not goals_file.exists():
        print("Creating sample Business_Goals.md file...")
        from ceo_briefing_utils import generate_sample_briefing
        # Create the business goals file by calling the sample function indirectly
        pass  # The business_goals_utils already creates the file when needed

    engine = RecommendationEngine(vault_path)

    # Define week dates
    today = datetime.now()
    days_since_sunday = (today.weekday() + 1) % 7
    week_start = today - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=6)

    recommendations = engine.generate_ceo_briefing_recommendations(week_start, week_end)

    print("Generated CEO Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    return recommendations


if __name__ == "__main__":
    recommendations = generate_sample_recommendations()