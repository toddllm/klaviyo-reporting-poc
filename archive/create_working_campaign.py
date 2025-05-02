#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime, timedelta

# Load API key
with open("private-api-key.txt", "r") as f:
    PRIVATE_KEY = f.read().strip()

# API Configuration
# TODO: Make API revision an environment variable to simplify future updates
API_REVISION = os.getenv("KLAVIYO_API_REVISION", "2025-04-15")
BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}",
    "revision": API_REVISION
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
    # Get an existing list for audience targeting
    list_id = get_list_by_name("Mock_Reporting_List")
    if not list_id:
        log("No list found to use as audience. Cannot create campaign.", "ERROR")
        return None
    
    campaign_name = f"Working_Campaign_{datetime.now().strftime('%H%M%S')}"
    log(f"Creating campaign '{campaign_name}'...")
    
    # Campaign endpoint
    url = f"{BASE_URL}/campaigns/"
    
    # Send time for tomorrow
    send_time = (datetime.now() + timedelta(days=1)).isoformat()
    
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "send_strategy": {
                    "method": "static",
                    "datetime": send_time
                },
                "audiences": {
                    "included": [list_id],
                    "excluded": []
                },
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "definition": {
                                    "channel": "email",
                                    "label": "Main Message",
                                    "content": {
                                        "subject": f"[TEST] {campaign_name}",
                                        "preview_text": "Test campaign for debugging",
                                        "from_email": "clara@clarathecoach.com",
                                        "from_label": "CTC",
                                        "reply_to_email": "clara@clarathecoach.com"
                                    }
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
        
        # Add list audience to the campaign
        add_audience_to_campaign(campaign_id, list_id)
        
        return campaign_id
    else:
        log(f"ERROR: Failed to create campaign: {response.status_code} {response.text}", "ERROR")
        return None

def add_audience_to_campaign(campaign_id, list_id):
    """Add a list audience to an existing campaign."""
    log(f"Adding list {list_id} to campaign {campaign_id}...")
    
    url = f"{BASE_URL}/campaign-audiences/"
    
    payload = {
        "data": {
            "type": "campaign-audience",
            "attributes": {
                "profile_source": "list",
                "include_source_id": list_id
            },
            "relationships": {
                "campaign": {
                    "data": {
                        "type": "campaign",
                        "id": campaign_id
                    }
                }
            }
        }
    }
    
    # Print the audience payload
    log("Using audience payload:")
    print(json.dumps(payload, indent=2))
    
    # Make the API call
    response = requests.post(url, headers=HEADERS, json=payload)
    
    # Handle the response
    if response.status_code in (200, 201):
        audience_id = response.json().get("data", {}).get("id")
        log(f"SUCCESS: Added audience to campaign, ID: {audience_id}")
        return True
    else:
        log(f"ERROR: Failed to add audience to campaign: {response.status_code} {response.text}", "ERROR")
        return False

def main():
    """Create a working campaign."""
    campaign_id = create_campaign()
    if campaign_id:
        log(f"Successfully created campaign with ID: {campaign_id}")
        log("You can now check this campaign in the Klaviyo dashboard")
    else:
        log("Failed to create campaign", "ERROR")

if __name__ == "__main__":
    main()
