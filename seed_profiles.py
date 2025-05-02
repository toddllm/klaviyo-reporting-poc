#!/usr/bin/env python3
import os
import sys
import random
import time
import uuid
import argparse
import requests
from datetime import datetime, timedelta, UTC
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
                # 200, 201, 202 are all considered success for upserts/list-subscribe
                # 200 = already existed/updated
                # 201 = resource created (first-time profile)
                # 202 = accepted for async list-subscribe batch
                if resp.status_code in (200, 201, 202):
                    return resp  # Success
                # For other status codes, raise_for_status converts 4xx / 5xx to HTTPError
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


def random_email(first, last, index, prefix=None):
    """Generate a random or deterministic email address
    
    Args:
        first (str): First name
        last (str): Last name
        index (int): Unique index for the email
        prefix (str, optional): Prefix for deterministic emails. If it contains '@',
                              it's treated as 'local@domain' and becomes 'local+index@domain'.
                              Otherwise, it becomes 'prefix+index@example.com'.
    
    Returns:
        str: Generated email address
    """
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
    last_purchase = (datetime.now(UTC) - timedelta(days=random.randint(1, 120))).isoformat()
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
    """Create profiles and subscribe them to a list in one API call
    
    Returns:
        tuple: (list of emails, status_code) for summary reporting
    """
    url = f"{BASE_URL}/lists/{AUDIENCE_ID}/relationships/profiles/"
    
    # Convert profiles to the expected JSON-API format
    data = [{
        "type": "profile",
        "attributes": profile
    } for profile in profiles]
    
    payload = {"data": data}
    
    response = post_json_api(url, payload, dry_run)
    if not dry_run:
        status_msg = {
            200: "updated",
            201: "created",
            202: "accepted for processing"
        }.get(response.status_code, "processed")
        print(f"{status_msg.capitalize()} {len(profiles)} profiles for list {AUDIENCE_ID} (status {response.status_code})")
    
    # Return emails and status code for summary reporting
    emails = [profile["email"] for profile in profiles]
    return emails, response.status_code


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
    profiles_updated = 0
    profiles_pending = 0
    batch_profiles = []
    
    for i in range(1, args.num + 1):
        profile = random_profile(i, args.prefix)
        batch_profiles.append(profile)
        
        # Process in batches
        if len(batch_profiles) >= BATCH_SIZE or i == args.num:
            try:
                emails, status_code = create_and_subscribe_profiles(batch_profiles, args.dry_run)
                count = len(batch_profiles)
                
                # Track status for summary reporting
                if status_code == 201:
                    profiles_created += count
                elif status_code == 200:
                    profiles_updated += count
                elif status_code == 202:
                    profiles_pending += count
                
                log(f"Progress: {profiles_created + profiles_updated + profiles_pending}/{args.num} profiles processed", args.dry_run)
                batch_profiles = []  # Reset batch
            except Exception as e:
                log(f"Error processing profiles: {str(e)}", args.dry_run)
                sys.exit(1)
    
    # Print summary
    total = profiles_created + profiles_updated + profiles_pending
    log(f"Summary: {total} profiles processed for list {AUDIENCE_ID}", args.dry_run)
    if not args.dry_run:
        if profiles_created > 0:
            log(f"  - {profiles_created} new profiles created", args.dry_run)
        if profiles_updated > 0:
            log(f"  - {profiles_updated} existing profiles updated", args.dry_run)
        if profiles_pending > 0:
            log(f"  - {profiles_pending} profiles accepted for processing", args.dry_run)


if __name__ == "__main__":
    main()
