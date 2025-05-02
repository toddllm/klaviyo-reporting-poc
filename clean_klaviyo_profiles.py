"""Utility script to clean up unused test/mock profiles in Klaviyo.

Based on the error message:
"Over account sending limit - Your active profile count of 426 exceeds your plan's limit."

This script will check for and remove profiles that:
1. Have .mock@ or mock_ in their email addresses
2. Are not part of any protected list we want to keep
"""
import requests
import os
import json
from collections import defaultdict
import time

BASE_URL = "https://a.klaviyo.com/api"
REVISION = "2025-04-15"

def get_api_key():
    with open("private-api-key.txt") as f:
        return f.read().strip()

HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "revision": REVISION,
    "Authorization": f"Klaviyo-API-Key {get_api_key()}"
}

# Helper functions to fetch data from Klaviyo
def fetch_with_pagination(endpoint, params=None):
    """Generic paginated fetch for any Klaviyo endpoint"""
    url = f"{BASE_URL}/{endpoint}"
    if params:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{param_str}"
    
    results = []
    while url:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print(f"Error fetching {url}: {r.status_code}")
            print(r.text)
            break
        
        data = r.json()
        results.extend(data.get("data", []))
        url = data.get("links", {}).get("next")
    
    return results

def fetch_all_lists():
    """Get all lists in the account"""
    return fetch_with_pagination("lists/")

def fetch_list_profiles(list_id):
    """Get all profiles in a specific list"""
    return fetch_with_pagination(f"lists/{list_id}/profiles/")

def fetch_all_profiles():
    """Get all profiles in the account"""
    return fetch_with_pagination("profiles/")

