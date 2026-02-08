#!/usr/bin/env python3
"""
Script to schedule the weekly CEO briefing generation.
"""
import os
import sys
from pathlib import Path
import subprocess
import platform


def setup_cron_job():
    """
    Setup a cron job to run the weekly briefing generation every Sunday at 11 PM.
    """
    if platform.system() == "Windows":
        setup_windows_task_scheduler()
    else:
        setup_unix_cron_job()


def setup_unix_cron_job():
    """
    Setup a cron job on Unix-like systems to run the weekly briefing generation every Sunday at 11 PM.
    """
    print("Setting up Unix cron job...")

    # Determine the current directory and construct the path to weekly_audit.py
    current_dir = Path(__file__).parent.resolve()
    script_path = current_dir / "weekly_audit.py"

    # Construct the command to run
    python_path = sys.executable
    command = f"{python_path} {script_path}"

    # Cron job entry: minute hour day month weekday command
    cron_job = f"0 23 * * 0 {command} >> {current_dir}/logs/weekly_audit.log 2>&1"

    # Read existing crontab
    try:
        existing_crontab = subprocess.run(['crontab', '-l'], capture_output=True, text=True, check=False)
        existing_lines = existing_crontab.stdout.strip().split('\n') if existing_crontab.stdout.strip() else []

        # Remove any existing entries for this script
        filtered_lines = [line for line in existing_lines if script_path.name not in line]

        # Add the new job
        filtered_lines.append(cron_job)

        # Write the updated crontab back
        updated_crontab = '\n'.join(filtered_lines) + '\n'

        # Write to a temporary file and install
        temp_file = '/tmp/temp_crontab'
        with open(temp_file, 'w') as f:
            f.write(updated_crontab)

        subprocess.run(['crontab', temp_file], check=True)
        os.remove(temp_file)

        print("Unix cron job installed successfully!")
        print(f"Cron job: {cron_job}")
    except subprocess.CalledProcessError:
        print("Failed to access crontab. Make sure you have the necessary permissions.")
    except Exception as e:
        print(f"Error setting up cron job: {e}")


def setup_windows_task_scheduler():
    """
    Setup a Windows Task Scheduler task to run the weekly briefing generation every Sunday at 11 PM.
    """
    print("Setting up Windows Task Scheduler task...")

    current_dir = Path(__file__).parent.resolve()
    script_path = current_dir / "weekly_audit.py"
    python_path = sys.executable

    # Create the PowerShell command to run the script
    # We'll use a batch file as an intermediate to make the scheduling easier
    batch_file_path = current_dir / "run_weekly_audit.bat"

    batch_content = f'''@echo off
cd /d "{current_dir}"
"{python_path}" "{script_path}"
'''

    # Write the batch file
    with open(batch_file_path, 'w') as f:
        f.write(batch_content)

    # Create the schtasks command
    task_name = "Weekly CEObriefing Generation"
    command = [
        'schtasks',
        '/CREATE',
        '/TN', f'"{task_name}"',
        '/TR', f'"{batch_file_path}"',
        '/SC', 'WEEKLY',
        '/D', 'SUN',  # Sunday
        '/ST', '23:00',  # 11:00 PM
        '/MO', '1',  # Every 1 week
        '/F'  # Force (overwrite if exists)
    ]

    try:
        result = subprocess.run(' '.join(command), shell=True, capture_output=True, text=True, check=True)
        print("Windows Task Scheduler task created successfully!")
        print(f"Task: {task_name}")
        print(f"Runs: Weekly on Sunday at 11:00 PM")
        print(f"Command: {batch_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create Windows Task Scheduler task: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Error setting up Windows Task Scheduler: {e}")


def remove_scheduled_job():
    """
    Remove the scheduled job (cron or Task Scheduler).
    """
    if platform.system() == "Windows":
        remove_windows_task()
    else:
        remove_unix_cron_job()


def remove_unix_cron_job():
    """
    Remove the Unix cron job for weekly briefing generation.
    """
    try:
        # Read existing crontab
        existing_crontab = subprocess.run(['crontab', '-l'], capture_output=True, text=True, check=False)
        if not existing_crontab.stdout.strip():
            print("No crontab entries found.")
            return

        existing_lines = existing_crontab.stdout.strip().split('\n')

        # Remove entries containing the script path
        current_dir = Path(__file__).parent.resolve()
        script_path = current_dir / "weekly_audit.py"

        filtered_lines = [line for line in existing_lines if script_path.name not in line]

        # Write the updated crontab back
        if len(filtered_lines) == len(existing_lines):
            print("No matching cron jobs found to remove.")
            return

        updated_crontab = '\n'.join(filtered_lines) + '\n' if filtered_lines else ''

        if updated_crontab:
            # Write to a temporary file and install
            temp_file = '/tmp/temp_crontab'
            with open(temp_file, 'w') as f:
                f.write(updated_crontab)

            subprocess.run(['crontab', temp_file], check=True)
            os.remove(temp_file)
        else:
            # Remove crontab entirely if no jobs left
            subprocess.run(['crontab', '-r'], check=True)

        print("Unix cron job removed successfully!")
    except subprocess.CalledProcessError:
        print("Failed to access crontab. Make sure you have the necessary permissions.")
    except Exception as e:
        print(f"Error removing cron job: {e}")


def remove_windows_task():
    """
    Remove the Windows Task Scheduler task for weekly briefing generation.
    """
    task_name = "Weekly CEObriefing Generation"
    command = [
        'schtasks',
        '/DELETE',
        '/TN', f'"{task_name}"',
        '/F'  # Force deletion without prompt
    ]

    try:
        result = subprocess.run(' '.join(command), shell=True, capture_output=True, text=True, check=True)
        print("Windows Task Scheduler task removed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove Windows Task Scheduler task: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Error removing Windows Task Scheduler task: {e}")


def test_scheduling():
    """
    Test the scheduling by running the weekly audit script manually.
    """
    print("Testing weekly audit script...")

    current_dir = Path(__file__).parent.resolve()
    script_path = current_dir / "weekly_audit.py"
    python_path = sys.executable

    try:
        result = subprocess.run([python_path, str(script_path)],
                              cwd=current_dir,
                              capture_output=True,
                              text=True,
                              timeout=60)  # 60 second timeout

        print("Test run completed!")
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("Test run timed out after 60 seconds.")
    except Exception as e:
        print(f"Error running test: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage weekly CEO briefing scheduling")
    parser.add_argument('action', choices=['setup', 'remove', 'test'],
                       help="Action to perform: setup, remove, or test")

    args = parser.parse_args()

    if args.action == 'setup':
        print("Setting up weekly CEO briefing scheduling...")
        setup_cron_job()
    elif args.action == 'remove':
        print("Removing weekly CEO briefing scheduling...")
        remove_scheduled_job()
    elif args.action == 'test':
        print("Testing weekly CEO briefing generation...")
        test_scheduling()