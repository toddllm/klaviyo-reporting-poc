#!/usr/bin/env python3
"""
Script to fix campaign creation in Klaviyo.
Based on the official API documentation.
"""
import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta

# Load the API key
with open('private-api-key.txt', 'r') as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

# Klaviyo list ID for campaign audience (set via env var)
AUDIENCE_ID = os.getenv("AUDIENCE_ID")
TEMPLATE_ID = os.getenv("TEMPLATE_ID")  # Klaviyo template ID for campaign messages

def log(message):
    """Log messages with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_or_create_template():
    url = f"{BASE_URL}/templates/?filter=equals(name,'Mock_Automation_Template')"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
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
          "editor": "code",
          "html": "<html><body><h1>{{ first_name|default:'Friend' }}, welcome!</h1></body></html>"
        }
      }
    }
    resp2 = requests.post(f"{BASE_URL}/templates", headers=headers, json=payload)
    resp2.raise_for_status()
    return resp2.json()["data"]["id"]

# Auto-create template if TEMPLATE_ID not set
if not TEMPLATE_ID:
    TEMPLATE_ID = get_or_create_template()
    if TEMPLATE_ID:
        os.environ["TEMPLATE_ID"] = TEMPLATE_ID
    else:
        log("TEMPLATE_ID not set and get_or_create_template failed; aborting.")
        sys.exit(1)

def create_campaign(name):
    """
    Create a campaign in Klaviyo with the correct API format.
    
    Args:
        name (str): Name of the campaign
    
    Returns:
        str: Campaign ID if successful, None otherwise
    """
    log(f"Creating campaign '{name}'...")
    
    # Determine audience_id: env var or auto-select 'Mock_Reporting_List'
    audience_id = AUDIENCE_ID
    if not audience_id:
        log("AUDIENCE_ID not set; fetching lists and selecting 'Mock_Reporting_List'")
        lists = list_all_lists()
        audience_id = next((lst["id"] for lst in lists if lst.get("attributes", {}).get("name") == "Mock_Reporting_List"), None)
        if audience_id:
            log(f"Auto-selected list ID {audience_id} for 'Mock_Reporting_List'")
        else:
            log("No 'Mock_Reporting_List' found; please set AUDIENCE_ID env var to a valid list ID")
            return None
    
    url = f"{BASE_URL}/campaigns/"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    
    # Schedule campaign send time for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # Create the campaign payload according to Klaviyo API docs
    campaign_payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": name,
                "audiences": {"included": [audience_id], "excluded": []},
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": tomorrow_str,
                        "is_local": True,
                        "send_past_recipients_immediately": False
                    }
                },
                "tracking_options": {
                    "custom_tracking_params": [
                        {"type": "static", "value": "klaviyo", "name": "utm_source"},
                        {"type": "dynamic", "value": "campaign_id", "name": "utm_medium"}
                    ],
                    "is_tracking_clicks": True,
                    "is_tracking_opens": True
                },
                "campaign-messages": {
                    "data": [
                        {
                            "type": "campaign-message",
                            "attributes": {
                                "definition": {
                                    "channel": "email",
                                    "label": name,
                                    "content": {
                                        "subject": name,
                                        "preview_text": "This is a mock campaign email",
                                        "from_email": os.getenv("FROM_EMAIL", "no-reply@example.com"),
                                        "from_label": os.getenv("FROM_LABEL", "Mock Sender"),
                                        "reply_to_email": os.getenv("REPLY_TO_EMAIL", "no-reply@example.com")
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    
    # Make sure to include filter for channel type in the URL
    campaign_response = requests.post(url, headers=headers, json=campaign_payload)
    
    if campaign_response.status_code not in (200, 201, 202):
        log(f"Error creating campaign: {campaign_response.status_code} {campaign_response.text}")
        return None
    
    campaign_id = campaign_response.json()["data"]["id"]
    log(f"Successfully created campaign '{name}' with ID: {campaign_id}")
    return campaign_id

def validate_campaign_exists(name):
    """
    Check if a campaign with the given name exists in Klaviyo.
    
    Args:
        name (str): Name of the campaign to check
    
    Returns:
        str: Campaign ID if exists, None otherwise
    """
    url = f"{BASE_URL}/campaigns/?filter=equals(messages.channel,'email')"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        log(f"Error fetching campaigns: {response.status_code} {response.text}")
        return None
    
    campaigns = response.json().get("data", [])
    
    for campaign in campaigns:
        if campaign.get("attributes", {}).get("name") == name:
            campaign_id = campaign.get("id")
            log(f"Found campaign '{name}' with ID: {campaign_id}")
            return campaign_id
    
    return None

def list_all_campaigns():
    """List all campaigns in the Klaviyo account."""
    url = f"{BASE_URL}/campaigns/?filter=equals(messages.channel,'email')"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        log(f"Error fetching campaigns: {response.status_code} {response.text}")
        return
    
    campaigns = response.json().get("data", [])
    
    log(f"Found {len(campaigns)} campaigns:")
    for i, campaign in enumerate(campaigns, 1):
        name = campaign.get("attributes", {}).get("name", "Unknown")
        campaign_id = campaign.get("id", "Unknown")
        status = campaign.get("attributes", {}).get("status", "Unknown")
        
        log(f"{i}. {name} (ID: {campaign_id}, Status: {status})")

def list_all_lists():
    """List all Klaviyo lists and their IDs."""
    url = f"{BASE_URL}/lists"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code} {response.text}")
        return []
    data = response.json().get("data", [])
    log("Available Klaviyo lists:")
    for lst in data:
        name = lst.get("attributes", {}).get("name", "Unknown")
        list_id = lst.get("id", "Unknown")
        log(f"- {name} (ID: {list_id})")
    return data

def send_campaign(campaign_id):
    payload = { "data": { "type": "campaign-send-job", "attributes": { "campaign_id": campaign_id } } }
    url = f"{BASE_URL}/campaign-send-jobs/"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code not in (200,201,202):
        log(f"Error sending campaign: {resp.status_code} {resp.text}")
        return False
    log(f"Successfully triggered send for campaign {campaign_id}")
    return True

def get_campaign_messages(campaign_id):
    """Get all messages belonging to a campaign."""
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log(f"Error fetching campaign messages: {response.status_code} {response.text}")
        return []
    return [msg.get("id") for msg in response.json().get("data", [])]

def assign_template_to_message(message_id):
    if not TEMPLATE_ID:
        log("TEMPLATE_ID not set; skipping template assignment")
            headers["content-type"] = "application/vnd.api+json"
            
            # Get the current message data
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            message_data = r.json().get("data", {})
            
            # Extract definition and content
            if "attributes" in message_data and "definition" in message_data["attributes"]:
                definition = message_data["attributes"]["definition"]
                if "content" in definition:
                    # Insert template_id in content
                    content = definition["content"]
                    content["template_id"] = TEMPLATE_ID
                    
                    payload = {
                        "data": {
                            "type": "campaign-message",
                            "id": message_id,
                            "attributes": {
                                "definition": definition
                            }
                        }
                    }
                    
                    r = requests.patch(url, headers=headers, json=payload)
                    if r.status_code < 300:
                        log(f"Successfully assigned template {TEMPLATE_ID} to message {message_id} (approach 1)")
                        return True
        except Exception as e:
            log(f"Approach {methods_tried}/{max_methods} failed: {e}")
        
        # Approach 2: Try using relationships endpoint
        try:
            methods_tried += 1
            url = f"{BASE_URL}/campaign-messages/{message_id}/relationships/template"
            payload = {
                "data": {
                    "type": "template",
                    "id": TEMPLATE_ID
                }
            }
            
            # Try both POST and PATCH
            for method in [requests.post, requests.patch]:
                try:
                    r = method(url, headers=headers, json=payload)
                    if r.status_code < 300:
                        log(f"Successfully assigned template {TEMPLATE_ID} to message {message_id} (approach 2)")
                        return True
                except:
                    pass
        except Exception as e:
            log(f"Approach {methods_tried}/{max_methods} failed: {e}")
        
        # Approach 3: Update campaign message with template in attributes
        try:
            methods_tried += 1
            url = f"{BASE_URL}/campaign-messages/{message_id}"
            payload = {
                "data": {
                    "type": "campaign-message",
                    "id": message_id,
                    "attributes": {
                        "template": TEMPLATE_ID
                    }
                }
            }
            
            r = requests.patch(url, headers=headers, json=payload)
            if r.status_code < 300:
                log(f"Successfully assigned template {TEMPLATE_ID} to message {message_id} (approach 3)")
                return True
        except Exception as e:
            log(f"Approach {methods_tried}/{max_methods} failed: {e}")
        
        # If we get here, all approaches failed
        log(f"All {max_methods} template assignment approaches failed for message {message_id}")
        log("Continuing with campaign scheduling despite template assignment failure")
        return False
        
    except requests.exceptions.RequestException as e:
        log(f"Failed to verify template or assign it: {e}")
        log("Continuing with campaign scheduling despite template assignment failure")
        return False

def schedule_campaign(campaign_id, when_iso):
    """Schedule a campaign via Klaviyo API."""
    # Instead of using campaign-schedules, update the campaign directly
    url = f"{BASE_URL}/campaigns/{campaign_id}"
    headers = HEADERS.copy()
    headers["accept"] = "application/vnd.api+json"
    headers["content-type"] = "application/vnd.api+json"
    headers["revision"] = "2025-04-15"
    
    # Update the send_strategy to schedule the campaign
    payload = {
        "data": {
            "type": "campaign",
            "id": campaign_id,
            "attributes": {
                "send_strategy": {
                    "method": "static",
                    "datetime": when_iso
                }
            }
        }
    }
    
    try:
        r = requests.patch(url, headers=headers, json=payload)
        r.raise_for_status()
        log(f"Campaign {campaign_id} scheduled for {when_iso}")
        return True
    except requests.exceptions.RequestException as e:
        log(f"Error scheduling campaign: {e} {r.text if 'r' in locals() else ''}")
        return False

def run():
    """Create or find test campaigns and send them."""
    log("Starting campaign send script...")
    # Compute send time for tomorrow
    when = datetime.now() + timedelta(days=1)
    when_iso = when.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    campaign_names = ["Mock_Welcome_Campaign", "Mock_Product_Update"]

    for name in campaign_names:
        # Get existing campaign or create a new one
        campaign_id = validate_campaign_exists(name)
        if campaign_id:
            log(f"Campaign '{name}' exists (ID: {campaign_id}), triggering send.")
        else:
            campaign_id = create_campaign(name)
            if campaign_id:
                log(f"Successfully created campaign '{name}' (ID: {campaign_id}).")
            else:
                log(f"Failed to create campaign: {name}")
                continue
        # Assign template to campaign messages
        message_ids = get_campaign_messages(campaign_id)
        for message_id in message_ids:
            assign_template_to_message(message_id)
        # Schedule campaign
        schedule_campaign(campaign_id, when_iso)

    # List all campaigns to verify
    log("\nListing all campaigns:")
    list_all_campaigns()

    log("Done!")

if __name__ == "__main__":
    run()
