import requests
import json
import os
from datetime import datetime
import config

def send_slack_message(message, blocks=None):
    """Send a message to Slack using the configured webhook URL"""
    payload = {
        "text": message
    }
    
    if blocks:
        payload["blocks"] = blocks
        
    response = requests.post(
        config.SLACK_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
    
    return response

def format_metrics_for_slack(metrics):
    """Format metrics data into Slack blocks for better presentation"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Campaign Performance Report - {datetime.now().strftime('%Y-%m-%d')}"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add metrics sections
    if metrics:
        metrics_section = {
            "type": "section",
            "fields": []
        }
        
        for key, value in metrics.items():
            metrics_section["fields"].append({
                "type": "mrkdwn",
                "text": f"*{key.title()}*\n{value}"
            })
        
        blocks.append(metrics_section)
    
    # Add report link
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*View detailed report:* <{config.LOOKER_REPORT_URL}|Looker Studio Dashboard>"
        }
    })
    
    return blocks

def send_report_to_slack(metrics, insights=None):
    """Send a formatted report to Slack with metrics and optional AI insights"""
    blocks = format_metrics_for_slack(metrics)
    
    # Add AI insights if available
    if insights:
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*AI Insights:*\n{insights}"
            }
        })
    
    # Send the message
    return send_slack_message(
        message=f"Campaign Performance Report - {datetime.now().strftime('%Y-%m-%d')}",
        blocks=blocks
    )

if __name__ == "__main__":
    # Example usage
    sample_metrics = {
        "delivered": "1,000",
        "opened": "450 (45%)",
        "clicked": "120 (12%)",
        "revenue": "$1,250.00"
    }
    
    sample_insights = """• Open rate increased by 5% compared to the previous campaign
• Click rate remained stable at 12%
• Revenue per recipient is up 15% from last week
• Best performing segment: Returning customers (52% open rate)"""
    
    # Only send if not in mock mode
    if config.MODE != "mock":
        response = send_report_to_slack(sample_metrics, sample_insights)
        print(f"Message sent to Slack: {response.status_code}")
    else:
        print("Running in mock mode. Message not sent to Slack.")
        print("Would have sent:")
        print(json.dumps(format_metrics_for_slack(sample_metrics), indent=2))
