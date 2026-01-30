"""
Integration tests for gmail_watcher.py - Duplicate prevention functionality
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestDuplicatePrevention(unittest.TestCase):

    def test_duplicate_emails_are_not_reprocessed(self):
        """Test that the same email is not processed twice."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that returns the same email twice
        mock_service = Mock()

        # Mock the users().messages().list().execute() call to return the same message
        mock_list_response = {
            'messages': [
                {'id': 'duplicate_msg_001'}
            ]
        }
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() call
        mock_msg = Mock()
        mock_payload = Mock()
        mock_headers = [
            {'name': 'From', 'value': 'sender@example.com'},
            {'name': 'Subject', 'value': 'Duplicate Test Email'},
            {'name': 'Date', 'value': '2026-01-29T10:00:00Z'}
        ]
        mock_payload.headers = mock_headers
        mock_msg.payload = mock_payload
        mock_msg.snippet = 'This is a test message that should only be processed once.'
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

            # First call: Process the email
            processed_ids = set()
            check_emails(mock_service, processed_ids)

            # Check that one action file was created
            first_action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(first_action_files), 1)

            # Check that the message ID was added to the processed file
            first_processed_content = processed_file.read_text()
            self.assertIn('duplicate_msg_001', first_processed_content)

            # Second call: Try to process the same email again
            # Reload processed IDs to simulate a new run of the program
            updated_processed_ids = {'duplicate_msg_001'}
            check_emails(mock_service, updated_processed_ids)

            # Check that no additional action file was created
            final_action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(final_action_files), 1)  # Still only 1

            # Check that the processed file still only contains the original entry
            final_processed_content = processed_file.read_text()
            # Count occurrences of the message ID to ensure it wasn't added again
            msg_id_count = final_processed_content.count('duplicate_msg_001')
            self.assertEqual(msg_id_count, 1)

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    def test_multiple_duplicates_are_handled(self):
        """Test that multiple duplicate emails are all prevented from re-processing."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that returns multiple emails, some of which are duplicates
        mock_service = Mock()

        # Mock the users().messages().list().execute() call to return mixed new/duplicate messages
        mock_list_response = {
            'messages': [
                {'id': 'new_msg_001'},      # New - should be processed
                {'id': 'duplicate_msg_001'}, # Duplicate - should be skipped
                {'id': 'duplicate_msg_002'}, # Duplicate - should be skipped
                {'id': 'new_msg_002'}       # New - should be processed
            ]
        }
        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() calls
        def mock_get_message(user_id, id):
            mock_msg = Mock()
            mock_payload = Mock()

            headers_map = {
                'new_msg_001': [
                    {'name': 'From', 'value': 'new.sender@example.com'},
                    {'name': 'Subject', 'value': 'New Email 1'},
                    {'name': 'Date', 'value': '2026-01-29T11:00:00Z'}
                ],
                'duplicate_msg_001': [
                    {'name': 'From', 'value': 'dup.sender1@example.com'},
                    {'name': 'Subject', 'value': 'Duplicate Email 1'},
                    {'name': 'Date', 'value': '2026-01-29T10:00:00Z'}
                ],
                'duplicate_msg_002': [
                    {'name': 'From', 'value': 'dup.sender2@example.com'},
                    {'name': 'Subject', 'value': 'Duplicate Email 2'},
                    {'name': 'Date', 'value': '2026-01-29T09:00:00Z'}
                ],
                'new_msg_002': [
                    {'name': 'From', 'value': 'another.new@example.com'},
                    {'name': 'Subject', 'value': 'New Email 2'},
                    {'name': 'Date', 'value': '2026-01-29T12:00:00Z'}
                ]
            }

            mock_payload.headers = headers_map.get(id, [])
            mock_msg.payload = mock_payload
            mock_msg.snippet = f'This is message {id}.'

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

            # Pre-populate the processed file with some duplicate IDs
            processed_file.write_text("duplicate_msg_001\nduplicate_msg_002\n")

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

            # Load the pre-existing processed IDs
            processed_ids = {'duplicate_msg_001', 'duplicate_msg_002'}

            # Process the messages
            check_emails(mock_service, processed_ids)

            # Check that only the new emails were processed (2 new, 2 duplicates skipped)
            final_action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(final_action_files), 2)

            # Check that only the new message IDs were added to the processed file
            final_processed_content = processed_file.read_text()
            self.assertIn('new_msg_001', final_processed_content)
            self.assertIn('new_msg_002', final_processed_content)
            # The duplicate counts should remain as they were initially
            self.assertEqual(final_processed_content.count('duplicate_msg_001'), 1)
            self.assertEqual(final_processed_content.count('duplicate_msg_002'), 1)

            # Verify that action files were only created for new messages
            for action_file in final_action_files:
                content = action_file.read_text()
                # Should contain either new_msg_001 or new_msg_002 but not the duplicates
                self.assertTrue('new_msg_001' in content or 'new_msg_002' in content)
                self.assertNotIn('duplicate_msg_001', content)
                self.assertNotIn('duplicate_msg_002', content)

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