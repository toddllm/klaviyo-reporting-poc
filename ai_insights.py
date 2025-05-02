import os
import random
import csv
import json
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

# Load metrics from CSV if available
def load_metrics_from_csv(file_path="metrics.csv"):
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            metrics = next(reader)
            # Convert string values to appropriate types
            for key in ['delivered', 'opened', 'clicked']:
                if key in metrics:
                    metrics[key] = int(metrics[key])
            if 'revenue' in metrics:
                metrics['revenue'] = float(metrics['revenue'])
            return metrics
    except (FileNotFoundError, StopIteration):
        return get_mock_metrics()

# POC: Generate AI insights without OpenAI
# When ready, just replace the mock_insight function with a real OpenAI call
def mock_insight(metrics, prev_metrics=None):
    open_rate = metrics["opened"] / metrics["delivered"]
    click_rate = metrics["clicked"] / metrics["delivered"]
    revenue_per = metrics["revenue"] / metrics["delivered"]
    
    # Calculate comparisons with previous campaign if available
    open_rate_diff = ""
    click_rate_diff = ""
    revenue_drop_flag = ""
    
    if prev_metrics:
        prev_open_rate = prev_metrics["opened"] / prev_metrics["delivered"]
        prev_click_rate = prev_metrics["clicked"] / prev_metrics["delivered"]
        prev_revenue_per = prev_metrics["revenue"] / prev_metrics["delivered"]
        
        open_diff_pct = ((open_rate - prev_open_rate) / prev_open_rate) * 100
        click_diff_pct = ((click_rate - prev_click_rate) / prev_click_rate) * 100
        
        open_rate_diff = f" ({open_diff_pct:+.1f}% compared to previous campaign)"
        click_rate_diff = f" ({click_diff_pct:+.1f}% compared to previous campaign)"
        
        if (revenue_per < prev_revenue_per * 0.8):  # 20% drop check
            revenue_drop_flag = " ⚠️ This is a significant drop (>20%) from the previous campaign."
    
    bullets = [
        f"Open rate was {open_rate:.1%}{open_rate_diff}, indicating strong subject line or engaged audience.",
        f"Click rate was {click_rate:.1%}{click_rate_diff}, suggesting {('good' if click_rate > 0.2 else 'room for improvement')} in content relevance.",
        f"Average revenue per recipient was ${revenue_per:.2f}.{revenue_drop_flag}"
    ]
    return bullets

def generate_html_summary(bullets, metrics):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Campaign Performance Summary</title>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #333; }}
ul {{ margin-top: 20px; }}
li {{ margin-bottom: 10px; }}
.metrics {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 20px; }}
.metrics-title {{ font-weight: bold; margin-bottom: 10px; }}
.metric {{ margin-left: 20px; }}
</style>
</head>
<body>
<h1>Campaign Performance Summary</h1>
<p>Campaign ID: {metrics['campaign_id']} | Date: {metrics['date']}</p>
<ul>"""
    
    for bullet in bullets:
        html += f"\n  <li>{bullet}</li>"
    
    html += "\n</ul>\n"
    html += """<div class="metrics">
<div class="metrics-title">Raw Metrics:</div>"""
    
    for k, v in metrics.items():
        if k not in ("date", "campaign_id"):
            html += f"\n  <div class=\"metric\">{k}: {v}</div>"
    
    html += "\n</div>\n</body>\n</html>"
    
    return html

def main():
    metrics = load_metrics_from_csv()
    print("[AI INSIGHTS] Metrics for campaign {} on {}:".format(metrics["campaign_id"], metrics["date"]))
    for k, v in metrics.items():
        if k not in ("date", "campaign_id"):
            print(f"  {k}: {v}")
    
    # Generate insights
    bullets = mock_insight(metrics)
    
    # Print text summary
    print("\n[AI INSIGHTS] Automated summary:")
    for bullet in bullets:
        print(f"- {bullet}")
    print("\n[AI INSIGHTS] (POC: Replace with OpenAI call when ready)")
    
    # Generate and save HTML summary
    html_summary = generate_html_summary(bullets, metrics)
    with open('summary.html', 'w') as f:
        f.write(html_summary)
    print("\n[AI INSIGHTS] HTML summary saved to summary.html")

if __name__ == "__main__":
    main()
