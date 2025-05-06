#!/usr/bin/env python3
"""
Script to subscribe all mock POC profiles to a Klaviyo list via the V1 API.
"""
import os
import requests
from config import get_config
from seed_profiles import random_profile

def subscribe_email(email, audience_id, api_key):
    """Subscribe an email via Klaviyo V1 list-members endpoint"""
    url = f"https://a.klaviyo.com/api/v1/list/{audience_id}/members"
    params = {'api_key': api_key}
    payload = {'profiles': [{'email': email}]}
    resp = requests.post(url, params=params, json=payload)
    resp.raise_for_status()
    return resp.json()


def main():
    cfg = get_config()
    api_key = cfg['KLAVIYO_API_KEY']
    audience_id = cfg['AUDIENCE_ID']
    num = int(os.environ.get('NUM_TEST_PROFILES', '30'))
    for i in range(1, num + 1):
        profile = random_profile(i, prefix='poc')
        email = profile['email']
        print(f"Subscribing mock {i}/{num}: {email}")
        try:
            resp = subscribe_email(email, audience_id, api_key)
            print(f"Subscribed {email}: {resp}")
        except Exception as e:
            print(f"Failed to subscribe {email}: {e}")
    print("Completed subscribing mock profiles.")


if __name__ == '__main__':
    main()
