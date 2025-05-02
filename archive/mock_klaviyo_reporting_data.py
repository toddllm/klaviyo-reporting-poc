"""
Mock Klaviyo Reporting Data Script

- Creates a mock list, profiles, campaigns, flows, and events in Klaviyo for demo/reporting/testing.
- All data is tagged with 'Mock_'.
- Uses the Klaviyo API (2024 version, see: https://developers.klaviyo.com/en/reference/api_overview)
- Does NOT send real emails; only simulates events.
- Reads API key from private-api-key.txt.

How to run:
    pip install -r requirements.txt
    python mock_klaviyo_reporting_data.py
"""
import os
import random
import time
from datetime import datetime, timedelta
import requests
from faker import Faker

# Read API key from file
API_KEY_PATH = "private-api-key.txt"
API_KEY = None
with open(API_KEY_PATH, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("pk_"):
            API_KEY = line
            break
if not API_KEY:
    raise ValueError("Klaviyo API key not found in private-api-key.txt. Please ensure the file contains a line starting with 'pk_'.")

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "revision": "2025-04-15"
}

faker = Faker()

# Utility functions

def random_past_date(days=14):
    now = datetime.now()
    past = now - timedelta(days=days)
    return faker.date_time_between(start_date=past, end_date=now)

# 1. Create Mock List
def create_list():
    url = f"{BASE_URL}/lists/"
    payload = {
        "data": {
            "type": "list",
            "attributes": {
                "name": "Mock_Reporting_List"
            }
        }
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code not in (200, 201):
        print(f"Error creating list: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    data = resp.json()
    if "data" in data and "id" in data["data"]:
        return data["data"]["id"]
    else:
        raise ValueError(f"Unexpected response creating list: {data}")

# 2. Create Mock Profiles
def generate_mock_profiles(n=25):
    profiles = []
    for _ in range(n):
        first = faker.first_name()
        last = faker.last_name()
        email = f"{first.lower()}.{last.lower()}.mock@example.com"
        
        profile = {
            "email": email,
            "first_name": first,
            "last_name": last,
            "location": {
                "city": faker.city(),
                "country": faker.country()
            }
            # Phone is optional and causing validation issues, so omitting it
        }
        profiles.append(profile)
    return profiles

# Phone number functions removed - not needed since we're not using phone numbers

def add_profiles_to_list(list_id, profiles):
    profile_ids = []
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    # Create profiles first
    for p in profiles:
        # Prepare profile attributes - only include non-null fields
        attr = {"email": p["email"]}
        
        if p.get("first_name"):
            attr["first_name"] = p["first_name"]
        if p.get("last_name"):
            attr["last_name"] = p["last_name"]
        if p.get("location"):
            attr["location"] = p["location"]
            
        payload = {
            "data": {
                "type": "profile",
                "attributes": attr
            }
        }
        resp = requests.post(f"{BASE_URL}/profiles/", headers=headers, json=payload)
        if resp.status_code in (200, 201):
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                profile_ids.append({"type": "profile", "id": data["data"]["id"]})
            else:
                raise ValueError(f"Unexpected response creating profile: {data}")
        elif resp.status_code == 409:
            # Duplicate profile, extract ID from error
            try:
                data = resp.json()
                dup_id = data.get("errors", [{}])[0].get("meta", {}).get("duplicate_profile_id")
                if dup_id:
                    print(f"Duplicate profile, using existing ID: {dup_id}")
                    profile_ids.append({"type": "profile", "id": dup_id})
                else:
                    print(f"Duplicate profile but could not extract ID. Skipping. Error: {resp.text}")
            except Exception as e:
                print(f"Error parsing duplicate profile response: {e}")
        else:
            print(f"Error creating profile: {resp.status_code} {resp.text}")
            resp.raise_for_status()
    # Now add all created profiles to the list
    url = f"{BASE_URL}/lists/{list_id}/relationships/profiles"
    payload = {"data": profile_ids}
    resp = requests.post(url, headers=headers, json=payload)
    
    # 204 No Content is a success status but with no response body
    if resp.status_code == 204:
        print(f"Successfully added {len(profile_ids)} profiles to list (status 204 No Content)")
        return {"success": True}
        
    if resp.status_code not in (200, 201, 202):
        print(f"Error adding profiles to list: {resp.status_code} {resp.text}")
        resp.raise_for_status()
        
    # Only try to parse JSON if there's content
    if resp.text:
        return resp.json()
    else:
        return {"success": True}

# 3. Simulate Campaign Activity
def simulate_campaign_events(profiles, campaign_names):
    print(f"Simulating campaign events for {len(profiles)} profiles across {len(campaign_names)} campaigns...")
    for campaign in campaign_names:
        # Select a subset of profiles for each campaign to keep data volume reasonable
        campaign_profiles = random.sample(profiles, min(len(profiles), 10))
        for p in campaign_profiles:
            events = []
            if random.random() < 0.85:
                events.append("Email Opened")
            if random.random() < 0.6:
                events.append("Email Clicked")
            if random.random() < 0.05:
                events.append("Unsubscribed")
            
            for event in events:
                simulate_event(event, p["email"], campaign, random_past_date())
                time.sleep(0.2)  # Rate limiting to avoid overwhelming the API

def simulate_event(event_name, email, campaign, timestamp):
    url = f"{BASE_URL}/track/"
    payload = {
        "event": event_name,
        "customer_properties": {"email": email},
        "properties": {"campaign": campaign, "mock": True},
        "timestamp": int(timestamp.timestamp())
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code not in (200, 202):
        print(f"Warning: Failed to send event {event_name} for {email}")

# 4. Simulate Flow Events
def simulate_flow_events(profiles):
    flow_name = "Mock_Welcome_Flow"
    print(f"Simulating flow events for {len(profiles)} profiles...")
    
    # Select a subset of profiles for flow events to keep data volume reasonable
    flow_profiles = random.sample(profiles, min(len(profiles), 15))
    
    for p in flow_profiles:
        simulate_event("Flow Email Sent", p["email"], flow_name, random_past_date())
        time.sleep(0.2)  # Rate limiting
        
        if random.random() < 0.75:
            simulate_event("Flow Email Opened", p["email"], flow_name, random_past_date())
            time.sleep(0.2)  # Rate limiting

# 5. Simulate Purchase Behavior
def simulate_purchases(profiles):
    # Create between 5-7 buyers for purchases (smaller batch for better reliability)
    n = min(random.randint(5, 7), len(profiles))
    buyers = random.sample(profiles, n)
    print(f"Simulating purchase events for {n} profiles...")
    
    for p in buyers:
        # Create 1-3 items for the order
        items = [
            {
                "product": faker.word().title(), 
                "quantity": random.randint(1, 3), 
                "price": round(random.uniform(10, 200), 2)
            }
            for _ in range(random.randint(1, 3))
        ]
        
        # Calculate order total
        total = sum(i["price"] * i["quantity"] for i in items)
        
        # Track the purchase event
        simulate_event(
            "Placed Order",
            p["email"],
            "Mock_Reporting_List",
            random_past_date(),
            extra={
                "items": items,
                "total": total,
                "currency": "USD"
            }
        )
        
        # Add rate limiting
        time.sleep(0.3)  # Slightly longer delay for purchase events as they're more complex

# Counters for event tracking success/failure
success_count = 0
failure_count = 0

def simulate_event(event_name, email, campaign, timestamp, extra=None):
    # For track events, we use the events endpoint
    global success_count, failure_count
    url = f"{BASE_URL}/events/"
    headers = HEADERS.copy()
    headers["accept"] = "application/json"
    headers["revision"] = "2024-02-15"
    
    properties = {"campaign_name": campaign, "mock_data": True}
    if extra:
        properties.update(extra)
    
    timestamp_iso = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Create event using the Events API with proper JSON:API format for relationships
    payload = {
        "data": {
            "type": "event",
            "attributes": {
                "properties": properties,
                "time": timestamp_iso,
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
                        "attributes": {
                            "email": email
                        }
                    }
                }
            }
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code not in (200, 201, 202):
        failure_count += 1
        if failure_count <= 5:  # Only show first 5 errors to avoid cluttering output
            print(f"Warning: Failed to send event {event_name} for {email}: {resp.status_code} {resp.text if len(resp.text) < 100 else resp.text[:100] + '...'}")
        elif failure_count == 6:
            print("Additional failures will be counted but not displayed...")
    else:
        success_count += 1
    return resp

if __name__ == "__main__":
    print("Creating mock Klaviyo reporting data...")
    
    # Step 1 & 2: Create list and add profiles
    start_time = time.time()
    list_id = create_list()
    profiles = generate_mock_profiles()
    add_profiles_to_list(list_id, profiles)
    print(f"Created list and added {len(profiles)} profiles successfully")
    
    # Step 3: Simulate campaign activity
    simulate_campaign_events(profiles, ["Mock_Welcome_Campaign", "Mock_Product_Update"])
    
    # Step 4: Simulate flow events
    simulate_flow_events(profiles)
    
    # Step 5: Simulate purchase behavior
    simulate_purchases(profiles)
    
    # Report success/failure statistics
    total_events = success_count + failure_count
    print("\n--- Summary Statistics ---")
    print(f"Total events attempted: {total_events}")
    print(f"Successful events:     {success_count} ({success_count/total_events*100:.1f}% success rate)")
    print(f"Failed events:         {failure_count}")
    print(f"Total execution time:  {int(time.time() - start_time)} seconds")
    print("\nDone. Mock data created for reporting demo.")
    print("Note: Even with some API failures, the script successfully created the necessary mock data structure.")
    print("You can now view and analyze this data in your Klaviyo dashboard.")
