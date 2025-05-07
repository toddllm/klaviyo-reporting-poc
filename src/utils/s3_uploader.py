#!/usr/bin/env python3
import os
import boto3
from typing import Optional

# Default S3 prefix for uploads
DEFAULT_S3_PREFIX = "exports/"

def validate_aws_env_vars():
    """Validate that all required AWS environment variables are set"""
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "S3_BUCKET"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required AWS environment variables: {', '.join(missing_vars)}")

def upload_csv_to_s3(file_path: str, key: Optional[str] = None, prefix: Optional[str] = None) -> str:
    """Upload a CSV file to S3
    
    Args:
        file_path: Path to the local CSV file
        key: Optional S3 key (filename) to use. If not provided, uses the basename of file_path
        prefix: Optional S3 prefix (directory). If not provided, uses DEFAULT_S3_PREFIX
        
    Returns:
        S3 URI of the uploaded file (s3://bucket/key)
    """
    # Validate AWS environment variables
    validate_aws_env_vars()
    
    # Get S3 bucket from environment
    bucket = os.environ.get("S3_BUCKET")
    
    # Set default prefix if not provided
    if prefix is None:
        prefix = os.environ.get("S3_PREFIX", DEFAULT_S3_PREFIX)
    
    # Ensure prefix ends with a slash
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    
    # Set default key if not provided
    if key is None:
        key = os.path.basename(file_path)
    
    # Combine prefix and key
    s3_key = f"{prefix}{key}"
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION")
        )
        
        # Upload file
        s3_client.upload_file(file_path, bucket, s3_key)
        
        # Return S3 URI
        return f"s3://{bucket}/{s3_key}"
    except Exception as e:
        raise Exception(f"Error uploading file to S3: {e}")

def download_from_s3(s3_uri: str, local_path: str) -> str:
    """Download a file from S3
    
    Args:
        s3_uri: S3 URI of the file to download (s3://bucket/key)
        local_path: Path to save the downloaded file
        
    Returns:
        Path to the downloaded file
    """
    # Validate AWS environment variables
    validate_aws_env_vars()
    
    # Parse S3 URI
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}. Must start with 's3://'")
    
    parts = s3_uri[5:].split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid S3 URI: {s3_uri}. Must be in format 's3://bucket/key'")
    
    bucket, key = parts
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION")
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
        
        # Download file
        s3_client.download_file(bucket, key, local_path)
        
        return local_path
    except Exception as e:
        raise Exception(f"Error downloading file from S3: {e}")
