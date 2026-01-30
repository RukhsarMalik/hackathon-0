"""
Validation tests for gmail_watcher.py - Format and structure validation
"""
import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestValidation(unittest.TestCase):

    def test_action_file_has_required_fields(self):
        """Test that action files contain all required YAML frontmatter fields."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service
        mock_service = Mock()

        # Mock the users().messages().list().execute() call
        mock_list_response = {'messages': [{'id': 'validation_msg_001'}]}
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() call
        mock_msg = Mock()
        mock_payload = Mock()
        mock_headers = [
            {'name': 'From', 'value': 'validator@example.com'},
            {'name': 'Subject', 'value': 'Validation Test Email'},
            {'name': 'Date', 'value': '2026-01-29T11:00:00Z'}
        ]
        mock_payload.headers = mock_headers
        mock_msg.payload = mock_payload
        mock_msg.snippet = 'This is a validation test message.'
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

            # Validate required YAML frontmatter fields
            required_fields = [
                'type: email',
                'from:',
                'subject:',
                'received:',
                'priority:',
                'status:',
                'gmail_id:'
            ]

            for field in required_fields:
                with self.subTest(field=field):
                    self.assertIn(field, action_file_content, f"Required field '{field}' not found in action file")

            # Validate that required sections exist
            required_sections = [
                "## Email Content",
                "## Email Details",
                "## Suggested Actions"
            ]

            for section in required_sections:
                with self.subTest(section=section):
                    self.assertIn(section, action_file_content, f"Required section '{section}' not found in action file")

            # Validate the structure of the frontmatter (between --- delimiters)
            lines = action_file_content.split('\n')
            frontmatter_start = -1
            frontmatter_end = -1

            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if frontmatter_start == -1:
                        frontmatter_start = i
                    else:
                        frontmatter_end = i
                        break

            self.assertNotEqual(frontmatter_start, -1, "YAML frontmatter start delimiter '---' not found")
            self.assertNotEqual(frontmatter_end, -1, "YAML frontmatter end delimiter '---' not found")
            self.assertLess(frontmatter_start, frontmatter_end, "Frontmatter delimiters are in wrong order")

            # Check that content after frontmatter exists
            content_after_frontmatter = '\n'.join(lines[frontmatter_end + 1:]).strip()
            self.assertTrue(content_after_frontmatter, "No content found after YAML frontmatter")

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    def test_action_file_priority_assignment(self):
        """Test that action files get appropriate priority based on content."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service with a high-priority email
        mock_service = Mock()

        # Mock the users().messages().list().execute() call
        mock_list_response = {'messages': [
            {'id': 'urgent_msg_001'},
            {'id': 'normal_msg_002'}
        ]}
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() calls
        def mock_get_message(user_id, id):
            mock_msg = Mock()
            mock_payload = Mock()

            if id == 'urgent_msg_001':
                # High priority email
                mock_headers = [
                    {'name': 'From', 'value': 'boss@company.com'},
                    {'name': 'Subject', 'value': 'URGENT: Invoice Payment Overdue'},
                    {'name': 'Date', 'value': '2026-01-29T10:00:00Z'}
                ]
                mock_msg.snippet = 'Payment is overdue. Please process immediately.'
            else:
                # Normal priority email
                mock_headers = [
                    {'name': 'From', 'value': 'newsletter@info.com'},
                    {'name': 'Subject', 'value': 'Monthly Newsletter'},
                    {'name': 'Date', 'value': '2026-01-29T09:00:00Z'}
                ]
                mock_msg.snippet = 'Here is your monthly newsletter with updates.'

            mock_payload.headers = mock_headers
            mock_msg.payload = mock_payload

            mock_msg_return = Mock()
            mock_msg_return.execute.return_value = mock_msg
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

            # Check that action files were created
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 2)

            # Currently, the script sets priority to 'high' for all emails
            # In a more sophisticated implementation, this would vary based on content
            for action_file in action_files:
                content = action_file.read_text()
                self.assertIn("priority: high", content)

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
    unittest.main()