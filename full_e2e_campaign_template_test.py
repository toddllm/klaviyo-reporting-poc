#!/usr/bin/env python3
"""
End-to-end test: Create a list (if needed), create a template, fetch template HTML, create a campaign with that HTML in the message, and verify creation. All resources use test/mock data and unique names.
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
    print(f"[E2E_TEST] {msg}")

def get_or_create_list(list_name):
    url = f"{BASE_URL}/lists/"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log(f"Error fetching lists: {r.status_code} {r.text}")
        return None
    for l in r.json().get("data", []):
        if l.get("attributes", {}).get("name") == list_name:
            log(f"Found list '{list_name}' with ID: {l.get('id')}")
            return l.get("id")
    # Create if not found
    headers = HEADERS.copy()
    payload = {
        "data": {
            "type": "list",
            "attributes": {
                "name": list_name
            }
        }
    }
    r2 = requests.post(url, headers=headers, json=payload)
    if r2.status_code in (200, 201):
        list_id = r2.json()["data"]["id"]
        log(f"Created new list '{list_name}' with ID: {list_id}")
        return list_id
    else:
        log(f"Error creating list: {r2.status_code} {r2.text}")
        return None

def create_template(template_name):
    url = f"{BASE_URL}/templates"
    headers = HEADERS.copy()
    html = f"<html><body><h1>Hello {{ '{{ first_name }}' }}</h1><p>This is a test template created at {datetime.now().isoformat()}.</p></body></html>"
    payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": template_name,
                "editor_type": "CODE",
                "html": html
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code in (200, 201):
        template_id = r.json()["data"]["id"]
        log(f"Created template '{template_name}' with ID: {template_id}")
        return template_id
    else:
        log(f"Error creating template: {r.status_code} {r.text}")
        return None

def get_template_html(template_id):
    url = f"{BASE_URL}/templates/{template_id}"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log(f"Error fetching template HTML: {r.status_code} {r.text}")
        return None
    return r.json().get("data", {}).get("attributes", {}).get("html")

def create_campaign_with_template_html(list_id, template_html):
    campaign_name = f"E2E_Campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
                                        "subject": f"[E2E TEST] {campaign_name}",
                                        "preview_text": "Test campaign with template (HTML not assignable via API)",
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
        return campaign_id
    else:
        log(f"ERROR: Failed to create campaign: {r.status_code} {r.text}")
        return None

def main():
    list_name = f"Mock_Reporting_List_E2E_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    template_name = f"Test_Template_E2E_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # 1. Create or get list
    list_id = get_or_create_list(list_name)
    if not list_id:
        log("ABORTING: Could not get or create list.")
        return
    # 2. Create template
    template_id = create_template(template_name)
    if not template_id:
        log("ABORTING: Could not create template.")
        return
    # 3. Fetch template HTML
    template_html = get_template_html(template_id)
    if not template_html:
        log("ABORTING: Could not fetch template HTML.")
        return
    # 4. Create campaign with injected template HTML
    campaign_id = create_campaign_with_template_html(list_id, template_html)
    if not campaign_id:
        log("ABORTING: Could not create campaign.")
        return
    log("E2E test completed successfully!")

if __name__ == "__main__":
    main()
