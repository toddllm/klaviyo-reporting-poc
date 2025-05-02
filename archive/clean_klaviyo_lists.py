"""Utility script to clean up duplicate / test lists in Klaviyo.

SAFE GUARDS:
• Keeps any list that is currently referenced by an existing campaign.
• Keeps any list whose name does NOT start with a known test prefix (Mock_, Test_, Isolated_, Working_).
• Keeps any list explicitly whitelisted, e.g., "Email List".
• Deletes ONLY lists that match a test prefix AND are not referenced by any campaign.
"""
import os
import requests
from collections import defaultdict

BASE_URL = "https://a.klaviyo.com/api"
REVISION = "2025-04-15"


def get_api_key():
    with open("private-api-key.txt") as f:
        return f.read().strip()

HEADERS_JSON = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "revision": REVISION,
    "Authorization": f"Klaviyo-API-Key {get_api_key()}"
}

# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------

def fetch_all_lists():
    url = f"{BASE_URL}/lists/"
    results = []
    while url:
        r = requests.get(url, headers=HEADERS_JSON)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("data", []))
        url = data.get("links", {}).get("next")
    return results


def fetch_all_campaigns():
    # We only need email campaigns
    url = f"{BASE_URL}/campaigns/?filter=equals(messages.channel,'email')"
    results = []
    while url:
        r = requests.get(url, headers=HEADERS_JSON)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("data", []))
        url = data.get("links", {}).get("next")
    return results


# ---------------------------------------------------------------------------
# Main clean-up logic
# ---------------------------------------------------------------------------

def main():
    protected_list_ids = set()

    # 1. Keep lists referenced by ANY campaign still in account
    campaigns = fetch_all_campaigns()
    for c in campaigns:
        audiences = c["attributes"].get("audiences", {})
        for lid in audiences.get("included", []):
            protected_list_ids.add(lid)
        for lid in audiences.get("excluded", []):
            protected_list_ids.add(lid)

    # 2. Explicitly protected by name
    WHITELIST_NAMES = {"Email List", "Newsletter", "Master Audience"}

    # 3. Determine deletable lists
    TEST_PREFIXES = ("Mock_", "Test_", "Isolated_", "Working_")

    lists = fetch_all_lists()
    delete_targets = []
    for l in lists:
        lid = l["id"]
        name = l["attributes"]["name"]
        if lid in protected_list_ids:
            continue  # referenced by campaign
        if name in WHITELIST_NAMES:
            continue
        if name.startswith(TEST_PREFIXES):
            delete_targets.append((lid, name))

    if not delete_targets:
        print("No lists need deletion – everything is clean!")
        return

    print("The following lists will be DELETED (not referenced by active campaigns):")
    for lid, name in delete_targets:
        print(f"  • {name} (id: {lid})")

    confirm = os.environ.get("CONFIRM_DELETE", "no").lower()
    if confirm not in {"yes", "y"}:
        print("\nDeletion NOT performed. Set environment variable CONFIRM_DELETE=yes to proceed.")
        return

    # Perform deletions
    for lid, name in delete_targets:
        url = f"{BASE_URL}/lists/{lid}"
        r = requests.delete(url, headers=HEADERS_JSON)
        if r.status_code in (200, 204):
            print(f"Deleted {name} (id: {lid})")
        else:
            print(f"FAILED to delete {name} (id: {lid}): {r.status_code} {r.text}")


if __name__ == "__main__":
    main()
