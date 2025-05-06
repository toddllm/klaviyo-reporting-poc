#!/usr/bin/env python3
import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

# Constants
DEFAULT_DATASET = "klaviyo_raw"
DEFAULT_TABLE_PREFIX = "events"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Configuration
def get_credentials(service_account_path=None):
    """Get BigQuery credentials from service account JSON file."""
    if service_account_path:
        return service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/bigquery"],
        )
    
    # Check for environment variable
    service_account_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_json and os.path.exists(service_account_json):
        return service_account.Credentials.from_service_account_file(
            service_account_json,
            scopes=["https://www.googleapis.com/auth/bigquery"],
        )
    
    # Use default credentials if available
    return None

def create_bigquery_client(service_account_path=None):
    """Create a BigQuery client with the provided credentials."""
    credentials = get_credentials(service_account_path)
    return bigquery.Client(credentials=credentials)

# Dataset and Table Management
def ensure_dataset_exists(client, dataset_id, location="US"):
    """Create the dataset if it doesn't exist."""
    dataset_ref = client.dataset(dataset_id)
    
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"Created dataset {dataset_id}")
    
    return dataset_ref

def get_table_id(client, dataset_id, table_prefix, report_type, date_suffix=None):
    """Generate a table ID based on the report type and optional date suffix."""
    if date_suffix:
        table_id = f"{table_prefix}_{report_type}_{date_suffix}"
    else:
        table_id = f"{table_prefix}_{report_type}"
    
    return f"{client.project}.{dataset_id}.{table_id}"

# Data Loading Functions
def load_json_to_bigquery(client, json_file, dataset_id, table_prefix, report_type, 
                       date_partition=True, dry_run=False):
    """Load JSON data into BigQuery with auto-detected schema."""
    # Extract date from filename if possible
    file_path = Path(json_file)
    file_date = None
    
    # Try to extract date from filename (format: supermetrics_raw_TYPE_YYYYMMDD.json)
    filename_parts = file_path.stem.split('_')
    if len(filename_parts) >= 4:
        try:
            file_date = datetime.strptime(filename_parts[-1], "%Y%m%d").strftime("%Y%m%d")
        except ValueError:
            pass
    
    # Generate table ID
    table_id = get_table_id(client, dataset_id, table_prefix, report_type, file_date if date_partition else None)
    
    if dry_run:
        print(f"[DRY RUN] Would load {json_file} to table {table_id}")
        # Read the file to count rows
        with open(json_file, 'r') as f:
            data = json.load(f)
            print(f"[DRY RUN] File contains {len(data)} rows")
        return table_id, len(data)
    
    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,  # Auto-detect schema
        ignore_unknown_values=True,
        # Set time partitioning if date_partition is True
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="date",  # Partition by the date field
        ) if date_partition else None,
    )
    
    # Convert JSON array to newline-delimited JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create a temporary newline-delimited JSON file
    temp_file = f"{json_file}.ndjson"
    with open(temp_file, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    
    # Load the data
    with open(temp_file, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file,
            table_id,
            job_config=job_config
        )
    
    # Wait for the job to complete
    load_job.result()
    
    # Clean up temporary file
    os.remove(temp_file)
    
    # Get the table to check row count
    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows to {table_id}")
    
    return table_id, table.num_rows

def load_csv_to_bigquery(client, csv_file, dataset_id, table_prefix, report_type, 
                      date_partition=True, dry_run=False):
    """Load CSV data into BigQuery with auto-detected schema."""
    # Extract date from filename if possible
    file_path = Path(csv_file)
    file_date = None
    
    # Try to extract date from filename (format: supermetrics_raw_TYPE_YYYYMMDD.csv)
    filename_parts = file_path.stem.split('_')
    if len(filename_parts) >= 4:
        try:
            file_date = datetime.strptime(filename_parts[-1], "%Y%m%d").strftime("%Y%m%d")
        except ValueError:
            pass
    
    # Generate table ID
    table_id = get_table_id(client, dataset_id, table_prefix, report_type, file_date if date_partition else None)
    
    if dry_run:
        print(f"[DRY RUN] Would load {csv_file} to table {table_id}")
        # Read the file to count rows
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            row_count = sum(1 for _ in reader)
            print(f"[DRY RUN] File contains {row_count} rows")
        return table_id, row_count
    
    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip the header row
        autodetect=True,  # Auto-detect schema
        # Set time partitioning if date_partition is True
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="date",  # Partition by the date field
        ) if date_partition else None,
    )
    
    # Load the data
    with open(csv_file, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file,
            table_id,
            job_config=job_config
        )
    
    # Wait for the job to complete
    load_job.result()
    
    # Get the table to check row count
    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows to {table_id}")
    
    return table_id, table.num_rows

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Load Klaviyo data into BigQuery")
    parser.add_argument("--file", required=True, help="Path to the JSON or CSV file to load")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help=f"BigQuery dataset ID (default: {DEFAULT_DATASET})")
    parser.add_argument("--table-prefix", default=DEFAULT_TABLE_PREFIX, help=f"Table name prefix (default: {DEFAULT_TABLE_PREFIX})")
    parser.add_argument("--report-type", required=True, choices=["campaign", "events"], help="Type of report (campaign or events)")
    parser.add_argument("--service-account", help="Path to service account JSON file")
    parser.add_argument("--no-partition", action="store_true", help="Disable date partitioning")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without loading data")
    args = parser.parse_args()
    
    # Check if ENABLE_BQ environment variable is set
    enable_bq = os.getenv("ENABLE_BQ", "false").lower() == "true"
    if not enable_bq and not args.dry_run:
        print("BigQuery loading is disabled. Set ENABLE_BQ=true to enable.")
        print("Running in dry-run mode instead.")
        args.dry_run = True
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist")
        return 1
    
    # Create BigQuery client
    try:
        client = create_bigquery_client(args.service_account)
    except Exception as e:
        print(f"Error creating BigQuery client: {e}")
        return 1
    
    # Ensure dataset exists
    try:
        ensure_dataset_exists(client, args.dataset)
    except Exception as e:
        print(f"Error creating dataset: {e}")
        return 1
    
    # Load data based on file type
    file_path = args.file.lower()
    try:
        if file_path.endswith(".json"):
            table_id, row_count = load_json_to_bigquery(
                client, args.file, args.dataset, args.table_prefix, 
                args.report_type, not args.no_partition, args.dry_run
            )
        elif file_path.endswith(".csv"):
            table_id, row_count = load_csv_to_bigquery(
                client, args.file, args.dataset, args.table_prefix, 
                args.report_type, not args.no_partition, args.dry_run
            )
        else:
            print(f"Error: Unsupported file type. Must be .json or .csv")
            return 1
        
        print(f"{'[DRY RUN] Would load' if args.dry_run else 'Loaded'} {row_count} rows to {table_id}")
        return 0
    except Exception as e:
        print(f"Error loading data: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
