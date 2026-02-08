"""
Structured JSON logging module for audit trails.
"""
import json
import os
from datetime import datetime
from pathlib import Path


class AuditLogger:
    """A structured JSON logger for audit trails."""

    def __init__(self, log_directory="Logs/Audit"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

    def write_log(self, event_type, service, action, correlation_id, status,
                  duration_ms=None, result_summary="", error_details=None,
                  tags=None, user_context=""):
        """
        Write a structured JSON audit log entry.

        Args:
            event_type: Type of event (mcp_call, task_processed, service_monitor, error_event)
            service: Service name (orchestrator, gmail_watcher, etc.)
            action: Specific action taken
            correlation_id: Unique identifier for the task/session
            status: Result status (success, failure, partial_success)
            duration_ms: Duration in milliseconds (optional)
            result_summary: Brief description of the outcome
            error_details: Error information if status is failure (optional)
            tags: Additional tags for categorization (optional)
            user_context: Context of triggering event (optional)
        """
        if tags is None:
            tags = []

        audit_entry = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "event_type": event_type,
            "service": service,
            "action": action,
            "correlation_id": correlation_id,
            "status": status,
            "duration_ms": duration_ms,
            "input_size_bytes": len(result_summary.encode('utf-8')) if result_summary else 0,
            "result_summary": result_summary,
            "user_context": user_context
        }

        if error_details:
            audit_entry["error_details"] = error_details

        if tags:
            audit_entry["tags"] = tags

        # Write to daily audit log file
        log_date = datetime.now().strftime('%Y-%m-%d')
        audit_log_file = self.log_directory / f"{log_date}_audit.json"

        try:
            # Append the log entry to the file
            with open(audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            print(f"AuditLogger failed to write log: {e}")

    def cleanup_old_logs(self, days_to_keep=90):
        """
        Clean up audit log files older than the specified number of days.

        Args:
            days_to_keep: Number of days to retain logs (default: 90)
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        for log_file in self.log_directory.glob("*_audit.json"):
            # Extract date from filename (assuming format YYYY-MM-DD_audit.json)
            try:
                file_date_str = log_file.name.split('_audit.json')[0]
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')

                if file_date < cutoff_date:
                    log_file.unlink()  # Remove old log file
                    print(f"Cleaned up old audit log: {log_file.name}")
            except ValueError:
                # Skip files with unexpected naming
                continue

    def rotate_logs_if_needed(self):
        """
        Rotate logs if the current daily log is getting too large.
        """
        today = datetime.now().strftime('%Y-%m-%d')
        current_log_file = self.log_directory / f"{today}_audit.json"

        if current_log_file.exists():
            # Get file size in bytes
            file_size = current_log_file.stat().st_size

            # Rotate if file is larger than 10MB (adjustable)
            MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

            if file_size > MAX_SIZE_BYTES:
                # Archive the current file with a timestamp
                timestamp = datetime.now().strftime('%H%M%S')
                archive_name = f"{today}_audit_{timestamp}_archived.json"
                archive_path = self.log_directory / archive_name

                current_log_file.rename(archive_path)
                print(f"Rotated audit log: {current_log_file.name} -> {archive_name}")


class AuditLogViewer:
    """A viewer for analyzing audit log files."""

    def __init__(self, log_directory="Logs/Audit"):
        self.log_directory = Path(log_directory)

    def read_daily_logs(self, date_str: str) -> list:
        """
        Read all audit log entries for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            List of log entries
        """
        log_file = self.log_directory / f"{date_str}_audit.json"

        if not log_file.exists():
            return []

        entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON in {log_file.name} at line {line_num}")

        return entries

    def search_logs(self, filters: dict) -> list:
        """
        Search audit logs with specified filters.

        Args:
            filters: Dictionary of filter criteria (e.g., service, event_type, status)

        Returns:
            List of matching log entries
        """
        all_entries = []

        # Get all log files
        log_files = list(self.log_directory.glob("*_audit.json"))

        # Sort by date (most recent first)
        log_files.sort(key=lambda x: x.name, reverse=True)

        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())

                        # Apply filters
                        match = True
                        for key, value in filters.items():
                            if key not in entry or entry[key] != value:
                                match = False
                                break

                        if match:
                            all_entries.append(entry)
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines

        return all_entries

    def get_service_statistics(self, date_str: str = None) -> dict:
        """
        Get statistics for services for a given date.

        Args:
            date_str: Date in YYYY-MM-DD format (if None, gets recent logs)

        Returns:
            Dictionary with service statistics
        """
        if date_str:
            entries = self.read_daily_logs(date_str)
        else:
            # Get entries from the last few days
            import datetime
            recent_entries = []
            for i in range(7):  # Last 7 days
                day = datetime.datetime.now() - datetime.timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                recent_entries.extend(self.read_daily_logs(day_str))
            entries = recent_entries

        stats = {}
        for entry in entries:
            service = entry.get('service', 'unknown')
            if service not in stats:
                stats[service] = {
                    'total_events': 0,
                    'success_count': 0,
                    'failure_count': 0,
                    'avg_duration_ms': 0,
                    'events': []
                }

            stats[service]['total_events'] += 1
            stats[service]['events'].append(entry)

            if entry.get('status') == 'success':
                stats[service]['success_count'] += 1
            elif entry.get('status') == 'failure':
                stats[service]['failure_count'] += 1

        # Calculate averages
        for service, service_stats in stats.items():
            durations = [e.get('duration_ms', 0) for e in service_stats['events'] if e.get('duration_ms')]
            if durations:
                service_stats['avg_duration_ms'] = sum(durations) / len(durations)

        return stats

    def generate_summary_report(self, days_back: int = 7) -> str:
        """
        Generate a summary report of audit logs for the past N days.

        Args:
            days_back: Number of days to include in the report

        Returns:
            String summary report
        """
        import datetime

        report_lines = []
        report_lines.append(f"Audit Log Summary - Last {days_back} Days")
        report_lines.append("=" * 40)

        # Get statistics
        stats = self.get_service_statistics()

        # Add overall stats
        total_events = sum(s['total_events'] for s in stats.values())
        total_success = sum(s['success_count'] for s in stats.values())
        total_failures = sum(s['failure_count'] for s in stats.values())

        report_lines.append(f"Total Events: {total_events}")
        report_lines.append(f"Successful: {total_success}")
        report_lines.append(f"Failed: {total_failures}")
        if total_events > 0:
            success_rate = (total_success / total_events) * 100
            report_lines.append(f"Success Rate: {success_rate:.2f}%")

        report_lines.append("")
        report_lines.append("Service Breakdown:")
        report_lines.append("-" * 20)

        for service, service_stats in sorted(stats.items(),
                                          key=lambda x: x[1]['total_events'], reverse=True):
            if service_stats['total_events'] > 0:  # Only show services with activity
                report_lines.append(f"{service}: {service_stats['total_events']} events "
                                  f"({service_stats['success_count']} success, "
                                  f"{service_stats['failure_count']} failures)")
                if service_stats['avg_duration_ms'] > 0:
                    report_lines.append(f"  Avg Duration: {service_stats['avg_duration_ms']:.2f}ms")

        return "\n".join(report_lines)

    def find_error_patterns(self, days_back: int = 7) -> dict:
        """
        Identify patterns in error logs over the specified number of days.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with error pattern analysis
        """
        import datetime

        # Get all entries from the last N days
        all_entries = []
        for i in range(days_back):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            all_entries.extend(self.read_daily_logs(day_str))

        # Filter for errors
        error_entries = [entry for entry in all_entries if entry.get('status') == 'failure']

        # Analyze patterns
        error_patterns = {
            'by_service': {},
            'by_type': {},
            'by_time': {},  # Time of day when errors occur
            'common_messages': {},
            'total_errors': len(error_entries)
        }

        for entry in error_entries:
            service = entry.get('service', 'unknown')
            event_type = entry.get('event_type', 'unknown')

            # Count by service
            error_patterns['by_service'][service] = error_patterns['by_service'].get(service, 0) + 1

            # Count by event type
            error_patterns['by_type'][event_type] = error_patterns['by_type'].get(event_type, 0) + 1

            # Extract time of day (hour)
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    error_patterns['by_time'][hour] = error_patterns['by_time'].get(hour, 0) + 1
                except:
                    pass  # Skip if timestamp is malformed

            # Extract error messages
            error_details = entry.get('error_details', {})
            if 'message' in error_details:
                message = error_details['message'][:100]  # Truncate long messages
                error_patterns['common_messages'][message] = error_patterns['common_messages'].get(message, 0) + 1

        return error_patterns

    def export_filtered_logs(self, output_file: str, filters: dict = None, days_back: int = 7):
        """
        Export filtered audit logs to a file for detailed analysis.

        Args:
            output_file: Path to the output file
            filters: Dictionary of filters to apply
            days_back: Number of days to include in the export
        """
        import datetime

        # Get entries based on filters
        if filters:
            filtered_entries = self.search_logs(filters)
        else:
            # Get all entries from the last N days
            filtered_entries = []
            for i in range(days_back):
                day = datetime.datetime.now() - datetime.timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                filtered_entries.extend(self.read_daily_logs(day_str))

        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in filtered_entries:
                f.write(json.dumps(entry) + '\n')

        print(f"Exported {len(filtered_entries)} log entries to {output_file}")

    def archive_logs(self, cutoff_date: str = None, days_old: int = 365):
        """
        Archive audit logs older than the specified date or number of days.

        Args:
            cutoff_date: Date in YYYY-MM-DD format (alternative to days_old)
            days_old: Number of days old logs must be to archive (default: 365 for yearly archiving)
        """
        import zipfile
        import datetime as dt_module
        from datetime import datetime

        if cutoff_date:
            cutoff = datetime.strptime(cutoff_date, '%Y-%m-%d')
        else:
            cutoff = datetime.now() - dt_module.timedelta(days=days_old)

        # Find all log files that are older than cutoff
        old_files = []
        for log_file in self.log_directory.glob("*_audit.json"):
            # Extract date from filename (assuming format YYYY-MM-DD_audit.json)
            try:
                file_date_str = log_file.name.split('_audit.json')[0]
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')

                if file_date < cutoff:
                    old_files.append(log_file)
            except ValueError:
                # Skip files with unexpected naming
                continue

        if not old_files:
            print(f"No log files older than {cutoff.strftime('%Y-%m-%d')} found to archive")
            return

        # Create archive
        archive_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = self.log_directory / f"audit_archive_{archive_date}.zip"

        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for old_file in old_files:
                zipf.write(old_file, old_file.name)
                print(f"Archived: {old_file.name}")

        print(f"Created archive: {archive_name} with {len(old_files)} files")

        # Optionally, delete original files after archiving
        # Uncomment the following lines if you want to remove the original files after archiving
        # for old_file in old_files:
        #     old_file.unlink()
        #     print(f"Removed original: {old_file.name}")

    def get_compliance_report(self) -> str:
        """
        Generate a compliance report showing log retention and archival status.

        Returns:
            String compliance report
        """
        import datetime

        report_lines = []
        report_lines.append("Audit Log Compliance Report")
        report_lines.append("=" * 35)

        # Check total number of log files
        all_log_files = list(self.log_directory.glob("*_audit.json"))
        report_lines.append(f"Total Log Files: {len(all_log_files)}")

        # Check age distribution
        today = datetime.now()
        current_year = today.year
        current_month = today.month

        files_by_age = {
            'this_month': 0,
            'this_year': 0,
            'older_than_year': 0
        }

        for log_file in all_log_files:
            try:
                file_date_str = log_file.name.split('_audit.json')[0]
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')

                if file_date.year == current_year and file_date.month == current_month:
                    files_by_age['this_month'] += 1
                elif file_date.year == current_year:
                    files_by_age['this_year'] += 1
                else:
                    files_by_age['older_than_year'] += 1
            except ValueError:
                continue

        report_lines.append(f"Files from this month: {files_by_age['this_month']}")
        report_lines.append(f"Files from this year (excluding this month): {files_by_age['this_year']}")
        report_lines.append(f"Files older than one year: {files_by_age['older_than_year']}")

        # Check for archive files
        archive_files = list(self.log_directory.glob("audit_archive_*.zip"))
        report_lines.append(f"Archived log sets: {len(archive_files)}")

        # Suggest actions
        report_lines.append("")
        report_lines.append("Recommendations:")
        if files_by_age['older_than_year'] > 0:
            report_lines.append("- Consider archiving logs older than one year")
        if len(archive_files) == 0:
            report_lines.append("- No archived logs found - consider implementing regular archiving")
        if files_by_age['older_than_year'] > 100:  # Arbitrary threshold
            report_lines.append("- Large number of old logs detected - recommend archiving")

        return "\n".join(report_lines)


# Global instances for convenience
audit_logger = AuditLogger()
audit_viewer = AuditLogViewer()


# Convenience functions for common logging
def compute_integrity_hash(log_entry: dict) -> str:
    """
    Compute a hash for integrity checking of log entries.

    Args:
        log_entry: The log entry dictionary to hash

    Returns:
        Hash string for the log entry
    """
    import hashlib
    import json

    # Serialize the log entry to a canonical JSON string
    serialized = json.dumps(log_entry, sort_keys=True, separators=(',', ':'))

    # Create a hash of the serialized entry
    hash_obj = hashlib.sha256(serialized.encode('utf-8'))
    return hash_obj.hexdigest()


def verify_integrity(log_entry: dict) -> bool:
    """
    Verify the integrity of a log entry by checking its hash.

    Args:
        log_entry: The log entry dictionary to verify

    Returns:
        True if the entry is valid, False if tampering is detected
    """
    if 'integrity_hash' not in log_entry:
        # If no integrity hash, the entry cannot be verified
        return False

    # Compute the expected hash (excluding the integrity_hash field itself)
    temp_entry = log_entry.copy()
    expected_hash = temp_entry.pop('integrity_hash', None)

    computed_hash = compute_integrity_hash(temp_entry)

    return computed_hash == expected_hash


class TamperEvidentAuditLogger:
    """
    Tamper-evident Audit Logger that adds integrity checking to log entries.
    """
    def __init__(self, log_directory="Logs/Audit", enable_integrity=True):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.enable_integrity = enable_integrity

    def write_log(self, event_type, service, action, correlation_id, status,
                  duration_ms=None, result_summary="", error_details=None,
                  tags=None, user_context=""):
        """
        Write a structured JSON audit log entry with optional integrity checking.
        """
        if tags is None:
            tags = []

        audit_entry = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "event_type": event_type,
            "service": service,
            "action": action,
            "correlation_id": correlation_id,
            "status": status,
            "duration_ms": duration_ms,
            "input_size_bytes": len(result_summary.encode('utf-8')) if result_summary else 0,
            "result_summary": result_summary,
            "user_context": user_context
        }

        if error_details:
            audit_entry["error_details"] = error_details

        if tags:
            audit_entry["tags"] = tags

        # Add integrity hash if enabled
        if self.enable_integrity:
            audit_entry["integrity_hash"] = compute_integrity_hash(audit_entry)

        # Write to daily audit log file
        log_date = datetime.now().strftime('%Y-%m-%d')
        audit_log_dir = self.log_directory
        audit_log_dir.mkdir(exist_ok=True)
        audit_log_file = audit_log_dir / f"{log_date}_audit.json"

        try:
            # Append the log entry to the file
            with open(audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            print(f"TamperEvidentAuditLogger failed to write log: {e}")


# Replace the global audit_logger with tamper-evident version
audit_logger = TamperEvidentAuditLogger()


def log_task_processed(task_name, task_type, correlation_id, duration_ms, status="success", result_summary=""):
    """Log task processing events."""
    audit_logger.write_log(
        event_type="task_processed",
        service="orchestrator",
        action=f"process_{task_name}",
        correlation_id=correlation_id,
        status=status,
        duration_ms=duration_ms,
        result_summary=result_summary,
        tags=["orchestrator", "task_processing", status, task_type]
    )


def log_mcp_call(service_name, action, correlation_id, duration_ms, status="success", error_details=None):
    """Log MCP (Model Context Protocol) calls."""
    audit_logger.write_log(
        event_type="mcp_call",
        service=service_name,
        action=action,
        correlation_id=correlation_id,
        status=status,
        duration_ms=duration_ms,
        result_summary=f"MCP call to {service_name} for {action}",
        error_details=error_details,
        tags=["mcp", "external_service", status, service_name]
    )


def log_service_monitor(service_name, correlation_id, status="healthy", result_summary=""):
    """Log service monitoring events."""
    audit_logger.write_log(
        event_type="service_monitor",
        service=service_name,
        action="health_check",
        correlation_id=correlation_id,
        status=status,
        result_summary=result_summary,
        tags=["monitoring", "service_health", status]
    )


def log_error_event(service_name, action, correlation_id, error_details, result_summary=""):
    """Log error events."""
    audit_logger.write_log(
        event_type="error_event",
        service=service_name,
        action=action,
        correlation_id=correlation_id,
        status="failure",
        result_summary=result_summary,
        error_details=error_details,
        tags=["error", "exception", "failure"]
    )