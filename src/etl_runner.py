#!/usr/bin/env python3
import os
import argparse
import json
import csv
import time
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from other modules using relative imports to avoid circular dependencies
try:
    from .klaviyo_api_ingest import fetch_all_campaigns, fetch_campaign_metrics
    from .lookml_field_mapper import normalize_records
    from .s3_uploader import upload_file
    from .utils.s3_uploader import upload_csv_to_s3
    from .fivetran_connector_runner import run_connector
    from .postgres_extract_export import fetch_to_dataframe, fetch_and_export_to_csv
except ImportError:
    # Fallback for direct script execution
    from klaviyo_api_ingest import fetch_all_campaigns, fetch_campaign_metrics
    from lookml_field_mapper import normalize_records
    from s3_uploader import upload_file
    from utils.s3_uploader import upload_csv_to_s3
    from fivetran_connector_runner import run_connector
    from postgres_extract_export import fetch_to_dataframe, fetch_and_export_to_csv

# Constants
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_OUTPUT_FILE = "klaviyo_campaign_metrics.csv"

# ETL Functions
def extract_klaviyo(dry_run=False):
    """Extract data from Klaviyo API"""
    print("Extracting data from Klaviyo API...")
    
    # Fetch all campaigns
    campaigns = fetch_all_campaigns(dry_run)
    print(f"Found {len(campaigns)} campaigns")
    
    # Fetch metrics for each campaign
    for campaign in campaigns:
        campaign_id = campaign["id"]
        print(f"Fetching metrics for campaign {campaign_id}...")
        metrics = fetch_campaign_metrics(campaign_id, dry_run)
        # Add metrics to campaign data
        campaign.update(metrics)
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.2)
    
    return campaigns

def extract_supermetrics(start_date: str, end_date: str, dry_run=False):
    """Extract data from Supermetrics API"""
    print(f"Extracting data from Supermetrics API for period {start_date} to {end_date}...")
    
    # Import here to avoid circular imports
    from src.supermetrics_klaviyo_pull import fetch_all_data
    
    # Fetch campaign data
    data = fetch_all_data(start_date, end_date, "campaign", dry_run)
    print(f"Fetched {len(data)} records from Supermetrics API")
    
    return data

def extract_fivetran(start_date: str, end_date: str, group_id: Optional[str] = None, 
                   connector_id: Optional[str] = None, table: Optional[str] = None, 
                   date_column: Optional[str] = None, dry_run=False) -> List[Dict[str, Any]]:
    """Extract data using Fivetran
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_id: Fivetran group ID (overrides env var FIVETRAN_GROUP_ID)
        connector_id: Fivetran connector ID (overrides env var FIVETRAN_CONNECTOR_ID)
        table: Postgres table name (overrides env var FIVETRAN_TABLE)
        date_column: Date column for filtering (default from postgres_extract_export)
        dry_run: If True, don't make actual API calls
        
    Returns:
        List of dictionaries containing the extracted data
    """
    print(f"Extracting data via Fivetran for period {start_date} to {end_date}...")
    
    # Get Fivetran credentials from env vars or parameters
    group_id = group_id or os.environ.get("FIVETRAN_GROUP_ID")
    connector_id = connector_id or os.environ.get("FIVETRAN_CONNECTOR_ID")
    
    if not group_id or not connector_id:
        raise ValueError("Fivetran group ID and connector ID must be provided via environment variables or parameters")
    
    # Get table name from env var or parameter, default to campaign (actual Fivetran table name)
    table = table or os.environ.get("FIVETRAN_TABLE", "campaign")
    
    # Step 1: Trigger Fivetran sync
    print(f"Triggering Fivetran sync for connector {connector_id} in group {group_id}...")
    sync_success = run_connector(group_id, connector_id, dry_run=dry_run)
    if not sync_success and not dry_run:
        raise RuntimeError("Fivetran sync failed")
    if not dry_run:
        print("Fivetran sync completed successfully")
    else:
        print("DRY RUN: Skipping actual Fivetran sync")
    
    # Step 2: Extract data from Postgres
    print(f"Extracting data from Postgres table {table}...")
    data = fetch_to_dataframe(
        table=table,
        start_date=start_date,
        end_date=end_date,
        date_column=date_column,
        dry_run=dry_run
    )
    
    print(f"Fetched {len(data)} records from Postgres")
    return data

