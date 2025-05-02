import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import slack_integration

def test_format_metrics_for_slack():
    sample_metrics = {
        "delivered": "1,000",
        "opened": "450 (45%)",
        "clicked": "120 (12%)",
        "revenue": "$1,250.00"
    }
    
    blocks = slack_integration.format_metrics_for_slack(sample_metrics)
    
    # Check that we have the expected number of blocks
    assert len(blocks) == 4
    
    # Check header block
    assert blocks[0]["type"] == "header"
    assert "Campaign Performance Report" in blocks[0]["text"]["text"]
    
    # Check metrics section
    assert blocks[2]["type"] == "section"
    assert len(blocks[2]["fields"]) == 4  # 4 metrics
    
    # Check report link
    assert blocks[3]["type"] == "section"
    assert "View detailed report" in blocks[3]["text"]["text"]
    assert "Looker Studio Dashboard" in blocks[3]["text"]["text"]

@patch('slack_integration.requests.post')
def test_send_slack_message(mock_post):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    # Call the function
    response = slack_integration.send_slack_message("Test message")
    
    # Verify the function called requests.post with the right arguments
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    
    # Check URL
    assert kwargs["headers"]["Content-Type"] == "application/json"
    
    # Check payload
    payload = json.loads(kwargs["data"])
    assert payload["text"] == "Test message"
    
    # Check response
    assert response == mock_response

@patch('slack_integration.send_slack_message')
def test_send_report_to_slack(mock_send):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_send.return_value = mock_response
    
    # Sample data
    sample_metrics = {"opened": "45%", "clicked": "12%"}
    sample_insights = "Open rate increased by 5%"
    
    # Call the function
    response = slack_integration.send_report_to_slack(sample_metrics, sample_insights)
    
    # Verify send_slack_message was called
    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    
    # Check message and blocks
    assert "Campaign Performance Report" in kwargs["message"]
    assert len(kwargs["blocks"]) > 0
    
    # Check response
    assert response == mock_response
