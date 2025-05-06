# PR 1: Klaviyo API Ingest Script - Implementation Guide

This guide provides detailed instructions for implementing the `klaviyo_api_ingest.py` script as part of PR 1 in the Narrow Scope POC PR Plan.

## Overview

The `klaviyo_api_ingest.py` script is responsible for fetching campaign metrics from the Klaviyo API. It should:

1. Authenticate with the Klaviyo API using an API key
2. Fetch a list of campaigns and their associated metrics
3. Handle pagination for large result sets
4. Implement error handling for API failures
5. Output the data to a local CSV or JSON file

## Implementation Steps

### 1. Create the Basic Script Structure

Create a new file at `src/klaviyo_api_ingest.py` with the following structure:

```python
#!/usr/bin/env python3
import os
import requests
import time
import json
import csv
import argparse
from datetime import datetime, timedelta

# Constants
BASE_URL = "https://a.klaviyo.com/api/v1"

# Configuration
def get_api_key():
    """Get Klaviyo API key from environment variable"""
    api_key = os.getenv("KLAVIYO_API_KEY")
    if not api_key:
        raise ValueError("KLAVIYO_API_KEY environment variable not set")
    return api_key

# API Functions
def fetch_campaigns(page_token=None, dry_run=False):
    """Fetch campaigns from Klaviyo API with pagination"""
    # Implementation here

def fetch_all_campaigns(dry_run=False):
    """Fetch all campaigns using pagination"""
    # Implementation here

def fetch_campaign_metrics(campaign_id, dry_run=False):
    """Fetch metrics for a specific campaign"""
    # Implementation here

# Output Functions
def write_to_csv(data, output_file="campaigns.csv"):
    """Write campaign data to CSV file"""
    # Implementation here

def write_to_json(data, output_file="campaigns.json"):
    """Write campaign data to JSON file"""
    # Implementation here

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Fetch campaign metrics from Klaviyo API")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", default="campaigns.csv", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    args = parser.parse_args()
    
    # Implementation here

if __name__ == "__main__":
    main()
```

### 2. Implement API Authentication

Update the `fetch_campaigns` function to authenticate with the Klaviyo API:

```python
def fetch_campaigns(page_token=None, dry_run=False):
    """Fetch campaigns from Klaviyo API with pagination"""
    api_key = get_api_key()
    params = {"api_key": api_key, "count": 100}
    if page_token:
        params["page_token"] = page_token
    
    if dry_run:
        print(f"[DRY RUN] Would fetch campaigns with params: {params}")
        # Return mock data for dry run
        return [
            {
                "id": "campaign_123",
                "name": "Test Campaign 1",
                "send_time": "2025-05-01T10:00:00Z",
                "subject": "Test Subject 1",
                "open_rate": 0.45,
                "click_rate": 0.20
            },
            {
                "id": "campaign_456",
                "name": "Test Campaign 2",
                "send_time": "2025-05-08T10:00:00Z",
                "subject": "Test Subject 2",
                "open_rate": 0.50,
                "click_rate": 0.25
            }
        ], "next_page_token_123"
    
    try:
        response = requests.get(f"{BASE_URL}/campaigns", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["data"], data.get("next_page_token")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching campaigns: {e}")
        return [], None
```

### 3. Implement Pagination

Update the `fetch_all_campaigns` function to handle pagination:

```python
def fetch_all_campaigns(dry_run=False):
    """Fetch all campaigns using pagination"""
    all_campaigns = []
    page_token = None
    page_count = 0
    max_pages = 10  # Limit for safety
    
    while page_count < max_pages:
        campaigns, next_page_token = fetch_campaigns(page_token, dry_run)
        all_campaigns.extend(campaigns)
        page_token = next_page_token
        page_count += 1
        
        if not page_token:
            break
        
        # Avoid rate limiting
        time.sleep(0.2)
    
    return all_campaigns
```

### 4. Implement Campaign Metrics Fetching

Add the `fetch_campaign_metrics` function:

```python
def fetch_campaign_metrics(campaign_id, dry_run=False):
    """Fetch metrics for a specific campaign"""
    api_key = get_api_key()
    params = {
        "api_key": api_key,
        "campaign_id": campaign_id,
        "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date": datetime.utcnow().strftime("%Y-%m-%d")
    }
    
    if dry_run:
        print(f"[DRY RUN] Would fetch metrics for campaign {campaign_id} with params: {params}")
        # Return mock data for dry run
        return {
            "delivered": 100,
            "opened": 45,
            "clicked": 20,
            "revenue": 250.0
        }
    
    try:
        response = requests.get(f"{BASE_URL}/campaign-metrics", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metrics for campaign {campaign_id}: {e}")
        return {}
```

### 5. Implement Output Functions

Implement the CSV and JSON output functions:

```python
def write_to_csv(data, output_file="campaigns.csv"):
    """Write campaign data to CSV file"""
    if not data:
        print("No data to write to CSV")
        return False
    
    # Define the fields we want to include
    fieldnames = ["id", "name", "send_time", "subject", "open_rate", "click_rate", "delivered", "opened", "clicked", "revenue"]
    
    try:
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Only include fields that are in our fieldnames list
                filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(filtered_row)
        print(f"Data written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False

def write_to_json(data, output_file="campaigns.json"):
    """Write campaign data to JSON file"""
    if not data:
        print("No data to write to JSON")
        return False
    
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Data written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to JSON: {e}")
        return False
```

### 6. Implement Main Function

Complete the `main` function:

```python
def main():
    parser = argparse.ArgumentParser(description="Fetch campaign metrics from Klaviyo API")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", default="campaigns.csv", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    args = parser.parse_args()
    
    print(f"Fetching campaigns from Klaviyo API...")
    campaigns = fetch_all_campaigns(args.dry_run)
    print(f"Found {len(campaigns)} campaigns")
    
    # Fetch metrics for each campaign
    for campaign in campaigns:
        campaign_id = campaign["id"]
        print(f"Fetching metrics for campaign {campaign_id}...")
        metrics = fetch_campaign_metrics(campaign_id, args.dry_run)
        # Add metrics to campaign data
        campaign.update(metrics)
    
    # Write data to file
    if args.format == "csv":
        write_to_csv(campaigns, args.output)
    else:
        write_to_json(campaigns, args.output)
```

### 7. Create Unit Tests

Create a new file at `tests/test_klaviyo_api_ingest.py` with the following content:

```python
import os
import pytest
import tempfile
import json
import csv
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
```

## Validation Steps

### For Developers

1. Create the necessary directory structure:
   ```bash
   mkdir -p src tests
   ```

2. Implement the `klaviyo_api_ingest.py` script as described above.

3. Implement the unit tests as described above.

4. Run the script in dry-run mode to verify it works correctly:
   ```bash
   python src/klaviyo_api_ingest.py --dry-run
   ```

5. Run the unit tests to verify they pass:
   ```bash
   pytest tests/test_klaviyo_api_ingest.py -v
   ```

### For Reviewers

1. Verify that the script follows the project's coding standards.

2. Check that the script handles API errors gracefully.

3. Verify that pagination works correctly for large result sets.

4. Ensure that the output files (CSV and JSON) are formatted correctly.

5. Run the unit tests to verify they pass:
   ```bash
   pytest tests/test_klaviyo_api_ingest.py -v
   ```

## Next Steps

After implementing and validating PR 1, proceed to PR 2: LookML Field Mapper.
