import os
import pytest
import tempfile
import json
import csv
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the imports in etl_runner.py
import unittest.mock
unittest.mock.patch.dict('sys.modules', {
    'klaviyo_api_ingest': unittest.mock.MagicMock(),
    'lookml_field_mapper': unittest.mock.MagicMock()
}).start()

from src.etl_runner import (
    extract,
    extract_fivetran,
    transform,
    load,
    write_to_csv,
    write_to_json,
    run_etl,
    prepare_for_supermetrics
)

# Sample test data
SAMPLE_RAW_DATA = [
    {
        "id": "campaign_123",
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
        "id": "campaign_456",
        "name": "Test Campaign 2",
        "send_time": "2025-05-08T10:00:00Z",
        "subject": "Test Subject 2",
        "open_rate": 0.50,
        "click_rate": 0.25,
        "list_id": "list_123",
        "delivered": 200,
        "opened": 100,
        "clicked": 50,
        "revenue": 500.0
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
        "id": "campaign_123",
        "delivered": 100,
        "opened": 45,
        "clicked": 20,
        "revenue": 250.0,
        "engagement_score": 0.375
    },
    {
        "campaign_name": "Test Campaign 2",
        "date": "2025-05-08",
        "subject_line": "Test Subject 2",
        "open_rate": 0.50,
        "click_rate": 0.25,
        "list_id": "list_123",
        "id": "campaign_456",
        "delivered": 200,
        "opened": 100,
        "clicked": 50,
        "revenue": 500.0,
        "engagement_score": 0.425
    }
]

# Test extract function
@patch("src.etl_runner.fetch_all_campaigns")
@patch("src.etl_runner.fetch_campaign_metrics")
@patch("src.etl_runner.time.sleep")
def test_extract(mock_sleep, mock_fetch_metrics, mock_fetch_campaigns):
    # Mock the API calls
    mock_fetch_campaigns.return_value = [
        {"id": "campaign_123", "name": "Test Campaign 1"},
        {"id": "campaign_456", "name": "Test Campaign 2"}
    ]
    
    mock_fetch_metrics.side_effect = [
        {"delivered": 100, "opened": 45, "clicked": 20, "revenue": 250.0},
        {"delivered": 200, "opened": 100, "clicked": 50, "revenue": 500.0}
    ]
    
    # Call the function
    result = extract(dry_run=True)
    
    # Assertions
    assert len(result) == 2
    assert result[0]["id"] == "campaign_123"
    assert result[0]["delivered"] == 100
    assert result[1]["id"] == "campaign_456"
    assert result[1]["delivered"] == 200
    assert mock_fetch_campaigns.call_count == 1
    assert mock_fetch_metrics.call_count == 2
    assert mock_sleep.call_count == 2

# Test extract_fivetran function
@patch("src.etl_runner.run_connector")
@patch("src.etl_runner.fetch_to_dataframe")
@patch.dict(os.environ, {"FIVETRAN_GROUP_ID": "test_group", "FIVETRAN_CONNECTOR_ID": "test_connector"})
def test_extract_fivetran(mock_fetch_to_dataframe, mock_run_connector):
    # Mock the function calls
    mock_run_connector.return_value = True
    mock_fetch_to_dataframe.return_value = SAMPLE_RAW_DATA
    
    # Call the function
    result = extract_fivetran("2025-05-01", "2025-05-31", dry_run=True)
    
    # Assertions
    assert result == SAMPLE_RAW_DATA
    mock_run_connector.assert_called_once_with("test_group", "test_connector", dry_run=True)
    mock_fetch_to_dataframe.assert_called_once_with(
        table="klaviyo_campaigns",
        start_date="2025-05-01",
        end_date="2025-05-31",
        date_column=None,
        dry_run=True
    )

# Test extract_fivetran with custom parameters
@patch("src.etl_runner.run_connector")
@patch("src.etl_runner.fetch_to_dataframe")
def test_extract_fivetran_custom_params(mock_fetch_to_dataframe, mock_run_connector):
    # Mock the function calls
    mock_run_connector.return_value = True
    mock_fetch_to_dataframe.return_value = SAMPLE_RAW_DATA
    
    # Call the function with custom parameters
    result = extract_fivetran(
        "2025-05-01", 
        "2025-05-31", 
        group_id="custom_group", 
        connector_id="custom_connector",
        table="custom_table",
        date_column="custom_date",
        dry_run=True
    )
    
    # Assertions
    assert result == SAMPLE_RAW_DATA
    mock_run_connector.assert_called_once_with("custom_group", "custom_connector", dry_run=True)
    mock_fetch_to_dataframe.assert_called_once_with(
        table="custom_table",
        start_date="2025-05-01",
        end_date="2025-05-31",
        date_column="custom_date",
        dry_run=True
    )

# Test extract_fivetran with missing parameters
@patch.dict(os.environ, {}, clear=True)
def test_extract_fivetran_missing_params():
    # Call the function without required parameters
    with pytest.raises(ValueError, match="Fivetran group ID and connector ID must be provided"):
        extract_fivetran("2025-05-01", "2025-05-31", dry_run=True)

# Test extract_fivetran with connector failure
@patch("src.etl_runner.run_connector")
@patch.dict(os.environ, {"FIVETRAN_GROUP_ID": "test_group", "FIVETRAN_CONNECTOR_ID": "test_connector"})
def test_extract_fivetran_connector_failure(mock_run_connector):
    # Mock the connector to fail
    mock_run_connector.return_value = False
    
    # Call the function
    with pytest.raises(RuntimeError, match="Fivetran sync failed"):
        extract_fivetran("2025-05-01", "2025-05-31")

