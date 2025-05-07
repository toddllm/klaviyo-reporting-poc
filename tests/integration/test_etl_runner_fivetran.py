import os
import sys
import pytest
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.etl_runner import run_etl

# Sample test data
SAMPLE_POSTGRES_DATA = [
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
        "revenue": 250.0,
        "created_at": "2025-05-01"
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
        "revenue": 500.0,
        "created_at": "2025-05-08"
    }
]

@pytest.mark.integration
@patch("src.etl_runner.run_connector")
@patch("src.etl_runner.fetch_to_dataframe")
@patch("src.etl_runner.normalize_records")
@patch.dict(os.environ, {
    "FIVETRAN_GROUP_ID": "test_group", 
    "FIVETRAN_CONNECTOR_ID": "test_connector",
    "FIVETRAN_TABLE": "klaviyo_campaigns"
})
def test_etl_runner_fivetran_integration(mock_normalize, mock_fetch_to_dataframe, mock_run_connector):
    """Test the ETL runner with Fivetran source in an end-to-end flow."""
    # Mock the function calls
    mock_run_connector.return_value = True
    mock_fetch_to_dataframe.return_value = SAMPLE_POSTGRES_DATA
    
    # Mock the normalize_records function to return the same data with some field mapping
    def normalize_mock(data):
        return [{
            "campaign_name": item["name"],
            "date": item["created_at"],
            "subject_line": item["subject"],
            "open_rate": item["open_rate"],
            "click_rate": item["click_rate"],
            "list_id": item["list_id"],
            "id": item["id"],
            "delivered": item["delivered"],
            "opened": item["opened"],
            "clicked": item["clicked"],
            "revenue": item["revenue"],
            "engagement_score": (item["open_rate"] + item["click_rate"]) / 2
        } for item in data]
    
    mock_normalize.side_effect = normalize_mock
    
    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        output_file = temp.name
    
    try:
        # Run the ETL process
        result = run_etl(
            dry_run=False,
            output_file=output_file,
            format="csv",
            source="fivetran",
            start_date="2025-05-01",
            end_date="2025-05-31"
        )
        
        # Assertions
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify file contents
        with open(output_file, "r") as f:
            content = f.read()
            # Check that all expected fields are in the header
            assert "campaign_name" in content
            assert "date" in content
            assert "subject_line" in content
            # Check that the data is in the file
            assert "Test Campaign 1" in content
            assert "2025-05-01" in content
            assert "Test Subject 1" in content
            assert "Test Campaign 2" in content
            assert "2025-05-08" in content
            assert "Test Subject 2" in content
    
    finally:
        # Clean up
        if os.path.exists(output_file):
            os.unlink(output_file)
