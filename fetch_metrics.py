#!/usr/bin/env python3

import os
import json
import csv
import requests
import argparse
from datetime import datetime, timedelta, UTC
from config import get_config


def get_metric_id(name, force_refresh=False):
    """Get metric ID by name, with caching"""
    cache_file = ".metric_ids.json"
    
    # Try to load from cache first
    if not force_refresh and os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            try:
                metric_ids = json.load(f)
                if name in metric_ids and metric_ids[name]:
                    return metric_ids[name]
            except json.JSONDecodeError:
                pass  # Cache file is invalid, continue to API lookup
    
    # Lookup via API
    config = get_config()
    headers = {
        "Authorization": f"Klaviyo-API-Key {config['KLAVIYO_API_KEY']}",
        "Klaviyo-Api-Version": "2025-04-15"
    }
    
    response = requests.get(
        "https://a.klaviyo.com/api/metrics/", 
        headers=headers,
        params={"filter": f"equals(name,'{name}')"}
    )
    
    data = response.json().get("data", [])
    metric_id = data[0]["id"] if data else None
    
    # Update cache
    metric_ids = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                metric_ids = json.load(f)
        except json.JSONDecodeError:
            pass  # Start with empty dict if cache is corrupted
    
    metric_ids[name] = metric_id
    
    with open(cache_file, 'w') as f:
        json.dump(metric_ids, f)
    
    return metric_id


def fetch_metrics(start_date=None, end_date=None, dry_run=False):
    """Fetch metrics for a campaign"""
    config = get_config()
    campaign_id = config['CAMPAIGN_ID']
    mode = config.get('MODE', 'mock')
    
    # Use UTC dates in ISO 8601 format
    if not start_date:
        start_date = (datetime.now(UTC).date() - timedelta(days=7)).isoformat()
    if not end_date:
        end_date = datetime.now(UTC).date().isoformat()
    
    if dry_run:
        print(f"Would fetch metrics for campaign {campaign_id} from {start_date} to {end_date} (UTC)")
        return True
    
    if mode == 'mock':
        # Generate mock data for testing
        mock_data = [
            {"date": start_date, "delivered": 100, "opened": 45, "clicked": 20, "revenue": 250.00},
            {"date": end_date, "delivered": 120, "opened": 60, "clicked": 30, "revenue": 350.00}
        ]
        
        with open('metrics.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "delivered", "opened", "clicked", "revenue"])
            writer.writeheader()
            for row in mock_data:
                writer.writerow(row)
        
        # Also save mock metric IDs for reference
        with open('.metric_ids.json', 'w') as f:
            json.dump({
                "Opened Email": "mock-open-id-123",
                "Clicked Email": "mock-click-id-456",
                "Placed Order": "mock-revenue-id-789"
            }, f)
        
        print(f"Generated mock metrics data in metrics.csv")
        return True
    
    # Real API mode
    headers = {
        "Authorization": f"Klaviyo-API-Key {config['KLAVIYO_API_KEY']}",
        "Klaviyo-Api-Version": "2025-04-15"
    }
    
    # Get metric IDs
    opened_id = get_metric_id("Opened Email")
    clicked_id = get_metric_id("Clicked Email")
    revenue_id = get_metric_id("Placed Order")
    
    if not all([opened_id, clicked_id, revenue_id]):
        print("Error: Could not find all required metric IDs")
        return False
    
    # Fetch open/click metrics
    metrics_data = []
    for metric_id in [opened_id, clicked_id]:
        response = requests.get(
            "https://a.klaviyo.com/api/metric-aggregates/",
            headers=headers,
            params={
                "measure": "unique",
                "metric_id": metric_id,
                "start_date": start_date,
                "end_date": end_date,
                "filters": f"[['equals','campaign_id','{campaign_id}']]"
            }
        )
        
        if response.status_code != 200:
            print(f"Error fetching metrics: {response.status_code} {response.text}")
            return False
        
        data = response.json()
        metrics_data.append(data)
    
    # Fetch revenue metrics separately
    revenue_response = requests.get(
        "https://a.klaviyo.com/api/metric-aggregates/",
        headers=headers,
        params={
            "measure": "sum",  # Use sum for revenue
            "metric_id": revenue_id,
            "start_date": start_date,
            "end_date": end_date,
            "filters": f"[['equals','campaign_id','{campaign_id}']]"
        }
    )
    
    if revenue_response.status_code != 200:
        print(f"Error fetching revenue: {revenue_response.status_code} {revenue_response.text}")
        return False
    
    revenue_data = revenue_response.json()
    
    # Process and combine the data
    combined_data = []
    for date_entry in metrics_data[0].get("data", []):
        date = date_entry.get("date")
        opened = date_entry.get("value", 0)
        
        # Find matching click data for this date
        clicked = 0
        for click_entry in metrics_data[1].get("data", []):
            if click_entry.get("date") == date:
                clicked = click_entry.get("value", 0)
                break
        
        # Find matching revenue data for this date
        revenue = 0
        for rev_entry in revenue_data.get("data", []):
            if rev_entry.get("date") == date:
                revenue = rev_entry.get("value", 0)
                break
        
        # Estimate delivered count (could be fetched from a different endpoint in a real implementation)
        delivered = int(opened * 2.5)  # Simple estimation for demo purposes
        
        combined_data.append({
            "date": date,
            "delivered": delivered,
            "opened": opened,
            "clicked": clicked,
            "revenue": revenue
        })
    
    # Write to CSV
    with open('metrics.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "delivered", "opened", "clicked", "revenue"])
        writer.writeheader()
        for row in combined_data:
            writer.writerow(row)
    
    # Also save metric IDs for reference
    with open('.metric_ids.json', 'w') as f:
        json.dump({
            "Opened Email": opened_id,
            "Clicked Email": clicked_id,
            "Placed Order": revenue_id
        }, f)
    
    print(f"Fetched metrics data for campaign {campaign_id} and saved to metrics.csv")
    return True


def main():
    parser = argparse.ArgumentParser(description="Fetch metrics for a Klaviyo campaign")
    parser.add_argument("--start-date", help="Start date in ISO format (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date in ISO format (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without making API calls")
    args = parser.parse_args()
    
    success = fetch_metrics(args.start_date, args.end_date, args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
