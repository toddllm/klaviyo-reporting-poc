import os
import random
import time
from datetime import datetime

# --- Config ---
CAMPAIGN_ID = os.environ.get("CAMPAIGN_ID", "mock_campaign_123")
TEMPLATE_ID = os.environ.get("TEMPLATE_ID", "WJ3kbV")
AUDIENCE_ID = os.environ.get("AUDIENCE_ID", "YdSN6t")
NUM_PROFILES = int(os.environ.get("NUM_TEST_PROFILES", "30"))

# --- Step 2: Mock Campaign Send ---
def mock_create_send_job():
    print(f"[MOCK] Creating send job for campaign {CAMPAIGN_ID} with template {TEMPLATE_ID}...")
    job_id = f"mock_sendjob_{random.randint(10000,99999)}"
    print(f"[MOCK] Send job created: {job_id}")
    return job_id

def mock_poll_status(job_id):
    print(f"[MOCK] Polling status for send job {job_id}...")
    for status in ["draft", "sending", "sent"]:
        print(f"[MOCK] Campaign status: {status}")
        time.sleep(0.5)
    print(f"[MOCK] Campaign {CAMPAIGN_ID} sent!")

# --- Step 3: Mock Engagement Events ---
def mock_generate_events():
    print("[MOCK] Generating engagement events (opens/clicks)...")
    events = []
    for i in range(NUM_PROFILES):
        email = f"testuser{i+1}@example.com"
        delivered = True
        opened = random.random() < 0.85
        clicked = opened and (random.random() < 0.35)
        revenue = round(random.uniform(0, 120), 2) if clicked and random.random() < 0.2 else 0
        events.append({
            "email": email,
            "delivered": delivered,
            "opened": opened,
            "clicked": clicked,
            "revenue": revenue
        })
    print(f"[MOCK] Generated events for {NUM_PROFILES} profiles.")
    return events

# --- Step 4: Mock Metrics Reporting ---
def mock_report_metrics(events):
    delivered = sum(1 for e in events if e["delivered"])
    opened = sum(1 for e in events if e["opened"])
    clicked = sum(1 for e in events if e["clicked"])
    revenue = sum(e["revenue"] for e in events)
    print("\n[MOCK] --- Campaign Metrics ---")
    print(f"Delivered: {delivered}")
    print(f"Opened: {opened}")
    print(f"Clicked: {clicked}")
    print(f"Revenue: ${revenue:.2f}")
    print("Top 5 recipients:")
    for e in events[:5]:
        print(f"  {e['email']} - opened: {e['opened']}, clicked: {e['clicked']}, revenue: {e['revenue']}")

# --- Main ---
def main():
    job_id = mock_create_send_job()
    mock_poll_status(job_id)
    events = mock_generate_events()
    mock_report_metrics(events)
    print("\n[MOCK] Reporting complete. No real emails sent.")

if __name__ == "__main__":
    main()
