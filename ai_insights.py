import os
import random
from datetime import datetime

# Simulate pulling yesterday's metrics (in real use, this would come from BigQuery or a CSV)
def get_mock_metrics():
    delivered = 30
    opened = 26
    clicked = 7
    revenue = 119.36
    campaign_id = os.environ.get("CAMPAIGN_ID", "mock_campaign_123")
    date = datetime.now().strftime("%Y-%m-%d")
    return {
        "date": date,
        "campaign_id": campaign_id,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "revenue": revenue
    }

# POC: Generate AI insights without OpenAI
# When ready, just replace the mock_insight function with a real OpenAI call

def mock_insight(metrics):
    open_rate = metrics["opened"] / metrics["delivered"]
    click_rate = metrics["clicked"] / metrics["delivered"]
    revenue_per = metrics["revenue"] / metrics["delivered"]
    bullets = [
        f"Open rate was {open_rate:.0%}, indicating strong subject line or engaged audience.",
        f"Click rate was {click_rate:.0%}, suggesting {('good' if click_rate > 0.2 else 'room for improvement')} in content relevance.",
        f"Average revenue per recipient was ${revenue_per:.2f}."
    ]
    return bullets

def main():
    metrics = get_mock_metrics()
    print("[AI INSIGHTS] Metrics for campaign {} on {}:".format(metrics["campaign_id"], metrics["date"]))
    for k, v in metrics.items():
        if k not in ("date", "campaign_id"):
            print(f"  {k}: {v}")
    print("\n[AI INSIGHTS] Automated summary:")
    for bullet in mock_insight(metrics):
        print(f"- {bullet}")
    print("\n[AI INSIGHTS] (POC: Replace with OpenAI call when ready)")

if __name__ == "__main__":
    main()
