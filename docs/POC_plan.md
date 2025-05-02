# POC Plan for Automated Reporting & AI Insights

---

## 🧭 End-to-End POC: Comprehensive Plan & Status

### 1. Goals

**Clara’s objectives:**
- **Save time** by automating weekly email performance reporting.
- **Generate AI-driven insights** from campaign metrics.
- **Deliver clean, auto-sent updates** to clients (Slack/email).

A successful POC must demonstrate that we can:
- ✅ Fetch Klaviyo campaign data (opens, clicks, revenue).
- ✅ Surface that data in a dashboard (Looker Studio).
- ✅ Produce an automated plain-English summary.
- ✅ Chain the full process without manual steps.

---

### 2. Environment & Config

**Set up environment variables:**
This ensures all scripts can be run both locally and in CI/CD.

```bash
export KLAVIYO_API_KEY="your-klaviyo-private-key"
export AUDIENCE_ID="your-list-id"
export CAMPAIGN_ID="your-campaign-id"
export TEMPLATE_ID="your-template-id"
export NUM_TEST_PROFILES=5
export MODE=mock  # or MODE=real for actual API calls
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/<YOUR_WEBHOOK>"
export LOOKER_REPORT_URL="https://datastudio.google.com/reporting/<REPORT_ID>"
```

**Alternative:** Use a `.env` file and load with `python-dotenv`.

```env
KLAVIYO_API_KEY=pk_xxx
AUDIENCE_ID=YdSN6t
CAMPAIGN_ID=AbCdEf
TEMPLATE_ID=WJ3kbV
NUM_TEST_PROFILES=5
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/<YOUR_WEBHOOK>
LOOKER_REPORT_URL=https://datastudio.google.com/reporting/<REPORT_ID>
```

**Domain sandbox:** Use a disposable sending domain under your DNS, and configure SPF/DKIM in Klaviyo to ensure test sends leave the account without impacting your primary domain's deliverability.

---

### 3. API Edge Cases & Gotchas

> **Note:** For detailed API usage guidelines, see [API Usage Guidelines](api_usage.md)

- **Template Assignment:** Use the documented endpoint `POST /api/campaign-message-assign-template/` with payload:
  ```json
  { "data": { "type": "campaign-message-assign-template", "attributes": { "campaign_id": "<CAMPAIGN_ID>", "template_id": "<TEMPLATE_ID>" }, "relationships": { "template": { "data": { "type": "template", "id": "<TEMPLATE_ID>" } } } } }
  ```
  Do not use undocumented routes.

- **Send Job Call:** Use `POST /api/campaign-send-jobs/` with header `Klaviyo-Api-Version: 2025-04-15` and payload leveraging `relationships`:
  ```json
  { "data": { "type": "campaign-send-job", "relationships": { "campaign": { "data": { "type": "campaign", "id": "<CAMPAIGN_ID>" } } } } }
  ```

- **Relationships Object Requirement:** ⚠️ The `relationships` object is **required** in many API payloads and is a common source of errors. Always include the full relationships structure as shown in the examples above, even if it seems redundant with information in the attributes. Omitting this structure will result in 400 Bad Request errors that can be difficult to debug.

- **Metric Aggregates:** Numeric `metric_id` is required. Look up IDs via `GET /api/metrics/?filter=equals(name,'<Metric Name>')` and cache results in `.metric_ids.json`.

- **Event Injection:** Only custom events can be injected reliably and will not appear in aggregate metrics. **Option B is load-test only**; default to Option A for POC metrics.

- **Preview vs Full Send:** A preview send logs only under “Email Preview Send.” For aggregate metrics, perform a **full send** (Send Now) to a list (size=1 is fine) and then pause the campaign.
- **Date Handling:** Always use ISO 8601 UTC format for date parameters (e.g., `2025-05-01` for May 1st, 2025). Explicitly use UTC in your code: `datetime.datetime.now(UTC)` instead of `datetime.datetime.now()`. Note that `datetime.datetime.utcnow()` is deprecated in newer Python versions.

