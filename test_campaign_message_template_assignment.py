#!/usr/bin/env python3
"""
Stepwise test harness for Klaviyo campaign creation, message fetch, and template assignment.
This script does NOT run the full mock data workflow and will not create unnecessary test data.
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# Load API key
with open("private-api-key.txt", "r") as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "revision": "2025-04-15",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def log(msg):
    print(f"[TEST] {msg}")

def get_list_id(list_name):
    url = f"{BASE_URL}/lists/"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    for l in r.json().get("data", []):
        if l.get("attributes", {}).get("name") == list_name:
            return l.get("id")
    return None

def create_campaign(name, list_id):
    url = f"{BASE_URL}/campaigns/"
    headers = HEADERS.copy()
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": name,
                "audiences": {
                    "included": [list_id],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "datetime": (datetime.now() + timedelta(days=1)).isoformat()
                },
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "definition": {
                                    "channel": "email",
                                    "content": {
                                        "subject": f"[TEST] {name}",
                                        "preview_text": "Test campaign from API",
                                        "from_email": "clara@clarathecoach.com",
                                        "from_label": "CTC"
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code not in (200, 201):
        log(f"Error creating campaign: {r.status_code} {r.text}")
        return None
    campaign_id = r.json()["data"]["id"]
    log(f"Created campaign '{name}' with ID: {campaign_id}")
    return campaign_id

def get_campaign_messages(campaign_id):
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log(f"Error fetching messages: {r.status_code} {r.text}")
        return []
    messages = r.json().get("data", [])
    message_ids = [msg.get("id") for msg in messages]
    log(f"Found message IDs: {message_ids}")
    return message_ids

def get_or_create_template(template_name):
    url = f"{BASE_URL}/templates"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log(f"Error fetching templates: {r.status_code} {r.text}")
        return None
    for t in r.json().get("data", []):
        if t.get("attributes", {}).get("name") == template_name:
            template_id = t.get("id")
            log(f"Found existing template '{template_name}' with ID: {template_id}")
            return template_id
    # Create new template if not found
    headers["Content-Type"] = "application/vnd.api+json"
    payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": template_name,
                "editor_type": "CODE",
                "html": "<html><body><h1>Hello {{ first_name }}</h1><p>This is a test template.</p></body></html>"
            }
        }
    }
    r2 = requests.post(url, headers=headers, json=payload)
    if r2.status_code not in (200, 201):
        log(f"Error creating template: {r2.status_code} {r2.text}")
        return None
    template_id = r2.json().get("data", {}).get("id")
    log(f"Created new template '{template_name}' with ID: {template_id}")
    return template_id

def assign_template(message_id, template_id):
    # Fetch message details
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code >= 400:
        log(f"Error fetching message details: {r.status_code} - {r.text}")
        return False
    message_data = r.json()
    definition = message_data.get("data", {}).get("attributes", {}).get("definition", {})
    if not definition or "content" not in definition:
        log("Cannot find valid definition in message")
        return False
    # Set template_id in content
    definition["content"]["template_id"] = template_id
    # Patch message with new definition
    patch_headers = HEADERS.copy()
    payload = {
        "data": {
            "type": "campaign-message",
            "id": message_id,
            "attributes": {
                "definition": definition
            }
        }
    }
    r2 = requests.patch(url, headers=patch_headers, json=payload)
    if r2.status_code < 300:
        log(f"Assigned template {template_id} to message {message_id}")
        return True
    else:
        log(f"FAILED: {r2.status_code} - {r2.text}")
        return False

def get_message_details(message_id):
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code >= 400:
        log(f"Error: {r.status_code} - {r.text}")
        return None
    message_data = r.json()
    log(f"Message details: {json.dumps(message_data, indent=2)}")
    return message_data

def main():
    list_name = "Mock_Reporting_List"
    template_name = f"Test_Template_{datetime.now().strftime('%Y%m%d_%H%M')}"
    campaign_name = f"Test_Campaign_{datetime.now().strftime('%Y%m%d_%H%M')}"

    log(f"Step 1: Get list ID for '{list_name}'")
    list_id = get_list_id(list_name)
    if not list_id:
        log(f"List '{list_name}' not found. ABORTING.")
        sys.exit(1)

    log(f"Step 2: Create campaign '{campaign_name}'")
    campaign_id = create_campaign(campaign_name, list_id)
    if not campaign_id:
        log("Failed to create campaign. ABORTING.")
        sys.exit(1)

    log(f"Step 3: Fetch campaign message IDs")
    message_ids = get_campaign_messages(campaign_id)
    if not message_ids:
        log("No messages found in campaign. ABORTING.")
        sys.exit(1)
    message_id = message_ids[0]

    log(f"Step 4: Get or create template '{template_name}'")
    template_id = get_or_create_template(template_name)
    if not template_id:
        log("Failed to get or create template. ABORTING.")
        sys.exit(1)

    log(f"Step 5: Assign template to campaign message")
    ok = assign_template(message_id, template_id)
    if not ok:
        log("Failed to assign template to message. ABORTING.")
        sys.exit(1)

    log(f"Step 6: Fetch and verify message details")
    details = get_message_details(message_id)
    if details:
        assigned_id = (details.get("data", {})
                            .get("relationships", {})
                            .get("template", {})
                            .get("data", {})
                            .get("id"))
        if assigned_id == template_id:
            log(f"SUCCESS: Template assignment verified!")
        else:
            log(f"WARNING: Template ID mismatch in message details.")
    log("Test script complete.")

if __name__ == "__main__":
    main()
