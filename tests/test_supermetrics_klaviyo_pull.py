#!/usr/bin/env python3
import os
import json
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import date

# Import the module to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.supermetrics_klaviyo_pull import (
    fetch_data,
    fetch_all_data,
    write_to_json,
    write_to_csv,
    REPORT_TYPE_MAP
)

# Test fixtures
@pytest.fixture
def mock_api_key():
    with patch.dict(os.environ, {"SUPERMETRICS_API_KEY": "test_api_key"}):
        yield

@pytest.fixture
def temp_data_dir():
    temp_dir = tempfile.mkdtemp()
    with patch("src.supermetrics_klaviyo_pull.DATA_DIR", temp_dir):
        yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_campaign_data():
    return [
        {
            "campaign_id": "campaign_123",
            "campaign_name": "Test Campaign 1",
            "send_time": "2025-05-01T10:00:00Z",
            "subject_line": "Test Subject 1",
            "open_rate": 0.45,
            "click_rate": 0.20,
            "delivered": 1000,
            "opened": 450,
            "clicked": 200
        },
        {
            "campaign_id": "campaign_456",
            "campaign_name": "Test Campaign 2",
            "send_time": "2025-05-08T10:00:00Z",
            "subject_line": "Test Subject 2",
            "open_rate": 0.50,
            "click_rate": 0.25,
            "delivered": 800,
            "opened": 400,
            "clicked": 200
        }
    ]

@pytest.fixture
def mock_events_data():
    return [
        {
            "event_id": "event_123",
            "campaign_id": "campaign_123",
            "event_name": "Open",
            "event_time": "2025-05-01T12:30:00Z",
            "email": "user1@example.com",
            "device": "Mobile"
        },
        {
            "event_id": "event_456",
            "campaign_id": "campaign_123",
            "event_name": "Click",
            "event_time": "2025-05-01T12:35:00Z",
            "email": "user1@example.com",
            "device": "Mobile"
        }
    ]

# Tests
@pytest.mark.parametrize("report_type,ds_id", [
    ("campaign", "klaviyo_campaigns"),
    ("events", "klaviyo_email_events")
])
def test_report_type_mapping(report_type, ds_id):
    assert REPORT_TYPE_MAP[report_type] == ds_id

@patch("src.supermetrics_klaviyo_pull.requests.post")
def test_fetch_data_success(mock_post, mock_api_key, mock_campaign_data):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": mock_campaign_data,
        "next_page_token": "next_page"
    }
    mock_post.return_value = mock_response
    
    # Call the function
    data, next_page_token = fetch_data("2025-05-01", "2025-05-31", "campaign")
    
    # Assertions
    assert data == mock_campaign_data
    assert next_page_token == "next_page"
    mock_post.assert_called_once()
    
    # Check that the correct payload was sent
    call_args = mock_post.call_args[1]
    assert call_args["json"]["ds_id"] == "klaviyo_campaigns"
    assert call_args["json"]["start_date"] == "2025-05-01"
    assert call_args["json"]["end_date"] == "2025-05-31"

@patch("src.supermetrics_klaviyo_pull.requests.post")
def test_fetch_data_with_pagination(mock_post, mock_api_key):
    # Setup mock responses for pagination
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {
        "data": [{"id": "1"}],
        "next_page_token": "page2"
    }
    
    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = {
        "data": [{"id": "2"}],
        "next_page_token": None
    }
    
    mock_post.side_effect = [mock_response1, mock_response2]
    
    # Call the function with pagination
    with patch("src.supermetrics_klaviyo_pull.time.sleep"):
        data = fetch_all_data("2025-05-01", "2025-05-31", "campaign")
    
    # Assertions
    assert len(data) == 2
    assert data[0]["id"] == "1"
    assert data[1]["id"] == "2"
    assert mock_post.call_count == 2

@patch("src.supermetrics_klaviyo_pull.requests.post")
def test_fetch_data_rate_limit_retry(mock_post, mock_api_key):
    # Setup mock responses for rate limiting
    mock_response1 = MagicMock()
    mock_response1.status_code = 429
    mock_response1.headers = {"Retry-After": "1"}
    
    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = {
        "data": [{"id": "1"}],
        "next_page_token": None
    }
    
    mock_post.side_effect = [mock_response1, mock_response2]
    
    # Call the function with rate limiting
    with patch("src.supermetrics_klaviyo_pull.time.sleep"):
        data, next_page_token = fetch_data("2025-05-01", "2025-05-31", "campaign")
    
    # Assertions
    assert data == [{"id": "1"}]
    assert next_page_token is None
    assert mock_post.call_count == 2

@patch("src.supermetrics_klaviyo_pull.requests.post")
def test_fetch_data_server_error_retry(mock_post, mock_api_key):
    # Setup mock responses for server error
    mock_response1 = MagicMock()
    mock_response1.status_code = 500
    
    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = {
        "data": [{"id": "1"}],
        "next_page_token": None
    }
    
    mock_post.side_effect = [mock_response1, mock_response2]
    
    # Call the function with server error
    with patch("src.supermetrics_klaviyo_pull.time.sleep"):
        data, next_page_token = fetch_data("2025-05-01", "2025-05-31", "campaign")
    
    # Assertions
    assert data == [{"id": "1"}]
    assert next_page_token is None
    assert mock_post.call_count == 2

def test_fetch_data_invalid_report_type(mock_api_key):
    # Test with invalid report type
    with pytest.raises(ValueError, match="Invalid report type"):
        fetch_data("2025-05-01", "2025-05-31", "invalid_type")

@patch("src.supermetrics_klaviyo_pull.requests.post")
def test_fetch_data_empty_response(mock_post, mock_api_key):
    # Setup mock response with empty data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [],
        "next_page_token": None
    }
    mock_post.return_value = mock_response
    
    # Call the function
    data, next_page_token = fetch_data("2025-05-01", "2025-05-31", "campaign")
    
    # Assertions
    assert data == []
    assert next_page_token is None

def test_write_to_json(temp_data_dir, mock_campaign_data):
    # Test writing data to JSON
    with patch("src.supermetrics_klaviyo_pull.date") as mock_date:
        mock_date.today.return_value = date(2025, 5, 15)
        json_file = write_to_json(mock_campaign_data, "campaign")
    
    # Assertions
    assert json_file is not None
    assert os.path.exists(json_file)
    
    # Verify file contents
    with open(json_file, "r") as f:
        saved_data = json.load(f)
    assert saved_data == mock_campaign_data

def test_write_to_csv(temp_data_dir, mock_campaign_data):
    # First write JSON file
    with patch("src.supermetrics_klaviyo_pull.date") as mock_date:
        mock_date.today.return_value = date(2025, 5, 15)
        json_file = write_to_json(mock_campaign_data, "campaign")
    
    # Then write CSV file
    csv_file = write_to_csv(mock_campaign_data, json_file)
    
    # Assertions
    assert csv_file is not None
    assert os.path.exists(csv_file)
    assert csv_file.endswith(".csv")
    
    # Verify file contents (basic check)
    with open(csv_file, "r") as f:
        header = f.readline().strip()
    
    # Check that all keys from the first record are in the header
    for key in mock_campaign_data[0].keys():
        assert key in header

def test_write_to_json_empty_data(temp_data_dir):
    # Test writing empty data to JSON
    json_file = write_to_json([], "campaign")
    assert json_file is None

def test_write_to_csv_empty_data(temp_data_dir):
    # Test writing empty data to CSV
    csv_file = write_to_csv([], "some_file.json")
    assert csv_file is None
