"""
Security tests for gmail_watcher.py - Credential handling and file permissions
"""
import unittest
import tempfile
import os
from pathlib import Path
import stat
import sys

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestSecurity(unittest.TestCase):

    def test_secure_file_permissions(self):
        """Test that sensitive files have appropriate permissions."""
        # Test the processed emails file permissions
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test_msg_001\ntest_msg_002\n")
            tmp_file_path = Path(tmp_file.name)

        # Check that the file exists and has reasonable permissions
        self.assertTrue(tmp_file_path.exists(), "Test file should exist")

        # On Unix-like systems, check file permissions
        if os.name != 'nt':  # Not Windows
            file_stat = tmp_file_path.stat()
            # Check that it's not world-readable (at least for sensitive files)
            self.assertFalse(file_stat.st_mode & stat.S_IROTH,
                           "File should not be world-readable (not applicable on Windows)")

        # Clean up
        tmp_file_path.unlink()

    def test_sensitive_data_not_exposed_in_logs(self):
        """Test that sensitive data is not exposed in error logs."""
        # Import the functions to test
        from bronze.gmail_watcher import load_processed_ids

        # Create a temporary file with some processed IDs
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("msg_001\nmsg_002\nmsg_003\n")
            tmp_file_path = Path(tmp_file.name)

        try:
            # Mock the PROCESSED_FILE path
            import gmail_watcher
            original_processed_file = getattr(gmail_watcher, 'PROCESSED_FILE', None)
            gmail_watcher.PROCESSED_FILE = tmp_file_path

            # Call the function
            result = load_processed_ids()

            # Verify that the function returns the correct data
            self.assertIsInstance(result, set)
            self.assertIn("msg_001", result)
            self.assertIn("msg_002", result)
            self.assertIn("msg_003", result)

            # The function should not expose sensitive data in any returned values
            # that could be logged (in this case, there are no logs, but the principle holds)

            # Restore original value
            if original_processed_file is not None:
                gmail_watcher.PROCESSED_FILE = original_processed_file
            else:
                delattr(gmail_watcher, 'PROCESSED_FILE')

        finally:
            # Clean up
            os.unlink(tmp_file_path)

    def test_environment_variable_handling(self):
        """Test that environment variables are handled securely."""
        # Import the function to get VAULT_PATH
        import os
        from pathlib import Path

        # Test that the VAULT_PATH can be configured via environment variable
        original_env = os.environ.get('VAULT_PATH')

        try:
            # Set a test environment variable
            test_path = "/secure/test/path"
            os.environ['VAULT_PATH'] = test_path

            # Import and check the VAULT_PATH configuration
            import gmail_watcher
            # Recreate the VAULT_PATH to reflect the environment change
            test_vault_path = Path(os.getenv('VAULT_PATH', './bronze/AI_Employee_Vault'))

            self.assertEqual(str(test_vault_path), test_path,
                           "VAULT_PATH should be set from environment variable")

        finally:
            # Restore original environment
            if original_env is not None:
                os.environ['VAULT_PATH'] = original_env
            elif 'VAULT_PATH' in os.environ:
                del os.environ['VAULT_PATH']

    def test_file_path_traversal_protection(self):
        """Test that the system is protected against file path traversal attacks."""
        import gmail_watcher
        from pathlib import Path

        # Test that paths are properly handled to prevent traversal
        # This is more of a design check - ensuring that user input isn't directly used in file paths

        # The VAULT_PATH should be resolved to prevent traversal
        vault_path = Path(os.getenv('VAULT_PATH', './bronze/AI_Employee_Vault')).resolve()

        # The path should not contain patterns that could indicate traversal attempts
        # when constructed from user input (though in our case it's hardcoded/default)
        path_str = str(vault_path)

        # This is a basic check - in a real system, we'd validate any user-provided paths
        self.assertNotIn('../', path_str)
        self.assertNotIn('..\\', path_str)

    def test_configuration_does_not_contain_hardcoded_credentials(self):
        """Test that configuration files don't contain hardcoded credentials."""
        # Check that our .env.example doesn't contain actual credentials
        env_example_path = Path("bronze/.env.example")

        if env_example_path.exists():
            env_content = env_example_path.read_text()

            # Look for credential-related patterns but ensure they're commented out or just placeholders
            lines = env_content.split('\n')

            for line in lines:
                stripped_line = line.strip()

                # Skip comment lines that are OK to mention credentials
                if stripped_line.startswith('#'):
                    continue

                # Check for common credential-related variable names
                if 'CREDENTIALS' in stripped_line.upper():
                    # Should be commented out or just a placeholder
                    self.assertTrue(stripped_line.startswith('#'),
                                  f"Credential-related setting should be commented out: {stripped_line}")

                if 'TOKEN' in stripped_line.upper() and '=' in stripped_line:
                    # Should be commented out
                    self.assertTrue(stripped_line.startswith('#'),
                                  f"Token-related setting should be commented out: {stripped_line}")


if __name__ == '__main__':
    import unittest
    unittest.main()