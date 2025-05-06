# PR 5: ETL Runner - Implementation Guide

This guide provides detailed instructions for implementing the `etl_runner.py` script as part of PR 5 in the Narrow Scope POC PR Plan.

## Overview

The `etl_runner.py` script is responsible for integrating the fetch → normalize → export pipeline. It should:

1. Combine functionality from `klaviyo_api_ingest.py` and `lookml_field_mapper.py`
2. Implement a consistent file output format
3. Include comprehensive error handling and logging
4. Support future integration with Supermetrics
5. Include unit tests

## Implementation Steps

### 1. Create the Basic Script Structure

Create a new file at `src/etl_runner.py` with the following structure:

```python
#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from datetime import datetime

# Import from other modules
from klaviyo_api_ingest import fetch_all_campaigns, fetch_campaign_metrics
from lookml_field_mapper import normalize_records

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("etl_runner")

# Constants
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_OUTPUT_FORMAT = "csv"

# ETL Functions
def extract(dry_run=False):
    """Extract data from Klaviyo API"""
    # Implementation here

def transform(raw_data):
    """Transform raw data to the normalized format"""
    # Implementation here

def load(data, output_file, output_format="csv"):
    """Load data to the specified output format"""
    # Implementation here

def run_etl(output_file=None, output_format="csv", dry_run=False):
    """Run the full ETL pipeline"""
    # Implementation here

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Run the ETL pipeline for Klaviyo campaign metrics")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    args = parser.parse_args()
    
    # Implementation here

if __name__ == "__main__":
    main()
```

### 2. Implement the Extract Function

Complete the `extract` function to fetch data from the Klaviyo API:

```python
def extract(dry_run=False):
    """Extract data from Klaviyo API"""
    logger.info("Extracting data from Klaviyo API...")
    
    try:
        # Fetch all campaigns
        campaigns = fetch_all_campaigns(dry_run)
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Fetch metrics for each campaign
        for campaign in campaigns:
            campaign_id = campaign["id"]
            logger.info(f"Fetching metrics for campaign {campaign_id}...")
            metrics = fetch_campaign_metrics(campaign_id, dry_run)
            # Add metrics to campaign data
            campaign.update(metrics)
        
        return campaigns
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        return []
```

### 3. Implement the Transform Function

Complete the `transform` function to normalize the data:

```python
def transform(raw_data):
    """Transform raw data to the normalized format"""
    if not raw_data:
        logger.warning("No data to transform")
        return []
    
    logger.info(f"Transforming {len(raw_data)} records...")
    
    try:
        # Use the normalize_records function from lookml_field_mapper.py
        normalized_data = normalize_records(raw_data)
        logger.info(f"Transformed {len(normalized_data)} records")
        return normalized_data
    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        return []
```

### 4. Implement the Load Function

Complete the `load` function to export the data:

```python
def load(data, output_file, output_format="csv"):
    """Load data to the specified output format"""
    if not data:
        logger.warning("No data to load")
        return False
    
    if not output_file:
        # Generate default output file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(DEFAULT_OUTPUT_DIR, f"klaviyo_metrics_{timestamp}.{output_format}")
    
    logger.info(f"Loading {len(data)} records to {output_file}...")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        if output_format == "csv":
            import csv
            # Get all unique keys from all records
            fieldnames = set()
            for record in data:
                fieldnames.update(record.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        else:  # json
            import json
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
        
        logger.info(f"Data loaded to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False
```

### 5. Implement the Run ETL Function

Complete the `run_etl` function to run the full pipeline:

```python
def run_etl(output_file=None, output_format="csv", dry_run=False):
    """Run the full ETL pipeline"""
    logger.info("Starting ETL pipeline...")
    
    # Extract
    raw_data = extract(dry_run)
    if not raw_data:
        logger.error("Extraction failed or returned no data")
        return False
    
    # Transform
    transformed_data = transform(raw_data)
    if not transformed_data:
        logger.error("Transformation failed or returned no data")
        return False
    
    # Load
    success = load(transformed_data, output_file, output_format)
    if not success:
        logger.error("Loading failed")
        return False
    
    logger.info("ETL pipeline completed successfully")
    return True
```

