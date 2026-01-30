"""
Unit tests for gmail_watcher.py - Email detection functionality
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestEmailDetection(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    def test_check_emails_processes_messages(self):
        """Test that check_emails processes email messages and creates action files."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service
        mock_service = Mock()

        # Mock the users().messages().list().execute() call
        mock_list_response = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() call for each message
        def mock_get_message(user_id, id):
            mock_msg = Mock()
            mock_payload = Mock()
            mock_headers = [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': f'Subject for {id}'},
                {'name': 'Date', 'value': '2026-01-29T10:30:00Z'}
            ]
            mock_payload.headers = mock_headers
            mock_msg.payload = mock_payload
            mock_msg.snippet = f'This is a test snippet for {id}'
            mock_msg_return = Mock()
            mock_msg_return.execute.return_value = mock_msg
            return mock_msg_return

        mock_get_method = Mock(side_effect=mock_get_message)
        mock_list_method.messages.return_value = mock_get_method

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            from pathlib import Path

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
            check_emails(mock_service, processed_ids)

            # Assertions
            # Check that action files were created
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 2)

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    def test_check_emails_skips_processed_messages(self):
        """Test that check_emails skips messages that have already been processed."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service
        mock_service = Mock()

        # Mock the users().messages().list().execute() call
        mock_list_response = {
            'messages': [
                {'id': 'msg1'},  # This should be skipped
                {'id': 'msg2'}   # This should be processed
            ]
        }
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() call for the message that should be processed
        def mock_get_message(user_id, id):
            if id == 'msg2':
                mock_msg = Mock()
                mock_payload = Mock()
                mock_headers = [
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Subject', 'value': f'Subject for {id}'},
                    {'name': 'Date', 'value': '2026-01-29T10:30:00Z'}
                ]
                mock_payload.headers = mock_headers
                mock_msg.payload = mock_payload
                mock_msg.snippet = f'This is a test snippet for {id}'
                mock_msg_return = Mock()
                mock_msg_return.execute.return_value = mock_msg
                return mock_msg_return
            else:
                self.fail(f"Message {id} should have been skipped")

        mock_get_method = Mock(side_effect=mock_get_message)
        mock_list_method.messages.return_value = mock_get_method

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            from pathlib import Path

            # Set up the vault structure
            vault_path = Path(temp_dir)
            needs_action_path = vault_path / "Needs_Action"
            logs_path = vault_path / "Logs"
            processed_file = logs_path / "processed_emails.txt"

            needs_action_path.mkdir(parents=True, exist_ok=True)
            logs_path.mkdir(parents=True, exist_ok=True)
            processed_file.write_text("msg1\n")  # Mark msg1 as already processed

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

            # Call the function with a set containing the processed message ID
            processed_ids = {'msg1'}
            check_emails(mock_service, processed_ids)

            # Assertions
            # Only one action file should be created (for msg2)
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 1)

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
    unittest.main()