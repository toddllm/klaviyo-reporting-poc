import os
import random
from datetime import datetime, timedelta

AUDIENCE_ID = os.environ.get("AUDIENCE_ID", "YdSN6t")

FIRST_NAMES = [
    "Jessica", "Roger", "Emily", "Joshua", "Rachel", "Kimberly", "Mary", "Joshua", "Michael", "Vicki",
    "Logan", "Eric", "Wendy", "Benjamin", "Elizabeth", "Christian", "John", "Ryan", "Gregory", "Misty"
]
LAST_NAMES = [
    "Farmer", "Payne", "Roman", "Thomas", "Lyons", "Crawford", "Vaughn", "Alexander", "Rodriguez", "Porter",
    "Avila", "Jenkins", "Lawson", "Black", "Hamilton", "Flowers", "Cox", "Stuart", "Adams", "Sullivan"
]
CATEGORIES = ["Apparel", "Electronics", "Beauty", "Home", "Toys", "Sports", "Books"]

def random_email(first, last):
    domain = random.choice(["example.com", "shop.com", "store.com"])
    return f"{first.lower()}.{last.lower()}.{random.randint(1000,9999)}@{domain}"

def random_profile():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = random_email(first, last)
    total_spent = round(random.uniform(10, 1000), 2)
    last_purchase = (datetime.now() - timedelta(days=random.randint(1, 120))).isoformat()
    favorite = random.choice(CATEGORIES)
    return {
        "$first_name": first,
        "$last_name": last,
        "$email": email,
        "total_spent": total_spent,
        "last_purchase_at": last_purchase,
        "favorite_category": favorite
    }

def fake_upsert_profile(profile):
    fake_id = f"mock_{profile['$first_name'].lower()}_{profile['$last_name'].lower()}_{random.randint(10000,99999)}"
    print(f"[MOCK] Upserted profile: {profile['$email']} (id: {fake_id})")
    return fake_id

def fake_subscribe_to_list(profile_id):
    print(f"[MOCK] Subscribed {profile_id} to list {AUDIENCE_ID}")

def main():
    num_profiles = int(os.environ.get("NUM_TEST_PROFILES", "30"))
    print(f"[MOCK] Seeding {num_profiles} test profiles...")
    ids = []
    for _ in range(num_profiles):
        profile = random_profile()
        pid = fake_upsert_profile(profile)
        fake_subscribe_to_list(pid)
        ids.append(pid)
    print(f"[MOCK] Seeded {len(ids)} profiles and subscribed to list {AUDIENCE_ID}.")
    print("[MOCK] No emails or real API calls were made.")

if __name__ == "__main__":
    main()
