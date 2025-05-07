# Narrow Scope POC PR Plan

⚠️ **IMPORTANT: ALL DEVELOPERS MUST FOLLOW THIS PLAN** ⚠️

This document outlines the specific PRs that should be created for implementing the narrow scope POC as described in `narrow-scope-POC.md`. Each PR should be implemented one at a time, with clear validation steps for both developers and reviewers.

**REQUIRED ACTIONS FOR ALL DEVELOPERS:**

1. **REFERENCE THIS PLAN IN EVERY PR DESCRIPTION** with a link to this document
2. **INCLUDE THE PR NUMBER AND TITLE FROM THIS PLAN** in your PR title
3. **ENSURE YOUR PR ALIGNS WITH ONE OF THE ITEMS BELOW**

**DO NOT create PRs that are not part of this plan without discussing with the team first.**

**EXAMPLE PR TITLE:** "PR 1: Klaviyo API Ingest Script"

**EXAMPLE PR DESCRIPTION START:**
```
Implements PR #1 from the [Narrow Scope POC PR Plan](../docs/NARROW_SCOPE_POC_PR_PLAN.md).

This PR adds the klaviyo_api_ingest.py script for fetching campaign metrics from the Klaviyo API.
```

---

## PR 1: Klaviyo API Ingest Script
**Branch:** feature/klaviyo-api-ingest
- [x] Create `src/klaviyo_api_ingest.py` for fetching campaign metrics from Klaviyo API
- [x] Implement API key authentication
- [x] Add functionality to fetch campaign list and associated metrics
- [x] Include pagination and error handling
- [x] Output data to a local CSV or JSON file
- [x] Add unit tests in `tests/test_klaviyo_api_ingest.py`

**Validation:**
1. Developer: Run `python src/klaviyo_api_ingest.py --dry-run` to verify API request format
2. Developer: Run unit tests with `pytest tests/test_klaviyo_api_ingest.py`
3. Reviewer: Verify error handling for API failures
4. Reviewer: Confirm pagination works correctly for large result sets

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR merged on May 6, 2025
- All tests passing: `pytest tests/test_klaviyo_api_ingest.py`
- Implementation includes API key authentication, pagination, error handling, and CSV/JSON output

---

## PR 2: LookML Field Mapper
**Branch:** feature/lookml-field-mapper
- [x] Create `src/lookml_field_mapper.py` for normalizing Klaviyo fields
- [x] Implement mapping dictionary from raw Klaviyo field names to reporting-ready field names
- [x] Add unit tests in `tests/test_lookml_field_mapper.py`
- [x] Ensure the mapper can be reused in pipeline or mock data setup

**Validation:**
1. Developer: Run unit tests with `pytest tests/test_lookml_field_mapper.py`
2. Developer: Verify mapping works with sample Klaviyo API response
3. Reviewer: Check that all required fields are mapped correctly
4. Reviewer: Ensure edge cases are handled (missing fields, null values, etc.)

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #35 merged on May 6, 2025
- All tests passing: `pytest tests/test_lookml_field_mapper.py`
- Implementation includes field mapping, date formatting, derived fields calculation, and error handling

---

## PR 3: Mock Looker Dataset
**Branch:** feature/mock-looker-dataset
- [x] Create `data/mock_looker_dataset.csv` with realistic mock data
- [x] Include fields: `date`, `campaign_name`, `send_time`, `open_rate`, `click_rate`, `subject_line`, `list_id`
- [x] Add at least 10 rows of realistic data
- [x] Add documentation on how to use the mock dataset

**Validation:**
1. Developer: Verify CSV format is correct and can be loaded with standard CSV libraries
2. Developer: Check that all required fields are present
3. Reviewer: Confirm data is realistic and representative
4. Reviewer: Validate that the CSV can be imported into Looker Studio

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] CSV format is valid
- [x] All required fields are present
- [x] Documentation is clear and complete

**Evidence:**
- PR merged on May 6, 2025
- CSV contains 16 rows of realistic campaign data
- All required fields are present and properly formatted
- Data spans April-June 2025 with varied metrics

---

## PR 4: Test Visualization Stub
**Branch:** feature/test-visualization-stub
- [x] Create `config/test_visualization_stub.json` with sample Looker Studio config
- [x] Define one line chart (open rate over time)
- [x] Define one bar chart (click rate by campaign)
- [x] Add comments explaining field requirements and naming assumptions

**Validation:**
1. Developer: Verify JSON is valid and well-formatted
2. Developer: Check that all required fields are referenced correctly
3. Reviewer: Confirm visualization config aligns with mock dataset
4. Reviewer: Validate that comments clearly explain field requirements

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] JSON is valid and well-formatted
- [x] Visualization config aligns with mock dataset
- [x] Comments are clear and helpful

