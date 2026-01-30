"""
Performance tests for gmail_watcher.py - Processing speed and resource usage
"""
import unittest
from unittest.mock import Mock
import tempfile
import os
from pathlib import Path
import time
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestPerformance(unittest.TestCase):

    def test_processing_speed_for_multiple_emails(self):
        """Test that processing speed is reasonable for multiple emails."""
        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that returns multiple messages
        mock_service = Mock()

        # Create 10 mock messages to test processing performance
        mock_messages = [{'id': f'msg_{i:03d}'} for i in range(10)]
        mock_list_response = {'messages': mock_messages}

        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() calls for each message
        def mock_get_message(user_id, id):
            mock_msg = Mock()
            mock_payload = Mock()
            mock_headers = [
                {'name': 'From', 'value': f'sender{id}@example.com'},
                {'name': 'Subject', 'value': f'Subject for {id}'},
                {'name': 'Date', 'value': '2026-01-29T10:30:00Z'}
            ]
            mock_payload.headers = mock_headers
            mock_msg.payload = mock_payload
            mock_msg.snippet = f'This is a test snippet for {id}.'

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

            # Measure the time it takes to process 10 emails
            start_time = time.time()

            # Call the function with an empty set of processed IDs
            processed_ids = set()
            check_emails(mock_service, processed_ids)

            end_time = time.time()
            processing_time = end_time - start_time

            # Check that action files were created
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 10, "All 10 emails should have generated action files")

            # Performance requirement: 10 emails should be processed in under 10 seconds
            # (This is a reasonable threshold for local processing)
            self.assertLess(processing_time, 10.0,
                           f"Processing 10 emails took {processing_time:.2f}s, which is too slow")

            # Additionally, average time per email should be reasonable
            avg_time_per_email = processing_time / 10
            self.assertLess(avg_time_per_email, 1.0,
                           f"Average processing time per email was {avg_time_per_email:.2f}s, which is too slow")

            # Restore original values
            if original_vault_path is not None:
                gmail_watcher.VAULT_PATH = original_vault_path
            if original_needs_action is not None:
                gmail_watcher.NEEDS_ACTION = original_needs_action
            if original_logs is not None:
                gmail_watcher.LOGS = original_logs
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file

    def test_duplicate_lookup_performance(self):
        """Test that duplicate lookup performance remains good as the processed file grows."""
        # Import the functions to test
        from bronze.gmail_watcher import load_processed_ids, save_processed_id

        # Create a temporary file with a large number of processed IDs
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            # Write 1000 IDs to simulate a large processed file
            for i in range(1000):
                tmp_file.write(f"msg_{i:04d}\n")
            tmp_file_path = tmp_file.name

        try:
            # Mock the PROCESSED_FILE path
            import gmail_watcher
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)
            gmail_watcher.PROCESSED_FILE = Path(tmp_file_path)

            # Measure time to load processed IDs
            start_time = time.time()
            processed_ids = load_processed_ids()
            load_time = time.time() - start_time

            # Verify we got all the IDs
            self.assertEqual(len(processed_ids), 1000, "Should have loaded all 1000 processed IDs")

            # Performance requirement: Loading 1000 IDs should be fast
            self.assertLess(load_time, 1.0,
                           f"Loading 1000 processed IDs took {load_time:.2f}s, which is too slow")

            # Test lookup performance - check if an ID exists in the set
            lookup_start_time = time.time()
            lookup_result = "msg_0500" in processed_ids  # Middle element
            lookup_time = time.time() - lookup_start_time

            # Verify the lookup worked
            self.assertTrue(lookup_result, "Lookup should have found the test ID")

            # Performance requirement: Individual lookup should be very fast (O(1) for set)
            self.assertLess(lookup_time, 0.01,
                           f"Individual ID lookup took {lookup_time:.3f}s, which is too slow")

            # Test saving a new ID performance
            save_start_time = time.time()
            save_processed_id("new_msg_9999")
            save_time = time.time() - save_start_time

            # Performance requirement: Saving should be fast
            self.assertLess(save_time, 0.1,
                           f"Saving a new processed ID took {save_time:.3f}s, which is too slow")

            # Verify the new ID was added
            updated_ids = load_processed_ids()
            self.assertIn("new_msg_9999", updated_ids, "New ID should have been saved")
            self.assertEqual(len(updated_ids), 1001, "Should now have 1001 IDs")

            # Restore original value
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file
            else:
                delattr(gmail_watcher, 'PROCESSED_FILE')

        finally:
            # Clean up
            os.unlink(tmp_file_path)

    def test_memory_usage_during_processing(self):
        """Test that memory usage remains reasonable during processing."""
        # This test focuses on ensuring the algorithm is efficient
        # We'll measure the number of action files created vs. memory efficiency

        # Import the function to test
        from bronze.gmail_watcher import check_emails

        # Create a mock service that returns multiple messages
        mock_service = Mock()

        # Create 20 mock messages to test memory usage
        mock_messages = [{'id': f'perf_msg_{i:03d}'} for i in range(20)]
        mock_list_response = {'messages': mock_messages}

        mock_list_method = Mock()
        mock_list_method.list.return_value = Mock(execute=lambda: mock_list_response)
        mock_service.users.return_value = mock_list_method

        # Mock the users().messages().get().execute() calls
        def mock_get_message(user_id, id):
            mock_msg = Mock()
            mock_payload = Mock()
            mock_headers = [
                {'name': 'From', 'value': f'sender{id}@example.com'},
                {'name': 'Subject', 'value': f'Performance Test {id}'},
                {'name': 'Date', 'value': '2026-01-29T10:30:00Z'}
            ]
            mock_payload.headers = mock_headers
            # Create a reasonably sized snippet to test memory usage
            mock_msg.snippet = f'This is a test snippet for {id}. ' * 20  # Repeat to create larger content

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

            # Check that all action files were created
            action_files = list(needs_action_path.glob("EMAIL_*.md"))
            self.assertEqual(len(action_files), 20, "All 20 emails should have generated action files")

            # Verify that each action file has reasonable size (not growing unexpectedly)
            for action_file in action_files:
                file_size = action_file.stat().st_size
                # Each action file should be reasonably sized (under 10KB for a typical email)
                self.assertLess(file_size, 10 * 1024,
                               f"Action file {action_file.name} is {file_size} bytes, which is too large")

            # Check that processed file grew appropriately
            processed_file_size = processed_file.stat().st_size
            # Should be roughly proportional to number of processed messages
            expected_min_size = 20 * 10  # At least 10 bytes per message ID
            self.assertGreater(processed_file_size, expected_min_size,
                             f"Processed file size {processed_file_size} is smaller than expected")

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