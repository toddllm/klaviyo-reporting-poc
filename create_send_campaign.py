#!/usr/bin/env python3
import requests
import argparse
import json
import time
import sys
from config import get_config

# Load configuration
config = get_config()
KLAVIYO_API_KEY = config['KLAVIYO_API_KEY']
AUDIENCE_ID = config['AUDIENCE_ID']
TEMPLATE_ID = config['TEMPLATE_ID']
KLAVIYO_API_VERSION = config['KLAVIYO_API_VERSION']

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "revision": KLAVIYO_API_VERSION,
    "Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}"
}

def log(message, dry_run=False):
    prefix = "[DRY-RUN]" if dry_run else "[CAMPAIGN]"
    print(f"{prefix} {message}")

def create_campaign(campaign_name, audience_id, dry_run=False):
    """Create a new campaign with the specified name and audience"""
    url = f"{BASE_URL}/campaigns/"
    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": campaign_name,
                "audiences": {
                    "included": [{
                        "id": f"list-{audience_id}",
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
    
    if dry_run:
        log(f"Would create campaign '{campaign_name}' with payload: {json.dumps(payload, indent=2)}", dry_run)
        return "dry-run-campaign-id"
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code not in (200, 201):
        log(f"Error creating campaign: {response.status_code} {response.text}")
        return None
    
    campaign_id = response.json()["data"]["id"]
    log(f"Created campaign '{campaign_name}' with ID: {campaign_id}")
    return campaign_id

def get_campaign_messages(campaign_id, dry_run=False):
    """Get all message IDs for a campaign"""
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    
    if dry_run:
        log(f"Would fetch messages for campaign ID: {campaign_id}", dry_run)
        return ["dry-run-message-id"]
    
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        log(f"Error fetching campaign messages: {response.status_code} {response.text}")
        return []
    
    messages = response.json().get("data", [])
    message_ids = [msg.get("id") for msg in messages]
    log(f"Found {len(message_ids)} messages for campaign {campaign_id}")
    return message_ids

def assign_template(message_id, template_id, dry_run=False):
    """Assign a template to a campaign message"""
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
    
    if dry_run:
        log(f"Would assign template {template_id} to message {message_id} with payload: {json.dumps(payload, indent=2)}", dry_run)
        return True
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code < 400:
        log(f"Assigned template {template_id} to message {message_id}")
        return True
    else:
        log(f"Failed to assign template: {response.status_code} - {response.text}")
        return False

def check_message_status(message_id, dry_run=False):
    """Check if a message is ready to be sent"""
    url = f"{BASE_URL}/campaign-messages/{message_id}"
    headers = HEADERS.copy()
    headers.pop("Content-Type", None)
    
    if dry_run:
        log(f"Would check status of message {message_id}", dry_run)
        return "ready"
    
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        log(f"Error checking message status: {response.status_code} {response.text}")
        return None
    
    status = response.json().get("data", {}).get("attributes", {}).get("status")
    log(f"Message {message_id} status: {status}")
    return status

def wait_for_message_ready(message_id, max_attempts=10, dry_run=False):
    """Wait for a message to be ready, polling with exponential backoff"""
    if dry_run:
        log(f"Would wait for message {message_id} to be ready", dry_run)
        return True
    
    attempt = 0
    while attempt < max_attempts:
        status = check_message_status(message_id)
        if status == "ready":
            return True
        
        wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16...
        log(f"Message not ready, waiting {wait_time} seconds before retry...")
        time.sleep(wait_time)
        attempt += 1
    
    log(f"Message {message_id} not ready after {max_attempts} attempts")
    return False

def send_campaign(campaign_id, dry_run=False):
    """Send a campaign"""
    url = f"{BASE_URL}/campaigns/{campaign_id}/send"
    payload = {
        "data": {
            "type": "campaign-send-job",
            "attributes": {}
        }
    }
    
    if dry_run:
        log(f"Would send campaign {campaign_id} with payload: {json.dumps(payload, indent=2)}", dry_run)
        return True
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code < 400:
        log(f"Campaign {campaign_id} sent successfully")
        return True
    else:
        log(f"Failed to send campaign: {response.status_code} - {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create and send a Klaviyo campaign")
    parser.add_argument("--name", default=f"Test Campaign {time.strftime('%Y-%m-%d %H:%M')}", 
                        help="Name of the campaign to create")
    parser.add_argument("--audience-id", default=AUDIENCE_ID, 
                        help="ID of the audience to target")
    parser.add_argument("--template-id", default=TEMPLATE_ID, 
                        help="ID of the template to use")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Perform a dry run without making actual API calls")
    args = parser.parse_args()
    
    # Create campaign
    campaign_id = create_campaign(args.name, args.audience_id, args.dry_run)
    if not campaign_id:
        sys.exit(1)
    
    # Get campaign messages
    message_ids = get_campaign_messages(campaign_id, args.dry_run)
    if not message_ids:
        log("No messages found for campaign. Aborting.")
        sys.exit(1)
    
    # Assign template to each message
    for message_id in message_ids:
        success = assign_template(message_id, args.template_id, args.dry_run)
        if not success:
            log(f"Failed to assign template to message {message_id}. Aborting.")
            sys.exit(1)
        
        # Wait for message to be ready before sending
        if not args.dry_run:
            log(f"Waiting for message {message_id} to be ready...")
            time.sleep(10)  # Initial wait to allow template assignment to process
            if not wait_for_message_ready(message_id, dry_run=args.dry_run):
                log(f"Message {message_id} not ready. Aborting.")
                sys.exit(1)
    
    # Send the campaign
    success = send_campaign(campaign_id, args.dry_run)
    if not success:
        log("Failed to send campaign. Aborting.")
        sys.exit(1)
    
    log(f"Campaign {args.name} created and sent successfully!")

if __name__ == "__main__":
    main()
