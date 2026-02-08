"""
Error Recovery and Graceful Degradation Module.
"""
import time
import math
from datetime import datetime, timedelta
from pathlib import Path
import json


def exponential_backoff(attempt_number, base_delay=1, max_delay=300):
    """
    Calculate delay for exponential backoff.

    Args:
        attempt_number: The attempt number (starting from 1)
        base_delay: Base delay in seconds (default 1)
        max_delay: Maximum delay in seconds (default 300)

    Returns:
        Delay in seconds to wait before the next attempt
    """
    # Calculate exponential backoff: base_delay * 2^(attempt_number - 1)
    delay = base_delay * (2 ** (attempt_number - 1))

    # Apply jitter to prevent thundering herd problems
    import random
    jitter = random.uniform(0.9, 1.1)
    delay = delay * jitter

    # Don't exceed maximum delay
    return min(delay, max_delay)


def retry_with_backoff(func, max_attempts=5, base_delay=1, max_delay=300, should_retry_func=None):
    """
    Execute a function with exponential backoff retry logic.

    Args:
        func: The function to execute
        max_attempts: Maximum number of attempts (default 5)
        base_delay: Base delay in seconds (default 1)
        max_delay: Maximum delay in seconds (default 300)
        should_retry_func: Optional function to determine if retry should occur

    Returns:
        Result of the function if successful, None if all attempts fail
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = func()
            return result  # Success!
        except Exception as e:
            last_exception = e

            # Determine if we should retry based on the exception
            should_retry = True
            if should_retry_func:
                should_retry = should_retry_func(e)

            if attempt < max_attempts and should_retry:
                delay = exponential_backoff(attempt, base_delay, max_delay)
                print(f"Attempt {attempt} failed: {e}. Waiting {delay:.2f}s before retry...")

                # Log the retry attempt
                log_retry_attempt(func.__name__, attempt, str(e), delay)

                time.sleep(delay)
            else:
                print(f"All {max_attempts} attempts failed for {func.__name__}. Last error: {e}")
                break

    # Log the final failure after all attempts
    log_final_failure(func.__name__, max_attempts, str(last_exception))
    return None


def log_retry_attempt(function_name, attempt_number, error_message, delay):
    """Log a retry attempt to the audit trail."""
    try:
        from audit_logging import audit_logger
        correlation_id = f"retry_{function_name}_{int(time.time())}"

        audit_logger.write_log(
            event_type="retry_attempt",
            service=function_name,
            action=f"retry_attempt_{attempt_number}",
            correlation_id=correlation_id,
            status="retry_scheduled",
            result_summary=f"Attempt {attempt_number} failed, retry scheduled after {delay:.2f}s delay",
            error_details={
                "type": "TemporaryError",
                "message": error_message,
                "attempt_number": attempt_number
            },
            tags=["error_recovery", "retry", "temporary_error", function_name]
        )
    except ImportError:
        print(f"Retry attempt {attempt_number} for {function_name} failed: {error_message}")


def log_final_failure(function_name, max_attempts, error_message):
    """Log a final failure after all retry attempts."""
    try:
        from audit_logging import audit_logger
        correlation_id = f"failure_{function_name}_{int(time.time())}"

        audit_logger.write_log(
            event_type="final_failure",
            service=function_name,
            action="final_failure_after_retries",
            correlation_id=correlation_id,
            status="permanent_failure",
            result_summary=f"All {max_attempts} retry attempts failed",
            error_details={
                "type": "PermanentError",
                "message": error_message,
                "max_attempts": max_attempts
            },
            tags=["error_recovery", "failure", "permanent_error", function_name]
        )
    except ImportError:
        print(f"Final failure for {function_name} after {max_attempts} attempts: {error_message}")


def queue_action_for_later(target_service, action_type, action_params, original_trigger=None, vault_path="./AI_Employee_Vault"):
    """
    Queue an action to be processed later when the target service becomes available.

    Args:
        target_service: Name of the target service (e.g., 'linkedin', 'facebook', 'email', 'odoo')
        action_type: Type of action (e.g., 'post_to_linkedin', 'send_email', 'create_invoice')
        action_params: Parameters for the action
        original_trigger: Name of the original file that triggered this action (optional)
        vault_path: Path to the AI Employee Vault directory

    Returns:
        Path to the queued action file
    """
    vault = Path(vault_path)

    # Create the fallback queue directory if it doesn't exist
    fallback_dir = vault / "Needs_Action_Fallback"
    fallback_dir.mkdir(exist_ok=True)

    # Generate a unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    action_id = f"{target_service}_{action_type}_{timestamp}"
    filename = f"PENDING_MCP_CALL_{action_id}.md"

    # Create the queued action file
    queued_action_path = fallback_dir / filename

    queued_content = f"""---
