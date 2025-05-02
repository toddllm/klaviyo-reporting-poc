#!/usr/bin/env python3
"""
Final validation script for Klaviyo Mock Data.
This script checks what mock data exists in your Klaviyo account
and reports on it in a comprehensive way.
"""
import os
import requests
import json
from datetime import datetime, timedelta
from tabulate import tabulate

# Load the API key
with open('private-api-key.txt', 'r') as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "revision": "2025-04-15",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def check_lists():
    """Check for mock lists and their profiles."""
    print("\n1. Checking Lists...")
    
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"  ❌ Error fetching lists: {response.status_code}")
        return []
    
    lists_data = response.json().get('data', [])
    mock_lists = [list_data for list_data in lists_data 
                 if list_data.get('attributes', {}).get('name', '').startswith('Mock_')]
    
    if mock_lists:
        print(f"  ✅ Found {len(mock_lists)} mock lists:")
        
        table_data = []
        for list_data in mock_lists:
            list_id = list_data.get('id')
            list_name = list_data.get('attributes', {}).get('name')
            
            # Get profiles count
            profile_count = get_profile_count(list_id)
            
            table_data.append([list_name, list_id, profile_count])
        
        print(tabulate(table_data, headers=["List Name", "List ID", "Profile Count"]))
        return mock_lists
    else:
        print("  ❌ No mock lists found")
        return []

def get_profile_count(list_id):
    """Get the number of profiles in a list."""
    url = f"{BASE_URL}/lists/{list_id}/profiles/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return "Error"
    
    profiles = response.json().get('data', [])
    return len(profiles)

def check_metrics_exists():
    """Check if important metrics exist."""
    print("\n2. Checking Metrics (Event Types)...")
    
    url = f"{BASE_URL}/metrics/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"  ❌ Error fetching metrics: {response.status_code}")
        return {}
    
    metrics_data = response.json().get('data', [])
    
    # Important metrics we want to check
    important_metrics = [
        "Flow Email Sent", 
        "Flow Email Opened", 
        "Placed Order",
        "Email Opened",
        "Email Clicked",
        "Unsubscribed"
    ]
    
    found_metrics = {}
    
    for metric_name in important_metrics:
        for metric in metrics_data:
            if metric.get('attributes', {}).get('name') == metric_name:
                found_metrics[metric_name] = metric.get('id')
                break
    
    table_data = []
    for metric_name in important_metrics:
        status = "✅ Found" if metric_name in found_metrics else "❌ Not Found"
        metric_id = found_metrics.get(metric_name, "N/A")
        table_data.append([metric_name, metric_id, status])
    
    print(tabulate(table_data, headers=["Metric Name", "Metric ID", "Status"]))
    return found_metrics

def check_recent_events(metric_id, metric_name):
    """Check if there are recent events for a metric."""
    print(f"\n  Checking recent events for {metric_name}...")
    
    # We can use the integration API to get events more reliably
    url = f"{BASE_URL}/metrics/"
    headers = HEADERS.copy()
    headers["revision"] = "2025-04-15"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"    ❌ Error querying metric data: {response.status_code}")
        return 0
    
    # For mock demo purposes, let's look at the property that indicates it's our mock data
    url = f"{BASE_URL}/events/?filter=equals(metric.id,'{metric_id}')"
    headers = HEADERS.copy()
    headers["revision"] = "2025-04-15"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"    ❌ Error querying events: {response.status_code}")
        return 0
    
    events = response.json().get('data', [])
    
    # Filter for events with our mock property
    mock_events = []
    for event in events:
        props = event.get('attributes', {}).get('properties', {})
        if props.get('is_mock') or props.get('source') == 'Mock Data Generator':
            mock_events.append(event)
    
    if mock_events:
        print(f"    ✅ Found {len(mock_events)} mock events")
        # Print sample event
        if len(mock_events) > 0:
            sample = mock_events[0]
            print(f"    Sample properties: {json.dumps(sample.get('attributes', {}).get('properties', {}), indent=2)[:200]}...")
    else:
        print(f"    ❌ No mock events found")
    
    return len(mock_events)

def run_validation():
    """Run a comprehensive validation of mock data."""
    print("=== Klaviyo Mock Data Validation ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check lists and profiles
    mock_lists = check_lists()
    
    # Check metrics (event types)
    found_metrics = check_metrics_exists()
    
    # Check for events for each metric we found
    event_counts = {}
    for metric_name, metric_id in found_metrics.items():
        event_count = check_recent_events(metric_id, metric_name)
        event_counts[metric_name] = event_count
    
    # Summary
    print("\n=== VALIDATION SUMMARY ===")
    
    print(f"\nMock Lists: {len(mock_lists)}")
    if mock_lists:
        total_profiles = sum(get_profile_count(lst.get('id')) for lst in mock_lists)
        print(f"Total Profiles: {total_profiles}")
    
    print(f"\nMetrics Found: {len(found_metrics)} of 6 expected")
    
    print("\nEvent Counts:")
    event_table = [[name, count] for name, count in event_counts.items()]
    print(tabulate(event_table, headers=["Event Type", "Count"]))
    
    total_events = sum(event_counts.values())
    if total_events > 0:
        print(f"\n✅ SUCCESS: Found {total_events} mock events in Klaviyo!")
        print("Your mock data has been successfully created and is available for reporting demos.")
    else:
        print("\n❌ WARNING: No mock events were found.")
        print("Try running the mock_klaviyo_final.py script again.")

if __name__ == "__main__":
    run_validation()