- **API Version Consistency:** ⚠️ Always include the `Klaviyo-Api-Version: 2025-04-15` header in **all** API requests to ensure consistent behavior, especially for newer endpoints. Missing this header is a common cause of unexpected API behavior and errors.
---

### 4. Profile Creation (`seed_profiles.py`)

**What it does:**
- Generates N realistic test profiles (first/last/email/total_spent/etc).
- Subscribes them to a Klaviyo list.
- Supports both mocked and real API modes.

**Sample code:**
```python
def random_profile():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = f"{first.lower()}.{last.lower()}.{random.randint(1000,9999)}@example.com"
    return {
        "$first_name": first,
        "$last_name": last,
        "$email": email,
        "total_spent": round(random.uniform(10, 1000), 2),
        "last_purchase_at": (datetime.now() - timedelta(days=random.randint(1, 120))).isoformat(),
        "favorite_category": random.choice(CATEGORIES)
    }
```

**How to run:**
```bash
python seed_profiles.py
```

**What to check:**
- Profiles appear in Klaviyo (if in real mode).
- Output confirms profile creation and list subscription.

---

### 5. Campaign Creation

**Manual (UI):**
- Go to Klaviyo > Campaigns > Create Campaign.
- Select your test list, template, subject, and sender.
- Save and note the campaign ID from the URL.

**API Example:**
```bash
curl -X POST "https://a.klaviyo.com/api/campaigns/" \
  -H "Authorization: Klaviyo-API-Key $KLAVIYO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "list_id": "YdSN6t",
        "template_id": "WJ3kbV",
        "subject": "Test Campaign",
        "from_email": "demo@yourdomain.com"
      }'
```
- Save the returned `id` as `CAMPAIGN_ID`.

**Template Assignment & Send Job:**
Use the canonical endpoint **before** creating a send job:

```bash
curl -X POST "https://a.klaviyo.com/api/campaign-message-assign-template/" \
  -H "Authorization: Klaviyo-API-Key $KLAVIYO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "data": {
          "type": "campaign-message-assign-template",
          "attributes": {
            "campaign_id": "'$CAMPAIGN_ID'",
            "template_id": "'$TEMPLATE_ID'"
          }
        }
      }'
```
Then create a send job (API version 2025-04-15):

```bash
curl -X POST "https://a.klaviyo.com/api/campaign-send-jobs/" \
  -H "Authorization: Klaviyo-API-Key $KLAVIYO_API_KEY" \
  -H "Klaviyo-Api-Version: 2025-04-15" \
  -H "Content-Type: application/json" \
  -d '{
        "data": {
          "type": "campaign-send-job",
          "relationships": {
            "campaign": {"data": {"type": "campaign", "id": "'$CAMPAIGN_ID'"}}
          }
        }
      }'
```
> **Note:** Use a **full send** (Send Now) to your list (size = 1 is fine) to generate aggregate metrics, then pause the campaign after the first message leaves the queue.

---

### 6. Simulating/Generating Events

**Option A: Manual**
- Send a preview/test campaign to your test profile.
- Open the email and click a link (generates real events).

**Option B (load-test only)**
- Implement `inject_events.py`:
    - Use Klaviyo’s `/events/` API to POST events:
    ```python
    import requests, os
    BASE_URL = "https://a.klaviyo.com/api/events/"
    headers = {"Authorization": f"Klaviyo-API-Key {os.environ['KLAVIYO_API_KEY']}", "Content-Type": "application/json"}
    payload = {
      "data": {
        "type": "event",
        "attributes": {
          "metric": {"data": {"type": "metric", "attributes": {"name": "Opened Email"}}},
          "profile": {"data": {"type": "profile", "attributes": {"email": "test@example.com"}}},
          "properties": {"campaign_id": os.environ["CAMPAIGN_ID"]}
        }
      }
    }
    resp = requests.post(BASE_URL, headers=headers, json=payload)
    print(resp.status_code, resp.text)
    ```
    - Loop over your test profiles and event types as needed.