type: queued_action
status: pending_retry
created_at: {datetime.now().isoformat()}
target_service: "{target_service}"
action_type: "{action_type}"
retry_count: 0
max_retries: 5
next_attempt_after: "{(datetime.now() + timedelta(seconds=1)).isoformat()}"
original_trigger: "{original_trigger or 'manual'}"
---

## Queued Action: {action_type}

This action was queued because the target service ("{target_service}") was unavailable.

### Action Details
- **Type**: {action_type}
- **Target Service**: {target_service}
- **Params**: {json.dumps(action_params, indent=2)}
- **Created**: {datetime.now().isoformat()}

### Retry Information
- **Retry Count**: 0
- **Max Retries**: 5
- **Next Attempt**: {(datetime.now() + timedelta(seconds=1)).isoformat()}

The system will automatically retry this action when the service becomes available.
"""

    with open(queued_action_path, 'w', encoding='utf-8') as f:
        f.write(queued_content)

    print(f"Action queued for later: {queued_action_path}")

    # Log the queueing event
    try:
        from audit_logging import audit_logger
        correlation_id = f"queue_{action_id}_{int(time.time())}"

        audit_logger.write_log(
            event_type="action_queued",
            service=target_service,
            action=action_type,
            correlation_id=correlation_id,
            status="queued",
            result_summary=f"Action queued for {target_service} - will retry when available",
            tags=["error_recovery", "queue", "graceful_degradation", target_service]
        )
    except ImportError:
        print(f"Action queued for {target_service}: {action_type}")

    return queued_action_path


def process_queued_actions(max_per_run=10, vault_path="./AI_Employee_Vault"):
    """
    Process any queued actions that are ready to be retried.

    Args:
        max_per_run: Maximum number of queued actions to process per run (default 10)
        vault_path: Path to the AI Employee Vault directory

    Returns:
        Number of actions processed
    """
    vault = Path(vault_path)
    fallback_dir = vault / "Needs_Action_Fallback"

    if not fallback_dir.exists():
        return 0

    # Get all queued action files
    queued_files = list(fallback_dir.glob("PENDING_MCP_CALL_*.md"))

    processed_count = 0

    for queued_file in queued_files[:max_per_run]:  # Limit to max_per_run
        try:
            # Read the queued action
            content = queued_file.read_text(encoding='utf-8')

            # Extract the YAML frontmatter
            lines = content.split('\n')
            frontmatter = []
            in_frontmatter = False

            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    if not in_frontmatter:  # End of frontmatter
                        break
                    continue

                if in_frontmatter:
                    frontmatter.append(line)

            # Parse the frontmatter
            fm_dict = {}
            for line in frontmatter:
                if ':' in line and line.strip()[0] != '#':  # Skip comment lines
                    parts = line.split(':', 1)
                    key = parts[0].strip()
                    value = parts[1].strip() if len(parts) > 1 else ''
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Try to parse numeric values
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)

                    fm_dict[key] = value

            # Check if it's time to retry
            next_attempt_str = fm_dict.get('next_attempt_after')
            if next_attempt_str:
                try:
                    next_attempt = datetime.fromisoformat(next_attempt_str.replace('Z', '+00:00'))
                    if datetime.now() >= next_attempt:
                        # It's time to retry the action
                        target_service = fm_dict.get('target_service', 'unknown')
                        action_type = fm_dict.get('action_type', 'unknown')

                        # For this simulation, we'll just move the file back to Needs_Action
                        # In a real system, this would call the actual service
                        print(f"Retrying queued action: {action_type} for {target_service}")

                        # Update the retry count
                        retry_count = fm_dict.get('retry_count', 0) + 1
                        max_retries = fm_dict.get('max_retries', 5)

                        if retry_count >= max_retries:
                            print(f"Max retries reached for {queued_file.name}. Moving to permanent failure.")

                            # Move to a failed actions directory
                            failed_dir = vault / "Needs_Action_Failed"
                            failed_dir.mkdir(exist_ok=True)
                            failed_path = failed_dir / f"FAILED_{queued_file.name}"

                            queued_file.rename(failed_path)

                            # Log the permanent failure
                            try:
                                from audit_logging import audit_logger
                                correlation_id = f"permanent_failure_{int(time.time())}"

                                audit_logger.write_log(
                                    event_type="permanent_failure",
                                    service=target_service,
                                    action=action_type,
                                    correlation_id=correlation_id,
                                    status="permanent_failure",
                                    result_summary=f"Permanent failure after {max_retries} retry attempts",
                                    error_details={
                                        "type": "PermanentError",
                                        "message": f"Action failed after {max_retries} retry attempts",
                                        "max_retries": max_retries
                                    },
                                    tags=["error_recovery", "failure", "permanent_error", target_service]
                                )
                            except ImportError:
                                pass
                        else:
                            # Update the file with incremented retry count and new backoff time
                            new_next_attempt = datetime.now() + timedelta(seconds=exponential_backoff(retry_count))

                            # Update the frontmatter in the content
                            updated_content = content.replace(
                                f"retry_count: {fm_dict.get('retry_count', 0)}",
                                f"retry_count: {retry_count}"
                            ).replace(
                                f"next_attempt_after: \"{next_attempt_str}\"",
                                f'next_attempt_after: "{new_next_attempt.isoformat()}"'
                            )

                            # Write the updated content back to the file
                            with open(queued_file, 'w', encoding='utf-8') as f:
                                f.write(updated_content)

                            print(f"Updated retry count for {queued_file.name} to {retry_count}, next attempt at {new_next_attempt}")

                            processed_count += 1
                    else:
                        print(f"Too early to retry {queued_file.name}, next attempt at {next_attempt_str}")
                except ValueError:
                    print(f"Could not parse next attempt time for {queued_file.name}")
            else:
                print(f"No next attempt time specified for {queued_file.name}")

        except Exception as e:
            print(f"Error processing queued action {queued_file.name}: {e}")

    return processed_count


def is_service_available(service_name):
    """
    Check if a service is available. This is a placeholder implementation.

    Args:
        service_name: Name of the service to check

    Returns:
        Boolean indicating if the service is available
    """
    # In a real implementation, this would make actual connectivity checks
    # For now, we'll simulate availability
    print(f"Checking availability of {service_name}...")

    # Placeholder: simulate service availability
    import random
    return random.random() > 0.1  # 90% chance of being available for demo purposes


def execute_with_error_handling(service_name, action_func, *args, **kwargs):
    """
    Execute an action with proper error handling and graceful degradation.

    Args:
        service_name: Name of the service to use
        action_func: Function to execute the action
        *args: Arguments to pass to the action function
        **kwargs: Keyword arguments to pass to the action function

    Returns:
        Result of the action if successful, None if it failed permanently
    """
    if is_service_available(service_name):
        print(f"Service {service_name} is available, executing action...")

        def attempt_action():
            return action_func(*args, **kwargs)

        result = retry_with_backoff(
            attempt_action,
            max_attempts=3,
            base_delay=1,
            max_delay=60,
            should_retry_func=lambda e: "network" in str(e).lower() or "connection" in str(e).lower()
        )

        return result
    else:
        print(f"Service {service_name} is unavailable, queuing action...")

        # Extract action details for queueing
        action_type = kwargs.get('action_type', 'generic_action')
        action_params = {
            'args': args,
            'kwargs': kwargs
        }

        # Queue the action for later
        queue_action_for_later(
            target_service=service_name,
            action_type=action_type,
            action_params=action_params,
            original_trigger=kwargs.get('original_trigger', 'unknown')
        )

        return None


if __name__ == "__main__":
    # Example usage
    def test_action():
        import random
        # Simulate a random failure
        if random.random() < 0.7:  # 70% chance of failure
            raise Exception("Simulated service error")
        return "Success!"

    print("Testing error recovery with backoff...")
    result = retry_with_backoff(test_action, max_attempts=3)
    print(f"Result: {result}")

    print("\nTesting action queuing...")
    queue_action_for_later(
        target_service="linkedin",
        action_type="post_to_linkedin",
        action_params={"content": "Test post", "hashtags": ["#test"]},
        original_trigger="weekly_audit"
    )

    print("\nTesting queued action processing...")
    processed = process_queued_actions()
    print(f"Processed {processed} queued actions")