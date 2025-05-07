# ✨ Demo‑Ready PR Plan – Narrow‑Scope Reporting POC (Clara Edition)

⚠️ **ALL PRs below target a *client‑facing* demo for an email‑marketing consultant.  
Each PR must reference this document in its description.** ⚠️

The goal is to show a *live* pipeline from Klaviyo → Fivetran → BigQuery → Looker Studio, plus an optional Google Sheets export that Clara can hand to clients as an "upsell" metrics workbook.  
No mocked data; everything runs against the existing Fivetran connector & BigQuery dataset.

---

## PR 22 • BigQuery Reporting View + Permissions
**Branch:** `feature/bq_reporting_view`

| Checklist | Details |
|-----------|----------|
| ☐ | Create `sql/create_reporting_view.sql` — view `klaviyopoc.v_email_metrics` aggregating **campaign**, **event**, **list** tables to daily campaign KPIs (`send_date`, `campaign_id`, `subject`, `sends`, `unique_opens`, `unique_clicks`, `revenue`). |
| ☐ | Add `scripts/deploy_reporting_view.sh` (idempotent gcloud/bq CLI deploy). |
| ☐ | Grant dataset/table‐level `bigquery.dataViewer` to `looker_sa@<project>.iam.gserviceaccount.com` (service account used by Looker Studio). |
| ☐ | Unit test: `tests/test_reporting_view.sql` (db‑t mock) verifies column names & row count parity with source. |

**Validation:**  
`bash scripts/deploy_reporting_view.sh --dry-run` prints pending DDL; run without flag deploys; test script returns 0.

---

## PR 23 • Looker Studio Template JSON
**Branch:** `feature/looker_template_dashboard`

| Checklist | Details |
|-----------|----------|
| ☐ | Export a **Looker Studio** dashboard (line chart open‑rate 30 d, bar CTR last 5 campaigns, scorecard 7‑day revenue, table of KPIs) as `config/looker_dashboard.json`. |
| ☐ | Document one‑click **"Make a copy"** instructions in `docs/client_demo.md`. |
| ☐ | Add helper `scripts/publish_looker_template.sh` that uses gcloud docs API to update the JSON ID if project changes. |
| ☐ | Screenshot PNGs placed in `docs/img/` for slide deck. |

**Validation:**  
Reviewer imports JSON into Looker Studio, selects data source → view loads with no field errors.

---

## PR 24 • Google Sheets Exporter (Optional Upsell)
**Branch:** `feature/sheets_exporter`

| Checklist | Details |
|-----------|----------|
| ☐ | Create `src/google_sheets_export.py` – reads `v_email_metrics` view, writes to a Google Sheet tab. |
| ☐ | Accept CLI flags: `--sheet-id`, `--range-name`, `--since-days` (default 30). |
| ☐ | Uses service‑account credentials json from `GOOGLE_CREDENTIALS_JSON` env var. |
| ☐ | Unit tests with `pytest` using `gspread` & `httpretty` mocks. |

**Validation:**  
`python src/google_sheets_export.py --dry-run` logs first 5 rows; live run writes sheet & prints URL.

---

## PR 25 • Demo Orchestrator v2
**Branch:** `feature/demo_orchestrator_v2`

| Checklist | Details |
|-----------|----------|
| ☐ | Extend `scripts/run_end_to_end_demo.sh` :<br>1️⃣ Trigger Fivetran sync<br>2️⃣ Poll `connector_status` until `succeeded` (max 10 min)<br>3️⃣ Deploy reporting view (PR 22)<br>4️⃣ Refresh Looker Studio data source via API (cached extract)<br>5️⃣ Optionally export to Sheets (PR 24). |
| ☐ | Add `--skip-sheets` flag. |
| ☐ | Emit clear ✔/✖ summary and demo URLs. |
| ☐ | Integration test with `moto` (S3) and `pytest‑subprocess` to stub external calls. |

---

## PR 26 • Client Demo Docs & Slide Deck
**Branch:** `feature/client_demo_docs`

| Checklist | Details |
|-----------|----------|
| ☐ | `docs/client_demo.md` — executive run‑sheet for a 15‑min Zoom demo. |
| ☐ | `docs/client_deck.pdf` (exported from Canva/Google Slides) with 6 slides:<br>Problem → Pipeline → Dashboard shots → "Next Steps". |
| ☐ | Include QR/link to Looker Studio template & Sheets workbook. |

---

## Environment variables (add/update in `.env`)
```ini
# --- BigQuery (already present) ---
BQ_PROJECT=clara-blueprint-script-24
BQ_DATASET=klaviyopoc

# --- Looker Studio Service Account ---
LOOKER_SA_EMAIL=looker_sa@clara-blueprint-script-24.iam.gserviceaccount.com

# --- Google Sheets Export (PR 24) ---
GOOGLE_SHEET_ID=1AbC...xyz      # create sheet + share with SA
GOOGLE_SHEET_RANGE_NAME=metrics_data
GOOGLE_CREDENTIALS_JSON=/path/to/gcp-sa.json  # SA key with Sheets scopes

# --- Demo Orchestrator options ---
E2E_SANITY_TABLES=campaign,event,list          # flow optional
DEMO_DEFAULT_SINCE_DAYS=30
```

---

## Implementation order

1. **PR 22** (view) → 2. **PR 23** (dashboard) → 3. **PR 24** (Sheets) → 4. **PR 25** (orchestrator) → 5. **PR 26** (docs).
   Each PR builds on the previous; merge sequentially.

---

### Success criteria for the live demo

* **End‑to‑end script completes with exit 0**
  – shows Fivetran sync ✔, view ✔, Looker refresh ✔, Sheets export ✔/skipped.
* Looker Studio dashboard loads with **no field errors** and displays current metrics.
* Google Sheet (if run) contains last‑30‑day KPI rows and auto‑calculates open/click rates.

Once these PRs are merged & validated, Clara can walk a prospect through *"Turn on our reporting add‑on in one click, get a live dashboard + shareable sheet"* — a tangible upsell ready for pilot clients. 🚀
