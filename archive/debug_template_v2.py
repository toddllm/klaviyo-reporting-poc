#!/usr/bin/env python3
"""
Debug script for investigating template assignment in Klaviyo API
"""
import requests
import json
import sys

# Load the API key
with open('private-api-key.txt', 'r') as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "revision": "2025-04-15",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def log(message):
    print(f"[DEBUG] {message}")

def try_create_message_template(message_id, template_id):
    """Create a campaign-message-template relationship"""
    log(f"Trying to create campaign-message-template for message {message_id} and template {template_id}")
    
    # This is a completely different approach - create a campaign-message-template object
    url = f"{BASE_URL}/campaigns"
    
    # First get available campaigns to see proper structure
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    
    # Get the message first
    message_url = f"{BASE_URL}/campaign-messages/{message_id}"
    response = requests.get(message_url, headers=headers)
    response.raise_for_status()
    
    # Get the campaign ID from the message
    campaign_id = response.json().get("data", {}).get("relationships", {}).get("campaign", {}).get("data", {}).get("id")
    if not campaign_id:
        log("Could not extract campaign ID from message")
        return False
    
    log(f"Retrieved campaign ID: {campaign_id}")
    
    # Now create a direct update of the campaign message to include the template in its JSON
    payload = {
        "data": {
            "type": "campaign",
            "id": campaign_id,
            "attributes": {
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message", 
                            "id": message_id,
                            "attributes": {
                                "template": {
                                    "id": template_id
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    
    log(f"Trying payload: {json.dumps(payload, indent=2)}")
    response = requests.patch(f"{BASE_URL}/campaigns/{campaign_id}", headers=HEADERS, json=payload)
    log(f"Response: {response.status_code} - {response.text}")
    
    return response.status_code < 300

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python debug_template_v2.py <message_id> <template_id>")
        sys.exit(1)
    
    message_id = sys.argv[1]
    template_id = sys.argv[2]
    
    if try_create_message_template(message_id, template_id):
        log("SUCCESS: Template assigned!")
    else:
        log("FAILED: Could not assign template")