### 6. Implement the Main Function

Complete the `main` function:

```python
def main():
    parser = argparse.ArgumentParser(description="Run the ETL pipeline for Klaviyo campaign metrics")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    args = parser.parse_args()
    
    success = run_etl(args.output, args.format, args.dry_run)
    sys.exit(0 if success else 1)
```

### 7. Add Supermetrics Integration Placeholder

Add a placeholder for future Supermetrics integration:

```python
# Add this after the imports

# Supermetrics Integration (Placeholder for future implementation)
class SupermetricsConnector:
    """Connector for Supermetrics integration"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("SUPERMETRICS_API_KEY")
    
    def fetch_data(self, query):
        """Fetch data from Supermetrics API"""
        logger.info("Supermetrics integration not yet implemented")
        return []
    
    def push_data(self, data):
        """Push data to Supermetrics"""
        logger.info("Supermetrics integration not yet implemented")
        return False
```

### 8. Create Unit Tests

Create a new file at `tests/test_etl_runner.py` with the following content:

```python
import os
import pytest
import tempfile
import json
import csv
from unittest.mock import patch, MagicMock
from src.etl_runner import (
    extract,
    transform,
    load,
    run_etl
)

# Sample test data
SAMPLE_RAW_DATA = [
    {
        "id": "campaign_1",
        "name": "Test Campaign 1",
        "send_time": "2025-05-01T10:00:00Z",
        "subject": "Test Subject 1",
        "open_rate": 0.45,
        "click_rate": 0.20,
        "list_id": "list_123",
        "delivered": 100,
        "opened": 45,
        "clicked": 20,
        "revenue": 250.0
    },
    {
        "id": "campaign_2",
        "name": "Test Campaign 2",
        "send_time": "2025-05-08T10:00:00Z",
        "subject": "Test Subject 2",
        "open_rate": 0.50,
        "click_rate": 0.25,
        "list_id": "list_123",
        "delivered": 120,
        "opened": 60,
        "clicked": 30,
        "revenue": 350.0
    }
]

SAMPLE_TRANSFORMED_DATA = [
    {
        "campaign_name": "Test Campaign 1",
        "date": "2025-05-01",
        "subject_line": "Test Subject 1",
        "open_rate": 0.45,
        "click_rate": 0.20,
        "list_id": "list_123",
        "id": "campaign_1",
        "delivered": 100,
        "opened": 45,
        "clicked": 20,
        "revenue": 250.0
    },
    {
        "campaign_name": "Test Campaign 2",
        "date": "2025-05-08",
        "subject_line": "Test Subject 2",
        "open_rate": 0.50,
        "click_rate": 0.25,
        "list_id": "list_123",
        "id": "campaign_2",
        "delivered": 120,
        "opened": 60,
        "clicked": 30,
        "revenue": 350.0
    }
]

# Test extract function
@patch("src.etl_runner.fetch_all_campaigns")
@patch("src.etl_runner.fetch_campaign_metrics")
def test_extract(mock_fetch_metrics, mock_fetch_campaigns):
    # Mock responses
    mock_fetch_campaigns.return_value = [
        {"id": "campaign_1", "name": "Test Campaign 1"},
        {"id": "campaign_2", "name": "Test Campaign 2"}
    ]
    mock_fetch_metrics.side_effect = [
        {"delivered": 100, "opened": 45, "clicked": 20, "revenue": 250.0},
        {"delivered": 120, "opened": 60, "clicked": 30, "revenue": 350.0}
    ]
    
    # Test function
    result = extract(dry_run=False)
    
    # Assertions
    assert len(result) == 2
    assert result[0]["id"] == "campaign_1"
    assert result[0]["delivered"] == 100
    assert result[1]["id"] == "campaign_2"
    assert result[1]["delivered"] == 120
    assert mock_fetch_campaigns.call_count == 1
    assert mock_fetch_metrics.call_count == 2

# Test transform function
@patch("src.etl_runner.normalize_records")
def test_transform(mock_normalize):
    # Mock response
    mock_normalize.return_value = SAMPLE_TRANSFORMED_DATA
    
    # Test function
    result = transform(SAMPLE_RAW_DATA)
    
    # Assertions
    assert len(result) == 2
    assert result[0]["campaign_name"] == "Test Campaign 1"
    assert result[1]["campaign_name"] == "Test Campaign 2"
    assert mock_normalize.call_count == 1
    mock_normalize.assert_called_with(SAMPLE_RAW_DATA)

# Test load function with CSV output
def test_load_csv():
    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Test function
        result = load(SAMPLE_TRANSFORMED_DATA, temp_path, "csv")
        
        # Assertions
        assert result is True
        
        # Verify file contents
        with open(temp_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["campaign_name"] == "Test Campaign 1"
            assert rows[1]["campaign_name"] == "Test Campaign 2"
    finally:
        # Clean up
        os.unlink(temp_path)

# Test load function with JSON output
def test_load_json():
    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Test function
        result = load(SAMPLE_TRANSFORMED_DATA, temp_path, "json")
        
        # Assertions
        assert result is True
        
        # Verify file contents
        with open(temp_path, "r") as f:
            loaded_data = json.load(f)
            assert len(loaded_data) == 2
            assert loaded_data[0]["campaign_name"] == "Test Campaign 1"
            assert loaded_data[1]["campaign_name"] == "Test Campaign 2"
    finally:
        # Clean up
        os.unlink(temp_path)

# Test run_etl function
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
@patch("src.etl_runner.load")
def test_run_etl(mock_load, mock_transform, mock_extract):
    # Mock responses
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = SAMPLE_TRANSFORMED_DATA
    mock_load.return_value = True
    
    # Test function
    result = run_etl("test_output.csv", "csv", dry_run=True)
    
    # Assertions
    assert result is True
    mock_extract.assert_called_once_with(True)
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)
    mock_load.assert_called_once_with(SAMPLE_TRANSFORMED_DATA, "test_output.csv", "csv")

# Test run_etl function with extraction failure
@patch("src.etl_runner.extract")
def test_run_etl_extract_failure(mock_extract):
    # Mock extraction failure
    mock_extract.return_value = []
    
    # Test function
    result = run_etl("test_output.csv", "csv", dry_run=True)
    
    # Assertions
    assert result is False
    mock_extract.assert_called_once_with(True)

# Test run_etl function with transformation failure
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
def test_run_etl_transform_failure(mock_transform, mock_extract):
    # Mock extraction success but transformation failure
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = []
    
    # Test function
    result = run_etl("test_output.csv", "csv", dry_run=True)
    
    # Assertions
    assert result is False
    mock_extract.assert_called_once_with(True)
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)

# Test run_etl function with load failure
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
@patch("src.etl_runner.load")
def test_run_etl_load_failure(mock_load, mock_transform, mock_extract):
    # Mock extraction and transformation success but load failure
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = SAMPLE_TRANSFORMED_DATA
    mock_load.return_value = False
    
    # Test function
    result = run_etl("test_output.csv", "csv", dry_run=True)
    
    # Assertions
    assert result is False
    mock_extract.assert_called_once_with(True)
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)
    mock_load.assert_called_once_with(SAMPLE_TRANSFORMED_DATA, "test_output.csv", "csv")
```

## Validation Steps

### For Developers

1. Ensure the `src` and `tests` directories exist:
   ```bash
   mkdir -p src tests
   ```

2. Implement the `etl_runner.py` script as described above.

3. Implement the unit tests as described above.

4. Run the script in dry-run mode to verify it works correctly:
   ```bash
   python src/etl_runner.py --dry-run
   ```

5. Run the unit tests to verify they pass:
   ```bash
   pytest tests/test_etl_runner.py -v
   ```

### For Reviewers

1. Verify that the script follows the project's coding standards.

2. Check that the script integrates functionality from `klaviyo_api_ingest.py` and `lookml_field_mapper.py`.

3. Verify that the script handles errors gracefully at each step of the ETL process.

4. Ensure that the output files (CSV and JSON) are formatted correctly.

5. Check that the script includes a placeholder for future Supermetrics integration.

6. Run the unit tests to verify they pass:
   ```bash
   pytest tests/test_etl_runner.py -v
   ```

## Next Steps

After implementing and validating PR 5, proceed to PR 6: README Updates.