**Evidence:**
- PR merged on May 6, 2025
- JSON is valid and well-formatted with comprehensive comments
- Configuration includes line chart for open rate over time and bar chart for click rate by campaign
- Implementation includes detailed field requirements and implementation notes

---

## PR 5: ETL Runner
**Branch:** feature/etl-runner
- [x] Create `src/etl_runner.py` to integrate fetch → normalize → export
- [x] Combine functionality from `klaviyo_api_ingest.py` and `lookml_field_mapper.py`
- [x] Implement consistent file output format
- [x] Add unit tests in `tests/test_etl_runner.py`
- [x] Include support for future Supermetrics integration

**Validation:**
1. Developer: Run `python src/etl_runner.py --dry-run` to verify end-to-end flow
2. Developer: Run unit tests with `pytest tests/test_etl_runner.py`
3. Reviewer: Verify error handling for each step of the ETL process
4. Reviewer: Confirm output format matches requirements for Looker Studio

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality
- [x] ETL process handles errors gracefully

**Evidence:**
- PR #39 merged on May 6, 2025
- All tests passing: `pytest tests/test_etl_runner.py`
- Implementation includes ETL pipeline with extract, transform, and load functions
- Error handling implemented for each step of the ETL process
- Support for future Supermetrics integration included

---

## PR 6: README Updates
**Branch:** feature/readme-updates
- [x] Update README.md with information about the narrow scope POC
- [x] Add sections for Overview, Setup, How to Run, and Next Steps
- [x] Include examples of how to use each script
- [x] Document known limitations and future enhancements

**Validation:**
1. Developer: Verify all scripts are documented correctly
2. Developer: Check that setup instructions are clear and complete
3. Reviewer: Confirm examples work as described
4. Reviewer: Validate that documentation is clear and helpful

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Documentation is clear and complete
- [x] Examples work as described
- [x] Known limitations are documented

**Evidence:**
- PR #41 created on May 6, 2025
- Documentation includes comprehensive README-NARROW-SCOPE-POC.md with detailed information
- Added src/README.md with usage instructions for each script
- Updated main README.md with narrow scope POC information and examples

---

## Implementation Notes

### Directory Structure
The narrow scope POC should follow this directory structure:
```
/
├── src/
│   ├── klaviyo_api_ingest.py
│   ├── lookml_field_mapper.py
│   ├── etl_runner.py
│   ├── supermetrics_klaviyo_pull.py  # PR 7
│   └── bq_loader.py                  # PR 8
├── tests/
│   ├── test_klaviyo_api_ingest.py
│   ├── test_lookml_field_mapper.py
│   ├── test_etl_runner.py
│   ├── test_supermetrics_klaviyo_pull.py  # PR 7
│   ├── test_bq_loader.py                  # PR 8
│   └── perf/
│       └── test_query_limits.py           # PR 10
├── data/
│   ├── mock_looker_dataset.csv
│   └── supermetrics_raw_YYYYMMDD.json     # PR 7 output
├── config/
│   ├── test_visualization_stub.json
│   └── looker_extract_klaviyo.json        # PR 9
├── docs/
│   └── looker_extract_setup.md            # PR 9
└── README.md
```

### Implementation Order
Implement the PRs in the order listed above. Each PR builds on the previous one, so it's important to follow the sequence.

For Phase 2 (PRs 7-10), the recommended implementation order is:
1. First implement PR 7 (Supermetrics → CSV Pull Script)
2. Then implement PR 8 (BigQuery Loader) and PR 9 (Looker Studio Extract Config) in parallel
3. Finally implement PR 10 (Data‑Volume Performance Tests) to validate the complete solution

### Testing Strategy

#### Phase 1 (PRs 1-6)
- Unit tests should be included for all Python scripts
- Mock API responses for testing `klaviyo_api_ingest.py`
- Test edge cases for field mapping in `lookml_field_mapper.py`
- Integration tests for `etl_runner.py` to verify end-to-end flow

#### Phase 2 (PRs 7-10)
- Mock Supermetrics API responses for testing `supermetrics_klaviyo_pull.py`
- Use BigQuery emulator for testing `bq_loader.py`
- Separate performance tests with pytest markers to avoid slowing down the regular test suite
- Implement CI workflow for automated performance testing

### Documentation

#### Phase 1 (PRs 1-6)
- Add docstrings to all functions
- Include examples in README.md
- Document known limitations and future enhancements

#### Phase 2 (PRs 7-10)
- Create step-by-step guide for Looker Studio Extract setup
- Document BigQuery schema and partitioning strategy
- Include performance test results and recommendations
- Update main README.md with information about the extended functionality

> After each PR merge, assign a tester to follow the **Validation** steps and attach **Evidence**. Once all PRs are merged and validated, the narrow scope POC is ready for demonstration. 🚀

