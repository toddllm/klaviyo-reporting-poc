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
    "revision": "2025-04-15",  # Try an older API version
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def log(message):
    print(f"[DEBUG] {message}")

def get_message_info(message_id):
    """Get information about a campaign message"""
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    headers = HEADERS.copy()
    
    response = requests.get(url, headers=headers)
    log(f"Message info response: {response.status_code}")
    if response.status_code < 300:
        return response.json()
    return None

def try_update_message(message_id, template_id):
    """Try to update a campaign message with a template"""
    log(f"Attempting to update message {message_id} with template {template_id}")
    
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/vnd.api+json"
    
    # Create a very simple payload
    payload = {
        "data": {
            "type": "campaign-message",
            "id": message_id,
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
    
    log(f"Sending payload to update message: {json.dumps(payload, indent=2)}")
    response = requests.patch(url, headers=headers, json=payload)
    log(f"Update response: {response.status_code} - {response.text}")
    return response.status_code < 300

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python debug_template_v3.py <message_id> <template_id>")
        sys.exit(1)
    
    message_id = sys.argv[1]
    template_id = sys.argv[2]
    
    # First get message info
    log(f"Getting info for message: {message_id}")
    message_info = get_message_info(message_id)
    if message_info:
        log(f"Message info: {json.dumps(message_info, indent=2)}")
    
    # Try to update the message with template
    if try_update_message(message_id, template_id):
        log("SUCCESS: Template assigned!")
    else:
        log("FAILED: Could not assign template")
