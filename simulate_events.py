#!/usr/bin/env python3

import os
import sys
import json
import uuid
import random
import argparse
import requests
from datetime import datetime, timedelta, UTC
from functools import wraps
from requests.exceptions import RequestException, HTTPError

from config import get_config

# Load configuration
config = get_config()
KLAVIYO_API_KEY = config['KLAVIYO_API_KEY']
KLAVIYO_API_VERSION = config['KLAVIYO_API_VERSION']

# API constants
BASE_URL = "https://a.klaviyo.com/api"
MAX_RETRIES = 5
BASE_DELAY = 1.0  # seconds


def klaviyo_retry(func):
    """Decorator to handle Klaviyo API rate limits and transient errors with exponential backoff"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        delay = BASE_DELAY
        while True:
            try:
                resp = func(*args, **kwargs)
                if resp.status_code in (200, 201, 202):
                    return resp  # Success
                resp.raise_for_status()
                return resp  # Success for any other 2xx
            except HTTPError as e:
                status = e.response.status_code
                if status == 429:  # Rate limited
                    # Honor Retry-After if available
                    retry_after = e.response.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after else delay
                    print(f"Rate limited. Waiting {wait} seconds before retry...")
                elif 500 <= status < 600:  # Transient server error
                    wait = delay
                    print(f"Server error {status}. Waiting {wait} seconds before retry...")
                else:
                    print(f"Error {status}: {e.response.text}")
                    raise  # Permanent failure
            except RequestException as e:
                # Connection reset, DNS, timeout, etc.
                wait = delay
                print(f"Request exception: {str(e)}. Waiting {wait} seconds before retry...")

            retries += 1
            if retries > MAX_RETRIES:
                raise RuntimeError(f"Max retries exceeded for {func.__name__}")

            jitter = random.uniform(0, 0.3 * wait)  # Add 0-30% jitter
            time.sleep(wait + jitter)
            delay *= 2  # Exponential backoff

    return wrapper


@klaviyo_retry
def post_json_api(url, payload, dry_run=False):
    """Make a POST request to the Klaviyo JSON API with proper headers"""
    if dry_run:
        print(f"[DRY-RUN] Would POST to {url} with payload: {payload}")
        return type('obj', (object,), {'status_code': 200, 'json': lambda: {}, 'raise_for_status': lambda: None})

    headers = {
        "Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}",
        "Klaviyo-Api-Version": KLAVIYO_API_VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Idempotency-Key": str(uuid.uuid4())  # Prevent duplicates on retry
    }
    return requests.post(url, headers=headers, json=payload, timeout=15)


@klaviyo_retry
def get_json_api(url, params=None, dry_run=False):
    """Make a GET request to the Klaviyo JSON API with proper headers"""
    if dry_run:
        print(f"[DRY-RUN] Would GET from {url} with params: {params}")
        return type('obj', (object,), {'status_code': 200, 'json': lambda: {}, 'raise_for_status': lambda: None})

    headers = {
        "Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}",
        "Klaviyo-Api-Version": KLAVIYO_API_VERSION,
        "Accept": "application/json"
    }
    return requests.get(url, headers=headers, params=params, timeout=15)


# Cache file path as a module-level constant for easier testing
cache_file = ".metric_ids.json"

def get_or_create_custom_metric(name, dry_run=False):
    """Get a metric ID by name, creating it if it doesn't exist
    
    Args:
        name (str): The name of the metric to get or create
        dry_run (bool): If True, don't make actual API calls
        
    Returns:
        str: The metric ID
    """
    # First try to get from cache
    metric_ids = {}
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                metric_ids = json.load(f)
                if name in metric_ids and metric_ids[name]:
                    return metric_ids[name]
        except json.JSONDecodeError:
            pass  # Cache file is invalid, continue to API lookup
    
    if dry_run:
        print(f"[DRY-RUN] Would get or create metric with name: {name}")
        metric_id = f"mock-{name.lower().replace(' ', '-')}-id-{random.randint(100, 999)}"
        metric_ids[name] = metric_id
        with open(cache_file, 'w') as f:
            json.dump(metric_ids, f)
        return metric_id
    
    # Try to get the metric
    url = f"{BASE_URL}/metrics/"
    params = {"filter": f"equals(name,'{name}')"}
    
    response = get_json_api(url, params)
    data = response.json().get("data", [])
    
    if data:  # Metric exists
        metric_id = data[0]["id"]
    else:  # Need to create the metric
        create_url = f"{BASE_URL}/metrics/"
        payload = {
            "data": {
                "type": "metric",
                "attributes": {
                    "name": name,
                    "service": "api"
                }
            }
        }
        
        response = post_json_api(create_url, payload)
        metric_id = response.json()["data"]["id"]
    
    # Update cache
    metric_ids[name] = metric_id
    with open(cache_file, 'w') as f:
        json.dump(metric_ids, f)
    
    return metric_id


def simulate_event(profile_id, metric_name, properties=None, dry_run=False):
    """Simulate an event for a profile
    
    Args:
        profile_id (str): The ID of the profile to simulate the event for
        metric_name (str): The name of the metric to simulate
        properties (dict): Additional properties for the event
        dry_run (bool): If True, don't make actual API calls
        
    Returns:
        bool: True if successful, False otherwise
    """
    if properties is None:
        properties = {}
    
    # Get or create the metric
    metric_id = get_or_create_custom_metric(metric_name, dry_run)
    
    # Create the event payload with metric_id inside the metric object per API v2025-04-15
    url = f"{BASE_URL}/events/"
    payload = {
        "data": {
            "type": "event",
            "attributes": {
                "properties": properties,
                "time": datetime.now(UTC).isoformat(),
                "value": properties.get("value", 0)
            },
            "relationships": {
                "profile": {
                    "data": {
                        "type": "profile",
                        "id": profile_id
                    }
                },
                "metric": {
                    "data": {
                        "type": "metric",
                        "id": metric_id
                    }
                }
            }
        }
    }
    
    response = post_json_api(url, payload, dry_run)
    
    if not dry_run:
        if response.status_code in (200, 201, 202):
            print(f"Successfully simulated {metric_name} event for profile {profile_id}")
            return True
        else:
            print(f"Failed to simulate event: {response.status_code} {response.text}")
            return False
    
    return True


def get_random_profile_id(dry_run=False):
    """Get a random profile ID from the account
    
    Args:
        dry_run (bool): If True, return a mock profile ID
        
    Returns:
        str: A profile ID
    """
    if dry_run:
        return f"mock-profile-{uuid.uuid4()}"
    
    url = f"{BASE_URL}/profiles/"
    params = {"page[size]": 1}
    
    response = get_json_api(url, params)
    data = response.json().get("data", [])
    
    if not data:
        print("No profiles found. Please create profiles first using seed_profiles.py")
        return None
    
    return data[0]["id"]


def main():
    parser = argparse.ArgumentParser(description="Simulate events for Klaviyo profiles")
    parser.add_argument("--metric", default="Opened Email", help="Metric name to simulate (default: Opened Email)")
    parser.add_argument("--profile-id", help="Specific profile ID to use (default: random profile)")
    parser.add_argument("--count", type=int, default=1, help="Number of events to simulate (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Print API calls without making them")
    args = parser.parse_args()
    
    # Get profile ID if not specified
    profile_id = args.profile_id or get_random_profile_id(args.dry_run)
    if not profile_id:
        return 1
    
    # Simulate events
    success_count = 0
    for i in range(args.count):
        properties = {
            "campaign_name": "Test Campaign",
            "subject": "Test Subject",
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        if simulate_event(profile_id, args.metric, properties, args.dry_run):
            success_count += 1
    
    print(f"Successfully simulated {success_count}/{args.count} events")
    return 0 if success_count == args.count else 1


if __name__ == "__main__":
    import time  # Import here to avoid issues with the decorator
    sys.exit(main())
