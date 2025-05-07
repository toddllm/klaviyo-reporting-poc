import os
import sys
import pytest
import tempfile
from unittest.mock import patch, MagicMock
import boto3
from moto import mock_aws

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
@mock_aws
@patch("src.etl_runner.run_connector")
@patch("src.etl_runner.fetch_to_dataframe")
@patch("src.etl_runner.normalize_records")
@patch.dict(os.environ, {
    "FIVETRAN_GROUP_ID": "test_group", 
    "FIVETRAN_CONNECTOR_ID": "test_connector",
    "FIVETRAN_TABLE": "klaviyo_campaigns",
    "AWS_ACCESS_KEY_ID": "test_key",
    "AWS_SECRET_ACCESS_KEY": "test_secret",
    "AWS_REGION": "us-east-1",
    "S3_BUCKET": "test-bucket",
    "S3_PREFIX": "klaviyo-exports/"
})
def test_etl_runner_fivetran_s3_integration(mock_normalize, mock_fetch_to_dataframe, mock_run_connector):
    """Test the ETL runner with Fivetran source and S3 upload in an end-to-end flow."""
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
    
    # Create S3 bucket
    s3_client = boto3.client(
        's3',
        region_name="us-east-1",
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret"
    )
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    
    try:
        # Run the ETL process with S3 upload
        start_date = "2025-05-01"
        end_date = "2025-05-31"
        result = run_etl(
            dry_run=False,
            output_file=output_file,
            format="csv",
            source="fivetran",
            start_date=start_date,
            end_date=end_date,
            upload_to_s3=True,
            keep_local=True
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
        
        # Verify S3 upload
        expected_s3_key = f"klaviyo-exports/klaviyo_export_{start_date}.csv"
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="klaviyo-exports/")
        
        # Check that the file was uploaded to S3
        assert "Contents" in response
        assert len(response["Contents"]) == 1
        assert response["Contents"][0]["Key"] == expected_s3_key
        
        # Check the content of the uploaded file
        s3_obj = s3_client.get_object(Bucket=bucket_name, Key=expected_s3_key)
        s3_content = s3_obj["Body"].read().decode("utf-8")
        
        # Verify the S3 file has the same content as the local file
        with open(output_file, "r") as f:
            local_content = f.read()
            assert s3_content == local_content
    
    finally:
        # Clean up
        if os.path.exists(output_file):
            os.unlink(output_file)
        
        # Clean up S3 bucket
        s3_client.delete_object(Bucket=bucket_name, Key=f"klaviyo-exports/klaviyo_export_{start_date}.csv")
        s3_client.delete_bucket(Bucket=bucket_name)

@pytest.mark.integration
@mock_aws
@patch("src.etl_runner.run_connector")
@patch("src.etl_runner.fetch_to_dataframe")
@patch("src.etl_runner.normalize_records")
@patch.dict(os.environ, {
    "FIVETRAN_GROUP_ID": "test_group", 
    "FIVETRAN_CONNECTOR_ID": "test_connector",
    "FIVETRAN_TABLE": "klaviyo_campaigns",
    "AWS_ACCESS_KEY_ID": "test_key",
    "AWS_SECRET_ACCESS_KEY": "test_secret",
    "AWS_REGION": "us-east-1",
    "S3_BUCKET": "test-bucket",
    "S3_PREFIX": "klaviyo-exports/"
})
def test_etl_runner_fivetran_s3_custom_key(mock_normalize, mock_fetch_to_dataframe, mock_run_connector):
    """Test the ETL runner with Fivetran source and S3 upload with a custom key."""
    # Mock the function calls
    mock_run_connector.return_value = True
    mock_fetch_to_dataframe.return_value = SAMPLE_POSTGRES_DATA
    mock_normalize.side_effect = lambda data: data  # Just return the data unchanged
    
    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
        output_file = temp.name
    
    # Create S3 bucket
    s3_client = boto3.client(
        's3',
        region_name="us-east-1",
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret"
    )
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    
    try:
        # Run the ETL process with S3 upload and custom key
        start_date = "2025-05-01"
        end_date = "2025-05-31"
        custom_s3_key = f"custom/path/report_{start_date}_{end_date}.csv"
        
        # Monkey patch the upload_csv_to_s3 function to use our custom key
        with patch("src.etl_runner.upload_csv_to_s3") as mock_upload:
            mock_upload.return_value = f"s3://{bucket_name}/{custom_s3_key}"
            
            result = run_etl(
                dry_run=False,
                output_file=output_file,
                format="csv",
                source="fivetran",
                start_date=start_date,
                end_date=end_date,
                upload_to_s3=True,
                keep_local=True
            )
            
            # Verify the upload was called with the right parameters
            mock_upload.assert_called_once()
            args, kwargs = mock_upload.call_args
            assert args[0] == output_file  # First arg should be the local file path
            
            # Assertions
            assert result is True
            assert os.path.exists(output_file)
    
    finally:
        # Clean up
        if os.path.exists(output_file):
            os.unlink(output_file)
        
        # Clean up S3 bucket
        s3_client.delete_bucket(Bucket=bucket_name)
