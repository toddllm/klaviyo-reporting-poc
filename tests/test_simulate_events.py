import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

import simulate_events


class TestGetOrCreateCustomMetric:
    def test_get_from_cache(self, tmp_path):
        # Create a temporary cache file
        cache_file = tmp_path / ".metric_ids.json"
        with open(cache_file, 'w') as f:
            json.dump({"Test Metric": "test-metric-id-123"}, f)
        
        with patch('simulate_events.cache_file', str(cache_file)):
            metric_id = simulate_events.get_or_create_custom_metric("Test Metric", dry_run=True)
            assert metric_id == "test-metric-id-123"
    
    def test_create_in_dry_run(self, tmp_path):
        # Create a temporary cache file
        cache_file = tmp_path / ".metric_ids.json"
        with open(cache_file, 'w') as f:
            json.dump({}, f)
        
        with patch('simulate_events.cache_file', str(cache_file)):
            metric_id = simulate_events.get_or_create_custom_metric("New Metric", dry_run=True)
            assert "mock-new-metric-id" in metric_id
            
            # Check that it was added to the cache
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                assert "New Metric" in cache
                assert cache["New Metric"] == metric_id
    
    @patch('simulate_events.get_json_api')
    @patch('simulate_events.post_json_api')
    def test_get_existing_metric(self, mock_post, mock_get, tmp_path):
        # Create a temporary cache file
        cache_file = tmp_path / ".metric_ids.json"
        with open(cache_file, 'w') as f:
            json.dump({}, f)
        
        # Mock the API response for an existing metric
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{
                "id": "existing-metric-id",
                "type": "metric",
                "attributes": {"name": "Existing Metric"}
            }]
        }
        mock_get.return_value = mock_response
        
        with patch('simulate_events.cache_file', str(cache_file)):
            metric_id = simulate_events.get_or_create_custom_metric("Existing Metric")
            assert metric_id == "existing-metric-id"
            
            # Check that it was added to the cache
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                assert "Existing Metric" in cache
                assert cache["Existing Metric"] == "existing-metric-id"
    
    @patch('simulate_events.get_json_api')
    @patch('simulate_events.post_json_api')
    def test_create_new_metric(self, mock_post, mock_get, tmp_path):
        # Create a temporary cache file
        cache_file = tmp_path / ".metric_ids.json"
        with open(cache_file, 'w') as f:
            json.dump({}, f)
        
        # Mock the API responses
        get_response = MagicMock()
        get_response.json.return_value = {"data": []}  # No existing metric
        mock_get.return_value = get_response
        
        post_response = MagicMock()
        post_response.json.return_value = {
            "data": {
                "id": "new-metric-id",
                "type": "metric",
                "attributes": {"name": "New Metric"}
            }
        }
        mock_post.return_value = post_response
        
        with patch('simulate_events.cache_file', str(cache_file)):
            metric_id = simulate_events.get_or_create_custom_metric("New Metric")
            assert metric_id == "new-metric-id"
            
            # Check that it was added to the cache
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                assert "New Metric" in cache
                assert cache["New Metric"] == "new-metric-id"
            
            # Verify the POST payload
            expected_payload = {
                "data": {
                    "type": "metric",
                    "attributes": {
                        "name": "New Metric",
                        "service": "api"
                    }
                }
            }
            mock_post.assert_called_once()
            actual_payload = mock_post.call_args[0][1]
            assert actual_payload == expected_payload


class TestSimulateEvent:
    @patch('simulate_events.get_or_create_custom_metric')
    @patch('simulate_events.post_json_api')
    def test_simulate_event_dry_run(self, mock_post, mock_get_metric):
        # Mock the get_or_create_custom_metric function
        mock_get_metric.return_value = "test-metric-id"
        
        # Call the function
        result = simulate_events.simulate_event(
            "test-profile-id", 
            "Test Metric", 
            {"test_property": "test_value"}, 
            dry_run=True
        )
        
        # Check the result
        assert result is True
        
        # Verify the metric ID was requested
        mock_get_metric.assert_called_once_with("Test Metric", True)
        
        # Verify the payload structure
        mock_post.assert_called_once()
        url, payload, dry_run = mock_post.call_args[0]
        assert url == "https://a.klaviyo.com/api/events/"
        assert dry_run is True
        
        # Check that metric_id is inside the metric object
        assert payload["data"]["relationships"]["metric"]["data"]["id"] == "test-metric-id"
        assert payload["data"]["relationships"]["metric"]["data"]["type"] == "metric"
    
    @patch('simulate_events.get_or_create_custom_metric')
    @patch('simulate_events.post_json_api')
    def test_simulate_event_real_call(self, mock_post, mock_get_metric):
        # Mock the get_or_create_custom_metric function
        mock_get_metric.return_value = "real-metric-id"
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        # Call the function
        result = simulate_events.simulate_event(
            "real-profile-id", 
            "Real Metric", 
            {"property": "value", "value": 10.5}, 
            dry_run=False
        )
        
        # Check the result
        assert result is True
        
        # Verify the metric ID was requested
        mock_get_metric.assert_called_once_with("Real Metric", False)
        
        # Verify the payload structure
        mock_post.assert_called_once()
        url, payload, dry_run = mock_post.call_args[0]
        assert url == "https://a.klaviyo.com/api/events/"
        assert dry_run is False
        
        # Check that metric_id is inside the metric object
        assert payload["data"]["relationships"]["metric"]["data"]["id"] == "real-metric-id"
        assert payload["data"]["relationships"]["metric"]["data"]["type"] == "metric"
        
        # Check that value is properly set
        assert payload["data"]["attributes"]["value"] == 10.5


class TestMainFunction:
    @patch('simulate_events.get_random_profile_id')
    @patch('simulate_events.simulate_event')
    def test_main_with_random_profile(self, mock_simulate, mock_get_profile):
        # Mock the profile ID
        mock_get_profile.return_value = "random-profile-id"
        
        # Mock the simulate_event function
        mock_simulate.return_value = True
        
        # Call main with dry run
        with patch('sys.argv', ['simulate_events.py', '--dry-run']):
            exit_code = simulate_events.main()
        
        # Check the result
        assert exit_code == 0
        
        # Verify the profile ID was requested
        mock_get_profile.assert_called_once_with(True)
        
        # Verify simulate_event was called
        mock_simulate.assert_called_once()
        profile_id, metric, properties, dry_run = mock_simulate.call_args[0]
        assert profile_id == "random-profile-id"
        assert metric == "Opened Email"  # Default metric
        assert dry_run is True
    
    @patch('simulate_events.simulate_event')
    def test_main_with_specific_profile(self, mock_simulate):
        # Mock the simulate_event function
        mock_simulate.return_value = True
        
        # Call main with specific profile and metric
        with patch('sys.argv', [
            'simulate_events.py', 
            '--profile-id', 'specific-profile-id',
            '--metric', 'Custom Metric',
            '--count', '3',
            '--dry-run'
        ]):
            exit_code = simulate_events.main()
        
        # Check the result
        assert exit_code == 0
        
        # Verify simulate_event was called 3 times
        assert mock_simulate.call_count == 3
        
        # Check the arguments for the first call
        profile_id, metric, properties, dry_run = mock_simulate.call_args_list[0][0]
        assert profile_id == "specific-profile-id"
        assert metric == "Custom Metric"
        assert dry_run is True
