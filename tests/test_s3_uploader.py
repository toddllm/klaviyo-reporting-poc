import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

import boto3
from moto import mock_aws

from src.s3_uploader import validate_s3_env_vars, get_s3_client, upload_file


def test_validate_s3_env_vars_success():
    # Test with all required environment variables set
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1"
    }):
        # This should not raise an exception
        validate_s3_env_vars()


def test_validate_s3_env_vars_missing():
    # Test with missing environment variables
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key"
        # Missing AWS_SECRET_ACCESS_KEY and AWS_REGION
    }, clear=True):
        with pytest.raises(ValueError) as excinfo:
            validate_s3_env_vars()
        assert "Missing required AWS S3 environment variables" in str(excinfo.value)
        assert "AWS_SECRET_ACCESS_KEY" in str(excinfo.value)
        assert "AWS_REGION" in str(excinfo.value)


def test_get_s3_client():
    # Test that the client is created with the correct configuration
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1"
    }):
        with patch("boto3.client") as mock_client:
            get_s3_client()
            # Check that boto3.client was called with the correct arguments
            mock_client.assert_called_once()
            args, kwargs = mock_client.call_args
            assert args[0] == 's3'
            assert kwargs['region_name'] == "us-east-1"
            assert kwargs['aws_access_key_id'] == "test_key"
            assert kwargs['aws_secret_access_key'] == "test_secret"
            assert 'config' in kwargs  # Just check that config is present


@mock_aws
def test_upload_file_success():
    # Set up environment variables
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1"
    }):
        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        try:
            # Create a test bucket
            s3_client = boto3.client(
                's3',
                region_name="us-east-1",
                aws_access_key_id="test_key",
                aws_secret_access_key="test_secret"
            )
            bucket_name = "test-bucket"
            s3_client.create_bucket(Bucket=bucket_name)
            
            # Test uploading the file
            key = "test-folder/test-file.txt"
            metadata = {"test-key": "test-value"}
            content_type = "text/plain"
            
            result = upload_file(
                temp_file_path,
                bucket_name,
                key,
                metadata=metadata,
                content_type=content_type
            )
            
            # Verify the result
            assert result == f"s3://{bucket_name}/{key}"
            
            # Verify the file was uploaded correctly
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            assert response["ContentType"] == content_type
            assert response["Metadata"] == metadata
            assert response["Body"].read() == b"Test content"
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)


def test_upload_file_file_not_found():
    # Test uploading a non-existent file
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1"
    }):
        with pytest.raises(FileNotFoundError):
            upload_file(
                "/path/to/nonexistent/file.txt",
                "test-bucket",
                "test-key"
            )


def test_upload_file_client_error():
    # Test handling of ClientError
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1"
    }):
        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        try:
            # Mock the S3 client to raise an exception
            mock_client = MagicMock()
            mock_client.upload_file.side_effect = ClientError(
                {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
                "UploadFile"
            )
            
            with patch("src.s3_uploader.get_s3_client", return_value=mock_client):
                with pytest.raises(ClientError) as excinfo:
                    upload_file(
                        temp_file_path,
                        "test-bucket",
                        "test-key"
                    )
                
                assert "AccessDenied" in str(excinfo.value)
                assert "Access Denied" in str(excinfo.value)
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
