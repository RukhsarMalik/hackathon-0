#!/usr/bin/env python3
"""
Watchdog Process Monitoring Service - Monitors system processes and restarts crashed ones.
"""
import os
import sys
import time
import subprocess
import psutil
import json
import signal
from pathlib import Path
from datetime import datetime
from threading import Thread


class ProcessMonitor:
    """Monitors specific processes and manages their lifecycle."""

    STOP_FILE = Path(__file__).parent / ".pids" / "watchdog.stop"

    def __init__(self, vault_path="./AI_Employee_Vault", pids_dir="./.pids"):
        self.vault_path = Path(vault_path)
        self.pids_dir = Path(pids_dir)
        self.pids_dir.mkdir(exist_ok=True)
        # Remove stale stop file on fresh start
        self.STOP_FILE.unlink(missing_ok=True)

        # Define the processes to monitor
        self.monitored_processes = {
            'orchestrator': {
                'cmd': ['python3', 'orchestrator.py'],
                'restart_limit': 5,  # Max 5 restarts per hour
                'restart_window': 3600,  # 1 hour in seconds
                'restart_times': []
            },
            'gmail_watcher': {
                'cmd': ['python3', 'gmail_watcher.py'],
                'restart_limit': 5,
                'restart_window': 3600,
                'restart_times': []
            },
            'linkedin_watcher': {
                'cmd': ['python3', 'linkedin_watcher.py'],
                'restart_limit': 5,
                'restart_window': 3600,
                'restart_times': []
            },
            'facebook_watcher': {
                'cmd': ['python3', 'facebook_watcher.py'],
                'restart_limit': 5,
                'restart_window': 3600,
                'restart_times': []
            },
            'approval_watcher': {
                'cmd': ['python3', 'approval_watcher.py'],
                'restart_limit': 5,
                'restart_window': 3600,
                'restart_times': []
            }
        }

        # Track process status and health checks
        self.process_status = {}
        self.health_check_counts = {}  # Tracks consecutive health checks
        self.last_error = {}
        self.restart_counts = {}  # Hourly restart counts
        self.last_restart_reset = time.time()

    def get_pid_file(self, service_name):
        """Get the PID file path for a service."""
        return self.pids_dir / f"{service_name}.pid"

    def read_pid_file(self, service_name):
        """Read the PID from file."""
        pid_file = self.get_pid_file(service_name)
        try:
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return None

    def write_pid_file(self, service_name, pid):
        """Write the PID to file."""
        pid_file = self.get_pid_file(service_name)
        try:
            with open(pid_file, 'w') as f:
                f.write(str(pid))
        except IOError:
            print(f"Error writing PID file for {service_name}")

    def is_process_running(self, service_name):
        """Check if the process for a service is running."""
        # First, try reading from the PID file
        pid = self.read_pid_file(service_name)
        if pid:
            try:
                proc = psutil.Process(pid)
                # Verify it's the correct process
                if self.is_correct_process(proc, service_name):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # PID file exists but process doesn't, remove the file
                self.get_pid_file(service_name).unlink(missing_ok=True)

        # If no PID file or wrong process, search by command
        for proc in psutil.process_iter(['pid', 'cmdline', 'name']):
            try:
                if self.is_correct_process(proc, service_name):
                    # Update the PID file
                    self.write_pid_file(service_name, proc.info['pid'])
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return None

    def is_correct_process(self, proc, service_name):
        """Check if the process matches the service we're looking for."""
        try:
            if service_name == 'orchestrator':
                # Check if the process is running orchestrator.py
                cmdline = proc.cmdline()
                return 'orchestrator.py' in ' '.join(cmdline)
            elif service_name == 'gmail_watcher':
                cmdline = proc.cmdline()
                return 'gmail_watcher.py' in ' '.join(cmdline)
            elif service_name == 'linkedin_watcher':
                cmdline = proc.cmdline()
                return 'linkedin_watcher.py' in ' '.join(cmdline)
            elif service_name == 'facebook_watcher':
                cmdline = proc.cmdline()
                return 'facebook_watcher.py' in ' '.join(cmdline)
            elif service_name == 'approval_watcher':
                cmdline = proc.cmdline()
                return 'approval_watcher.py' in ' '.join(cmdline)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return False
        return False

    def start_process(self, service_name):
        """Start a process for a service."""
        config = self.monitored_processes[service_name]
        cmd = config['cmd']

        try:
            # Start the process in the gold directory
            proc = subprocess.Popen(
                cmd,
                cwd=self.vault_path.parent,  # Parent directory is the gold directory
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

            # Write the PID to file
            self.write_pid_file(service_name, proc.pid)

            # Log the start
            self.log_service_event(service_name, 'process_started', f'Started process with PID {proc.pid}')

            return proc
        except Exception as e:
            print(f"Error starting {service_name}: {e}")
            self.log_service_event(service_name, 'start_failed', f'Failed to start: {str(e)}')
            return None

    def is_stopped(self):
        """Check if watchdog has been told to stop (graceful shutdown)."""
        return self.STOP_FILE.exists()

    def check_and_restart_process(self, service_name):
        """Check if a process is running and restart if needed."""
        # If stop file exists, do NOT restart anything
        if self.is_stopped():
            return True

        # Update hourly restart counts
        current_time = time.time()
        if current_time - self.last_restart_reset > 3600:  # 1 hour
            self.restart_counts.clear()
            self.last_restart_reset = current_time

        proc = self.is_process_running(service_name)

        if proc:
            # Process is running, update status
            status = {
                'service_name': service_name,
                'status': 'healthy',
                'pid': proc.pid,
                'last_heartbeat': datetime.now().isoformat(),
                'uptime_seconds': int(time.time() - proc.create_time()),
                'restart_count': self.restart_counts.get(service_name, 0)
            }
            self.process_status[service_name] = status

            # Update health check counter
            self.health_check_counts[service_name] = self.health_check_counts.get(service_name, 0) + 1

            # Reset consecutive error count if process is healthy
            if service_name in self.last_error and 'error' in self.last_error[service_name]:
                del self.last_error[service_name]['error']

            return True
        else:
            # Process is not running, need to restart
            self.update_service_status(service_name, 'down')

            # Check if we're within restart limits
            restart_count = self.restart_counts.get(service_name, 0)
            if restart_count >= self.monitored_processes[service_name]['restart_limit']:
                print(f"Restart limit exceeded for {service_name}, not restarting")
                self.log_service_event(service_name, 'restart_limited',
                                     f'Restart limit exceeded ({restart_count} restarts in last hour)')
                return False

            print(f"Restarting {service_name}...")
            new_proc = self.start_process(service_name)

            if new_proc:
                self.restart_counts[service_name] = self.restart_counts.get(service_name, 0) + 1
                self.log_service_event(service_name, 'process_restarted',
                                     f'Process restarted with PID {new_proc.pid}')
                return True
            else:
                self.log_service_event(service_name, 'restart_failed', 'Failed to restart process')
                return False

    def update_service_status(self, service_name, status, error_msg=None):
        """Update the service status."""
        uptime_seconds = 0
        pid = self.read_pid_file(service_name)

        status_info = {
            'service_name': service_name,
            'status': status,
            'pid': pid,
            'last_heartbeat': datetime.now().isoformat(),
            'restart_count': self.restart_counts.get(service_name, 0),
            'uptime_seconds': uptime_seconds
        }

        if error_msg:
            status_info['last_error'] = error_msg
            self.last_error[service_name] = {'error': error_msg}

        self.process_status[service_name] = status_info

    def log_service_event(self, service_name, event_type, message):
        """Log service events to the audit log."""
        try:
            # Import the audit logging module
            from audit_logging import audit_logger
            correlation_id = f"watchdog_{service_name}_{int(time.time())}"

            audit_logger.write_log(
                event_type=event_type,
                service=f"watchdog_{service_name}",
                action=message[:50],  # Shortened for action field
                correlation_id=correlation_id,
                status="info" if "restart" in event_type or "start" in event_type else "error",
                result_summary=message,
                tags=["watchdog", "monitoring", service_name, event_type]
            )
        except ImportError:
            print(f"Audit logging module not available: {message}")
        except Exception as e:
            print(f"Error writing audit log: {e}")

    def update_dashboard_status(self):
        """Update the Dashboard.md with current service status."""
        try:
            dashboard_path = self.vault_path / "Dashboard.md"
            if not dashboard_path.exists():
                print("Dashboard.md not found, skipping status update")
                return

            content = dashboard_path.read_text(encoding='utf-8')

            # Find the Services section and update it
            lines = content.split('\n')
            new_lines = []
            in_services_section = False
            services_section_replaced = False

            for line in lines:
                if line.strip() == '## Services':
                    in_services_section = True
                    new_lines.append(line)
                    # Add the current service statuses
                    for service_name, status in self.process_status.items():
                        status_text = status.get('status', 'unknown')
                        pid = status.get('pid', 'N/A')
                        uptime = status.get('uptime_seconds', 0)

                        new_lines.append(f"- **{service_name}**: {status_text} (PID: {pid}, Uptime: {uptime}s)")
                    services_section_replaced = True
                elif in_services_section and line.strip().startswith('- **') and ('orchestrator' in line or 'watcher' in line):
                    # Skip old service status lines since we're replacing the whole section
                    continue
                elif in_services_section and line.strip().startswith('#') and line.strip() != '## Services':
                    # End of Services section
                    in_services_section = False
                    new_lines.append(line)
                else:
                    new_lines.append(line)

            if not services_section_replaced:
                # If there was no Services section, add it
                new_lines.extend([
                    '',
                    '## Services',
                ])
                for service_name, status in self.process_status.items():
                    status_text = status.get('status', 'unknown')
                    pid = status.get('pid', 'N/A')
                    uptime = status.get('uptime_seconds', 0)

                    new_lines.append(f"- **{service_name}**: {status_text} (PID: {pid}, Uptime: {uptime}s)")

            # Write back to file
            dashboard_path.write_text('\n'.join(new_lines), encoding='utf-8')

        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def run_health_check_cycle(self):
        """Run one cycle of health checks for all monitored processes."""
        print("Running health check cycle...")

        for service_name in self.monitored_processes.keys():
            self.check_and_restart_process(service_name)

        # Update dashboard with current status
        self.update_dashboard_status()

        # Clean up old restart counts
        current_time = time.time()
        for service_name in list(self.restart_counts.keys()):
            # This implementation keeps track of restarts per hour
            # We could add more sophisticated cleanup here if needed
            pass


def run_watchdog():
    """Main watchdog function."""
    monitor = ProcessMonitor()

    print("Starting Watchdog Process Monitoring Service...")
    print("Monitoring processes:")
    for service in monitor.monitored_processes.keys():
        print(f"  - {service}")

    try:
        while True:
            monitor.run_health_check_cycle()

            # Wait before next check
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\nShutting down Watchdog Process Monitoring Service...")
        return


if __name__ == "__main__":
    run_watchdog()