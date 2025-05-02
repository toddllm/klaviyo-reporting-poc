#!/usr/bin/env python3
import os
import sys
import random
import time
import uuid
import argparse
import requests
from datetime import datetime, timedelta
from functools import wraps
from requests.exceptions import RequestException, HTTPError

from config import get_config

# Load configuration
config = get_config()
KLAVIYO_API_KEY = config['KLAVIYO_API_KEY']
AUDIENCE_ID = config['AUDIENCE_ID']
KLAVIYO_API_VERSION = config['KLAVIYO_API_VERSION']

# API constants
BASE_URL = "https://a.klaviyo.com/api"
MAX_RETRIES = 5
BASE_DELAY = 1.0  # seconds
BATCH_SIZE = 100  # profiles per request (max 1000)

# Sample data
FIRST_NAMES = [
    "Jessica", "Roger", "Emily", "Joshua", "Rachel", "Kimberly", "Mary", "Joshua", "Michael", "Vicki",
    "Logan", "Eric", "Wendy", "Benjamin", "Elizabeth", "Christian", "John", "Ryan", "Gregory", "Misty"
]
LAST_NAMES = [
    "Farmer", "Payne", "Roman", "Thomas", "Lyons", "Crawford", "Vaughn", "Alexander", "Rodriguez", "Porter",
    "Avila", "Jenkins", "Lawson", "Black", "Hamilton", "Flowers", "Cox", "Stuart", "Adams", "Sullivan"
]
CATEGORIES = ["Apparel", "Electronics", "Beauty", "Home", "Toys", "Sports", "Books"]


def klaviyo_retry(func):
    """Decorator to handle Klaviyo API rate limits and transient errors with exponential backoff"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        delay = BASE_DELAY
        while True:
            try:
                resp = func(*args, **kwargs)
                # raise_for_status converts 4xx / 5xx to HTTPError
                resp.raise_for_status()
                return resp  # Success
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


def random_email(first, last, index, prefix=None):
    """Generate a random or deterministic email address"""
    if prefix:
        if "@" in prefix:
            local, domain = prefix.split("@", 1)
            return f"{local}+{index}@{domain}"
        else:
            return f"{prefix}+{index}@example.com"
    
    domain = random.choice(["example.com", "shop.com", "store.com"])
    return f"{first.lower()}.{last.lower()}.{random.randint(1000,9999)}@{domain}"


def random_profile(index, prefix=None):
    """Generate a random profile with optional deterministic email"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = random_email(first, last, index, prefix)
    total_spent = round(random.uniform(10, 1000), 2)
    last_purchase = (datetime.utcnow() - timedelta(days=random.randint(1, 120))).isoformat()
    favorite = random.choice(CATEGORIES)
    
    return {
        "email": email,
        "first_name": first,
        "last_name": last,
        "properties": {
            "total_spent": total_spent,
            "last_purchase_at": last_purchase,
            "favorite_category": favorite
        }
    }


def create_and_subscribe_profiles(profiles, dry_run=False):
    """Create profiles and subscribe them to a list in one API call"""
    url = f"{BASE_URL}/lists/{AUDIENCE_ID}/relationships/profiles/"
    
    # Convert profiles to the expected JSON-API format
    data = [{
        "type": "profile",
        "attributes": profile
    } for profile in profiles]
    
    payload = {"data": data}
    
    response = post_json_api(url, payload, dry_run)
    if not dry_run:
        print(f"Created and subscribed {len(profiles)} profiles to list {AUDIENCE_ID}")
    return response


def log(message, dry_run=False):
    """Log a message with appropriate prefix"""
    prefix = "[DRY-RUN]" if dry_run else "[PROFILES]"
    print(f"{prefix} {message}")


def main():
    parser = argparse.ArgumentParser(description="Seed Klaviyo profiles and subscribe to a list")
    parser.add_argument("--prefix", help="Use prefix@domain for deterministic emails; will generate prefix+<i>@domain")
    parser.add_argument("--num", type=int, default=int(os.environ.get("NUM_TEST_PROFILES", "30")),
                        help="Number of profiles to seed (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Print API calls without making them")
    args = parser.parse_args()
    
    log(f"Seeding {args.num} profiles...", args.dry_run)
    
    # Generate profiles in batches to avoid rate limits
    profiles_created = 0
    batch_profiles = []
    
    for i in range(1, args.num + 1):
        profile = random_profile(i, args.prefix)
        batch_profiles.append(profile)
        
        # Process in batches
        if len(batch_profiles) >= BATCH_SIZE or i == args.num:
            try:
                create_and_subscribe_profiles(batch_profiles, args.dry_run)
                profiles_created += len(batch_profiles)
                log(f"Progress: {profiles_created}/{args.num} profiles created", args.dry_run)
                batch_profiles = []  # Reset batch
            except Exception as e:
                log(f"Error creating profiles: {str(e)}", args.dry_run)
                sys.exit(1)
    
    log(f"Successfully created and subscribed {profiles_created} profiles to list {AUDIENCE_ID}", args.dry_run)


if __name__ == "__main__":
    main()
