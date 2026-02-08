"""
Historical Goal Tracking and Trend Analysis Module.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import csv
from collections import defaultdict


class HistoricalTracker:
    """
    Track historical data for goals and perform trend analysis.
    """
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)

        # Create a directory for historical data
        self.history_dir = self.vault_path / "History"
        self.history_dir.mkdir(exist_ok=True)

        # Subdirectories for different types of historical data
        self.revenue_history_dir = self.history_dir / "Revenue"
        self.kpi_history_dir = self.history_dir / "KPI"
        self.deadline_history_dir = self.history_dir / "Deadlines"
        self.subscription_history_dir = self.history_dir / "Subscriptions"

        # Create subdirectories
        for dir_path in [self.revenue_history_dir, self.kpi_history_dir,
                         self.deadline_history_dir, self.subscription_history_dir]:
            dir_path.mkdir(exist_ok=True)

    def log_revenue_data(self, date: str, revenue: float, target: float = None):
        """
        Log daily revenue data for historical tracking.

        Args:
            date: Date in YYYY-MM-DD format
            revenue: Actual revenue for the date
            target: Target revenue for the date (optional)
        """
        file_path = self.revenue_history_dir / f"revenue_daily.csv"

        # Check if file exists and write header if needed
        write_header = not file_path.exists()

        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'actual_revenue', 'target_revenue', 'variance']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if write_header:
                writer.writeheader()

            variance = revenue - (target or 0)
            writer.writerow({
                'date': date,
                'actual_revenue': revenue,
                'target_revenue': target or 0,
                'variance': variance
            })

    def log_kpi_data(self, kpi_name: str, date: str, value: float, target: float = None):
        """
        Log KPI data for historical tracking.

        Args:
            kpi_name: Name of the KPI
            date: Date in YYYY-MM-DD format
            value: Current value of the KPI
            target: Target value of the KPI (optional)
        """
        file_path = self.kpi_history_dir / f"{kpi_name.replace(' ', '_').replace('/', '_')}_daily.csv"

        # Check if file exists and write header if needed
        write_header = not file_path.exists()

        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'value', 'target', 'variance']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if write_header:
                writer.writeheader()

            variance = value - (target or 0)
            writer.writerow({
                'date': date,
                'value': value,
                'target': target or 0,
                'variance': variance
            })

    def log_deadline_status(self, deadline_name: str, date: str, status: str, days_remaining: int = None):
        """
        Log deadline status for historical tracking.

        Args:
            deadline_name: Name of the deadline/project
            date: Date in YYYY-MM-DD format
            status: Current status (e.g., "on_track", "at_risk", "overdue", "completed")
            days_remaining: Days remaining until deadline (optional)
        """
        file_path = self.deadline_history_dir / f"deadlines_daily.csv"

        # Check if file exists and write header if needed
        write_header = not file_path.exists()

        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'deadline_name', 'status', 'days_remaining']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if write_header:
                writer.writeheader()

            writer.writerow({
                'date': date,
                'deadline_name': deadline_name,
                'status': status,
                'days_remaining': days_remaining or 0
            })

    def get_revenue_trend(self, kpi_name: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Calculate trend for a KPI over the specified number of days.

        Args:
            kpi_name: Name of the KPI to analyze
            days_back: Number of days to look back for trend analysis

        Returns:
            Dictionary with trend analysis results
        """
        file_path = self.kpi_history_dir / f"{kpi_name.replace(' ', '_').replace('/', '_')}_daily.csv"

        if not file_path.exists():
            return {
                'trend': 'unknown',
                'slope': 0,
                'r_squared': 0,
                'data_points': 0,
                'avg_change_per_day': 0
            }

        # Read the CSV file
        import pandas as pd
        df = pd.read_csv(file_path)

        # Get the last 'days_back' days of data
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] >= datetime.now() - timedelta(days=days_back)]

        if len(df) < 2:
            return {
                'trend': 'insufficient_data',
                'slope': 0,
                'r_squared': 0,
                'data_points': len(df),
                'avg_change_per_day': 0
            }

        # Perform linear regression to find trend
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(df)), df['value'])

        # Calculate average change per day
        avg_change = slope

        # Determine trend direction
        trend_direction = "stable"
        if slope > 0.1:  # Adjust threshold as needed
            trend_direction = "improving"
        elif slope < -0.1:
            trend_direction = "declining"

        return {
            'trend': trend_direction,
            'slope': slope,
            'r_squared': r_value ** 2,
            'data_points': len(df),
            'avg_change_per_day': avg_change,
            'current_value': df['value'].iloc[-1] if len(df) > 0 else 0,
            'start_value': df['value'].iloc[0] if len(df) > 0 else 0
        }

    def get_revenue_performance(self, period: str = "monthly") -> Dict[str, Any]:
        """
        Get revenue performance metrics for a specified period.

        Args:
            period: Time period to analyze ("daily", "weekly", "monthly", "yearly")

        Returns:
            Dictionary with revenue performance metrics
        """
        file_path = self.revenue_history_dir / "revenue_daily.csv"

        if not file_path.exists():
            return {
                'total_revenue': 0,
                'target_revenue': 0,
                'achievement_rate': 0,
                'trend': 'unknown',
                'variance': 0
            }

        import pandas as pd
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])

        # Group by the specified period
        if period == "daily":
            grouped = df.groupby(df['date'].dt.date).sum()
        elif period == "weekly":
            grouped = df.groupby(df['date'].dt.to_period('W')).sum()
        elif period == "monthly":
            grouped = df.groupby(df['date'].dt.to_period('M')).sum()
        elif period == "yearly":
            grouped = df.groupby(df['date'].dt.to_period('Y')).sum()
        else:
            raise ValueError(f"Unsupported period: {period}")

        # Calculate metrics
        latest_period = grouped.iloc[-1] if len(grouped) > 0 else None

        if latest_period is not None:
            total_actual = latest_period['actual_revenue']
            total_target = latest_period['target_revenue']
            variance = latest_period['variance']
            achievement_rate = (total_actual / total_target * 100) if total_target != 0 else 0

            # Determine trend by comparing with previous period
            trend = "unknown"
            if len(grouped) > 1:
                prev_period = grouped.iloc[-2]
                if latest_period['actual_revenue'] > prev_period['actual_revenue']:
                    trend = "increasing"
                elif latest_period['actual_revenue'] < prev_period['actual_revenue']:
                    trend = "decreasing"
                else:
                    trend = "stable"
        else:
            total_actual = 0
            total_target = 0
            variance = 0
            achievement_rate = 0
            trend = "no_data"

        return {
            'total_revenue': total_actual,
            'target_revenue': total_target,
            'achievement_rate': achievement_rate,
            'trend': trend,
            'variance': variance
        }

    def get_kpi_trends(self, days_back: int = 30) -> Dict[str, Dict[str, Any]]:
        """
        Get trends for all tracked KPIs.

        Args:
            days_back: Number of days to look back for trend analysis

        Returns:
            Dictionary mapping KPI names to their trend analysis
        """
        trends = {}

        # Get all KPI files in the directory
        for file_path in self.kpi_history_dir.glob("*_daily.csv"):
            kpi_name = file_path.stem.replace("_daily", "").replace('_', ' ')
            trend_data = self.get_revenue_trend(kpi_name, days_back)
            trends[kpi_name] = trend_data

        return trends

    def generate_historical_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate a comprehensive historical report for a specified date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with comprehensive historical report
        """
        from datetime import datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        # Revenue performance
        revenue_performance = self.get_revenue_performance("monthly")

        # KPI trends
        kpi_trends = self.get_kpi_trends(days_back=30)

        # Collect all deadline statuses in the date range
        deadline_status_file = self.deadline_history_dir / "deadlines_daily.csv"
        deadline_summary = {}

        if deadline_status_file.exists():
            import pandas as pd
            df = pd.read_csv(deadline_status_file)
            df['date'] = pd.to_datetime(df['date'])

            # Filter for the date range
            filtered_df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]

            # Summarize by deadline
            for _, row in filtered_df.iterrows():
                deadline_name = row['deadline_name']
                if deadline_name not in deadline_summary:
                    deadline_summary[deadline_name] = {
                        'statuses': [],
                        'dates': [],
                        'latest_status': row['status'],
                        'days_remaining': row['days_remaining']
                    }
                deadline_summary[deadline_name]['statuses'].append(row['status'])
                deadline_summary[deadline_name]['dates'].append(row['date'].strftime('%Y-%m-%d'))

        return {
            'report_dates': {
                'start_date': start_date,
                'end_date': end_date
            },
            'revenue_analysis': revenue_performance,
            'kpi_trends': kpi_trends,
            'deadline_summary': deadline_summary,
            'generated_at': datetime.now().isoformat()
        }


def calculate_revenue_trend(revenue_data: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    Calculate trend for revenue data.

    Args:
        revenue_data: List of dictionaries with 'date' and 'amount' keys

    Returns:
        Dictionary with trend analysis
    """
    if len(revenue_data) < 2:
        return {
            'trend_direction': 'insufficient_data',
            'average_growth': 0,
            'r_squared': 0
        }

    # Sort by date
    sorted_data = sorted(revenue_data, key=lambda x: x['date'])

    # Extract values for calculation
    values = [item['amount'] for item in sorted_data]

    # Calculate basic trend metrics
    start_val = values[0]
    end_val = values[-1]

    if start_val != 0:
        total_change = ((end_val - start_val) / start_val) * 100
        avg_change = sum(values[i+1] - values[i] for i in range(len(values)-1)) / (len(values) - 1)
    else:
        total_change = float('inf') if end_val > 0 else 0
        avg_change = end_val / len(values) if len(values) > 0 else 0

    # Determine trend direction
    if total_change > 5:  # Adjust threshold as needed
        trend_direction = "positive"
    elif total_change < -5:
        trend_direction = "negative"
    else:
        trend_direction = "neutral"

    return {
        'trend_direction': trend_direction,
        'total_change_percent': round(total_change, 2),
        'average_change_per_period': round(avg_change, 2),
        'data_points': len(values)
    }


