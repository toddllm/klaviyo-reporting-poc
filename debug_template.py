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

def get_message_details(message_id):
    """Get detailed information about a campaign message"""
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)  # Remove content-type for GET
    
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        log(f"Error: {response.status_code} - {response.text}")
        return None
    
    message_data = response.json()
    log(f"Message details: {json.dumps(message_data, indent=2)}")
    return message_data

def try_template_assignment(message_id, template_id):
    """Try different ways to assign a template to a message"""
    log(f"Trying to assign template {template_id} to message {message_id}")
    
    # First, get the message details
    message_data = get_message_details(message_id)
    if not message_data:
        return False
    
    # Try updating the message definition
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    definition = message_data.get("data", {}).get("attributes", {}).get("definition", {})
    
    if not definition or "content" not in definition:
        log("Cannot find valid definition in message")
        return False
    
    # Update definition to set template_id
    definition["content"]["template_id"] = template_id
    
    payload = {
        "data": {
            "type": "campaign-message",
            "id": message_id,
            "attributes": {
                "definition": definition
            }
        }
    }
    
    log(f"Attempting to update message with payload: {json.dumps(payload, indent=2)}")
    response = requests.patch(url, headers=HEADERS, json=payload)
    log(f"Response: {response.status_code} - {response.text}")
    
    return response.status_code < 300

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python debug_template.py <message_id> <template_id>")
        sys.exit(1)
    
    message_id = sys.argv[1]
    template_id = sys.argv[2]
    
    if try_template_assignment(message_id, template_id):
        log("SUCCESS: Template assigned!")
    else:
        log("FAILED: Could not assign template")
