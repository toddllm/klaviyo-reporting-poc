import os
import pytest
import tempfile
import json
import csv
import requests
from unittest.mock import patch, MagicMock
from src.klaviyo_api_ingest import (
    get_api_key,
    fetch_campaigns,
    fetch_all_campaigns,
    fetch_campaign_metrics,
    write_to_csv,
    write_to_json
)

# Test API key retrieval
def test_get_api_key_success():
    with patch.dict(os.environ, {"KLAVIYO_API_KEY": "test_api_key"}):
        assert get_api_key() == "test_api_key"

def test_get_api_key_missing():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            get_api_key()

# Test campaign fetching
@patch("src.klaviyo_api_ingest.requests.get")
def test_fetch_campaigns_success(mock_get):
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": "campaign_123", "name": "Test Campaign"}
        ],
        "next_page_token": "next_token"
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test function
    campaigns, token = fetch_campaigns(dry_run=False)
    
    # Assertions
    assert len(campaigns) == 1
    assert campaigns[0]["id"] == "campaign_123"
    assert token == "next_token"

@patch("src.klaviyo_api_ingest.requests.get")
def test_fetch_campaigns_error(mock_get):
    # Mock error response
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    
    # Test function
    campaigns, token = fetch_campaigns(dry_run=False)
    
    # Assertions
    assert campaigns == []
    assert token is None

# Test pagination
@patch("src.klaviyo_api_ingest.fetch_campaigns")
def test_fetch_all_campaigns(mock_fetch):
    # Mock responses for pagination
    mock_fetch.side_effect = [
        ([{"id": "campaign_1"}], "token1"),
        ([{"id": "campaign_2"}], "token2"),
        ([{"id": "campaign_3"}], None)
    ]
    
    # Test function
    campaigns = fetch_all_campaigns(dry_run=False)
    
    # Assertions
    assert len(campaigns) == 3
    assert campaigns[0]["id"] == "campaign_1"
    assert campaigns[1]["id"] == "campaign_2"
    assert campaigns[2]["id"] == "campaign_3"
    assert mock_fetch.call_count == 3

# Test metrics fetching
@patch("src.klaviyo_api_ingest.requests.get")
def test_fetch_campaign_metrics(mock_get):
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "delivered": 100,
        "opened": 45,
        "clicked": 20,
        "revenue": 250.0
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test function
    metrics = fetch_campaign_metrics("campaign_123", dry_run=False)
    
    # Assertions
    assert metrics["delivered"] == 100
    assert metrics["opened"] == 45
    assert metrics["clicked"] == 20
    assert metrics["revenue"] == 250.0

# Test output functions
def test_write_to_csv():
    # Test data
    data = [
        {"id": "campaign_1", "name": "Test 1", "open_rate": 0.45},
        {"id": "campaign_2", "name": "Test 2", "open_rate": 0.50}
    ]
    
    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Test function
        result = write_to_csv(data, temp_path)
        assert result is True
        
        # Verify file contents
        with open(temp_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["id"] == "campaign_1"
            assert rows[1]["id"] == "campaign_2"
    finally:
        # Clean up
        os.unlink(temp_path)

def test_write_to_json():
    # Test data
    data = [
        {"id": "campaign_1", "name": "Test 1", "open_rate": 0.45},
        {"id": "campaign_2", "name": "Test 2", "open_rate": 0.50}
    ]
    
    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Test function
        result = write_to_json(data, temp_path)
        assert result is True
        
        # Verify file contents
        with open(temp_path, "r") as f:
            loaded_data = json.load(f)
            assert len(loaded_data) == 2
            assert loaded_data[0]["id"] == "campaign_1"
            assert loaded_data[1]["id"] == "campaign_2"
    finally:
        # Clean up
        os.unlink(temp_path)
