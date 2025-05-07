import os
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

logger = logging.getLogger(__name__)

def validate_s3_env_vars():
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required AWS S3 environment variables: {', '.join(missing_vars)}"
        )

def get_s3_client():
    validate_s3_env_vars()
    
    # Configure retry behavior with exponential backoff
    config = Config(
        retries={
            'max_attempts': 5,
            'mode': 'adaptive'
        }
    )
    
    return boto3.client(
        's3',
        region_name=os.environ.get('AWS_REGION'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        config=config
    )

def upload_file(local_path, bucket, key, metadata=None, content_type=None):
    """
    Upload a file to an S3 bucket with exponential backoff retry logic
    
    Args:
        local_path (str): Path to the local file to upload
        bucket (str): S3 bucket name
        key (str): S3 object key (path within bucket)
        metadata (dict, optional): Metadata to attach to the S3 object
        content_type (str, optional): Content type of the file
        
    Returns:
        str: The URL of the uploaded file if successful, None otherwise
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    
    try:
        s3_client = get_s3_client()
        
        # Prepare upload parameters
        upload_args = {
            'Bucket': bucket,
            'Key': key,
            'Body': open(local_path, 'rb')
        }
        
        if metadata:
            upload_args['Metadata'] = metadata
            
        if content_type:
            upload_args['ContentType'] = content_type
        
        # Perform the upload
        s3_client.upload_file(
            local_path,
            bucket,
            key,
            ExtraArgs={
                'Metadata': metadata or {},
                'ContentType': content_type or 'application/octet-stream'
            }
        )
        
        logger.info(f"Successfully uploaded {local_path} to s3://{bucket}/{key}")
        return f"s3://{bucket}/{key}"
    
    except ClientError as e:
        logger.error(f"S3 upload error: {e}")
        raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload a file to S3")
    parser.add_argument("local_path", help="Path to the local file to upload")
    parser.add_argument("bucket", help="S3 bucket name")
    parser.add_argument("key", help="S3 object key (path within bucket)")
    parser.add_argument("--content-type", help="Content type of the file")
    parser.add_argument("--metadata", help="Metadata as key=value pairs, comma-separated")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually upload, just validate and log")
    
    args = parser.parse_args()
    
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        for pair in args.metadata.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                metadata[key.strip()] = value.strip()
    
    if args.dry_run:
        print(f"DRY RUN: Would upload {args.local_path} to s3://{args.bucket}/{args.key}")
        if args.content_type:
            print(f"Content-Type: {args.content_type}")
        if metadata:
            print(f"Metadata: {metadata}")
        return
    
    try:
        result = upload_file(
            args.local_path,
            args.bucket,
            args.key,
            metadata=metadata,
            content_type=args.content_type
        )
        print(f"Successfully uploaded to {result}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
