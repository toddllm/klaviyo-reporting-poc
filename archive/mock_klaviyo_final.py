#!/usr/bin/env python3
"""
Final Klaviyo Mock Data Generator
With proper API validation and error handling

Creates:
- Lists with profiles
- Campaign events
- Flow events
- Purchase events

All with proper tracking in Klaviyo for reporting demos.
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
def get_list_id(name):
    """Get a list ID by name from Klaviyo."""
    url = f"{BASE_URL}/lists/"
    
    headers = HEADERS.copy()
    headers["revision"] = "2025-04-15"  # Add the revision header
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code} {response.text}", "ERROR")
        return None
    
    for list_data in response.json().get("data", []):
        if list_data.get("attributes", {}).get("name") == name:
            return list_data.get("id")
    
    return None

def create_list(name="Mock_Reporting_List"):
    """Create a new list in Klaviyo."""
    log(f"Creating list '{name}'...")
    
    url = f"{BASE_URL}/lists/"
    headers = HEADERS.copy()
    headers["revision"] = "2025-04-15"  # Updated revision date
    
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
    headers["revision"] = "2025-04-15"  # Updated revision date
    
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
    headers["revision"] = "2025-04-15"  # Updated revision date
    
    payload = {"data": created_profile_ids}
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in (200, 201, 202, 204):
        log(f"Successfully added {len(created_profile_ids)} profiles to list {list_id}")
        return created_profile_ids
    else:
        log(f"Error adding profiles to list: {response.status_code} {response.text}", "ERROR")
        return []

# Step 3: Create campaigns
def create_campaign(name):
    """Create a campaign in Klaviyo."""
    log(f"Creating campaign '{name}'...")
    
    # Get the mock list for audience targeting
    list_id = get_list_id("Mock_Reporting_List")
    
    url = f"{BASE_URL}/campaigns/"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"  # Use a stable revision date
    
    # Create a simplified campaign with minimal required fields
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": name,
                "audiences": {
                    "included": [{
                        "id": f"list-{list_id}",
                        "type": "dynamic-segment"
                    }] if list_id else [],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "send_time": (datetime.now() + timedelta(days=1)).isoformat()
                    }
                },
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "channel": "email",
                                "label": name,
                                "content": {
                                    "subject": f"[TEST] {name}",
                                    "preview_text": "Mock campaign from API",
                                    "from_email": "clara@clarathecoach.com",
                                    "from_label": "CTC"
                                }
                            }
                        }
                    ]
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

# Step 5: Track events
def track_event(event_name, profile_id, properties=None, time_value=None):
    """Track an event for a profile using the metrics API."""
    url = f"{BASE_URL}/events/"
    headers = HEADERS.copy()
    headers["revision"] = "2025-04-15"  # Updated revision date
    
    if not properties:
        properties = {}
    
    # Add mock flag to properties
    properties["is_mock"] = True
    properties["source"] = "Mock Data Generator"
    properties["mock_created"] = datetime.now().strftime("%Y-%m-%d")
    
    # Format timestamp
    if time_value:
        timestamp = time_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Use correct JSON:API format for events
    payload = {
        "data": {
            "type": "event",
            "attributes": {
                "properties": properties,
                "time": timestamp,
                "metric": {
                    "data": {
                        "type": "metric",
                        "attributes": {
                            "name": event_name
                        }
                    }
                },
                "profile": {
                    "data": {
                        "type": "profile",
                        "id": profile_id
                    }
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code not in (200, 201, 202):
        log(f"Error tracking event {event_name}: {response.status_code} {response.text}", "ERROR")
        return False
    
    log(f"Successfully tracked event '{event_name}'")
    return True

# Step 6: Simulate campaign events
def simulate_campaign_events(profile_data, campaign_names):
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
    
    for campaign_name, campaign_id in campaign_ids.items():
        # Select a subset of profiles for this campaign
        campaign_profiles = random.sample(profile_data, min(10, len(profile_data)))
        
        for profile in campaign_profiles:
            profile_id = profile["id"]
            
            # Opened emails (85% chance)
            if random.random() < 0.85:
                timestamp = random_past_date()
                properties = {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_id
                }
                
                success = track_event("Email Opened", profile_id, properties, timestamp)
                if success:
                    success_count += 1
                time.sleep(0.2)  # Rate limiting
            
            # Clicked emails (60% chance)
            if random.random() < 0.6:
                timestamp = random_past_date()
                properties = {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_id,
                    "url": "https://example.com/mock-link"
                }
                
                success = track_event("Email Clicked", profile_id, properties, timestamp)
                if success:
                    success_count += 1
                time.sleep(0.2)  # Rate limiting
            
            # Unsubscribes (5% chance)
            if random.random() < 0.05:
                timestamp = random_past_date()
                properties = {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_id,
                    "reason": "Mock unsubscribe"
                }
                
                success = track_event("Unsubscribed", profile_id, properties, timestamp)
                if success:
                    success_count += 1
                time.sleep(0.2)  # Rate limiting
    
    log(f"Successfully simulated {success_count} campaign events")
    return success_count, campaign_ids

# Step 7: Simulate flow events
def simulate_flow_events(profile_data):
    """Simulate events for a mock welcome flow."""
    flow_name = "Mock_Welcome_Flow"
    log(f"Simulating flow events for '{flow_name}'...")
    
    # We don't need to actually create the flow in Klaviyo
    # Just simulate the events that would be associated with it
    flow_id = f"mock-flow-{random.randint(10000, 99999)}"
    
    # Track events
    success_count = 0
    
    # Select a subset of profiles for flow events
    flow_profiles = random.sample(profile_data, min(15, len(profile_data)))
    
    for profile in flow_profiles:
        profile_id = profile["id"]
        
        # Flow Email Sent
        timestamp = random_past_date()
        properties = {
            "flow_name": flow_name,
            "flow_id": flow_id,
            "message_id": f"mock-message-{random.randint(1000, 9999)}"
        }
        
        success = track_event("Flow Email Sent", profile_id, properties, timestamp)
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
            
            success = track_event("Flow Email Opened", profile_id, properties, timestamp)
            if success:
                success_count += 1
            time.sleep(0.2)  # Rate limiting
    
    log(f"Successfully simulated {success_count} flow events")
    return success_count

# Step 8: Simulate purchase behavior
def simulate_purchases(profile_data):
    """Simulate purchase events for a subset of profiles."""
    log("Simulating purchase events...")
    
    success_count = 0
    
    # Select a subset of profiles for purchases
    n = min(random.randint(5, 7), len(profile_data))
    buyers = random.sample(profile_data, n)
    
    for profile in buyers:
        profile_id = profile["id"]
        
        # Generate 1-3 items for this order
        items = []
        for _ in range(random.randint(1, 3)):
            items.append({
                "ProductName": faker.word().title(),
                "Price": round(random.uniform(10, 200), 2),
                "Quantity": random.randint(1, 3),
                "ProductID": f"MOCK-{random.randint(10000, 99999)}"
            })
        
        # Calculate order total
        total = sum(item["Price"] * item["Quantity"] for item in items)
        
        # Create order properties
        timestamp = random_past_date()
        properties = {
            "OrderId": f"MOCK-ORDER-{random.randint(10000, 99999)}",
            "Total": total,
            "ItemCount": len(items),
            "Items": items,
            "Currency": "USD",
            "IsMock": True
        }
        
        # Track the purchase event
        success = track_event("Placed Order", profile_id, properties, timestamp)
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
    profile_data = add_profiles_to_list(list_id, profiles)
    if not profile_data:
        log("Failed to add profiles to list, aborting", "ERROR")
        return False
    
    # Step 3: Simulate campaign events
    campaign_events, campaign_ids = simulate_campaign_events(
        profile_data, 
        ["Mock_Welcome_Campaign", "Mock_Product_Update"]
    )
    
    # Step 4: Simulate flow events
    flow_events = simulate_flow_events(profile_data)
    
    # Step 5: Simulate purchase events
    purchase_events = simulate_purchases(profile_data)
    
    # Summary
    total_time = int(time.time() - start_time)
    log(f"\n=== MOCK DATA GENERATION COMPLETE ===")
    log(f"Created list '{list_id}' with {len(profile_data)} profiles")
    log(f"Created campaigns: {', '.join(campaign_ids.keys())}")
    log(f"Generated {campaign_events} campaign events")
    log(f"Generated {flow_events} flow events")
    log(f"Generated {purchase_events} purchase events")
    log(f"Total execution time: {total_time} seconds")
    
    log("\nVerify this data in your Klaviyo account at:")
    log("https://www.klaviyo.com/dashboard")
    
    return True

if __name__ == "__main__":
    run()