# Test transform function
@patch("src.etl_runner.normalize_records")
def test_transform(mock_normalize):
    # Mock the normalize_records function
    mock_normalize.return_value = SAMPLE_TRANSFORMED_DATA
    
    # Call the function
    result = transform(SAMPLE_RAW_DATA)
    
    # Assertions
    assert result == SAMPLE_TRANSFORMED_DATA
    mock_normalize.assert_called_once_with(SAMPLE_RAW_DATA)

# Test load function with CSV
def test_load_csv():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Call the function
        result = load(SAMPLE_TRANSFORMED_DATA, temp_path, "csv")
        
        # Assertions
        assert result is True
        assert os.path.exists(temp_path)
        
        # Verify file contents
        with open(temp_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["campaign_name"] == "Test Campaign 1"
            assert rows[1]["campaign_name"] == "Test Campaign 2"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

# Test load function with JSON
def test_load_json():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Call the function
        result = load(SAMPLE_TRANSFORMED_DATA, temp_path, "json")
        
        # Assertions
        assert result is True
        assert os.path.exists(temp_path)
        
        # Verify file contents
        with open(temp_path, "r") as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["campaign_name"] == "Test Campaign 1"
            assert data[1]["campaign_name"] == "Test Campaign 2"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

# Test load function with unsupported format
def test_load_unsupported_format():
    result = load(SAMPLE_TRANSFORMED_DATA, "test.txt", "txt")
    assert result is False

# Test write_to_csv function
def test_write_to_csv():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Call the function
        result = write_to_csv(SAMPLE_TRANSFORMED_DATA, temp_path)
        
        # Assertions
        assert result is True
        assert os.path.exists(temp_path)
        
        # Verify file contents
        with open(temp_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["campaign_name"] == "Test Campaign 1"
            assert rows[1]["campaign_name"] == "Test Campaign 2"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

# Test write_to_json function
def test_write_to_json():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
        temp_path = temp.name
    
    try:
        # Call the function
        result = write_to_json(SAMPLE_TRANSFORMED_DATA, temp_path)
        
        # Assertions
        assert result is True
        assert os.path.exists(temp_path)
        
        # Verify file contents
        with open(temp_path, "r") as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["campaign_name"] == "Test Campaign 1"
            assert data[1]["campaign_name"] == "Test Campaign 2"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

# Test run_etl function
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
@patch("src.etl_runner.load")
def test_run_etl_success(mock_load, mock_transform, mock_extract):
    # Mock the functions
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = SAMPLE_TRANSFORMED_DATA
    mock_load.return_value = True
    
    # Call the function
    result = run_etl(dry_run=True, output_file="test.csv")
    
    # Assertions
    assert result is True
    mock_extract.assert_called_once_with("klaviyo", None, None, None, None, None, None, True)
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)
    mock_load.assert_called_once()

# Test run_etl function with fivetran source
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
@patch("src.etl_runner.load")
def test_run_etl_fivetran_success(mock_load, mock_transform, mock_extract):
    # Mock the functions
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = SAMPLE_TRANSFORMED_DATA
    mock_load.return_value = True
    
    # Call the function with fivetran source
    result = run_etl(
        dry_run=True, 
        output_file="test.csv", 
        source="fivetran",
        start_date="2025-05-01",
        end_date="2025-05-31",
        group_id="test_group",
        connector_id="test_connector",
        table="test_table",
        date_column="test_date"
    )
    
    # Assertions
    assert result is True
    mock_extract.assert_called_once_with(
        "fivetran", 
        "2025-05-01", 
        "2025-05-31", 
        "test_group", 
        "test_connector", 
        "test_table", 
        "test_date", 
        True
    )
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)
    mock_load.assert_called_once()

# Test run_etl function with extract failure
@patch("src.etl_runner.extract")
def test_run_etl_extract_failure(mock_extract):
    # Mock the function to return empty data
    mock_extract.return_value = []
    
    # Call the function
    result = run_etl(dry_run=True, output_file="test.csv")
    
    # Assertions
    assert result is False
    mock_extract.assert_called_once_with("klaviyo", None, None, None, None, None, None, True)

# Test run_etl function with transform failure
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
def test_run_etl_transform_failure(mock_transform, mock_extract):
    # Mock the functions
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = []
    
    # Call the function
    result = run_etl(dry_run=True, output_file="test.csv")
    
    # Assertions
    assert result is False
    mock_extract.assert_called_once_with("klaviyo", None, None, None, None, None, None, True)
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)

# Test run_etl function with load failure
@patch("src.etl_runner.extract")
@patch("src.etl_runner.transform")
@patch("src.etl_runner.load")
def test_run_etl_load_failure(mock_load, mock_transform, mock_extract):
    # Mock the functions
    mock_extract.return_value = SAMPLE_RAW_DATA
    mock_transform.return_value = SAMPLE_TRANSFORMED_DATA
    mock_load.return_value = False
    
    # Call the function
    result = run_etl(dry_run=True, output_file="test.csv")
    
    # Assertions
    assert result is False
    mock_extract.assert_called_once_with("klaviyo", None, None, None, None, None, None, True)
    mock_transform.assert_called_once_with(SAMPLE_RAW_DATA)
    mock_load.assert_called_once()

# Test prepare_for_supermetrics function
def test_prepare_for_supermetrics():
    # This is just a placeholder function for now
    result = prepare_for_supermetrics("test.csv")
    assert result is True