**Note:** Mass-injected custom events do **not** appear in Klaviyo dashboards or aggregate endpoints; use Option B only for load/unit tests.
**Recommendation:** Default to **Option A** (preview + manual open/click) for real metrics unless you validate Option B.
**Event naming:** Use custom metric names (e.g., `"Demo Open"`) and ensure `ai_insights.py` processes both system & custom metrics.

---

### 7. Fetching Metrics (`fetch_metrics.py`)

**Purpose:**
- Pull open/click/revenue data for your campaign from Klaviyo.
- Output to `metrics.csv` for dashboarding.

**Metric ID lookup**
Before aggregating, fetch numeric IDs of required metrics:

```python
import requests, json, os
headers = {"Authorization": f"Klaviyo-API-Key {os.environ['KLAVIYO_API_KEY']}"}
names = ["Opened Email", "Clicked Email", "Placed Order"]
metric_ids = {}
for name in names:
    resp = requests.get(
        "https://a.klaviyo.com/api/metrics/", headers=headers,
        params={"filter": f"equals(name,'{name}')"}
    )
    data = resp.json().get("data", [])
    metric_ids[name] = data[0]["id"] if data else None
with open('.metric_ids.json', 'w') as f:
    json.dump(metric_ids, f)
```

**Sample code:**
```python
import requests, os, csv
API_KEY = os.environ["KLAVIYO_API_KEY"]
CAMPAIGN_ID = os.environ["CAMPAIGN_ID"]
headers = {"Authorization": f"Klaviyo-API-Key {API_KEY}"}
resp = requests.get(
    "https://a.klaviyo.com/api/metric-aggregates/",
    headers=headers,
    params={
        "measure": "unique",
        "metric_id": "<metric_id>",
        "start_date": (datetime.utcnow().date() - timedelta(days=7)).isoformat(),
        "end_date": datetime.utcnow().date().isoformat(),
        "filters": f"[['equals','campaign_id','{CAMPAIGN_ID}']]"
    }
)
data = resp.json()
with open('metrics.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["date","delivered","opened","clicked","revenue"])
    writer.writeheader()
    for row in data["data"]:
        writer.writerow({ ... })  # Map API fields to CSV columns
```

---

### 8. Dashboarding (Looker Studio)

**Steps:**
- Upload or sync `metrics.csv` to Google Sheets or BigQuery.
- Create a Looker Studio report:
    - Add charts for opens, clicks, revenue.
    - Filter by campaign/date as needed.
- Save and share the dashboard link.

**Auto-refresh Google Sheet:** Use `gspread` to update after each run:
```python
import gspread
gc = gspread.service_account(filename='creds.json')
sh = gc.open("Metrics Sheet")
ws = sh.sheet1
ws.clear()
ws.update([ ["date","delivered","opened","clicked","revenue"] ] + rows, value_input_option='RAW')
```
**Sheet named-range gotcha:** After first upload, set Data > Named ranges > metrics to `A1:E1000`. Subsequent `gspread.update()` calls will stay inside that range.

---

### 9. AI Insights (`ai_insights.py`)

**Purpose:**
- Generate a plain-English summary of campaign performance.

```python
import openai, os, csv, json
openai.api_key = os.environ.get('OPENAI_API_KEY')
with open('metrics.csv') as f:
    metrics = next(csv.DictReader(f))
prompt = f"""
You are an email-marketing analyst. Summarise yesterday’s campaign in 4 bullets:
- compare open + click rate with the previous campaign (provide % diff)
- flag if revenue per recipient dropped >20%
Metrics JSON:
{json.dumps(metrics)}
"""
response = openai.Completion.create(
    engine='gpt-3.5-turbo', prompt=prompt, max_tokens=200
)
print(response.choices[0].text.strip())
```
- Fallback to mock summary if `OPENAI_API_KEY` is not set.

