# 📦 POC Demo PR Plan (Phase 2)  
**Goal:** deliver one or more fully‑working proof‑of‑concept demos that pull *live* Klaviyo data (via either Supermetrics or Klaviyo API), load it through our ETL, store the output artifacts, and send an automated summary email through AWS SES using a domain that already exists in our AWS account.  
**All PRs below extend the original "Narrow Scope POC PR Plan".  Reference that plan URL in every PR description.**

---

### PR 7 (merged separately – no action here)  
`feature/supermetrics-klaviyo-pull` – **already in flight**

---

## PR 8: Runtime Configuration & Secrets Loader  
**Branch:** `feature/runtime-config`  
- [ ] Add `.env.example` file with **all required variables** (see table below)  
- [ ] Create `src/config.py` to load env vars and expose a typed settings object  
- [ ] Fail fast with helpful error messages if mandatory vars are missing  
- [ ] Unit tests in `tests/test_config.py`

**Validation**  
1. `pytest tests/test_config.py` passes  
2. Running `python -c "import config, pprint; pprint.pprint(config.settings.dict())"` prints populated values when `.env` is present  

---

## PR 9: Live ETL Runner (Supermetrics → Mapper → CSV → S3)  
**Branch:** `feature/etl-live-supermetrics`  
- [ ] Extend `etl_runner.py` to accept `--source supermetrics` and call `supermetrics_klaviyo_pull.py`  
- [ ] Pipe pulled JSON → `lookml_field_mapper.py` → CSV  
- [ ] Upload final CSV to `s3://$S3_BUCKET/klaviyo_campaign_metrics_{{ds}}.csv`  
- [ ] Add CLI args for date range (`--start`, `--end`)  
- [ ] Add integration tests with moto‑mocked S3 (`tests/test_etl_runner_live.py`)  

**Validation**  
1. `pytest -k live` passes using moto  
2. Manual run with real creds writes file to S3 and prints object URL  

---

## PR 10: AWS SES Bootstrap Script  
**Branch:** `feature/aws-ses-bootstrap`  
- [ ] Create `scripts/ses_bootstrap.py`  
  * Verifies domain (if not already)  
  * Creates/updates an *SMTP‑enabled* IAM user `ses_poc_sender` (least privilege)  
  * Sets up sending identity `$SES_SENDER_EMAIL` and DKIM signing on `$SES_DOMAIN`  
  * Optionally lifts sandbox limitation if credentials allow (skip gracefully otherwise)  
- [ ] Outputs any required DNS records to stdout for manual confirmation  
- [ ] Unit tests with `moto` where possible (`tests/test_ses_bootstrap.py`)  

**Validation**  
1. `python scripts/ses_bootstrap.py --dry-run` shows planned actions  
2. Running without `--dry-run` creates identity and prints "✅ SES ready"  

---

## PR 11: SES Email Sender & Health‑Check  
**Branch:** `feature/email-summary-sender`  
- [ ] Add `src/email_sender.py` which:  
  * Queries yesterday's CSV from S3  
  * Builds a simple HTML table (campaign, sent, opens, clicks)  
  * Sends email from `$SES_SENDER_EMAIL` to `$SES_SENDER_EMAIL` (self‑test)  
- [ ] Include retry/back‑off for throttling (SES 14 TPS default)  
- [ ] Unit tests with `moto` SES  

**Validation**  
1. `pytest tests/test_email_sender.py` passes  
2. Manual run sends test email to inbox; email shows table w/ ≥1 row  

---

## PR 12: End‑to‑End Demo Orchestrator  
**Branch:** `feature/poc-demo-cli`  
- [ ] Add `src/poc_demo.py` that sequentially runs:  
  1. **ETL Live Runner** (PR 9) for `--start {{yesterday}} --end {{yesterday}}`  
  2. **Email Sender** (PR 11) to mail the summary  
- [ ] Provide `--dry-run` and `--log-level` flags  
- [ ] Add make target: `make demo`  

**Validation**  
1. `make demo` completes with "🎉 Demo finished, email sent"  
2. S3 contains CSV, inbox contains summary email  

---

## PR 13: Dockerized Demo Environment  
**Branch:** `feature/docker-demo`  
- [ ] Add `Dockerfile` (python:3.12-slim) & `docker-compose.yml`  
- [ ] Image installs dependencies, copies code, expects `.env` mount  
- [ ] Entrypoint executes `poc_demo.py`  
- [ ] README update for one‑command demo:  
  ```bash
  docker compose --env-file .env up demo
  ```

**Validation**

1. `docker compose build` succeeds
2. `docker compose --env-file .env up demo` sends email without local Python install

---

### 🔑 Environment Variables (.env)

| Variable                     | Description                                              |
| ---------------------------- | -------------------------------------------------------- |
| **KLAVIYO_API_KEY**        | (Optional) direct Klaviyo API key for fallback scripts   |
| **SUPERMETRICS_API_KEY**   | Supermetrics API key (Enterprise)                        |
| **SUPERMETRICS_CLIENT_ID** | Supermetrics workspace/client ID                         |
| **AWS_ACCESS_KEY_ID**     | IAM user credentials with S3 + SES permissions           |
| **AWS_SECRET_ACCESS_KEY** | ″                                                        |
| **AWS_REGION**              | e.g. `us-east-1` (must support SES)                      |
| **S3_BUCKET**               | Existing or auto‑created bucket for ETL outputs          |
| **SES_DOMAIN**              | Verified domain in your AWS account (e.g. `example.com`) |
| **SES_SENDER_EMAIL**       | Email address in the domain to act as sender             |
| **SES_REPLY_TO**           | (Optional) reply‑to address                              |
| **DEFAULT_TIMEZONE**        | e.g. `UTC` (overrides Supermetrics default EET)          |

> **NOTE:** If the domain is *not yet verified* in SES, run `scripts/ses_bootstrap.py` first and add the printed DNS records to Route 53. Wait for SES to show "Verified" before sending live emails.

---

### Implementation Order

1. PR 8 – config loader
2. PR 9 – live ETL
3. PR 10 – SES bootstrap
4. PR 11 – email sender
5. PR 12 – demo orchestrator
6. PR 13 – dockerization

Each PR must:

* Reference this **POC Demo PR Plan** in the description
* Include validation checklist in the PR body
* Pass CI (lint + tests) before merge

Once all PRs are merged, run `make demo` (or Docker command) to showcase an end‑to‑end, live‑data POC demo. 🚀
