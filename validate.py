#!/usr/bin/env python3
"""
Validation script for Klaviyo mock data.
Checks for the existence of lists, profiles, campaigns, flows, and events.
"""
import os
import requests
import json
import time
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

def check_list_exists(list_name):
    """Check if a list with the given name exists."""
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching lists: {response.status_code} {response.text}")
        return False, None
    
    lists_data = response.json().get('data', [])
    for list_data in lists_data:
        if list_data.get('attributes', {}).get('name') == list_name:
            return True, list_data
    
    return False, None

def get_list_profiles(list_id):
    """Get profiles in a list."""
    url = f"{BASE_URL}/lists/{list_id}/profiles/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching profiles for list {list_id}: {response.status_code} {response.text}")
        return []
    
    return response.json().get('data', [])

def check_campaign_exists(campaign_name):
    """Check if a campaign with the given name exists."""
    url = f"{BASE_URL}/campaigns/?filter=equals(messages.channel,'email')"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching campaigns: {response.status_code} {response.text}")
        return False, None
    
    campaigns_data = response.json().get('data', [])
    for campaign_data in campaigns_data:
        if campaign_data.get('attributes', {}).get('name') == campaign_name:
            return True, campaign_data
    
    return False, None

def get_metrics():
    """Get available metrics (event types)."""
    url = f"{BASE_URL}/metrics/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching metrics: {response.status_code} {response.text}")
        return []
    
    return response.json().get('data', [])

def check_events_count(metric_id, days=14):
    """Check the count of events for a given metric in the past X days."""
    # Calculate date range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Format times for API
    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # Get count of events
    url = f"{BASE_URL}/metrics/timeline?filter=equals(metric_id,'{metric_id}')&start_date={start_str}&end_date={end_str}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching events for metric {metric_id}: {response.status_code} {response.text}")
        return 0
    
    # Parse and sum events
    data = response.json()
    events = data.get('data', {}).get('attributes', {}).get('data', [])
    total_count = sum(point.get('count', 0) for point in events)
    
    return total_count

def validate_mock_data():
    """
    Validate all mock data components:
    - Lists
    - Profiles
    - Campaigns
    - Flows
    - Events
    """
    results = {
        "Lists": [],
        "Profiles": 0,
        "Events": []
    }
    
    # Check for Mock_Reporting_List
    print("\n1. Validating Lists:")
    list_exists, list_data = check_list_exists("Mock_Reporting_List")
    if list_exists:
        list_id = list_data.get('id')
        results["Lists"].append({
            "Name": "Mock_Reporting_List",
            "ID": list_id,
            "Status": "✅ Found"
        })
        
        # Get profile count
        profiles = get_list_profiles(list_id)
        results["Profiles"] = len(profiles)
        print(f"   ✅ Found list 'Mock_Reporting_List' with {len(profiles)} profiles")
    else:
        results["Lists"].append({
            "Name": "Mock_Reporting_List",
            "ID": "N/A",
            "Status": "❌ Not Found"
        })
        print("   ❌ 'Mock_Reporting_List' not found")
    
    # Check for campaign names in events
    print("\n2. Validating Campaign Events:")
    metrics = get_metrics()
    campaign_events = ["Email Opened", "Email Clicked", "Unsubscribed"]
    
    for event_name in campaign_events:
        found = False
        for metric in metrics:
            if metric.get('attributes', {}).get('name') == event_name:
                metric_id = metric.get('id')
                event_count = check_events_count(metric_id)
                
                results["Events"].append({
                    "Event": event_name,
                    "Count": event_count,
                    "Status": "✅ Found" if event_count > 0 else "❌ No Events"
                })
                
                print(f"   {'✅' if event_count > 0 else '❌'} {event_name}: {event_count} events in last 14 days")
                found = True
                break
        
        if not found:
            results["Events"].append({
                "Event": event_name,
                "Count": 0,
                "Status": "❌ Metric Not Found"
            })
            print(f"   ❌ {event_name}: Metric not found")
    
    # Check flow events
    print("\n3. Validating Flow Events:")
    flow_events = ["Flow Email Sent", "Flow Email Opened"]
    
    for event_name in flow_events:
        found = False
        for metric in metrics:
            if metric.get('attributes', {}).get('name') == event_name:
                metric_id = metric.get('id')
                event_count = check_events_count(metric_id)
                
                results["Events"].append({
                    "Event": event_name,
                    "Count": event_count,
                    "Status": "✅ Found" if event_count > 0 else "❌ No Events"
                })
                
                print(f"   {'✅' if event_count > 0 else '❌'} {event_name}: {event_count} events in last 14 days")
                found = True
                break
        
        if not found:
            results["Events"].append({
                "Event": event_name,
                "Count": 0,
                "Status": "❌ Metric Not Found"
            })
            print(f"   ❌ {event_name}: Metric not found")
    
    # Check purchase events
    print("\n4. Validating Purchase Events:")
    for metric in metrics:
        if metric.get('attributes', {}).get('name') == "Placed Order":
            metric_id = metric.get('id')
            event_count = check_events_count(metric_id)
            
            results["Events"].append({
                "Event": "Placed Order",
                "Count": event_count,
                "Status": "✅ Found" if event_count > 0 else "❌ No Events"
            })
            
            print(f"   {'✅' if event_count > 0 else '❌'} Placed Order: {event_count} events in last 14 days")
            break
    
    # Print summary
    print("\n=== VALIDATION SUMMARY ===")
    
    print("\nLists:")
    list_table = [[l["Name"], l["ID"], l["Status"]] for l in results["Lists"]]
    print(tabulate(list_table, headers=["Name", "ID", "Status"]))
    
    print(f"\nProfiles: {results['Profiles']} in Mock_Reporting_List")
    
    print("\nEvents:")
    event_table = [[e["Event"], e["Count"], e["Status"]] for e in results["Events"]]
    print(tabulate(event_table, headers=["Event Type", "Count", "Status"]))
    
    # Print overall status
    total_events = sum(e["Count"] for e in results["Events"])
    list_found = any(l["Status"] == "✅ Found" for l in results["Lists"])
    
    if list_found and results["Profiles"] > 0 and total_events > 0:
        print("\n✅ OVERALL: Mock data appears to be successfully created")
    else:
        print("\n❌ OVERALL: Issues found with mock data creation")

if __name__ == "__main__":
    print("Validating Klaviyo mock data...")
    validate_mock_data()
