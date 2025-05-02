#!/usr/bin/env python3
"""
Test script to debug Klaviyo template assignment
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

def get_campaign_messages(campaign_id):
    """Get all messages belonging to a campaign."""
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        log(f"Got messages response: {r.status_code}")
        response_data = r.json()
        messages = response_data.get("data", [])
        if messages:
            message_id = messages[0].get("id")
            log(f"Found message ID: {message_id}")
            return message_id
        else:
            log("No messages found for campaign")
            return None
    except Exception as e:
        log(f"Error getting campaign messages: {e}")
        return None

def assign_template(message_id, template_id):
    """Try multiple approaches to assign a template to a message."""
    log(f"Trying to assign template {template_id} to message {message_id}")
    
    # Approach 1: update campaign message
    try:
        url = f"{BASE_URL}/campaign-messages/{message_id}"
        payload = {
            "data": {
                "type": "campaign-message",
                "id": message_id,
                "attributes": {},
                "relationships": {
                    "template": {
                        "data": {
                            "type": "template",
                            "id": template_id
                        }
                    }
                }
            }
        }
        log(f"Trying PATCH to {url}")
        r = requests.patch(url, headers=HEADERS, json=payload)
        log(f"Response: {r.status_code} - {r.text}")
        return r.status_code < 400
    except Exception as e:
        log(f"Error in approach 1: {e}")
    
    return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_template_assign.py <campaign_id> <template_id>")
        sys.exit(1)
    
    campaign_id = sys.argv[1]
    template_id = sys.argv[2]
    
    log(f"Testing with campaign {campaign_id} and template {template_id}")
    
    # Get message ID from campaign
    message_id = get_campaign_messages(campaign_id)
    if not message_id:
        log("Could not get message ID, exiting")
        sys.exit(1)
    
    # Try to assign template
    success = assign_template(message_id, template_id)
    if success:
        log("Successfully assigned template!")
    else:
        log("Failed to assign template")

if __name__ == "__main__":
    main()
