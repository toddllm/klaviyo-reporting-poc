#!/usr/bin/env python3
"""
Wrapper script to create a campaign, fetch its message IDs, and assign a template to all messages.
Usage: python klaviyo_campaign_full_workflow.py <campaign_name> <template_name>
"""
import requests
import sys
import json
import time

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
    print(f"[FULL_WORKFLOW] {message}")

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

def get_or_create_template(template_name):
    url = f"{BASE_URL}/templates"
    headers_get = HEADERS.copy()
    headers_get.pop("Content-Type", None)
    r = requests.get(url, headers=headers_get)
    r.raise_for_status()
    for t in r.json().get("data", []):
        if t.get("attributes", {}).get("name") == template_name:
            return t.get("id")
    # If not found, create one
    headers_post = HEADERS.copy()
    payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": template_name,
                "editor_type": "CODE",
                "html": "<html><body><h1>Hello {{ first_name|default:'Friend' }}</h1></body></html>"
            }
        }
    }
    r2 = requests.post(url, headers=headers_post, json=payload)
    r2.raise_for_status()
    return r2.json().get("data", {}).get("id")

def create_campaign(campaign_name, list_id):
    url = f"{BASE_URL}/campaigns/"
    headers = HEADERS.copy()
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "audiences": {
                    "included": [{
                        "id": f"list-{list_id}",
                        "type": "dynamic-segment"
                    }],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "send_time": (time.strftime('%Y-%m-%dT%H:%M:%S+00:00'))
                    }
                }
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code not in (200, 201):
        log(f"Error creating campaign: {r.status_code} {r.text}")
        return None
    campaign_id = r.json()["data"]["id"]
    log(f"Created campaign '{campaign_name}' with ID: {campaign_id}")
    return campaign_id

def get_campaign_messages(campaign_id):
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    messages = r.json().get("data", [])
    return [msg.get("id") for msg in messages]

def assign_template(message_id, template_id):
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
    r = requests.patch(url, headers=HEADERS, json=payload)
    if r.status_code < 400:
        log(f"Assigned template {template_id} to message {message_id}")
        return True
    else:
        log(f"FAILED: {r.status_code} - {r.text}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python klaviyo_campaign_full_workflow.py <campaign_name> <template_name>")
        sys.exit(1)
    campaign_name = sys.argv[1]
    template_name = sys.argv[2]
    list_name = "Mock_Reporting_List"
    log(f"Getting list ID for '{list_name}'")
    list_id = get_list_id(list_name)
    if not list_id:
        log(f"List '{list_name}' not found. Aborting.")
        sys.exit(1)
    log(f"Getting or creating template '{template_name}'")
    template_id = get_or_create_template(template_name)
    if not template_id:
        log(f"Could not get or create template '{template_name}'. Aborting.")
        sys.exit(1)
    log(f"Creating campaign '{campaign_name}'")
    campaign_id = create_campaign(campaign_name, list_id)
    if not campaign_id:
        log("Failed to create campaign. Aborting.")
        sys.exit(1)
    log(f"Fetching campaign messages for campaign {campaign_id}")
    message_ids = get_campaign_messages(campaign_id)
    if not message_ids:
        log("No messages found in campaign. Aborting.")
        sys.exit(1)
    log(f"Assigning template to all campaign messages...")
    for message_id in message_ids:
        assign_template(message_id, template_id)
    log("Workflow complete.")

if __name__ == "__main__":
    main()
