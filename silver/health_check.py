#!/usr/bin/env python3
"""
Health Check - Verifies all AI Employee services are running and system is healthy.
"""
import os
import re
import sys
import json
import signal
import time
from pathlib import Path
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
PID_DIR = Path('.pids')
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DASHBOARD = VAULT_PATH / "Dashboard.md"
MAX_DASHBOARD_AGE_HOURS = 24
MAX_TASK_AGE_HOURS = 2

EXPECTED_SERVICES = ['gmail', 'filesystem', 'linkedin', 'orchestrator', 'approval', 'mcp_email']


def check_process_alive(pid_file):
    """
    Check if a process is alive by reading its PID file and sending signal 0.

    Args:
        pid_file: Path to the PID file

    Returns:
        Tuple of (alive: bool, pid: int or None, message: str)
    """
    if not pid_file.exists():
        return False, None, "PID file not found"

    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, Exception):
        return False, None, "Invalid PID file"

    try:
        os.kill(pid, 0)
        return True, pid, "Running"
    except ProcessLookupError:
        return False, pid, f"Process {pid} not found"
    except PermissionError:
        # Process exists but we can't signal it — still alive
        return True, pid, f"Running (PID {pid})"


def check_dashboard_freshness():
    """
    Check if Dashboard.md has been updated within MAX_DASHBOARD_AGE_HOURS.

    Returns:
        Tuple of (fresh: bool, last_updated: str, message: str)
    """
    if not DASHBOARD.exists():
        return False, None, "Dashboard.md not found"

    try:
        content = DASHBOARD.read_text(encoding='utf-8')
        match = re.search(r'last_updated:\s*(\S+)', content)
        if not match:
            return False, None, "No last_updated field found"

        last_updated_str = match.group(1)
        # Parse ISO format (handle both with and without timezone)
        last_updated_str = last_updated_str.replace('Z', '+00:00')
        try:
            last_updated = datetime.fromisoformat(last_updated_str)
            # Make naive for comparison
            last_updated = last_updated.replace(tzinfo=None)
        except ValueError:
            return False, last_updated_str, f"Cannot parse date: {last_updated_str}"

        age = datetime.now() - last_updated
        if age > timedelta(hours=MAX_DASHBOARD_AGE_HOURS):
            return False, last_updated_str, f"Stale ({age.total_seconds()/3600:.1f}h old)"
        else:
            return True, last_updated_str, f"Fresh ({age.total_seconds()/3600:.1f}h old)"

    except Exception as e:
        return False, None, f"Error reading Dashboard: {e}"


def check_stuck_tasks():
    """
    List tasks in Needs_Action/ that are older than MAX_TASK_AGE_HOURS.

    Returns:
        Tuple of (has_stuck: bool, stuck_files: list, message: str)
    """
    if not NEEDS_ACTION.exists():
        return False, [], "Needs_Action/ not found"

    now = time.time()
    stuck = []

    for f in NEEDS_ACTION.glob('*.md'):
        # Skip skill files
        if f.name.startswith('SKILL_') or f.name == 'SKILLS.md':
            continue

        age_hours = (now - f.stat().st_mtime) / 3600
        if age_hours > MAX_TASK_AGE_HOURS:
            stuck.append((f.name, f"{age_hours:.1f}h"))

    if stuck:
        return True, stuck, f"{len(stuck)} stuck task(s)"
    else:
        return False, [], "No stuck tasks"


def run_health_check(output_json=False):
    """
    Run all health checks and print results.

    Args:
        output_json: If True, output results as JSON

    Returns:
        Exit code: 0 if healthy, 1 if issues found
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'dashboard': {},
        'stuck_tasks': {},
        'overall': 'HEALTHY',
    }

    issues = 0

    # Check services
    print("\n=== Service Status ===")
    print(f"{'Service':<15} {'Status':<10} {'PID':<8} {'Details'}")
    print("-" * 55)

    for service in EXPECTED_SERVICES:
        pid_file = PID_DIR / f"{service}.pid"
        alive, pid, message = check_process_alive(pid_file)
        status = "UP" if alive else "DOWN"
        pid_str = str(pid) if pid else "N/A"

        if not alive:
            issues += 1

        print(f"{service:<15} {status:<10} {pid_str:<8} {message}")
        results['services'][service] = {
            'alive': alive,
            'pid': pid,
            'message': message,
        }

    # Check dashboard
    print("\n=== Dashboard Status ===")
    fresh, last_updated, message = check_dashboard_freshness()
    status = "FRESH" if fresh else "STALE"
    if not fresh:
        issues += 1
    print(f"Status: {status} | Last Updated: {last_updated or 'N/A'} | {message}")
    results['dashboard'] = {
        'fresh': fresh,
        'last_updated': last_updated,
        'message': message,
    }

    # Check stuck tasks
    print("\n=== Stuck Tasks ===")
    has_stuck, stuck_files, message = check_stuck_tasks()
    if has_stuck:
        issues += 1
        for name, age in stuck_files:
            print(f"  STUCK: {name} ({age} old)")
    else:
        print(f"  {message}")
    results['stuck_tasks'] = {
        'has_stuck': has_stuck,
        'files': [{'name': n, 'age': a} for n, a in stuck_files],
        'message': message,
    }

    # Overall
    if issues > 0:
        results['overall'] = 'UNHEALTHY'
    print(f"\n=== Overall: {results['overall']} ({issues} issue(s)) ===\n")

    if output_json:
        print(json.dumps(results, indent=2))

    return 0 if issues == 0 else 1


def main():
    """Main entry point with argument parsing."""
    output_json = '--json' in sys.argv
    exit_code = run_health_check(output_json=output_json)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
