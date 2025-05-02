# Klaviyo API Usage Guidelines

## API Version Headers

### Klaviyo-Api-Version Header

All API requests to Klaviyo should include the `Klaviyo-Api-Version` header to ensure compatibility and consistent behavior.

```
Klaviyo-Api-Version: 2025-04-15
```

**Why this is important:**
- Ensures your code works with a specific API version even when Klaviyo makes updates
- Prevents unexpected breaking changes in your integration
- Required for certain endpoints like campaign send jobs

**Example usage:**

```python
headers = {
    "Authorization": f"Klaviyo-API-Key {os.environ['KLAVIYO_API_KEY']}",
    "Content-Type": "application/json",
    "Klaviyo-Api-Version": "2025-04-15"
}
```

```bash
curl -X POST "https://a.klaviyo.com/api/campaign-send-jobs/" \
  -H "Authorization: Klaviyo-API-Key $KLAVIYO_API_KEY" \
  -H "Klaviyo-Api-Version: 2025-04-15" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

## Relationship Objects in Payloads

Many Klaviyo API endpoints require properly formatted relationship objects in the payload. These are essential for correctly associating resources.

### Template Assignment Example

```json
{
  "data": {
    "type": "campaign-message-assign-template",
    "attributes": {
      "campaign_id": "<CAMPAIGN_ID>",
      "template_id": "<TEMPLATE_ID>"
    },
    "relationships": {
      "template": {
        "data": {
          "type": "template",
          "id": "<TEMPLATE_ID>"
        }
      }
    }
  }
}
```

### Campaign Send Job Example

```json
{
  "data": {
    "type": "campaign-send-job",
    "relationships": {
      "campaign": {
        "data": {
          "type": "campaign",
          "id": "<CAMPAIGN_ID>"
        }
      }
    }
  }
}
```

## Common API Edge Cases

### Template Assignment Before Send

Always assign a template to a campaign before creating a send job. There should be a delay or status check between these operations:

```python
# 1. Assign template
template_response = requests.post("https://a.klaviyo.com/api/campaign-message-assign-template/", headers=headers, json=template_payload)

# 2. Wait for template assignment to propagate
time.sleep(10)  # Simple approach

# Or poll for status (preferred approach)
def wait_for_campaign_ready(campaign_id):
    while True:
        status_response = requests.get(f"https://a.klaviyo.com/api/campaigns/{campaign_id}", headers=headers)
        status = status_response.json().get("status")
        if status == "ready":
            return True
        time.sleep(2)

# 3. Create send job only after template is assigned
send_response = requests.post("https://a.klaviyo.com/api/campaign-send-jobs/", headers=headers, json=send_payload)
```

### Metric ID Lookup and Caching

Metric IDs are required for aggregation endpoints and should be looked up by name and cached:

```python
def get_metric_id(name, force_refresh=False):
    """Get metric ID by name, with caching"""
    cache_file = ".metric_ids.json"
    
    # Try to load from cache first
    if not force_refresh and os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            try:
                metric_ids = json.load(f)
                if name in metric_ids and metric_ids[name]:
                    return metric_ids[name]
            except json.JSONDecodeError:
                pass  # Cache file is invalid, continue to API lookup
    
    # Lookup via API
    headers = {
        "Authorization": f"Klaviyo-API-Key {os.environ['KLAVIYO_API_KEY']}",
        "Klaviyo-Api-Version": "2025-04-15"
    }
    response = requests.get(
        "https://a.klaviyo.com/api/metrics/", 
        headers=headers,
        params={"filter": f"equals(name,'{name}')"}
    )
    
    data = response.json().get("data", [])
    metric_id = data[0]["id"] if data else None
    
    # Update cache
    metric_ids = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                metric_ids = json.load(f)
        except json.JSONDecodeError:
            pass  # Start with empty dict if cache is corrupted
    
    metric_ids[name] = metric_id
    
    with open(cache_file, 'w') as f:
        json.dump(metric_ids, f)
    
    return metric_id
```

## Date Handling

Always use ISO 8601 UTC format for date parameters:

```python
start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).date().isoformat()
end_date = datetime.datetime.utcnow().date().isoformat()

# Example: "2025-05-01" for May 1st, 2025
```

Specify the timezone explicitly in your code to avoid confusion:

```python
# Bad - uses local timezone
start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()

# Good - explicitly uses UTC
start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).date().isoformat()
```
