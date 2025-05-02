#!/usr/bin/env python3
"""
Test: Create a Klaviyo campaign and inject template HTML into the campaign-message at creation time.
This script runs in isolation from the full workflow.
"""
import requests
import json
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
    print(f"[ISOLATE_TEST] {msg}")

def get_template_html(template_id):
    url = f"{BASE_URL}/templates/{template_id}"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log(f"Error fetching template HTML: {r.status_code} {r.text}")
        return None
    return r.json().get("data", {}).get("attributes", {}).get("html")

def assign_template_to_message(message_id, template_id):
    url = f"{BASE_URL}/campaign-message-assign-template"
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
    headers = HEADERS.copy()
    headers["Accept"] = "application/vnd.api+json"
    headers["Content-Type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code in (200, 201, 202):
        log(f"SUCCESS: Assigned template {template_id} to message {message_id}")
    else:
        log(f"ERROR: Failed to assign template {template_id} to message {message_id}: {r.status_code} {r.text}")

def create_campaign_with_template_html(list_id, template_id):
    campaign_name = f"Isolated_Campaign_{datetime.now().strftime('%Y%m%d_%H%M')}"
    send_time = (datetime.now() + timedelta(days=1)).isoformat()
    url = f"{BASE_URL}/campaigns/"
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "audiences": {
                    "included": [list_id],
                    "excluded": []
                },
                "send_strategy": {
                    "method": "static",
                    "datetime": send_time
                },
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "definition": {
                                    "channel": "email",
                                    "content": {
                                        "subject": f"[ISOLATE TEST] {campaign_name}",
                                        "preview_text": "Test campaign with template HTML injected",
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
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        campaign_id = r.json()["data"]["id"]
        log(f"SUCCESS: Created campaign '{campaign_name}' with ID: {campaign_id}")
        # Fetch campaign message IDs
        msg_url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
        msg_resp = requests.get(msg_url, headers=HEADERS)
        if msg_resp.status_code == 200:
            msg_data = msg_resp.json().get("data", [])
            for msg in msg_data:
                message_id = msg.get("id")
                if message_id:
                    assign_template_to_message(message_id, template_id)
        else:
            log(f"ERROR: Could not fetch campaign messages for campaign {campaign_id}")
        return campaign_id
    else:
        log(f"ERROR: Failed to create campaign: {r.status_code} {r.text}")
        return None

def get_list_id(list_name):
    url = f"{BASE_URL}/lists/"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log(f"Error fetching lists: {r.status_code} {r.text}")
        return None
    for l in r.json().get("data", []):
        if l.get("attributes", {}).get("name") == list_name:
            return l.get("id")
    return None

def get_or_create_template():
    url = f"{BASE_URL}/templates/?filter=equals(name,'Mock_Automation_Template')"
    headers = HEADERS.copy()
    headers["Accept"] = "application/vnd.api+json"
    headers["Content-Type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and r.json()["data"]:
        return r.json()["data"][0]["id"]
    # template not found ➜ create
    payload = {
      "data": {
        "type": "template",
        "attributes": {
          "name": "Mock_Automation_Template",
          "editor_type": "CODE",
          "html": "<html><body><h1>{{ first_name|default:'Friend' }}, welcome!</h1></body></html>"
        }
      }
    }
    resp2 = requests.post(f"{BASE_URL}/templates", headers=headers, json=payload)
    resp2.raise_for_status()
    return resp2.json()["data"]["id"]

def main():
    list_name = "Mock_Reporting_List"
    template_id = get_or_create_template()
    list_id = get_list_id(list_name)
    if not list_id:
        log(f"List '{list_name}' not found. ABORTING.")
        return
    create_campaign_with_template_html(list_id, template_id)

if __name__ == "__main__":
    main()