def main():
    # Step 1: Find all current lists, especially those that should be protected
    all_lists = fetch_all_lists()
    list_id_to_name = {l["id"]: l["attributes"]["name"] for l in all_lists}
    
    # Lists to protect (we won't delete profiles from these)
    protected_list_ids = []
    for list_id, name in list_id_to_name.items():
        # Check if the list is:
        # a) NOT a test/mock list name
        if not any(prefix in name for prefix in ["Mock_", "Test_", "Isolated_", "Working_"]):
            protected_list_ids.append(list_id)
            print(f"Protected list: {name} (id: {list_id})")
    
    # Step 2: Get all profiles that are in protected lists
    protected_profile_ids = set()
    for list_id in protected_list_ids:
        profiles = fetch_list_profiles(list_id)
        for profile in profiles:
            protected_profile_ids.add(profile["id"])
        print(f"Protected {len(profiles)} profiles from list {list_id_to_name[list_id]}")
    
    # Step 3: Process all profiles, grouping by email address
    # We'll keep one of each unique email (up to 25) and delete duplicates
    all_profiles = fetch_all_profiles()
    
    # Group profiles by email address
    email_groups = defaultdict(list)
    real_profiles = []
    
    for profile in all_profiles:
        profile_id = profile["id"]
        email = profile["attributes"].get("email", "").lower()
        
        # Skip protected profiles
        if profile_id in protected_profile_ids:
            continue
            
        # Group mock profiles
        if ".mock@" in email or "mock_" in email:
            # Track attributes for better selection
            mock_obj = {
                "id": profile_id,
                "email": email,
                "first_name": profile["attributes"].get("first_name"),
                "last_name": profile["attributes"].get("last_name")
            }
            email_groups[email].append(mock_obj)
        else:
            # Non-mock profiles are kept as-is
            real_profiles.append((profile_id, email))
    
    # Select up to one profile from each unique email, prioritizing those with names
    profiles_to_keep = []
    
    # First pass: select one profile from each email group that has a name
    for email, profiles in email_groups.items():
        # Sort by whether they have first_name and last_name (profiles with names first)
        profiles.sort(key=lambda p: 0 if p["first_name"] and p["last_name"] else 1)
        # Keep the best profile (first after sorting)
        profiles_to_keep.append(profiles[0])
    
    # Limit to 25 profiles if we have more
    profiles_to_keep = profiles_to_keep[:25]
    
    # Now determine which profiles to delete
    keep_ids = {p["id"] for p in profiles_to_keep}
    profiles_to_delete = []
    
    for email, group in email_groups.items():
        for profile in group:
            if profile["id"] not in keep_ids:
                profiles_to_delete.append((profile["id"], profile["email"]))
    
    # Print summary
    print(f"\nKeeping {len(profiles_to_keep)} unique mock profiles:")
    for i, profile in enumerate(profiles_to_keep[:5], 1):
        print(f"  {i}. {profile['email']} (id: {profile['id']})")
    if len(profiles_to_keep) > 5:
        print(f"  ... and {len(profiles_to_keep) - 5} more")
        
    print(f"\nFound {len(profiles_to_delete)} duplicate mock profiles to delete:")
    for i, (profile_id, email) in enumerate(profiles_to_delete[:5], 1):
        print(f"  {i}. {email} (id: {profile_id})")
    if len(profiles_to_delete) > 5:
        print(f"  ... and {len(profiles_to_delete) - 5} more")
    
    # Check for confirmation
    confirm = os.environ.get("CONFIRM_DELETE", "no").lower()
    if confirm not in {"yes", "y"}:
        print("\nDeletion NOT performed. Set environment variable CONFIRM_DELETE=yes to proceed.")
        return
    
    print("\nTesting GDPR deletion with a single profile first...")
    
    def request_profile_deletion(email):
        payload = {
            "data": {
                "type": "data-privacy-deletion-job",
                "attributes": {
                    "profile": {
                        "data": {
                            "type": "profile",
                            "attributes": {
                                "email": email
                            }
                        }
                    }
                }
            }
        }
        resp = requests.post(
            f"{BASE_URL}/data-privacy-deletion-jobs/",
            headers=HEADERS,
            json=payload
        )
        return resp
    
    if profiles_to_delete:
        test_id, test_email = profiles_to_delete[0]
        print(f"Attempting GDPR-compliant deletion: {test_email}")
        r = request_profile_deletion(test_email)
        if r.status_code in (200, 202):
            print(f"✅ TEST SUCCESSFUL: Deletion requested for {test_email}")
            proceed = input(f"\nContinue deleting the remaining {len(profiles_to_delete)-1} profiles? (yes/no): ").strip().lower()
            if proceed not in ('yes', 'y'):
                print("Aborting the remaining deletions.")
                return
            # Use a user-controlled delay (default 5s) between requests
            try:
                delay = float(os.environ.get("DELETE_DELAY_SECONDS", "5"))
            except Exception:
                delay = 5
            debug = os.environ.get("DEBUG_DELETE", "no").lower() in ("yes", "y", "1", "true")
            print(f"\n[INFO] Deleting profiles with a delay of {delay} seconds between requests (set DELETE_DELAY_SECONDS env var to change).\n")
            success_count = 1
            for i, (profile_id, email) in enumerate(profiles_to_delete[1:], 1):
                resp = request_profile_deletion(email)
                if resp.status_code in (200, 202):
                    success_count += 1
                    if success_count <= 5 or success_count % 50 == 0:
                        print(f"Requested deletion: {email} ({success_count}/{len(profiles_to_delete)})")
                else:
                    msg = f"Failed to request deletion for {email}: {resp.status_code}"
                    if debug and hasattr(resp, 'text'):
                        msg += f"\nResponse body: {resp.text}"
                    print(msg)
                time.sleep(delay)
            print(f"\nSuccessfully requested deletion for {success_count} of {len(profiles_to_delete)} duplicate mock profiles.")
            print("Allow several minutes for Klaviyo to process and update your active profile count.")
        else:
            print(f"❌ TEST FAILED: Could not request deletion for {test_email}")
            print(f"Error: {r.status_code} {r.text if hasattr(r, 'text') else ''}")
            print("Aborting all deletions to avoid further errors.")
            return
    else:
        print("No profiles to delete.")
        
    print(f"You now have {len(profiles_to_keep)} unique mock profiles plus {len(real_profiles)} real profiles.")
    
if __name__ == "__main__":
    main()