def extract(source="klaviyo", start_date=None, end_date=None, group_id=None, 
           connector_id=None, table=None, date_column=None, dry_run=False):
    """Extract data from the specified source"""
    if source == "klaviyo":
        return extract_klaviyo(dry_run)
    elif source == "supermetrics":
        if not start_date or not end_date:
            raise ValueError("Supermetrics source requires start_date and end_date parameters")
        return extract_supermetrics(start_date, end_date, dry_run)
    elif source == "fivetran":
        if not start_date or not end_date:
            raise ValueError("Fivetran source requires start_date and end_date parameters")
        return extract_fivetran(start_date, end_date, group_id, connector_id, table, date_column, dry_run)
    else:
        raise ValueError(f"Unsupported source: {source}")

def transform(raw_data):
    """Transform data using the LookML field mapper"""
    print("Transforming data...")
    
    # Normalize the records
    normalized_data = normalize_records(raw_data)
    print(f"Transformed {len(normalized_data)} records")
    
    return normalized_data

def load(data, output_file, format="csv"):
    """Load data to the specified output file"""
    print(f"Loading data to {output_file}...")
    
    if not data:
        print("No data to write")
        return False
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    if format.lower() == "csv":
        return write_to_csv(data, output_file)
    elif format.lower() == "json":
        return write_to_json(data, output_file)
    else:
        print(f"Unsupported format: {format}")
        return False