---

# Phase 2: Extended Functionality

*(The following PRs extend the Narrow Scope POC with additional features)*

## PR 7: Supermetrics → CSV Pull Script  
**Branch:** `feature/supermetrics-klaviyo-pull`  
- [x] Add `src/supermetrics_klaviyo_pull.py` – CLI script that pulls Klaviyo data via Supermetrics API (JSON‐based connector end‑point)  
- [x] Support auth via `SUPERMETRICS_API_KEY` env var  
- [x] Accept params: `--start-date`, `--end-date`, `--report-type` (campaign | events)  
- [x] Write results to `data/supermetrics_raw_YYYYMMDD.json` and optional CSV  
- [x] Retry & rate‑limit logic per Supermetrics guidelines  
- [x] Unit tests: `tests/test_supermetrics_klaviyo_pull.py` (mock HTTP responses)  

**Validation**  
1. Dev ► Run dry‑run: `python src/supermetrics_klaviyo_pull.py --start-date 2025-05-01 --end-date 2025-05-02 --report-type campaign --dry-run`  
2. Dev ► Run full fetch; confirm JSON/CSV written with ≥1 row  
3. Reviewer ► Verify pagination + rate‑limit handling works with mocked 429 response  
4. Reviewer ► Confirm output schema matches mapper expectations  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #45 merged on May 6, 2025
- All tests passing: `pytest tests/test_supermetrics_klaviyo_pull.py`
- Implementation includes API key authentication, pagination, error handling, and CSV/JSON output
- Dry run functionality works as expected

---

## PR 8: BigQuery Loader (Optional Warehouse Path)  
**Branch:** `feature/bq-loader`  
- [x] Add `src/bq_loader.py` to load Supermetrics‐generated CSV/JSON into BigQuery table `klaviyo_raw.events`  
- [x] Use `google-cloud-bigquery` client; creds via service‑account JSON  
- [x] Schema auto‑detect + partition by `date` column  
- [x] Add CI step `pytest tests/test_bq_loader.py` with BigQuery emulator (or mock)  

**Validation**  
1. Dev ► Load sample file from PR 7 into a local/emulated BQ instance  
2. Dev ► Query table; ensure row count matches source file  
3. Reviewer ► Confirm partitioning & clustering flags set  
4. Reviewer ► Check idempotency (re‑running loader does not duplicate rows)  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #46 merged on May 6, 2025
- All tests passing: `pytest tests/test_bq_loader.py`
- Implementation includes BigQuery loading for both JSON and CSV files
- Supports schema auto-detection and partitioning by date column
- Feature flag `ENABLE_BQ=true` implemented for optional deployment

---

## PR 9: Looker Studio Extract Config (Cached Dataset)  
**Branch:** `feature/looker-extract-config`  
- [x] Add `config/looker_extract_klaviyo.json` – template for Google "Extract Data" connector  
- [x] Pre‑filters: last 90 days, aggregate by **Campaign ID** + **Date**  
- [x] Document step‑by‑step import instructions in `docs/looker_extract_setup.md`  
- [x] Include screenshot placeholders (saved as `/docs/img/…`)  

**Validation**  
1. Dev ► Import JSON into Looker Studio; verify extract created without errors  
2. Reviewer ► Confirm row count ≤100 MB limit and fields align with mock dataset  
3. Reviewer ► Ensure doc steps are reproducible on fresh account  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] JSON is valid and well-formatted
- [x] Documentation is clear and complete

**Evidence:**
- PR #48 merged on May 6, 2025
- Configuration includes extract settings for BigQuery source and destination
- Documentation includes comprehensive step-by-step guide with screenshots
- Added tests to validate the configuration file structure and content

---

## PR 10: Data‑Volume Performance Tests  
**Branch:** `feature/perf-tests`  
- [x] Create `tests/perf/test_query_limits.py` – measures fetch time & rows for 1‑, 7‑, 30‑day ranges  
- [x] Use pytest marker `@perf` to exclude from default suite  
- [x] Output summary CSV `perf_results.csv` (query, rows, seconds, success flag)  
- [x] Add GitHub Action workflow `ci-perf.yml` (manual trigger) to run perf tests weekly  

**Validation**  
1. Dev ► Run `pytest -m perf` locally; verify results file produced  
2. Reviewer ► Check thresholds: 1‑day <60 s, 7‑day <300 s on sample data  
3. Reviewer ► Confirm CI workflow succeeds and uploads artifact  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Tests are properly marked and isolated
- [x] CI workflow is correctly configured

**Evidence:**
- PR #49 merged on May 6, 2025
- Implementation includes performance tests for 1-day, 7-day, and 30-day ranges
- Tests properly marked with @perf to exclude from default suite
- CI workflow configured for weekly runs with artifact upload
- All tests passing with proper import paths

