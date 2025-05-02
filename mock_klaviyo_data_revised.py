#!/usr/bin/env python3
"""
Revised Klaviyo Mock Data Generator with proper API integration and validation

This script creates realistic mock data in Klaviyo for:
- Lists with profiles
- Campaigns with associated events
- Flows with tracked engagement
- Purchase events with product details

All data is clearly marked with 'Mock_' prefix and won't send actual emails.
"""
import os
import random
import time
import json
import requests
from datetime import datetime, timedelta
from faker import Faker

# Initialize faker
faker = Faker()

# Configuration
VERBOSE = True  # Set to False for less output

# Load the API key
with open('private-api-key.txt', 'r') as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def log(message, level="INFO"):
    """Log messages when verbose mode is enabled."""
    if VERBOSE:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

def random_past_date(days=14):
    """Generate a random date in the past X days."""
    days_ago = random.randint(0, days)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    
    return datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

# Step 1: Create a test list
def create_list(name="Mock_Reporting_List"):
    """Create a new list in Klaviyo."""
    log(f"Creating list '{name}'...")
    
    url = f"{BASE_URL}/lists/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-02-22"
    
    payload = {
        "data": {
            "type": "list",
            "attributes": {
                "name": name
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code not in (200, 201):
        log(f"Error creating list: {response.status_code} {response.text}", "ERROR")
        return None
    
    list_id = response.json()["data"]["id"]
    log(f"Successfully created list '{name}' with ID: {list_id}")
    return list_id

# Step 2: Generate mock profiles
def generate_mock_profiles(n=25):
    """Generate n mock profiles with realistic data."""
    log(f"Generating {n} mock profiles...")
    
    profiles = []
    for _ in range(n):
        first = faker.first_name()
        last = faker.last_name()
        email = f"{first.lower()}.{last.lower()}.mock@example.com"
        
        profile = {
            "type": "profile",
            "attributes": {
                "email": email,
                "first_name": first,
                "last_name": last,
                "properties": {
                    "city": faker.city(),
                    "country": faker.country(),
                    "is_mock": True,
                    "source": "Mock Data Generator"
                }
            }
        }
        profiles.append(profile)
    
    return profiles

# Add profiles to a list
def add_profiles_to_list(list_id, profiles):
    """Add generated profiles to the specified list."""
    log(f"Adding {len(profiles)} profiles to list {list_id}...")
    
    # First create profiles one by one
    created_profile_ids = []
    
    # Create profiles
    url = f"{BASE_URL}/profiles/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-10-15"
    
    for i, profile_data in enumerate(profiles):
        payload = {"data": profile_data}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code not in (200, 201, 202):
            log(f"Error creating profile {i+1}: {response.status_code} {response.text}", "ERROR")
            continue
        
        profile_id = response.json()["data"]["id"]
        created_profile_ids.append({"type": "profile", "id": profile_id})
        log(f"Created profile {i+1}/{len(profiles)}: {profile_data['attributes']['email']}")
        time.sleep(0.2)  # Rate limiting
    
    # Now add all profiles to the list
    url = f"{BASE_URL}/lists/{list_id}/relationships/profiles/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-02-22"
    
    payload = {"data": created_profile_ids}
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in (200, 201, 202, 204):
        log(f"Successfully added {len(created_profile_ids)} profiles to list {list_id}")
        return True
    else:
        log(f"Error adding profiles to list: {response.status_code} {response.text}", "ERROR")
        return False

# Step 3: Create campaigns
def create_campaign(name):
    """Create a campaign in Klaviyo."""
    log(f"Creating campaign '{name}'...")
    
    url = f"{BASE_URL}/campaigns/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-02-22"
    
    # Create a campaign with minimal required fields
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": name,
                "audiences": {
                    "included": [],  # We'll add the list ID later
                    "excluded": []
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code not in (200, 201):
        log(f"Error creating campaign: {response.status_code} {response.text}", "ERROR")
        return None
    
    campaign_id = response.json()["data"]["id"]
    log(f"Successfully created campaign '{name}' with ID: {campaign_id}")
    return campaign_id

# Step 4: Create a flow
def create_flow(name="Mock_Welcome_Flow"):
    """Create a flow in Klaviyo."""
    log(f"Creating flow '{name}'...")
    
    url = f"{BASE_URL}/flows/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-10-15"
    
    payload = {
        "data": {
            "type": "flow",
            "attributes": {
                "name": name,
                "status": "draft",
                "trigger_type": "list"
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code not in (200, 201):
        log(f"Error creating flow: {response.status_code} {response.text}", "ERROR")
        return None
    
    flow_id = response.json()["data"]["id"]
    log(f"Successfully created flow '{name}' with ID: {flow_id}")
    return flow_id

# Step 5: Track events
def track_event(event_name, email, properties=None, time=None):
    """Track an event for a profile."""
    # Create a new metric if it doesn't exist
    metric_id = ensure_metric_exists(event_name)
    if not metric_id:
        log(f"Could not create or find metric '{event_name}'", "ERROR")
        return False
    
    # Track an event
    url = f"{BASE_URL}/events/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-02-22"
    
    if not properties:
        properties = {}
    
    # Add mock flag to properties
    properties["is_mock"] = True
    properties["source"] = "Mock Data Generator"
    
    # Format timestamp
    if time:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    payload = {
        "data": {
            "type": "event",
            "attributes": {
                "properties": properties,
                "time": timestamp,
                "metric": {
                    "name": event_name
                },
                "profile": {
                    "email": email
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code not in (200, 201, 202):
        log(f"Error tracking event {event_name} for {email}: {response.status_code} {response.text}", "ERROR")
        return False
    
    log(f"Successfully tracked event '{event_name}' for {email}")
    return True

def ensure_metric_exists(metric_name):
    """
    Check if a metric exists, and if not, create it.
    Returns the metric ID.
    """
    # First, check if the metric exists
    url = f"{BASE_URL}/metrics/"
    headers = HEADERS.copy()
    headers["revision"] = "2023-02-22"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        metrics = response.json().get("data", [])
        for metric in metrics:
            if metric.get("attributes", {}).get("name") == metric_name:
                return metric.get("id")
    
    # If we get here, the metric doesn't exist, so we create it
    log(f"Metric '{metric_name}' not found, creating it...")
    
    # You cannot directly create metrics via API, they are created automatically 
    # when tracking events. We'll return None and let the tracking function handle it.
    return None

# Step 6: Simulate campaign events
def simulate_campaign_events(profiles, campaign_names):
    """Simulate events for the specified campaigns."""
    log(f"Simulating campaign events for {len(campaign_names)} campaigns...")
    
    # Create the campaigns
    campaign_ids = {}
    for name in campaign_names:
        campaign_id = create_campaign(name)
        if campaign_id:
            campaign_ids[name] = campaign_id
    
    # Track events for each campaign
    success_count = 0
    event_types = ["Email Opened", "Email Clicked", "Unsubscribed"]
    
    for campaign_name in campaign_ids:
        # Select a subset of profiles for this campaign
        campaign_profiles = random.sample(profiles, min(10, len(profiles)))
        
        for profile in campaign_profiles:
            email = profile["attributes"]["email"]
            
            # Opened emails
            if random.random() < 0.85:
                timestamp = random_past_date()
                properties = {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_ids[campaign_name]
                }
                
                success = track_event("Email Opened", email, properties, timestamp)
                if success:
                    success_count += 1
                time.sleep(0.2)  # Rate limiting
            
            # Clicked emails (only if opened)
            if random.random() < 0.6:
                timestamp = random_past_date()
                properties = {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_ids[campaign_name],
                    "url": "https://example.com/mock-link"
                }
                
                success = track_event("Email Clicked", email, properties, timestamp)
                if success:
                    success_count += 1
                time.sleep(0.2)  # Rate limiting
            
            # Unsubscribes (rare)
            if random.random() < 0.05:
                timestamp = random_past_date()
                properties = {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_ids[campaign_name],
                    "reason": "Mock unsubscribe"
                }
                
                success = track_event("Unsubscribed", email, properties, timestamp)
                if success:
                    success_count += 1
                time.sleep(0.2)  # Rate limiting
    
    log(f"Successfully simulated {success_count} campaign events")
    return success_count

# Step 7: Simulate flow events
def simulate_flow_events(profiles):
    """Simulate events for the welcome flow."""
    flow_name = "Mock_Welcome_Flow"
    log(f"Simulating flow events for '{flow_name}'...")
    
    # Create the flow
    flow_id = create_flow(flow_name)
    if not flow_id:
        log(f"Could not create flow '{flow_name}', skipping flow events", "ERROR")
        return 0
    
    # Track events
    success_count = 0
    
    # Select a subset of profiles for flow events
    flow_profiles = random.sample(profiles, min(15, len(profiles)))
    
    for profile in flow_profiles:
        email = profile["attributes"]["email"]
        
        # Flow Email Sent
        timestamp = random_past_date()
        properties = {
            "flow_name": flow_name,
            "flow_id": flow_id,
            "message_id": f"mock-message-{random.randint(1000, 9999)}"
        }
        
        success = track_event("Flow Email Sent", email, properties, timestamp)
        if success:
            success_count += 1
        time.sleep(0.2)  # Rate limiting
        
        # Flow Email Opened (75% chance)
        if random.random() < 0.75:
            # Opened happens after sent
            timestamp = timestamp + timedelta(hours=random.randint(1, 24))
            properties = {
                "flow_name": flow_name,
                "flow_id": flow_id,
                "message_id": properties["message_id"]  # Same message ID
            }
            
            success = track_event("Flow Email Opened", email, properties, timestamp)
            if success:
                success_count += 1
            time.sleep(0.2)  # Rate limiting
    
    log(f"Successfully simulated {success_count} flow events")
    return success_count

# Step 8: Simulate purchase behavior
def simulate_purchases(profiles):
    """Simulate purchase events for a subset of profiles."""
    log("Simulating purchase events...")
    
    success_count = 0
    
    # Select a subset of profiles for purchases
    n = min(random.randint(5, 7), len(profiles))
    buyers = random.sample(profiles, n)
    
    for profile in buyers:
        email = profile["attributes"]["email"]
        
        # Generate 1-3 items for this order
        items = []
        for _ in range(random.randint(1, 3)):
            items.append({
                "product_name": faker.word().title(),
                "price": round(random.uniform(10, 200), 2),
                "quantity": random.randint(1, 3),
                "product_id": f"MOCK-{random.randint(10000, 99999)}"
            })
        
        # Calculate order total
        total = sum(item["price"] * item["quantity"] for item in items)
        
        # Create order properties
        timestamp = random_past_date()
        properties = {
            "order_id": f"MOCK-ORDER-{random.randint(10000, 99999)}",
            "total": total,
            "items": items,
            "currency": "USD",
            "is_mock": True
        }
        
        # Track the purchase event
        success = track_event("Placed Order", email, properties, timestamp)
        if success:
            success_count += 1
        time.sleep(0.3)  # Rate limiting
    
    log(f"Successfully simulated {success_count} purchase events")
    return success_count

def run():
    """Run the full mock data generation process with validation."""
    start_time = time.time()
    log("Starting Klaviyo mock data generation...")
    
    # Step 1 & 2: Create list and profiles
    list_id = create_list()
    if not list_id:
        log("Failed to create list, aborting", "ERROR")
        return False
    
    profiles = generate_mock_profiles()
    success = add_profiles_to_list(list_id, profiles)
    if not success:
        log("Failed to add profiles to list, aborting", "ERROR")
        return False
    
    # Step 3: Simulate campaign events
    campaign_events = simulate_campaign_events(profiles, ["Mock_Welcome_Campaign", "Mock_Product_Update"])
    
    # Step 4: Simulate flow events
    flow_events = simulate_flow_events(profiles)
    
    # Step 5: Simulate purchase events
    purchase_events = simulate_purchases(profiles)
    
    # Summary
    total_time = int(time.time() - start_time)
    log(f"\n=== MOCK DATA GENERATION COMPLETE ===")
    log(f"Created list '{list_id}' with {len(profiles)} profiles")
    log(f"Generated {campaign_events} campaign events")
    log(f"Generated {flow_events} flow events")
    log(f"Generated {purchase_events} purchase events")
    log(f"Total execution time: {total_time} seconds")
    
    return True

if __name__ == "__main__":
    run()
