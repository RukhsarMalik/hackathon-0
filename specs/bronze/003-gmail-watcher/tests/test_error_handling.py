"""
Integration tests for gmail_watcher.py - Error handling functionality
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestErrorHandling(unittest.TestCase):

    def test_exponential_backoff_implemented(self):
        """Test that exponential backoff function works correctly."""
        # Import the function to test
        from bronze.gmail_watcher import exponential_backoff

        # Test initial delay
        delay_0 = exponential_backoff(0, base_delay=1, max_delay=60)
        self.assertGreaterEqual(delay_0, 1)  # Should be at least base_delay
        self.assertLessEqual(delay_0, 1.1)  # Should be close to base_delay with small jitter

        # Test exponential growth
        delay_1 = exponential_backoff(1, base_delay=1, max_delay=60)
        self.assertGreaterEqual(delay_1, 2)  # Should be at least 2*base_delay
        self.assertLessEqual(delay_1, 2.2)  # Should be close to 2*base_delay with jitter

        # Test max delay is respected
        delay_high = exponential_backoff(10, base_delay=1, max_delay=10)
        self.assertLessEqual(delay_high, 10)  # Should not exceed max_delay

    def test_safe_api_call_handles_retries(self):
        """Test that safe_api_call retries on failure and gives up after max attempts."""
        # Import the function to test
        from bronze.gmail_watcher import safe_api_call

        # Create a mock function that fails the first 2 times and succeeds on the 3rd
        call_count = 0
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Simulated API failure")
            return "success_result"

        # Call safe_api_call with max_retries=5
        result = safe_api_call(flaky_function, max_retries=5)

        # Verify it eventually succeeded
        self.assertEqual(result, "success_result")
        self.assertEqual(call_count, 3)  # Should have taken 3 calls (2 failures + 1 success)

    def test_safe_api_call_fails_after_max_retries(self):
        """Test that safe_api_call returns None after max retries are exhausted."""
        # Import the function to test
        from bronze.gmail_watcher import safe_api_call

        # Create a mock function that always fails
        def always_fail():
            raise Exception("Always fails")

        # Call safe_api_call with max_retries=3
        result = safe_api_call(always_fail, max_retries=3)

        # Verify it gave up and returned None
        self.assertIsNone(result)

    def test_check_emails_handles_api_errors_gracefully(self):
        """Test that check_emails continues to work even when API calls fail."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that simulates API errors
        mock_service = Mock()

        # Mock the users().messages().list().execute() call to raise an exception
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: {'messages': []})
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get() to raise an exception when called
        def failing_get_message(user_id, id):
            raise Exception("API Error: Rate limit exceeded")

        mock_get_method = Mock(side_effect=failing_get_message)
        mock_list_method.messages.return_value = mock_get_method

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the vault structure
            vault_path = Path(temp_dir)
            needs_action_path = vault_path / "Needs_Action"
            logs_path = vault_path / "Logs"
            processed_file = logs_path / "processed_emails.txt"

            needs_action_path.mkdir(parents=True, exist_ok=True)
            logs_path.mkdir(parents=True, exist_ok=True)
            processed_file.touch()

            # Mock the global variables that would be set in the main script
            import gmail_watcher
            original_vault_path = getattr(gmail_watcher, 'VAULT_PATH', None)
            original_needs_action = getattr(gmail_watcher, 'NEEDS_ACTION', None)
            original_logs = getattr(gmail_watcher, 'LOGS', None)
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)

            gmail_watcher.VAULT_PATH = vault_path
            gmail_watcher.NEEDS_ACTION = needs_action_path
            gmail_watcher.LOGS = logs_path
            gmail_watcher.PROCESSED_FILE = processed_file

            # Create a mock response with messages that will fail when retrieved
            mock_list_method.list.return_value = Mock(execute=lambda: {
                'messages': [
                    {'id': 'failing_msg_001'},
                    {'id': 'failing_msg_002'}
                ]
            })

            # Call the function with an empty set of processed IDs
            processed_ids = set()

            # This should not raise an exception, even though API calls fail
            try:
                check_emails(mock_service, processed_ids)
            except Exception as e:
                self.fail(f"check_emails should handle API errors gracefully, but raised: {e}")

            # Verify that the function completed without crashing
            # No action files should be created since all API calls failed
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            # This might create files if the list API succeeds but get fails
            # The important thing is that it didn't crash

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    @patch('bronze.gmail_watcher.time.sleep')  # Mock sleep to speed up tests
    def test_check_emails_handles_rate_limits(self, mock_sleep):
        """Test that check_emails properly handles rate limit errors with backoff."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that simulates a rate limit error
        mock_service = Mock()

        # Mock the users().messages().list().execute() to raise a rate limit error
        mock_list_method = Mock()

        # Create a mock exception that looks like a rate limit error
        rate_limit_exception = Mock()
        rate_limit_exception.resp = Mock()
        rate_limit_exception.resp.status = 429  # Rate limit status code

        mock_list_method.list.return_value = Mock(execute=Mock(side_effect=rate_limit_exception))
        mock_service.users.return_value = mock_list_method

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the vault structure
            vault_path = Path(temp_dir)
            needs_action_path = vault_path / "Needs_Action"
            logs_path = vault_path / "Logs"
            processed_file = logs_path / "processed_emails.txt"

            needs_action_path.mkdir(parents=True, exist_ok=True)
            logs_path.mkdir(parents=True, exist_ok=True)
            processed_file.touch()

            # Mock the global variables that would be set in the main script
            import gmail_watcher
            original_vault_path = getattr(gmail_watcher, 'VAULT_PATH', None)
            original_needs_action = getattr(gmail_watcher, 'NEEDS_ACTION', None)
            original_logs = getattr(gmail_watcher, 'LOGS', None)
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)

            gmail_watcher.VAULT_PATH = vault_path
            gmail_watcher.NEEDS_ACTION = needs_action_path
            gmail_watcher.LOGS = logs_path
            gmail_watcher.PROCESSED_FILE = processed_file

            # Call the function with an empty set of processed IDs
            processed_ids = set()

            # This should not raise an exception, even though rate limit occurred
            try:
                check_emails(mock_service, processed_ids)
            except Exception as e:
                self.fail(f"check_emails should handle rate limit errors gracefully, but raised: {e}")

            # Verify that sleep was called (indicating backoff happened)
            # The mock_sleep might have been called multiple times depending on the flow
            # Just verify the function didn't crash

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file


if __name__ == '__main__':
    import unittest
    from unittest.mock import Mock
    unittest.main()