---

## Implementation Notes (for PRs 7–10)  
* Continue using the directory structure defined in the original plan.  
* PR 7 output becomes an accepted input path for the existing **ETL Runner** (PR 5) – do **not** refactor ETL yet; just ensure compatibility.  

---

# Phase 3: POC Demo Implementation

*(The following PRs implement a fully-working end-to-end demo)*

## PR 11: Runtime Configuration & Secrets Loader  
**Branch:** `feature/runtime-config`  
- [x] Add `.env.example` file with **all required variables** (see table below)  
- [x] Create `src/config.py` to load env vars and expose a typed settings object  
- [x] Fail fast with helpful error messages if mandatory vars are missing  
- [x] Unit tests in `tests/test_config.py`

**Validation**  
1. `pytest tests/test_config.py` passes  
2. Running `python -c "import config, pprint; pprint.pprint(config.settings.dict())"` prints populated values when `.env` is present  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #50 merged on May 6, 2025
- All tests passing: `pytest tests/test_config.py`
- Implementation includes `.env.example` with all required variables
- `src/config.py` loads env vars and exposes a typed settings object
- Validation and error handling for missing required variables implemented

---

## PR 12: Live ETL Runner (Supermetrics → Mapper → CSV → S3)  
**Branch:** `feature/etl-live-supermetrics`  
- [x] Extend `etl_runner.py` to accept `--source supermetrics` and call `supermetrics_klaviyo_pull.py`  
- [x] Pipe pulled JSON → `lookml_field_mapper.py` → CSV  
- [x] Upload final CSV to `s3://$S3_BUCKET/klaviyo_campaign_metrics_{{ds}}.csv`  
- [x] Add CLI args for date range (`--start`, `--end`)  
- [x] Add integration tests with moto‑mocked S3 (`tests/test_etl_runner_live.py`)  

**Validation**  
1. `pytest -k live` passes using moto  
2. Manual run with real creds writes file to S3 and prints object URL  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Integration tests cover key functionality

**Evidence:**
- PR #52 created on May 6, 2025
- Implementation includes Supermetrics integration, S3 upload, and date range parameters
- Integration tests with moto-mocked S3 passing

---

## PR 13: AWS SES Bootstrap Script  
**Branch:** `feature/aws-ses-bootstrap`  
- [x] Create `scripts/ses_bootstrap.py`  
  * Verifies domain (if not already)  
  * Creates/updates an *SMTP‑enabled* IAM user `ses_poc_sender` (least privilege)  
  * Sets up sending identity `$SES_SENDER_EMAIL` and DKIM signing on `$SES_DOMAIN`  
  * Optionally lifts sandbox limitation if credentials allow (skip gracefully otherwise)  
- [x] Outputs any required DNS records to stdout for manual confirmation  
- [x] Unit tests with `moto` where possible (`tests/test_ses_bootstrap.py`)  

**Validation**  
1. `python scripts/ses_bootstrap.py --dry-run` shows planned actions  
2. Running without `--dry-run` creates identity and prints "✅ SES ready"  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #50 merged on May 6, 2025
- All tests passing: `pytest tests/test_ses_bootstrap.py`
- Implementation includes domain verification, DKIM setup, email verification, and IAM user creation
- Dry run functionality works as expected

---

## PR 14: SES Email Sender & Health‑Check  
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

## PR 15: End‑to‑End Demo Orchestrator  
**Branch:** `feature/poc-demo-cli`  
- [ ] Add `src/poc_demo.py` that sequentially runs:  
  1. **ETL Live Runner** (PR 12) for `--start {{yesterday}} --end {{yesterday}}`  
  2. **Email Sender** (PR 14) to mail the summary  
- [ ] Provide `--dry-run` and `--log-level` flags  
- [ ] Add make target: `make demo`  

**Validation**  
1. `make demo` completes with "🎉 Demo finished, email sent"  
2. S3 contains CSV, inbox contains summary email  

---

## PR 16: Dockerized Demo Environment  
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

### Implementation Order for Phase 3

1. PR 11 – Runtime Configuration & Secrets Loader
2. PR 12 – Live ETL Runner (Supermetrics → Mapper → CSV → S3)
3. PR 13 – AWS SES Bootstrap Script
4. PR 14 – SES Email Sender & Health‑Check
5. PR 15 – End‑to‑End Demo Orchestrator
6. PR 16 – Dockerized Demo Environment

Each PR must:

* Reference this **POC Demo PR Plan** in the description
* Include validation checklist in the PR body
* Pass CI (lint + tests) before merge

Once all PRs are merged, run `make demo` (or Docker command) to showcase an end‑to‑end, live‑data POC demo. 🚀
