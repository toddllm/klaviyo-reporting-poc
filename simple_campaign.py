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

def get_list_by_name(list_name):
    """Get a list by its name, returns the first match."""
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code} {response.text}", "ERROR")
        return None
    
    lists = response.json().get("data", [])
    
    # Find the first list that matches the name
    for list_item in lists:
        if list_item.get("attributes", {}).get("name") == list_name:
            list_id = list_item.get("id")
            log(f"Found list '{list_name}' with ID: {list_id}")
            return list_id
    
    log(f"No list found with name '{list_name}'", "WARNING")
    return None

def create_campaign():
    """Create a simple email campaign."""
    campaign_name = f"Simple_Campaign_{datetime.now().strftime('%H%M%S')}"
    log(f"Creating campaign '{campaign_name}'...")
    
    url = f"{BASE_URL}/campaigns/"
    
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "channel": "email",
                                "label": "Main Message",
                                "content": {
                                    "subject": f"[TEST] {campaign_name}",
                                    "preview_text": "Test campaign for debugging",
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
    
    # Print the full payload
    log("Using payload:")
    print(json.dumps(payload, indent=2))
    
    # Make the API call
    response = requests.post(url, headers=HEADERS, json=payload)
    
    # Handle the response
    if response.status_code in (200, 201):
        campaign_data = response.json().get("data", {})
        campaign_id = campaign_data.get("id")
        log(f"SUCCESS: Created campaign '{campaign_name}' with ID: {campaign_id}")
        return campaign_id
    else:
        log(f"ERROR: Failed to create campaign: {response.status_code} {response.text}", "ERROR")
        return None

def main():
    """Create a simple campaign."""
    campaign_id = create_campaign()
    if campaign_id:
        log(f"Successfully created campaign with ID: {campaign_id}")
        log("You can now check this campaign in the Klaviyo dashboard")
    else:
        log("Failed to create campaign", "ERROR")

if __name__ == "__main__":
    main()
