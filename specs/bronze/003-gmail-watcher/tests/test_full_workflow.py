"""
Integration tests for gmail_watcher.py - Complete workflow simulation
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestFullWorkflow(unittest.TestCase):

    def test_complete_email_processing_workflow(self):
        """Test the complete workflow from email detection to action file creation."""
        # Import the functions to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that simulates the full Gmail API interaction
        mock_service = Mock()

        # Mock the users().messages().list().execute() call to return multiple messages
        mock_list_response = {
            'messages': [
                {'id': 'msg_complete_001'},
                {'id': 'msg_complete_002'}
            ]
        }
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() calls for each message
        def mock_get_message(user_id, id):
            mock_msg = Mock()
            mock_payload = Mock()

            # Different headers and snippets for each message
            headers_map = {
                'msg_complete_001': [
                    {'name': 'From', 'value': 'boss@company.com'},
                    {'name': 'Subject', 'value': 'URGENT: Quarterly Report Due Today'},
                    {'name': 'Date', 'value': '2026-01-29T09:00:00Z'}
                ],
                'msg_complete_002': [
                    {'name': 'From', 'value': 'newsletter@example.com'},
                    {'name': 'Subject', 'value': 'Weekly Newsletter - January Updates'},
                    {'name': 'Date', 'value': '2026-01-29T08:30:00Z'}
                ]
            }

            snippets_map = {
                'msg_complete_001': 'Please submit the quarterly report by end of day today. This is critical for the board meeting.',
                'msg_complete_002': 'Here are this week\'s updates and upcoming events...'
            }

            mock_payload.headers = headers_map.get(id, [])
            mock_msg.payload = mock_payload
            mock_msg.snippet = snippets_map.get(id, f'Default snippet for {id}')

            mock_msg_return = Mock()
            mock_msg_return.execute.return_value = mock_msg
            return mock_msg_return

        mock_get_method = Mock(side_effect=mock_get_message)
        mock_list_method.messages.return_value = mock_get_method

        # Create a temporary directory for testing the full workflow
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
            initial_count = len(list(needs_action_path.glob("EMAIL_*.md")))

            check_emails(mock_service, processed_ids)

            # Verify the workflow completed successfully
            # Check that action files were created for both messages
            final_action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(final_action_files), 2)

            # Verify that processed IDs file was updated
            processed_content = processed_file.read_text()
            self.assertIn('msg_complete_001', processed_content)
            self.assertIn('msg_complete_002', processed_content)

            # Verify each action file has proper structure
            for action_file in final_action_files:
                content = action_file.read_text()

                # Check for required YAML frontmatter
                self.assertIn("type: email", content)
                self.assertIn("priority: high", content)  # Should be high for urgent keywords
                self.assertIn("status: pending", content)

                # Check for required sections
                self.assertIn("## Email Content", content)
                self.assertIn("## Email Details", content)
                self.assertIn("## Suggested Actions", content)

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    def test_workflow_handles_api_errors_gracefully(self):
        """Test that the workflow continues even when some API calls fail."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that simulates partial API failures
        mock_service = Mock()

        # Mock the users().messages().list().execute() call to return messages
        mock_list_response = {
            'messages': [
                {'id': 'msg_success_001'},
                {'id': 'msg_fail_002'}  # This one will cause an error
            ]
        }
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() calls
        def mock_get_message(user_id, id):
            if id == 'msg_fail_002':
                # Simulate an API error for this message
                mock_msg_return = Mock()
                mock_msg_return.execute.side_effect = Exception("API Error for msg_fail_002")
                return mock_msg_return
            else:
                # Successful response for the other message
                mock_msg = Mock()
                mock_payload = Mock()
                mock_headers = [
                    {'name': 'From', 'value': 'colleague@example.com'},
                    {'name': 'Subject', 'value': 'Successful Message'},
                    {'name': 'Date', 'value': '2026-01-29T10:00:00Z'}
                ]
                mock_payload.headers = mock_headers
                mock_msg.payload = mock_payload
                mock_msg.snippet = 'This message should be processed successfully.'

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

            # Verify that the workflow continued despite the error
            # Only one action file should be created (for the successful message)
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 1)

            # The successful message should be in the processed file
            processed_content = processed_file.read_text()
            self.assertIn('msg_success_001', processed_content)
            # The failed message should not be in the processed file
            self.assertNotIn('msg_fail_002', processed_content)

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