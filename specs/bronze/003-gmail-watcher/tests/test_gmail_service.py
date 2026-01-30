"""
Unit tests for gmail_watcher.py - Gmail service functionality
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the bronze directory to the path so we can import gmail_watcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestGmailService(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    @patch('gmail_watcher.Path')
    @patch('gmail_watcher.pickle')
    @patch('gmail_watcher.Request')
    @patch('gmail_watcher.InstalledAppFlow')
    @patch('gmail_watcher.build')
    def test_get_gmail_service_with_valid_credentials(self, mock_build, mock_flow, mock_request, mock_pickle, mock_path):
        """Test that get_gmail_service returns a valid service object when credentials are valid."""
        # Mock the token loading
        mock_path.return_value.exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = True
        mock_creds.expired = False
        mock_pickle.load.return_value = mock_creds

        # Import the function to test
        from bronze.gmail_watcher import get_gmail_service

        # Mock the build function to return a mock service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Call the function
        result = get_gmail_service()

        # Assertions
        self.assertEqual(result, mock_service)
        mock_build.assert_called_once()

    @patch('gmail_watcher.Path')
    @patch('gmail_watcher.pickle')
    @patch('gmail_watcher.Request')
    @patch('gmail_watcher.InstalledAppFlow')
    @patch('gmail_watcher.build')
    def test_get_gmail_service_handles_expired_token(self, mock_build, mock_flow, mock_request, mock_pickle, mock_path):
        """Test that get_gmail_service handles expired tokens by refreshing them."""
        # Mock the token loading
        mock_path.return_value.exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = True
        mock_pickle.load.return_value = mock_creds

        # Import the function to test
        from bronze.gmail_watcher import get_gmail_service

        # Mock the build function to return a mock service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock the refresh
        mock_creds.refresh = Mock()

        # Call the function
        result = get_gmail_service()

        # Assertions
        self.assertEqual(result, mock_service)
        mock_creds.refresh.assert_called_once()
        mock_build.assert_called_once()

    def test_validate_authentication_success(self):
        """Test that validate_authentication returns True for valid service."""
        # Import the function to test
        from bronze.gmail_watcher import validate_authentication

        # Create a mock service that returns a valid profile
        mock_service = Mock()
        mock_users = Mock()
        mock_get_profile = Mock()
        mock_get_profile.execute.return_value = {'emailAddress': 'test@example.com'}
        mock_users.getProfile.return_value = mock_get_profile
        mock_service.users.return_value = mock_users

        # Call the function
        result = validate_authentication(mock_service)

        # Assertions
        self.assertTrue(result)
        mock_users.getProfile.assert_called_once_with(userId='me')
        mock_get_profile.execute.assert_called_once()


if __name__ == '__main__':
    unittest.main()