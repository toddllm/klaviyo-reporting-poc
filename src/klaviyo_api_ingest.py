#!/usr/bin/env python3
import os
import requests
import time
import json
import csv
import argparse
from datetime import datetime, timedelta, UTC

# Constants
BASE_URL = "https://a.klaviyo.com/api/v1"

# Configuration
def get_api_key():
    """Get Klaviyo API key from environment variable"""
    api_key = os.getenv("KLAVIYO_API_KEY")
    if not api_key:
        raise ValueError("KLAVIYO_API_KEY environment variable not set")
    return api_key

# API Functions
def fetch_campaigns(page_token=None, dry_run=False):
    """Fetch campaigns from Klaviyo API with pagination"""
    api_key = get_api_key()
    params = {"api_key": api_key, "count": 100}
    if page_token:
        params["page_token"] = page_token
    
    if dry_run:
        print(f"[DRY RUN] Would fetch campaigns with params: {params}")
        # Return mock data for dry run
        return [
            {
                "id": "campaign_123",
                "name": "Test Campaign 1",
                "send_time": "2025-05-01T10:00:00Z",
                "subject": "Test Subject 1",
                "open_rate": 0.45,
                "click_rate": 0.20
            },
            {
                "id": "campaign_456",
                "name": "Test Campaign 2",
                "send_time": "2025-05-08T10:00:00Z",
                "subject": "Test Subject 2",
                "open_rate": 0.50,
                "click_rate": 0.25
            }
        ], "next_page_token_123"
    
    try:
        response = requests.get(f"{BASE_URL}/campaigns", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["data"], data.get("next_page_token")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching campaigns: {e}")
        return [], None

def fetch_all_campaigns(dry_run=False):
    """Fetch all campaigns using pagination"""
    all_campaigns = []
    page_token = None
    page_count = 0
    max_pages = 10  # Limit for safety
    
    while page_count < max_pages:
        campaigns, next_page_token = fetch_campaigns(page_token, dry_run)
        all_campaigns.extend(campaigns)
        page_token = next_page_token
        page_count += 1
        
        if not page_token:
            break
        
        # Avoid rate limiting
        time.sleep(0.2)
    
    return all_campaigns

def fetch_campaign_metrics(campaign_id, dry_run=False):
    """Fetch metrics for a specific campaign"""
    api_key = get_api_key()
    params = {
        "api_key": api_key,
        "campaign_id": campaign_id,
        "start_date": (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date": datetime.now(UTC).strftime("%Y-%m-%d")
    }
    
    if dry_run:
        print(f"[DRY RUN] Would fetch metrics for campaign {campaign_id} with params: {params}")
        # Return mock data for dry run
        return {
            "delivered": 100,
            "opened": 45,
            "clicked": 20,
            "revenue": 250.0
        }
    
    try:
        response = requests.get(f"{BASE_URL}/campaign-metrics", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metrics for campaign {campaign_id}: {e}")
        return {}

# Output Functions
def write_to_csv(data, output_file="campaigns.csv"):
    """Write campaign data to CSV file"""
    if not data:
        print("No data to write to CSV")
        return False
    
    # Define the fields we want to include
    fieldnames = ["id", "name", "send_time", "subject", "open_rate", "click_rate", "delivered", "opened", "clicked", "revenue"]
    
    try:
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Only include fields that are in our fieldnames list
                filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(filtered_row)
        print(f"Data written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False

def write_to_json(data, output_file="campaigns.json"):
    """Write campaign data to JSON file"""
    if not data:
        print("No data to write to JSON")
        return False
    
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Data written to {output_file}")
        return True
    except Exception as e:
        print(f"Error writing to JSON: {e}")
        return False

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Fetch campaign metrics from Klaviyo API")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making actual API calls")
    parser.add_argument("--output", default="campaigns.csv", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format")
    args = parser.parse_args()
    
    print(f"Fetching campaigns from Klaviyo API...")
    campaigns = fetch_all_campaigns(args.dry_run)
    print(f"Found {len(campaigns)} campaigns")
    
    # Fetch metrics for each campaign
    for campaign in campaigns:
        campaign_id = campaign["id"]
        print(f"Fetching metrics for campaign {campaign_id}...")
        metrics = fetch_campaign_metrics(campaign_id, args.dry_run)
        # Add metrics to campaign data
        campaign.update(metrics)
    
    # Write data to file
    if args.format == "csv":
        write_to_csv(campaigns, args.output)
    else:
        write_to_json(campaigns, args.output)

if __name__ == "__main__":
    main()
