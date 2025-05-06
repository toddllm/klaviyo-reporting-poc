#!/usr/bin/env python3
import os
import argparse
import json
import csv
import time
from datetime import datetime

# Import from other modules
from klaviyo_api_ingest import fetch_all_campaigns, fetch_campaign_metrics
from lookml_field_mapper import normalize_records

# Constants
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_OUTPUT_FILE = "klaviyo_campaign_metrics.csv"

# ETL Functions
def extract(dry_run=False):
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

def run_etl(dry_run=False, output_file=None, format="csv"):
    """Run the full ETL process"""
    # Set default output file if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"klaviyo_metrics_{timestamp}.{format}"
        output_file = os.path.join(DEFAULT_OUTPUT_DIR, filename)
    
    try:
        # Extract
        raw_data = extract(dry_run)
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
def main():
    parser = argparse.ArgumentParser(description="ETL Runner for Klaviyo Campaign Metrics")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    parser.add_argument("--supermetrics", action="store_true", help="Prepare data for Supermetrics integration")
    args = parser.parse_args()
    
    # Run the ETL process
    success = run_etl(args.dry_run, args.output, args.format)
    
    # Prepare for Supermetrics if requested
    if success and args.supermetrics:
        output_file = args.output or os.path.join(DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE)
        prepare_for_supermetrics(output_file, args.format)

if __name__ == "__main__":
    main()
