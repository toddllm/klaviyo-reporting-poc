#!/usr/bin/env python3

import os
import json
import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock

from fetch_metrics import get_metric_id, fetch_metrics


def test_get_metric_id_caching():
    # Create a temporary cache file
    test_cache = {
        "Opened Email": "123",
        "Clicked Email": "456"
    }
    
    with open(".metric_ids.json", "w") as f:
        json.dump(test_cache, f)
    
    # Test that the function uses the cache
    with patch("requests.get") as mock_get:
        metric_id = get_metric_id("Opened Email")
        assert metric_id == "123"
        mock_get.assert_not_called()  # Should not call API when cache exists
    
    # Test force refresh
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": "789"}]}
        mock_get.return_value = mock_response
        
        metric_id = get_metric_id("Opened Email", force_refresh=True)
        assert metric_id == "789"
        mock_get.assert_called_once()  # Should call API when force_refresh=True
    
    # Clean up
    os.remove(".metric_ids.json")


def test_fetch_metrics_date_handling():
    # Test that the function uses UTC dates in ISO 8601 format
    with patch("requests.get") as mock_get, \
         patch("builtins.open", MagicMock()), \
         patch("csv.DictWriter", MagicMock()), \
         patch("json.dump", MagicMock()):
        
        # Mock responses for the API calls
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        # Call with explicit dates
        test_start = "2025-05-01"
        test_end = "2025-05-08"
        fetch_metrics(test_start, test_end)
        
        # Check that the dates were passed correctly to the API
        calls = mock_get.call_args_list
        for call in calls:
            args, kwargs = call
            if "params" in kwargs and "start_date" in kwargs["params"]:
                assert kwargs["params"]["start_date"] == test_start
                assert kwargs["params"]["end_date"] == test_end


def test_metric_window():
    # Test that the function correctly handles the date window
    with patch("requests.get") as mock_get, \
         patch("builtins.open", MagicMock()), \
         patch("csv.DictWriter", MagicMock()), \
         patch("json.dump", MagicMock()):
        
        # Mock responses for the API calls
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        # Call without explicit dates (should use default window)
        fetch_metrics()
        
        # Check that the dates were calculated correctly
        calls = mock_get.call_args_list
        for call in calls:
            args, kwargs = call
            if "params" in kwargs and "start_date" in kwargs["params"]:
                # Default start date should be 7 days ago in UTC
                expected_start = (datetime.now(UTC).date() - timedelta(days=7)).isoformat()
                expected_end = datetime.now(UTC).date().isoformat()
                
                assert kwargs["params"]["start_date"] == expected_start
                assert kwargs["params"]["end_date"] == expected_end


def test_dry_run_mode():
    # Test that dry run mode doesn't make API calls
    with patch("requests.get") as mock_get:
        result = fetch_metrics(dry_run=True)
        assert result is True
        mock_get.assert_not_called()


def test_mock_mode():
    # Test that mock mode generates fake data without API calls
    with patch("requests.get") as mock_get, \
         patch("builtins.open", MagicMock()), \
         patch("csv.DictWriter", MagicMock()), \
         patch("json.dump", MagicMock()), \
         patch("fetch_metrics.get_config", return_value={"MODE": "mock", "CAMPAIGN_ID": "test"}):
        
        result = fetch_metrics()
        assert result is True
        mock_get.assert_not_called()
