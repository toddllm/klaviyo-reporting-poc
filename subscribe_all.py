#!/usr/bin/env python3
"""
Script to subscribe all POC mock profiles to Klaviyo list via JSON:API endpoint.
"""
from config import get_config
from seed_profiles import random_profile, create_and_subscribe_profiles


def main():
    cfg = get_config()
    num_profiles = cfg.get('NUM_TEST_PROFILES', 30)
    prefix = 'poc'
    # Generate profiles deterministically
    profiles = [random_profile(i, prefix=prefix) for i in range(1, num_profiles + 1)]
    # Subscribe all in one batch (idempotent upsert)
    emails, status = create_and_subscribe_profiles(profiles, dry_run=False)
    print(f"Subscribed {len(emails)} profiles, status code: {status}")


if __name__ == '__main__':
    main()
