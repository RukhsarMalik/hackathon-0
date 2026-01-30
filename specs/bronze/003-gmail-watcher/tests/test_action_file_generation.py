"""
Unit tests for gmail_watcher.py - Action file generation functionality
"""
import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestActionFileGeneration(unittest.TestCase):

    def test_action_file_has_correct_format(self):
        """Test that generated action files have correct YAML frontmatter and structure."""
        # Import the function to test (the check_emails function which creates action files)
        from bronze.gmail_watcher import check_emails

        # Create a mock service that returns a message with specific headers
        mock_service = Mock()

        # Mock the users().messages().list().execute() call
        mock_list_response = {'messages': [{'id': 'test_msg_12345'}]}
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() call
        mock_msg = Mock()
        mock_payload = Mock()
        mock_headers = [
            {'name': 'From', 'value': 'sender@example.com'},
            {'name': 'Subject', 'value': 'Test Subject for Action File'},
            {'name': 'Date', 'value': '2026-01-29T10:30:00Z'}
        ]
        mock_payload.headers = mock_headers
        mock_msg.payload = mock_payload
        mock_msg.snippet = 'This is a test email snippet that should appear in the action file.'
        mock_msg_return = Mock()
        mock_msg_return.execute.return_value = mock_msg

        def mock_get_message(user_id, id):
            return mock_msg_return

        mock_get_method = Mock(side_effect=mock_get_message)
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

            # Call the function with an empty set of processed IDs
            processed_ids = set()
            check_emails(mock_service, processed_ids)

            # Check that an action file was created
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 1)

            # Read the action file content
            action_file_content = action_files[0].read_text()

            # Check for YAML frontmatter
            self.assertIn("---", action_file_content[:100], "YAML frontmatter delimiter not found at start")

            # Check for required fields in frontmatter
            self.assertIn("type: email", action_file_content)
            self.assertIn("from: sender@example.com", action_file_content)
            self.assertIn("subject: Test Subject for Action File", action_file_content)
            self.assertIn("received:", action_file_content)
            self.assertIn("priority: high", action_file_content)
            self.assertIn("status: pending", action_file_content)
            self.assertIn("gmail_id: test_msg_12345", action_file_content)

            # Check for body content
            self.assertIn("## Email Content", action_file_content)
            self.assertIn("This is a test email snippet", action_file_content)
            self.assertIn("## Email Details", action_file_content)
            self.assertIn("- **From**: sender@example.com", action_file_content)
            self.assertIn("## Suggested Actions", action_file_content)

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    def test_action_file_sanitizes_filename(self):
        """Test that action files have sanitized filenames to handle special characters."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service with a subject containing special characters
        mock_service = Mock()

        # Mock the users().messages().list().execute() call
        mock_list_response = {'messages': [{'id': 'special_msg_123'}]}
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() call with special characters in subject
        mock_msg = Mock()
        mock_payload = Mock()
        mock_headers = [
            {'name': 'From', 'value': 'sender@example.com'},
            {'name': 'Subject', 'value': 'Test Subject with Special Chars: /\\:*?"<>|'},
            {'name': 'Date', 'value': '2026-01-29T10:30:00Z'}
        ]
        mock_payload.headers = mock_headers
        mock_msg.payload = mock_payload
        mock_msg.snippet = 'Test snippet.'
        mock_msg_return = Mock()
        mock_msg_return.execute.return_value = mock_msg

        def mock_get_message(user_id, id):
            return mock_msg_return

        mock_get_method = Mock(side_effect=mock_get_message)
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

            # Call the function with an empty set of processed IDs
            processed_ids = set()
            check_emails(mock_service, processed_ids)

            # Check that an action file was created
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 1)

            # Check that the filename doesn't contain problematic characters
            filename = action_files[0].name
            # The special characters should be replaced with underscores
            self.assertNotIn(':', filename)
            self.assertNotIn('*', filename)
            self.assertNotIn('?', filename)
            self.assertNotIn('"', filename)
            self.assertNotIn('<', filename)
            self.assertNotIn('>', filename)
            self.assertNotIn('|', filename)

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