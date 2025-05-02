import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_send_campaign import (
    create_campaign,
    get_campaign_messages,
    assign_template,
    check_message_status,
    wait_for_message_ready,
    send_campaign
)

class TestCampaignCreation(unittest.TestCase):
    
    @patch('requests.post')
    def test_create_campaign(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": {"id": "test-campaign-id"}}
        mock_post.return_value = mock_response
        
        # Call function
        result = create_campaign("Test Campaign", "test-audience-id")
        
        # Assertions
        self.assertEqual(result, "test-campaign-id")
        mock_post.assert_called_once()
        
    @patch('requests.get')
    def test_get_campaign_messages(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "message-1"},
                {"id": "message-2"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Call function
        result = get_campaign_messages("test-campaign-id")
        
        # Assertions
        self.assertEqual(result, ["message-1", "message-2"])
        mock_get.assert_called_once()
    
    @patch('requests.patch')
    def test_assign_template(self, mock_patch):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        # Call function
        result = assign_template("test-message-id", "test-template-id")
        
        # Assertions
        self.assertTrue(result)
        mock_patch.assert_called_once()
    
    @patch('requests.get')
    def test_check_message_status(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "status": "ready"
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Call function
        result = check_message_status("test-message-id")
        
        # Assertions
        self.assertEqual(result, "ready")
        mock_get.assert_called_once()
    
    @patch('create_send_campaign.check_message_status')
    @patch('time.sleep')
    def test_wait_for_message_ready(self, mock_sleep, mock_check_status):
        # Setup mock response
        mock_check_status.return_value = "ready"
        
        # Call function
        result = wait_for_message_ready("test-message-id")
        
        # Assertions
        self.assertTrue(result)
        mock_check_status.assert_called_once()
        mock_sleep.assert_not_called()
    
    @patch('requests.post')
    def test_send_campaign(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        # Call function
        result = send_campaign("test-campaign-id")
        
        # Assertions
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    def test_dry_run_mode(self):
        # Test dry run mode for all functions
        self.assertEqual(create_campaign("Test", "audience-id", dry_run=True), "dry-run-campaign-id")
        self.assertEqual(get_campaign_messages("campaign-id", dry_run=True), ["dry-run-message-id"])
        self.assertTrue(assign_template("message-id", "template-id", dry_run=True))
        self.assertEqual(check_message_status("message-id", dry_run=True), "ready")
        self.assertTrue(wait_for_message_ready("message-id", dry_run=True))
        self.assertTrue(send_campaign("campaign-id", dry_run=True))

if __name__ == '__main__':
    unittest.main()