**Output formats:** Provide both plain text and Markdown/HTML for easy copy-paste:
```python
md_summary = f"- Open rate: {open_rate}%\n- Click rate: {click_rate}%"
print(md_summary)
html = markdown_to_html(md_summary)
with open('summary.html','w') as f: f.write(html)
```

---

### 10. Orchestration (`run_poc.sh` & helpers)

Use a structured pipeline script:

```bash
run_poc.sh
└── 01 seed_profiles.py           # MODE guard
└── 02 create_send_campaign.py    # template assign + send job
└── 03 simulate_open.py           # optional, load-test only
└── 04 fetch_metrics.py
└── 05 ai_insights.py
└── 06 push_to_sheet.py           # optional
└── 07 post_to_slack.py           # optional

# Poll for metrics readiness to avoid race conditions
until python fetch_metrics.py --dry-run; do
  echo "Metrics not ready, sleeping 60s…"
  sleep 60
done
python fetch_metrics.py
```

**How to automate:**
- Add to CRON for weekly runs:
    ```
    0 9 * * MON /path/to/run_poc.sh
    ```
**Fail-safes:** Wrap real API calls with `if MODE == "real":` guards to prevent accidental sends.

---

### 11. Clean Code & Repeatability

- Centralize config in `config.py` or `.env`.
- Use CLI flags for mock/real mode.
- Add docstrings and usage examples to each script.
- Keep a clear README with:
    - Setup instructions
    - Example commands
    - Troubleshooting tips
- Add `.env.example` with placeholder keys.
- Guard external POSTs with `if MODE != "mock":`.

---

### 12. Deliverables & Review Checklist

- [ ] Metric lookup helper (`get_metric_id(name)` in `fetch_metrics.py`)
- [ ] `create_send_campaign.py` (template assign + send job)
- [ ] `poll_for_metrics.sh` wrapper for fetch retry
- [ ] README call-flow diagram (seed → send → fetch → GPT → Looker)
- [ ] Screenshot pack for Clara (Klaviyo overview, Looker dashboard, Slack summary)
- [ ] Add `SLACK_WEBHOOK_URL` & `LOOKER_REPORT_URL` to `.env.example`

### 13. What to tell Clara at demo time
> “Here’s the Looker link at $LOOKER_REPORT_URL. The numbers update automatically every Monday via Slack. If you add a new client, run `seed_profiles.py --real` once; then it’s hands-off.”

---

## 🧱 POC Stack Overview

| Layer            | Tool                    | Role                                                     |
|------------------|-------------------------|----------------------------------------------------------|
| Data source      | Klaviyo API             | Pull real or injected event data                         |
| Data storage     | CSV / Google Sheets     | Temporary store for Looker Studio                       |
| Dashboard        | Looker Studio           | Visualize opens, clicks, revenue                        |
| Insight layer    | Python script (+ OpenAI)| Generate summary bullets based on metric trends         |
| Delivery         | Slack webhook / SMTP    | Send summary to Clara or client                          |

---

## 🚀 Summary & Next Steps

**Success Criteria:** Clara receives a weekly AI report automatically with no manual intervention.

**Immediate Next Steps:**
1. Confirm default settings: `NUM_TEST_PROFILES=5`, `MODE=mock`.
2. Use Option A: send preview + manual open/click to generate real metrics.
3. Update campaign flow: assign template & create send job via API (`/campaign-message-assign-template` then `/campaign-send-jobs/`).
4. Implement Google Sheet auto-refresh (gspread) post-metrics fetch.
5. Enhance `ai_insights.py`: enrich prompts, output plain text + Markdown/HTML.
6. Create `send_summary.py` to deliver the AI summary to Slack or email.
7. Add `.env.example` and fail-safe guards (`if MODE != "mock":`).
8. Record a Loom walkthrough and share with Clara.

*End of POC plan.*
