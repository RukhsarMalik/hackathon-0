"""
Unit tests for gmail_watcher.py - Duplicate detection functionality
"""
import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestDuplicateDetection(unittest.TestCase):

    def test_load_processed_ids_empty_file(self):
        """Test that load_processed_ids returns an empty set when the file is empty."""
        # Import the function to test
        from bronze.gmail_watcher import load_processed_ids

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("")  # Empty file
            tmp_file_path = tmp_file.name

        try:
            # Mock the PROCESSED_FILE path
            import gmail_watcher
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)
            gmail_watcher.PROCESSED_FILE = Path(tmp_file_path)

            # Call the function
            result = load_processed_ids()

            # Assertions
            self.assertIsInstance(result, set)
            self.assertEqual(len(result), 0)

            # Restore original value
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file
            else:
                delattr(gmail_watcher, 'PROCESSED_FILE')

        finally:
            # Clean up
            os.unlink(tmp_file_path)

    def test_load_processed_ids_with_content(self):
        """Test that load_processed_ids returns correct IDs from the file."""
        # Import the function to test
        from bronze.gmail_watcher import load_processed_ids

        # Create a temporary file with some IDs
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("msg123\nmsg456\nmsg789\n")
            tmp_file_path = tmp_file.name

        try:
            # Mock the PROCESSED_FILE path
            import gmail_watcher
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)
            gmail_watcher.PROCESSED_FILE = Path(tmp_file_path)

            # Call the function
            result = load_processed_ids()

            # Assertions
            self.assertIsInstance(result, set)
            self.assertIn("msg123", result)
            self.assertIn("msg456", result)
            self.assertIn("msg789", result)
            self.assertEqual(len(result), 3)

            # Restore original value
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file
            else:
                delattr(gmail_watcher, 'PROCESSED_FILE')

        finally:
            # Clean up
            os.unlink(tmp_file_path)

    def test_save_processed_id(self):
        """Test that save_processed_id adds an ID to the file."""
        # Import the function to test
        from bronze.gmail_watcher import save_processed_id, load_processed_ids

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("existing_msg1\n")
            tmp_file_path = tmp_file.name

        try:
            # Mock the PROCESSED_FILE path
            import gmail_watcher
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)
            gmail_watcher.PROCESSED_FILE = Path(tmp_file_path)

            # Initially, we have one ID
            initial_ids = load_processed_ids()
            self.assertEqual(len(initial_ids), 1)
            self.assertIn("existing_msg1", initial_ids)

            # Save a new ID
            save_processed_id("new_msg123")

            # Reload and check
            updated_ids = load_processed_ids()
            self.assertEqual(len(updated_ids), 2)
            self.assertIn("existing_msg1", updated_ids)
            self.assertIn("new_msg123", updated_ids)

            # Restore original value
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file
            else:
                delattr(gmail_watcher, 'PROCESSED_FILE')

        finally:
            # Clean up
            os.unlink(tmp_file_path)

    def test_save_processed_id_avoids_duplicates(self):
        """Test that save_processed_id doesn't add duplicate IDs to the file."""
        # Import the function to test
        from bronze.gmail_watcher import save_processed_id, load_processed_ids

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("existing_msg1\n")
            tmp_file_path = tmp_file.name

        try:
            # Mock the PROCESSED_FILE path
            import gmail_watcher
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)
            gmail_watcher.PROCESSED_FILE = Path(tmp_file_path)

            # Initially, we have one ID
            initial_ids = load_processed_ids()
            self.assertEqual(len(initial_ids), 1)

            # Try to save the same ID twice
            save_processed_id("existing_msg1")
            save_processed_id("existing_msg1")

            # Reload and check - should still only have one unique ID
            updated_ids = load_processed_ids()
            self.assertEqual(len(updated_ids), 1)
            self.assertIn("existing_msg1", updated_ids)

            # Restore original value
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file
            else:
                delattr(gmail_watcher, 'PROCESSED_FILE')

        finally:
            # Clean up
            os.unlink(tmp_file_path)


if __name__ == '__main__':
    unittest.main()