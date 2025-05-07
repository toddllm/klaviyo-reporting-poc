import os
import sys
import pytest
import tempfile
import json
import boto3
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the moto library for mocking AWS services
from moto import mock_s3

# Import the modules to test
from src.etl_runner import main, run_etl
from src.utils.s3_uploader import upload_csv_to_s3

# Sample test data
SAMPLE_SUPERMETRICS_DATA = [
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

# Mock the supermetrics_klaviyo_pull.fetch_all_data function
@pytest.fixture
def mock_supermetrics_fetch(monkeypatch):
    def mock_fetch(start_date, end_date, report_type, dry_run=False):
        return SAMPLE_SUPERMETRICS_DATA
    
    # Create a module mock
    mock_module = MagicMock()
    mock_module.fetch_all_data = mock_fetch
    
    # Apply the mock
    monkeypatch.setitem(sys.modules, 'src.supermetrics_klaviyo_pull', mock_module)
    
    return mock_fetch

# Mock the normalize_records function
@pytest.fixture
def mock_normalize_records(monkeypatch):
    def mock_normalize(records):
        # Simple transformation that keeps most fields and adds a date field
        normalized = []
        for record in records:
            transformed = record.copy()
            # Extract date from send_time if available
            if 'send_time' in record:
                transformed['date'] = record['send_time'].split('T')[0]
            normalized.append(transformed)
        return normalized
    
    # Apply the mock
    monkeypatch.setattr('src.lookml_field_mapper.normalize_records', mock_normalize)
    
    return mock_normalize

# Set up the S3 mock environment
@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['S3_BUCKET'] = 'test-bucket'
    
    yield
    
    # Clean up
    del os.environ['AWS_ACCESS_KEY_ID']
    del os.environ['AWS_SECRET_ACCESS_KEY']
    del os.environ['AWS_REGION']
    del os.environ['S3_BUCKET']

@pytest.fixture
def s3_client(aws_credentials):
    with mock_s3():
        # Create the S3 bucket
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        yield s3

# Test the ETL runner with Supermetrics source and S3 upload
@mock_s3
def test_etl_runner_supermetrics_s3(mock_supermetrics_fetch, mock_normalize_records, aws_credentials, tmp_path):
    # Create a temporary output file
    output_file = os.path.join(tmp_path, 'output.csv')
    
    # Run the ETL process
    result = run_etl(
        dry_run=False,
        output_file=output_file,
        format='csv',
        source='supermetrics',
        start_date='2025-05-01',
        end_date='2025-05-08',
        upload_to_s3=True,
        keep_local=True
    )
    
    # Check that the ETL process was successful
    assert result is True
    
    # Check that the output file was created
    assert os.path.exists(output_file)
    
    # Check that the file was uploaded to S3
    s3 = boto3.client('s3', region_name='us-east-1')
    objects = s3.list_objects_v2(Bucket='test-bucket')
    
    # Check that there is at least one object in the bucket
    assert 'Contents' in objects
    
    # Check that the object key matches the expected format
    expected_key = f"exports/klaviyo_export_2025-05-01.csv"
    found = False
    for obj in objects['Contents']:
        if obj['Key'] == expected_key:
            found = True
            break
    
    assert found, f"Expected S3 key {expected_key} not found"
    
    # Download the file from S3 and check its contents
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        s3.download_file('test-bucket', expected_key, tmp.name)
        with open(tmp.name, 'r') as f:
            content = f.read()
        
        # Check that the file contains the expected data
        assert 'campaign_name' in content
        assert 'Test Campaign 1' in content
        assert 'Test Campaign 2' in content

# Test the ETL runner with command-line arguments
@mock_s3
def test_etl_runner_cli(mock_supermetrics_fetch, mock_normalize_records, aws_credentials, tmp_path):
    # Create a temporary output file
    output_file = os.path.join(tmp_path, 'output.csv')
    
    # Set up command-line arguments
    args = [
        '--source', 'supermetrics',
        '--start', '2025-05-01',
        '--end', '2025-05-08',
        '--output', output_file,
        '--upload-to-s3'
    ]
    
    # Run the main function with the arguments
    exit_code = main(args)
    
    # Check that the main function returned success
    assert exit_code == 0
    
    # Check that the output file was created
    assert os.path.exists(output_file)
    
    # Check that the file was uploaded to S3
    s3 = boto3.client('s3', region_name='us-east-1')
    objects = s3.list_objects_v2(Bucket='test-bucket')
    
    # Check that there is at least one object in the bucket
    assert 'Contents' in objects

# Test the S3 uploader utility
@mock_s3
def test_s3_uploader(aws_credentials, tmp_path):
    # Create a test file
    test_file = os.path.join(tmp_path, 'test.csv')
    with open(test_file, 'w') as f:
        f.write('header1,header2\nvalue1,value2\n')
    
    # Upload the file to S3
    s3_uri = upload_csv_to_s3(test_file, 'test.csv')
    
    # Check that the S3 URI is correct
    assert s3_uri == 's3://test-bucket/exports/test.csv'
    
    # Check that the file was uploaded to S3
    s3 = boto3.client('s3', region_name='us-east-1')
    objects = s3.list_objects_v2(Bucket='test-bucket')
    
    # Check that there is at least one object in the bucket
    assert 'Contents' in objects
    
    # Check that the object key matches the expected format
    expected_key = 'exports/test.csv'
    found = False
    for obj in objects['Contents']:
        if obj['Key'] == expected_key:
            found = True
            break
    
    assert found, f"Expected S3 key {expected_key} not found"
    
    # Download the file from S3 and check its contents
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        s3.download_file('test-bucket', expected_key, tmp.name)
        with open(tmp.name, 'r') as f:
            content = f.read()
        
        # Check that the file contains the expected data
        assert content == 'header1,header2\nvalue1,value2\n'