def generate_weekly_kpi_summary(kpi_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Generate a summary of KPI performance over the past week.

    Args:
        kpi_data: Dictionary mapping KPI names to their historical data

    Returns:
        Dictionary with KPI summary
    """
    summary = {}

    for kpi_name, data_points in kpi_data.items():
        if not data_points:
            summary[kpi_name] = {
                'status': 'no_data',
                'current_value': 0,
                'average_trend': 'stable'
            }
            continue

        # Calculate metrics
        values = [dp['value'] for dp in data_points if 'value' in dp]
        if not values:
            summary[kpi_name] = {
                'status': 'no_valid_data',
                'current_value': 0,
                'average_trend': 'stable'
            }
            continue

        current_value = values[-1]
        avg_value = sum(values) / len(values)

        # Determine trend based on last few values
        if len(values) >= 3:
            recent_avg = sum(values[-3:]) / 3
            if recent_avg > avg_value * 1.05:  # 5% above average
                trend = "improving"
            elif recent_avg < avg_value * 0.95:  # 5% below average
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        summary[kpi_name] = {
            'status': 'tracked',
            'current_value': current_value,
            'average_value': avg_value,
            'average_trend': trend,
            'data_points_count': len(values)
        }

    return summary


if __name__ == "__main__":
    # Example usage
    tracker = HistoricalTracker()

    # Log some sample data
    today = datetime.now().strftime('%Y-%m-%d')
    tracker.log_revenue_data(today, 12500.00, 15000.00)
    tracker.log_kpi_data("Customer Acquisition Rate", today, 12.5, 10.0)
    tracker.log_deadline_status("Q1 Product Launch", today, "on_track", 15)

    # Get a report
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = today
    report = tracker.generate_historical_report(start_date, end_date)

    print("Historical Report Generated:")
    print(json.dumps(report, indent=2, default=str))