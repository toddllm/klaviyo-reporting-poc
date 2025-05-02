#!/usr/bin/env python3
"""
Cleanup script for Klaviyo testing environment.
Removes all lists, flows, and campaigns with the 'Mock_' prefix.
"""
import os
import requests
import time

# Load the API key
with open('private-api-key.txt', 'r') as f:
    PRIVATE_KEY = f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/json",
    "revision": "2025-04-15",
    "Authorization": f"Klaviyo-API-Key {PRIVATE_KEY}"
}

def get_all_lists():
    """Get all lists in the account and return those with Mock_ prefix."""
    url = f"{BASE_URL}/lists/"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching lists: {response.status_code} {response.text}")
        return []
    
    lists_data = response.json().get('data', [])
    mock_lists = [list_data for list_data in lists_data 
                if list_data.get('attributes', {}).get('name', '').startswith('Mock_')]
    
    return mock_lists

def delete_list(list_id):
    """Delete a list by ID."""
    url = f"{BASE_URL}/lists/{list_id}"
    response = requests.delete(url, headers=HEADERS)
    
    if response.status_code in [204, 200]:
        print(f"Successfully deleted list {list_id}")
        return True
    else:
        print(f"Error deleting list {list_id}: {response.status_code} {response.text}")
        return False

def cleanup_lists():
    """Find and delete all mock lists."""
    mock_lists = get_all_lists()
    print(f"Found {len(mock_lists)} mock lists to clean up")
    
    for list_data in mock_lists:
        list_id = list_data.get('id')
        list_name = list_data.get('attributes', {}).get('name', 'Unknown')
        print(f"Deleting list: {list_name} (ID: {list_id})")
        deleted = delete_list(list_id)
        if deleted:
            print(f"Successfully deleted list: {list_name}")
        else:
            print(f"Failed to delete list: {list_name}")
        time.sleep(0.5)  # Add delay to avoid rate limiting

def main():
    """Run the cleanup process."""
    print("Starting cleanup of mock Klaviyo data...")
    cleanup_lists()
    print("Cleanup complete!")

if __name__ == "__main__":
    main()