def write_to_csv(data, output_file):
    """Write data to CSV file"""
    try:
        # Get all unique field names from the data
        fieldnames = set()
        for record in data:
            fieldnames.update(record.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Data written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False

def write_to_json(data, output_file):
    """Write data to JSON file"""
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Data written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to JSON: {e}")
        return False

def run_etl(dry_run=False, output_file=None, format="csv", source="klaviyo", 
          start_date=None, end_date=None, upload_to_s3=False, keep_local=True,
          group_id=None, connector_id=None, table=None, date_column=None):
    """Run the full ETL process
    
    Args:
        dry_run: If True, don't make actual API calls
        output_file: Path to output file. If None, a default path is used
        format: Output format (csv or json)
        source: Data source (klaviyo, supermetrics, or fivetran)
        start_date: Start date for data extraction (required for supermetrics and fivetran)
        end_date: End date for data extraction (required for supermetrics and fivetran)
        upload_to_s3: If True, upload the output file to S3. If a string, it should be an S3 URI template
                     that can include {start} and {end} placeholders.
        keep_local: If True, keep the local output file after S3 upload
        group_id: Fivetran group ID (overrides env var FIVETRAN_GROUP_ID)
        connector_id: Fivetran connector ID (overrides env var FIVETRAN_CONNECTOR_ID)
        table: Postgres table name (overrides env var FIVETRAN_TABLE)
        date_column: Date column for filtering (default from postgres_extract_export)
        
    Returns:
        True if successful, False otherwise
    """
    # Set default output file if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"klaviyo_metrics_{timestamp}.{format}"
        output_file = os.path.join(DEFAULT_OUTPUT_DIR, filename)
    
    try:
        # Extract
        raw_data = extract(source, start_date, end_date, group_id, connector_id, table, date_column, dry_run)
        if not raw_data:
            print("No data extracted. ETL process failed.")
            return False
        
        # Transform
        transformed_data = transform(raw_data)
        if not transformed_data:
            print("Data transformation failed. ETL process failed.")
            return False
        
        # Load
        success = load(transformed_data, output_file, format)
        if not success:
            print("Data loading failed. ETL process failed.")
            return False
        
        print(f"ETL process completed successfully. Output: {output_file}")
        
        # Upload to S3 if requested
        if upload_to_s3 and not dry_run:
            try:
                # Get date strings for template substitution
                date_str = start_date if start_date else datetime.now().strftime("%Y-%m-%d")
                end_str = end_date if end_date else date_str
                
                # Handle the case where upload_to_s3 is an S3 URI template
                if isinstance(upload_to_s3, str) and upload_to_s3.startswith("s3://"):
                    # Parse the S3 URI template
                    s3_uri_template = upload_to_s3
                    
                    # Replace placeholders with actual values
                    s3_uri = s3_uri_template.format(start=date_str, end=end_str)
                    
                    # Extract bucket and key from the URI
                    if not s3_uri.startswith("s3://"):
                        raise ValueError(f"Invalid S3 URI: {s3_uri}. Must start with 's3://'")
                    
                    parts = s3_uri[5:].split("/", 1)
                    if len(parts) != 2:
                        raise ValueError(f"Invalid S3 URI: {s3_uri}. Must be in format 's3://bucket/key'")
                    
                    bucket, key = parts
                    
                    # Upload to S3 using the parsed bucket and key
                    s3_uri = upload_file(output_file, bucket, key)
                else:
                    # Generate default S3 key using start_date and end_date if available
                    if end_date:
                        s3_key = f"klaviyo_export_{date_str}_{end_str}.csv"
                    else:
                        s3_key = f"klaviyo_export_{date_str}.csv"
                    
                    # Upload to S3 using the default key
                    s3_uri = upload_csv_to_s3(output_file, s3_key)
                
                print(f"File uploaded to {s3_uri}")
                
                # Remove local file if not keeping it
                if not keep_local:
                    os.remove(output_file)
                    print(f"Local file {output_file} removed")
            except Exception as e:
                print(f"S3 upload failed: {e}")
                # Continue even if S3 upload fails
        
        return True
    except Exception as e:
        print(f"ETL process failed: {e}")
        return False

# Supermetrics Integration Placeholder
def prepare_for_supermetrics(data_file, format="csv"):
    """Prepare data for future Supermetrics integration"""
    print(f"Preparing {data_file} for Supermetrics integration...")
    print("Note: This is a placeholder for future Supermetrics integration.")
    
    # In a real implementation, this would transform the data into a format
    # that can be consumed by Supermetrics or create the necessary configuration
    # for Supermetrics to access the data.
    
    return True

# Main Function
def main(argv=None):
    parser = argparse.ArgumentParser(description="ETL Runner for Klaviyo Campaign Metrics")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    parser.add_argument("--source", choices=["klaviyo", "supermetrics", "fivetran"], default="klaviyo", 
                        help="Data source to extract from")
    parser.add_argument("--start", help="Start date in YYYY-MM-DD format (required for supermetrics and fivetran)")
    parser.add_argument("--end", help="End date in YYYY-MM-DD format (required for supermetrics and fivetran)")
    parser.add_argument("--upload-to-s3", nargs="?", const=True, help="Upload the output file to S3. Can be used as a flag or with an S3 URI (e.g., s3://bucket/prefix/{start}_{end}.csv)")
    parser.add_argument("--keep-local", action="store_true", default=True, help="Keep the local output file after S3 upload")
    parser.add_argument("--supermetrics-legacy", action="store_true", help="Prepare data for Supermetrics integration (legacy)")
    
    # Fivetran-specific arguments
    fivetran_group = parser.add_argument_group('Fivetran options')
    fivetran_group.add_argument("--group-id", help="Fivetran group ID (overrides FIVETRAN_GROUP_ID env var)")
    fivetran_group.add_argument("--connector-id", help="Fivetran connector ID (overrides FIVETRAN_CONNECTOR_ID env var)")
    fivetran_group.add_argument("--table", help="Postgres table name (overrides FIVETRAN_TABLE env var)")
    fivetran_group.add_argument("--date-column", help="Date column for filtering")
    
    args = parser.parse_args(argv)
    
    # Validate arguments
    if args.source == "supermetrics" and (not args.start or not args.end):
        parser.error("--start and --end are required when using --source supermetrics")
    
    if args.source == "fivetran" and (not args.start or not args.end):
        parser.error("--start and --end are required when using --source fivetran")
    
    # Handle the upload_to_s3 argument
    upload_to_s3 = args.upload_to_s3
    if upload_to_s3 is True:
        # If used as a flag, set to True
        upload_to_s3 = True
    elif isinstance(upload_to_s3, str):
        # If provided as a string, use it as an S3 URI template
        if not upload_to_s3.startswith("s3://"):
            parser.error("--upload-to-s3 value must be an S3 URI starting with 's3://'")
    
    # Run the ETL process
    success = run_etl(
        dry_run=args.dry_run,
        output_file=args.output,
        format=args.format,
        source=args.source,
        start_date=args.start,
        end_date=args.end,
        upload_to_s3=upload_to_s3,
        keep_local=args.keep_local,
        group_id=args.group_id,
        connector_id=args.connector_id,
        table=args.table,
        date_column=args.date_column
    )
    
    # Prepare for Supermetrics if requested (legacy support)
    if success and args.supermetrics_legacy:
        output_file = args.output or os.path.join(DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE)
        prepare_for_supermetrics(output_file, args.format)
        
    return 0 if success else 1

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)
