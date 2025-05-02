#!/usr/bin/env python3
import requests
import json
from datetime import datetime

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

def get_segments():
    """Get all segments from the Klaviyo account."""
    url = f"{BASE_URL}/segments/"
    log(f"Fetching segments from {url}")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching segments: {response.status_code} {response.text}", "ERROR")
        return []
    
    segments = response.json().get("data", [])
    log(f"Found {len(segments)} segments")
    
    for segment in segments:
        segment_id = segment.get("id")
        segment_name = segment.get("attributes", {}).get("name")
        log(f"Segment: {segment_name} (ID: {segment_id})")
        print(json.dumps(segment, indent=2))
        print("-" * 80)
    
    return segments

def get_lists():
    """Get all lists from the Klaviyo account."""
    url = f"{BASE_URL}/lists/"
    log(f"Fetching lists from {url}")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code} {response.text}", "ERROR")
        return []
    
    lists = response.json().get("data", [])
    log(f"Found {len(lists)} lists")
    
    for list_item in lists:
        list_id = list_item.get("id")
        list_name = list_item.get("attributes", {}).get("name")
        log(f"List: {list_name} (ID: {list_id})")
        print(json.dumps(list_item, indent=2))
        print("-" * 80)
    
    return lists

def get_tags():
    """Get all tags from the Klaviyo account."""
    url = f"{BASE_URL}/tags/"
    log(f"Fetching tags from {url}")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching tags: {response.status_code} {response.text}", "ERROR")
        return []
    
    tags = response.json().get("data", [])
    log(f"Found {len(tags)} tags")
    
    for tag in tags:
        tag_id = tag.get("id")
        tag_name = tag.get("attributes", {}).get("name")
        log(f"Tag: {tag_name} (ID: {tag_id})")
        print(json.dumps(tag, indent=2))
        print("-" * 80)
    
    return tags

def get_campaign_by_id(campaign_id):
    """Get details of a specific campaign."""
    url = f"{BASE_URL}/campaigns/{campaign_id}/"
    log(f"Fetching campaign details from {url}")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching campaign: {response.status_code} {response.text}", "ERROR")
        return None
    
    campaign = response.json().get("data", {})
    print(json.dumps(campaign, indent=2))
    return campaign

def get_campaigns():
    """Get all campaigns from the Klaviyo account."""
    url = f"{BASE_URL}/campaigns/"
    log(f"Fetching campaigns from {url}")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching campaigns: {response.status_code} {response.text}", "ERROR")
        return []
    
    campaigns = response.json().get("data", [])
    log(f"Found {len(campaigns)} campaigns")
    
    for campaign in campaigns[:3]:  # Limit to first 3 to avoid huge output
        campaign_id = campaign.get("id")
        campaign_name = campaign.get("attributes", {}).get("name")
        log(f"Campaign: {campaign_name} (ID: {campaign_id})")
        print(json.dumps(campaign, indent=2))
        print("-" * 80)
    
    return campaigns

def main():
    """Fetch and display all relevant information."""
    log("Fetching all Klaviyo account information for debugging...")
    
    # Get lists
    log("\n=== LISTS ===")
    lists = get_lists()
    
    # Get segments
    log("\n=== SEGMENTS ===")
    segments = get_segments()
    
    # Get tags
    log("\n=== TAGS ===")
    tags = get_tags()
    
    # Get campaigns
    log("\n=== CAMPAIGNS ===")
    campaigns = get_campaigns()
    
    # If there are any campaigns, get details of the first one
    if campaigns:
        log("\n=== CAMPAIGN DETAILS (First Campaign) ===")
        get_campaign_by_id(campaigns[0].get("id"))
    
    log("Completed fetching Klaviyo information.")

if __name__ == "__main__":
    main()
