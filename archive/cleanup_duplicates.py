#!/usr/bin/env python3
"""
Script to clean up duplicate mock lists in Klaviyo.
This keeps only the most populated list and removes the rest.
"""
import requests
import json
from datetime import datetime

# Load the API key
with open('private-api-key.txt', 'r') as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "revision": "2025-04-15",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def log(message):
    """Log messages with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_all_mock_lists():
    """Get all lists with 'Mock_' prefix and their profile counts."""
    log("Finding all mock lists...")
    
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        log(f"Error fetching lists: {response.status_code}")
        return []
    
    lists_data = response.json().get('data', [])
    mock_lists = []
    
    for list_data in lists_data:
        if list_data.get('attributes', {}).get('name', '').startswith('Mock_'):
            list_id = list_data.get('id')
            list_name = list_data.get('attributes', {}).get('name')
            
            # Get profile count
            profile_count = get_profile_count(list_id)
            log(f"Found list: {list_name} (ID: {list_id}) with {profile_count} profiles")
            
            mock_lists.append({
                'id': list_id,
                'name': list_name,
                'profile_count': profile_count
            })
    
    return mock_lists

def get_profile_count(list_id):
    """Get the number of profiles in a list."""
    url = f"{BASE_URL}/lists/{list_id}/profiles/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return 0
    
    profiles = response.json().get('data', [])
    return len(profiles)

def delete_list(list_id):
    """Delete a list by ID."""
    log(f"Deleting list {list_id}...")
    
    url = f"{BASE_URL}/lists/{list_id}"
    response = requests.delete(url, headers=HEADERS)
    
    if response.status_code in (204, 200):
        log(f"Successfully deleted list {list_id}")
        return True
    else:
        log(f"Error deleting list {list_id}: {response.status_code}")
        return False

def cleanup_duplicate_lists():
    """
    Keep only the most populated list and remove others.
    If multiple lists have the same name, keep the one with most profiles.
    """
    mock_lists = get_all_mock_lists()
    
    if not mock_lists:
        log("No mock lists found, nothing to clean up.")
        return
    
    log(f"Found {len(mock_lists)} mock lists")
    
    # Group lists by name
    lists_by_name = {}
    for list_data in mock_lists:
        name = list_data['name']
        if name not in lists_by_name:
            lists_by_name[name] = []
        lists_by_name[name].append(list_data)
    
    # For each group, keep the one with most profiles
    lists_to_keep = []
    lists_to_delete = []
    
    for name, list_group in lists_by_name.items():
        if len(list_group) == 1:
            # Only one list with this name, keep it
            lists_to_keep.append(list_group[0])
        else:
            # Multiple lists with same name, keep the one with most profiles
            list_group.sort(key=lambda x: x['profile_count'], reverse=True)
            lists_to_keep.append(list_group[0])
            lists_to_delete.extend(list_group[1:])
    
    # Report what we're keeping
    log("\nKeeping these lists:")
    for list_data in lists_to_keep:
        log(f"- {list_data['name']} (ID: {list_data['id']}) with {list_data['profile_count']} profiles")
    
    # Delete the duplicates
    if lists_to_delete:
        log(f"\nDeleting {len(lists_to_delete)} duplicate lists:")
        for list_data in lists_to_delete:
            deleted = delete_list(list_data['id'])
            if deleted:
                log(f"✓ Deleted {list_data['name']} (ID: {list_data['id']})")
            else:
                log(f"✗ Failed to delete {list_data['name']} (ID: {list_data['id']})")
    else:
        log("\nNo duplicate lists to delete.")
    
    log("\nCleanup complete!")

if __name__ == "__main__":
    log("Starting duplicate list cleanup...")
    cleanup_duplicate_lists()
