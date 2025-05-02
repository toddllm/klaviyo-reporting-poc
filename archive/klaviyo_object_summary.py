import requests
import json
import os

def get_api_key():
    with open("private-api-key.txt") as f:
        return f.read().strip()

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Accept": "application/vnd.api+json",
    "revision": "2025-04-15",
    "Authorization": f"Klaviyo-API-Key {get_api_key()}"
}

def fetch_list(name):
    url = f"{BASE_URL}/lists/?filter=equals(name,'{name}')"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def fetch_template(name):
    url = f"{BASE_URL}/templates/?filter=equals(name,'{name}')"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def fetch_campaign(campaign_id):
    url = f"{BASE_URL}/campaigns/{campaign_id}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def fetch_campaign_messages(campaign_id):
    url = f"{BASE_URL}/campaigns/{campaign_id}/campaign-messages"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def print_markdown_summary():
    list_name = "Mock_Reporting_List"
    template_name = "Mock_Automation_Template"
    # Fetch list
    list_data = fetch_list(list_name)
    # Use the most recently created list with this name
    lists = list_data.get("data", [])
    list_obj = lists[-1] if lists else None
    # Fetch template
    template_data = fetch_template(template_name)
    template_obj = template_data.get("data", [])[0] if template_data.get("data") else None
    # Print summary
    print("""
# Klaviyo Campaign Automation: Object Summary

## 1. List Object: `Mock_Reporting_List`

**Purpose:**
A list is a collection of profiles (recipients) that you will target with your campaign.

**API Example:**
```http
GET /api/lists/?filter=equals(name,'Mock_Reporting_List')
Headers: Accept: application/vnd.api+json, revision: 2025-04-15
```

**Sample Response:**
```json
%s
```
**Key Field:**
- `id` (e.g., `%s`): Used as the audience for your campaign.

---

## 2. Template Object: `Mock_Automation_Template`

**Purpose:**
A template defines the HTML (and optionally text/AMP) content structure for your campaign message.

**API Example:**
```http
GET /api/templates/?filter=equals(name,'Mock_Automation_Template')
Headers: Accept: application/vnd.api+json, revision: 2025-04-15
```

**Sample Response:**
```json
%s
```
**Key Field:**
- `id` (e.g., `%s`): Used to assign the template to a campaign message.

---
""" % (
        json.dumps(list_obj, indent=2) if list_obj else "{}",
        list_obj.get("id") if list_obj else "",
        json.dumps(template_obj, indent=2) if template_obj else "{}",
        template_obj.get("id") if template_obj else ""
    ))
    # If you want to go further, prompt the user for a campaign ID or scan for recent campaigns
    # For demonstration, let's print the most recent campaign message for a known campaign id
    campaign_id = os.environ.get("KLAVIYO_CAMPAIGN_ID", "01JT645JWWK77F1ZD9KT96R2TV")
    try:
        campaign_msg_data = fetch_campaign_messages(campaign_id)
        campaign_msg_obj = campaign_msg_data.get("data", [])[0] if campaign_msg_data.get("data") else None
        print("""
## 3. Campaign Message Object

**Purpose:**
A campaign message is the actual message sent to recipients. It is associated with a campaign and a template.

**API Example:**
```http
GET /api/campaigns/%s/campaign-messages
Headers: Accept: application/vnd.api+json, revision: 2025-04-15
```

**Sample Response:**
```json
%s
```
**Key Fields:**
- `id`: %s (unique message ID)
- `template.id`: %s — the template currently assigned to this message.

---
""" % (
            campaign_id,
            json.dumps(campaign_msg_obj, indent=2) if campaign_msg_obj else "{}",
            campaign_msg_obj.get("id") if campaign_msg_obj else "",
            campaign_msg_obj.get("relationships", {}).get("template", {}).get("data", {}).get("id") if campaign_msg_obj else ""
        ))
    except Exception as e:
        print("\nCould not fetch campaign message details: %s\n" % str(e))
    print("""
## How They Connect

1. **List**: You create or fetch a list (`Mock_Reporting_List`) to use as your audience.
2. **Template**: You create or fetch a template (`Mock_Automation_Template`) containing your HTML.
3. **Campaign**: You create a campaign, specifying the list as the audience.
4. **Campaign Message**: Created as part of the campaign, but initially has no template.
5. **Template Assignment**: You assign the template to the campaign message using the special endpoint.

---

If you want to see the exact JSON returned for any other object or relationship, or want to walk through the creation of a new campaign step-by-step with live API calls, let me know!
""")

if __name__ == "__main__":
    print_markdown_summary()
