#!/usr/bin/env python3
import os
import sys
import json
import csv
import argparse
import time
from datetime import datetime, date
import requests

# Constants
SUPERMETRICS_API_ENDPOINT = "https://api.supermetrics.com/enterprise/v2/query/data/json"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
REPORT_TYPE_MAP = {
    "campaign": "klaviyo_campaigns",
    "events": "klaviyo_email_events"
}

# Configuration
def get_api_key(dry_run=False):
    api_key = os.getenv("SUPERMETRICS_API_KEY")
    if not api_key and not dry_run:
        raise ValueError("SUPERMETRICS_API_KEY environment variable not set")
    return api_key or "dummy_key_for_dry_run"

# API Functions
def fetch_data(start_date, end_date, report_type, page_token=None, dry_run=False):
    api_key = get_api_key(dry_run)
    ds_id = REPORT_TYPE_MAP.get(report_type)
    if not ds_id:
        raise ValueError(f"Invalid report type: {report_type}. Must be one of {list(REPORT_TYPE_MAP.keys())}")
    
    headers = {
        "Content-Type": "application/json",
        "api_key": api_key
    }
    
    payload = {
        "ds_id": ds_id,
        "start_date": start_date,
        "end_date": end_date,
        "fields": ["*"]  # Request all available fields
    }
    
    if page_token:
        payload["page_token"] = page_token
    
    if dry_run:
        print(f"[DRY RUN] Would fetch {report_type} data with payload: {payload}")
        # Return mock data for dry run
        if report_type == "campaign":
            mock_data = [
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
        else:  # events
            mock_data = [
                {
                    "event_id": "event_123",
                    "campaign_id": "campaign_123",
                    "event_name": "Open",
                    "event_time": "2025-05-01T12:30:00Z",
                    "email": "user1@example.com",
                    "device": "Mobile"
                },
                {
                    "event_id": "event_456",
                    "campaign_id": "campaign_123",
                    "event_name": "Click",
                    "event_time": "2025-05-01T12:35:00Z",
                    "email": "user1@example.com",
                    "device": "Mobile"
                }
            ]
        
        # Simulate pagination for dry run
        next_token = "mock_page_2" if not page_token else None
        return mock_data, next_token
    
    max_retries = 5
    retry_count = 0
    backoff_time = 1
    
    while retry_count < max_retries:
        try:
            response = requests.post(
                SUPERMETRICS_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", backoff_time))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                retry_count += 1
                backoff_time = min(backoff_time * 2, 60)  # Exponential backoff, max 60 seconds
                continue
            
            # Handle server errors
            if response.status_code >= 500:
                print(f"Server error (HTTP {response.status_code}). Retrying after {backoff_time} seconds...")
                time.sleep(backoff_time)
                retry_count += 1
                backoff_time = min(backoff_time * 2, 60)  # Exponential backoff, max 60 seconds
                continue
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", []), data.get("next_page_token")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, 60)  # Exponential backoff, max 60 seconds
            else:
                print(f"Max retries ({max_retries}) reached. Giving up.")
                return [], None
    
    return [], None

def fetch_all_data(start_date, end_date, report_type, dry_run=False):
    all_data = []
    page_token = None
    page_count = 0
    max_pages = 100  # Safety limit
    
    print(f"Fetching {report_type} data from {start_date} to {end_date}...")
    
    while page_count < max_pages:
        data, next_page_token = fetch_data(start_date, end_date, report_type, page_token, dry_run)
        all_data.extend(data)
        page_token = next_page_token
        page_count += 1
        
        print(f"Fetched page {page_count} with {len(data)} records. Total records: {len(all_data)}")
        
        if not page_token:
            break
        
        # Respect rate limits
        time.sleep(6)  # ~10 queries per minute
    
    if page_count >= max_pages:
        print(f"Warning: Reached maximum page limit ({max_pages}). Data may be incomplete.")
    
    return all_data

# Output Functions
def write_to_json(data, report_type, dry_run=False):
    if not data:
        print("No data to write to JSON")
        return None
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate filename with current date
    timestamp = date.today().strftime("%Y%m%d")
    output_file = os.path.join(DATA_DIR, f"supermetrics_raw_{report_type}_{timestamp}.json")
    
    if dry_run:
        print(f"[DRY RUN] Would write {len(data)} records to {output_file}")
        return output_file
    
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Data written to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error writing to JSON: {e}")
        return None

def write_to_csv(data, json_file, dry_run=False):
    if not data or not json_file:
        print("No data or JSON file path to write CSV")
        return None
    
    # Generate CSV filename based on JSON filename
    output_file = json_file.replace(".json", ".csv")
    
    if dry_run:
        print(f"[DRY RUN] Would write {len(data)} records to {output_file}")
        return output_file
    
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
        return output_file
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return None

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Fetch Klaviyo data via Supermetrics API")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format")
    parser.add_argument("--report-type", required=True, choices=["campaign", "events"], 
                        help="Type of report to fetch (campaign or events)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--csv", action="store_true", help="Also output data as CSV")
    args = parser.parse_args()
    
    # Validate dates
    try:
        datetime.strptime(args.start_date, "%Y-%m-%d")
        datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return 1
    
    # Fetch data
    data = fetch_all_data(args.start_date, args.end_date, args.report_type, args.dry_run)
    
    if not data:
        print("No data fetched. Exiting.")
        return 1
    
    # Write to JSON
    json_file = write_to_json(data, args.report_type, args.dry_run)
    
    # Write to CSV if requested
    if args.csv and json_file:
        write_to_csv(data, json_file, args.dry_run)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
