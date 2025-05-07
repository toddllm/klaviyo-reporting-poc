# Data‑Sanity POC — PR Drafts

This mini‑plan introduces an automated BigQuery sanity‑check step that can run:

* **locally** (`scripts/bq_sanity_check.py --env .env`)
* **as part of `run_end_to_end_demo.sh`**
* **in CI** (GitHub Actions, Circle, etc.)

Each PR is intentionally small, reviewable, and independently merge‑able.

---

## PR 17  •  BigQuery Sanity‑Check Script (Python)

**Branch** `feature/bq-sanity-check`

| Item | Description |
|------|-------------|
| **Files** | `scripts/bq_sanity_check.py` (new) |
| **Deps** | Adds `google-cloud-bigquery` and `python-dotenv` to `requirements.txt` |
| **Functionality** |<ul><li>Reads <code>BQ_PROJECT</code> and <code>BQ_DATASET</code> (plus an optional <code>TABLE_LIST</code>) from the environment.</li><li>For each table: <br>• counts rows <br>• shows latest <code>updated_at</code> timestamp (if column exists) <br>• flags empty or missing tables (exit code &gt; 0)</li></ul>|
| **CLI** |```bash
python scripts/bq_sanity_check.py --env .env --tables campaign,event,flow,list
```|
| **Unit Tests** | Uses <code>pytest</code> with <code>google-cloud-bigquery</code> stub client (no real BQ calls). |

**Validation**

1. Developer: `python scripts/bq_sanity_check.py --env .env --dry-run`
2. Reviewer: Point at a real project/dataset; verify counts & exit codes.

---

## PR 18  •  Hook Sanity Check into End‑to‑End Demo

**Branch** `feature/e2e-add-sanity-step`

| Item | Description |
|------|-------------|
| **File updated** | `scripts/run_end_to_end_demo.sh` |
| **Change** | After the ETL step succeeds, call: <br>`python scripts/bq_sanity_check.py --env .env --tables "$E2E_SANITY_TABLES"` |
| **Env** | Adds optional `E2E_SANITY_TABLES` (default `campaign,event,flow,list`). |

**Validation**

1. Run `bash scripts/run_end_to_end_demo.sh --dry-run` → should still succeed.
2. Run full demo; script fails fast if any table missing/empty.

---

## PR 19  •  CI Job: Nightly Sanity Check

**Branch** `feature/ci-bq-sanity`

| Item | Description |
|------|-------------|
| **File** | `.github/workflows/bq_sanity.yml` |
| **Job** | Nightly (UTC 03:00) <br>• Checkout repo <br>• `pip install -r requirements.txt` <br>• Decrypt & load `.env.ci` secrets (BQ project/dataset, service‑account key) <br>• Run `python scripts/bq_sanity_check.py` |
| **Fail‑fast** | Job fails if any required table is missing or empty. |

---

## PR 20  •  Docs & Env Template Update

**Branch** `feature/docs-bq-sanity`

| Item | Description |
|------|-------------|
| **Files** |<ul><li>`docs/bq_sanity_check.md` (usage & troubleshooting)</li><li>`env_template` updated with <code>BQ_PROJECT</code>, <code>BQ_DATASET</code>, <code>E2E_SANITY_TABLES</code></li></ul>|

---

### Required `.env` entries (add if missing)

```ini
# --- BigQuery ---
BQ_PROJECT=clara-blueprint-script-24
BQ_DATASET=klaviyo_reporting    # or whatever Fivetran created
# Comma‑separated list of tables for sanity check
E2E_SANITY_TABLES=campaign,event,flow,list
```

*(The Python script auto‑auths via Application Default Credentials or
`GOOGLE_APPLICATION_CREDENTIALS` pointing at a JSON key.)*

---

### Why Python over Bash?

* **Better portability** (same code runs in macOS, Linux, CI).
* **Easier extensions** (e.g., null‑check critical columns,
  assert row count > N, etc.).
* **First‑class BigQuery client** with automatic retries/back‑off.
