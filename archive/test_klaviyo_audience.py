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

def get_lists():
    """Get all lists from the Klaviyo account."""
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code} {response.text}", "ERROR")
        return []
    
    lists = response.json().get("data", [])
    return lists

def get_segments():
    """Get all segments from the Klaviyo account."""
    url = f"{BASE_URL}/segments/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching segments: {response.status_code} {response.text}", "ERROR")
        return []
    
    segments = response.json().get("data", [])
    return segments

def test_create_campaign(audience_format):
    """Test creating a campaign with a specific audience format."""
    campaign_name = f"Audience_Test_{datetime.now().strftime('%H%M%S')}"
    log(f"Testing campaign creation with audience format: {audience_format}")
    
    url = f"{BASE_URL}/campaigns/"
    
    # Tomorrow's date in ISO format
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "audiences": {
                    "included": [audience_format],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": tomorrow
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
                                    "subject": f"[TEST] {campaign_name}",
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
    response = requests.post(url, headers=HEADERS, json=payload)
    
    # Handle the response
    if response.status_code in (200, 201):
        campaign_id = response.json()["data"]["id"]
        log(f"SUCCESS: Created campaign with ID: {campaign_id}")
        return True
    else:
        log(f"FAILED: Error creating campaign: {response.status_code} {response.text}", "ERROR")
        return False

def main():
    """Test different audience formats until one works."""
    # Get available lists
    lists = get_lists()
    if not lists:
        log("No lists found. Cannot proceed.", "ERROR")
        return
    
    # Use the first list for testing
    list_id = lists[0]["id"]
    list_name = lists[0]["attributes"]["name"]
    log(f"Using list: {list_name} with ID: {list_id}")
    
    # Get available segments
    segments = get_segments()
    segment_id = None
    if segments:
        segment_id = segments[0]["id"]
        segment_name = segments[0]["attributes"]["name"]
        log(f"Using segment: {segment_name} with ID: {segment_id}")
    
    # Test different audience formats
    audience_formats = [
        # Format 1: Simple list reference
        {"type": "list", "id": list_id},
        
        # Format 2: List with segment type
        {"type": "segment", "id": f"list-{list_id}"},
        
        # Format 3: Using relationships format
        {"type": "relation", "data": {"type": "list", "id": list_id}},
        
        # Format 4: Using dynamic-segment format (if segments exist)
        {"type": "dynamic-segment", "id": f"list-{list_id}"}
    ]
    
    # Add segment if available
    if segment_id:
        audience_formats.append({"type": "segment", "id": segment_id})
    
    # Test each format
    for i, format in enumerate(audience_formats):
        log(f"Testing audience format #{i+1}: {format}")
        success = test_create_campaign(format)
        if success:
            log(f"FOUND WORKING FORMAT: {format}")
            break
        log("Continuing to next format...\n")

if __name__ == "__main__":
    main()
