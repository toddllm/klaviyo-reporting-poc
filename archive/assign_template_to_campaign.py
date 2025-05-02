#!/usr/bin/env python3
"""
Assign a template to all messages in a given Klaviyo campaign.
Usage: python assign_template_to_campaign.py <campaign_id> <template_id>
"""
import requests
import sys
import json

# Load API key
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
    print(f"[ASSIGN_TEMPLATE] {message}")

def get_campaign_messages(campaign_id):
    """Get all message IDs belonging to a campaign."""
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        response_data = r.json()
        messages = response_data.get("data", [])
        message_ids = [msg.get("id") for msg in messages]
        log(f"Found message IDs: {message_ids}")
        return message_ids
    except Exception as e:
        log(f"Error getting campaign messages: {e}")
        return []

def assign_template(message_id, template_id):
    """Assign a template to a campaign message."""
    url = f"{BASE_URL}/campaign-messages/{message_id}"
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
    try:
        r = requests.patch(url, headers=HEADERS, json=payload)
        log(f"Assigning template: PATCH {url} => {r.status_code}")
        if r.status_code < 400:
            log(f"SUCCESS: Assigned template {template_id} to message {message_id}")
            return True
        else:
            log(f"FAILED: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        log(f"Exception during template assignment: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python assign_template_to_campaign.py <campaign_id> <template_id>")
        sys.exit(1)
    campaign_id = sys.argv[1]
    template_id = sys.argv[2]
    log(f"Assigning template {template_id} to all messages in campaign {campaign_id}")
    message_ids = get_campaign_messages(campaign_id)
    if not message_ids:
        log("No messages found in campaign. Exiting.")
        sys.exit(1)
    success_count = 0
    for message_id in message_ids:
        if assign_template(message_id, template_id):
            success_count += 1
    log(f"Finished. Successfully assigned template to {success_count}/{len(message_ids)} messages.")

if __name__ == "__main__":
    main()
