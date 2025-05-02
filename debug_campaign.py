#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime, timedelta

# Load API key
with open("private-api-key.txt", "r") as f:
    PRIVATE_KEY = f.read().strip()

# API Configuration
BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}",
    "revision": "2025-04-15"
}

def log(message, level="INFO"):
    """Print a log message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level}: {message}")

def get_first_list():
    """Get the first list from the account."""
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code} {response.text}", "ERROR")
        return None
    
    lists = response.json().get("data", [])
    if not lists:
        log("No lists found in the account", "ERROR")
        return None
    
    list_id = lists[0].get("id")
    list_name = lists[0].get("attributes", {}).get("name")
    log(f"Using list: {list_name} (ID: {list_id})")
    return list_id

def create_minimal_campaign():
    """Create a campaign with minimal required fields."""
    list_id = get_first_list()
    if not list_id:
        return None
    
    campaign_name = f"Debug_Campaign_{datetime.now().strftime('%H%M%S')}"
    log(f"Creating minimal campaign '{campaign_name}'...")
    
    url = f"{BASE_URL}/campaigns/"
    
    # Try with empty included array - the API docs suggest this should work
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "audiences": {
                    "included": [],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": (datetime.now() + timedelta(days=1)).isoformat()
                    }
                },
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "channel": "email",
                                "label": "Test Message",
                                "content": {
                                    "subject": "[TEST] Debug Campaign",
                                    "preview_text": "Test campaign",
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
    
    log("Using minimal payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code in (200, 201):
        campaign_id = response.json()["data"]["id"]
        log(f"Success! Created campaign with ID: {campaign_id}")
        return campaign_id
    else:
        log(f"Error creating campaign: {response.status_code} {response.text}", "ERROR")
    
    # If first attempt failed, try alternative method with list directly
    log("Trying alternative audience format...")
    
    payload["data"]["attributes"]["audiences"]["included"] = [{"type": "list", "id": list_id}]
    
    log("Using payload with direct list reference:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code in (200, 201):
        campaign_id = response.json()["data"]["id"]
        log(f"Success! Created campaign with ID: {campaign_id}")
        return campaign_id
    else:
        log(f"Error creating campaign: {response.status_code} {response.text}", "ERROR")
    
    # Try yet another format
    log("Trying another audience format...")
    
    payload["data"]["attributes"]["audiences"]["included"] = [{
        "type": "segment", 
        "id": list_id
    }]
    
    log("Using payload with segment reference:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code in (200, 201):
        campaign_id = response.json()["data"]["id"]
        log(f"Success! Created campaign with ID: {campaign_id}")
        return campaign_id
    else:
        log(f"Error creating campaign: {response.status_code} {response.text}", "ERROR")
        
    return None

if __name__ == "__main__":
    create_minimal_campaign()
