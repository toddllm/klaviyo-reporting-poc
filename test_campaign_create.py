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
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def log(message, level="INFO"):
    """Print a log message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level}: {message}")

def get_first_list():
    """Get the first list from the account for testing purposes."""
    log("Fetching available lists...")
    
    url = f"{BASE_URL}/lists/"
    headers = HEADERS.copy()
    headers["revision"] = "2025-04-15"
    
    response = requests.get(url, headers=headers)
    
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

def test_campaign_creation():
    """Test campaign creation with various payload structures to find what works."""
    # Get a list for audience targeting
    list_id = get_first_list()
    if not list_id:
        log("Cannot proceed without a list", "ERROR")
        return
    
    log("Attempting to create a test campaign...")
    
    url = f"{BASE_URL}/campaigns/"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    
    # Send time for campaign
    send_time = (datetime.now() + timedelta(days=1)).isoformat()
    
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": "API_TEST_CAMPAIGN",
                "audiences": {
                    "included": [{
                        "type": "segment",
                        "data": {
                            "type": "list",
                            "id": list_id
                        }
                    }],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": send_time
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
                                    "subject": "[TEST] API Test Campaign",
                                    "preview_text": "Test campaign from API",
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
    
    # Print the payload for debugging
    log("Using payload:")
    print(json.dumps(payload, indent=2))
    
    # Make the API call
    response = requests.post(url, headers=headers, json=payload)
    
    # Handle the response
    if response.status_code in (200, 201):
        campaign_id = response.json()["data"]["id"]
        log(f"Successfully created campaign with ID: {campaign_id}")
        return campaign_id
    else:
        log(f"Error creating campaign: {response.status_code} {response.text}", "ERROR")
        return None

if __name__ == "__main__":
    test_campaign_creation()
