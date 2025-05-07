# Fivetran + BigQuery Integration PR Plan

⚠️ **IMPORTANT: ALL DEVELOPERS MUST FOLLOW THIS PLAN** ⚠️

This document outlines the specific PRs that should be created for implementing the Fivetran + BigQuery integration for the Klaviyo Reporting POC. Each PR should be implemented one at a time, with clear validation steps for both developers and reviewers.

**REQUIRED ACTIONS FOR ALL DEVELOPERS:**

1. **REFERENCE THIS PLAN IN EVERY PR DESCRIPTION** with a link to this document
2. **INCLUDE THE PR NUMBER AND TITLE FROM THIS PLAN** in your PR title
3. **ENSURE YOUR PR ALIGNS WITH ONE OF THE ITEMS BELOW**

**DO NOT create PRs that are not part of this plan without discussing with the team first.**

**EXAMPLE PR TITLE:** "PR 13: Fivetran API Client"

**EXAMPLE PR DESCRIPTION START:**
```
Implements PR #13 from the [Fivetran + BigQuery Integration PR Plan](../docs/FIVETRAN_BIGQUERY_PR_PLAN.md).

This PR adds the fivetran_api_client.py script for interacting with the Fivetran API.
```

---

## Phase 1: Core Functionality (PRs 1-6)

*Note: Phase 1 PRs (1-6) have already been implemented and merged. They provide the foundation for the Klaviyo API integration and ETL pipeline.*

---

# Phase 2: Fivetran + BigQuery Integration

*(The following PRs replace the previously planned Supermetrics integration with Fivetran + BigQuery)*

## PR 13: Fivetran API Client
**Branch:** `feature/fivetran-api-client`  
- [ ] Add `src/fivetran_api_client.py`  
  * Thin wrapper around Fivetran REST API (`/groups`, `/connectors`, `/connectors/:id/sync`)  
  * Helper to trigger a manual sync & poll status until `SUCCESS` or `FAILURE`  
  * Basic rate‑limit back‑off handling  
- [ ] Unit tests `tests/test_fivetran_api_client.py` with mocked HTTP responses (use `responses`)

**Validation**
1. `pytest tests/test_fivetran_api_client.py` passes.  
2. Reviewer confirms correct endpoint paths & error handling.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 14: Connector Runner (Trigger + Wait)
**Branch:** `feature/fivetran-connector-runner`  
- [ ] Add `src/fivetran_connector_runner.py`  
  * CLI: `python -m src.fivetran_connector_runner --group $GROUP --connector $ID`  
  * Calls `fivetran_api_client.trigger_sync()` then waits (poll interval configurable)  
  * Exits 0 on success, non‑zero on error/time‑out  
- [ ] Unit tests `tests/test_fivetran_connector_runner.py`

**Validation**
1. Dry‑run with dummy IDs works.  
2. Tests cover success, failure, timeout paths.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 15: Postgres Extract → CSV Export
**Branch:** `feature/postgres-extract-export`  
- [ ] Add `src/postgres_extract_export.py`  
  * Connects to the Fivetran destination Postgres (env‑driven)  
  * Parameter `--table klaviyo_campaigns` (default) + optional `--start` / `--end` dates  
  * Dumps query result to `data/klaviyo_export_YYYYMMDD.csv`  
- [ ] Integration tests with Docker‑based Postgres service in `tests/integration/`

**Validation**
1. `python src/postgres_extract_export.py --limit 10 --dry-run` prints sample rows.  
2. Reviewer checks CSV schema matches downstream mapper expectations.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 16: ETL Runner v2 (`--source fivetran`)
**Branch:** `feature/etl-runner-fivetran`  
- [ ] Extend `src/etl_runner.py`  
  * New `--source fivetran` flag → internally:  
    1. call `fivetran_connector_runner`  
    2. call `postgres_extract_export`  
    3. feed CSV → existing `lookml_field_mapper`  
- [ ] Add CLI date args `--start --end` (ISO‑8601)  
- [ ] Update unit + happy‑path integration tests.

**Validation**
1. `python src/etl_runner.py --source fivetran --start 2024-05-01 --end 2024-05-07 --dry-run` runs full pipeline locally.  
2. Reviewer verifies intermediate and final CSVs are created.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 17: S3 Uploader Utility
**Branch:** `feature/s3-uploader`  
- [ ] Add `src/s3_uploader.py`  
  * Function `upload_file(local_path, bucket, key)`  
  * Uses `boto3`; retries w/ exponential back‑off.  
- [ ] moto‑mocked tests `tests/test_s3_uploader.py`

**Validation**
1. Moto tests pass.  
2. Upload errors raise clear exceptions.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 18: Live ETL Runner (Fivetran → CSV → S3)
**Branch:** `feature/live-etl-runner`  
- [ ] Implement functionality for Fivetran path:  
  * `etl_runner --source fivetran ... --upload-s3 s3://bucket/prefix/{start}_{end}.csv`  
  * Default key uses **start date**.  
- [ ] End‑to‑end integration test with moto S3 (skip Fivetran call, mock success).

**Validation**
1. End‑to‑end test saves file to mocked S3.  
2. Reviewer checks key naming & metadata.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 19: AWS SES Email Smoke Test
**Branch:** `feature/aws-ses-smoketest`  
- [ ] Add `scripts/ses_smoketest.py`  
  * Sends a test email via AWS SES using existing verified domain.  
  * Params: `--to`, `--subject`, `--body`.  
- [ ] README snippet on running smoke test.  
- [ ] moto‑based unit test (for signature only).

**Validation**
1. `python scripts/ses_smoketest.py --to you@example.com --dry-run` logs request.  
2. (Optional) Live run sends email successfully (requires SES prod creds).

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 20: Documentation & .env Template
**Branch:** `feature/docs-fivetran-switch`  
- [ ] Update `README.md` & `docs/POC_OVERVIEW.md`  
- [ ] Add `.env.example` with **all** new vars (see below).  
- [ ] Diagram illustrating Fivetran → Postgres → Mapper → CSV → S3.

**Validation**
1. Reviewer can stand up pipeline via README in <30 min.  
2. All env vars clearly documented.

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Documentation is clear and complete

---

### Required `.env` Entries (for full, non‑mocked demo)

| Variable | Purpose |
|----------|----------|
| **FIVETRAN_API_KEY** | Fivetran user API key |
| **FIVETRAN_API_SECRET** | Fivetran API secret |
| **FIVETRAN_GROUP_ID** | Group ID containing the connector |
| **FIVETRAN_CONNECTOR_ID** | Klaviyo connector ID |
| **PG_HOST** | Postgres host (Fivetran destination) |
| **PG_PORT** | Postgres port (default 5432) |
| **PG_DB** | Postgres database name |
| **PG_USER** | Postgres user |
| **PG_PASSWORD** | Postgres password |
| **AWS_ACCESS_KEY_ID** | IAM key w/ `ses:SendEmail` & `s3:PutObject` |
| **AWS_SECRET_ACCESS_KEY** | IAM secret |
| **AWS_REGION** | e.g. `us-east-1` |
| **S3_BUCKET** | Target bucket for CSV exports |
| **S3_PREFIX** | Folder/prefix, e.g. `klaviyo-poc/` |
| **SES_FROM_EMAIL** | Verified sender email/domain |

---

### Directory Additions
```
/
├── src/
│   ├── fivetran_api_client.py
│   ├── fivetran_connector_runner.py
│   ├── postgres_extract_export.py
│   ├── s3_uploader.py
├── scripts/
│   └── ses_smoketest.py
├── tests/
│   ├── test_fivetran_api_client.py
│   ├── test_fivetran_connector_runner.py
│   ├── test_s3_uploader.py
│   └── integration/
│       └── test_postgres_extract_export.py
├── docs/
│   └── POC_OVERVIEW.md
└── .env.example
```

> Implement PRs **in numeric order**. After PR 20 is merged and validated, we'll have a live Fivetran‑powered POC capable of syncing real Klaviyo data, mapping it, exporting to CSV, archiving to S3, and sending a verification email via AWS SES. 🚀

---

# Phase 3: POC Demo Implementation

*(The following PRs implement a fully-working end-to-end demo)*

## PR 21: BigQuery Integration
**Branch:** `feature/bigquery-integration`  
- [ ] Add `src/bigquery_loader.py` to load CSV data into BigQuery  
  * Connect to BigQuery using service account credentials  
  * Create tables with appropriate schema  
  * Load data with partitioning by date  
- [ ] Unit tests in `tests/test_bigquery_loader.py`

**Validation**
1. `pytest tests/test_bigquery_loader.py` passes  
2. Reviewer confirms data loads correctly with proper schema

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

---

## PR 22: Looker Studio Connection
**Branch:** `feature/looker-studio-connection`  
- [ ] Add `docs/looker_bigquery_setup.md` with step-by-step instructions  
- [ ] Create sample Looker Studio dashboard configuration  
- [ ] Document BigQuery schema and field mappings

**Validation**
1. Reviewer can follow instructions to connect Looker Studio to BigQuery  
2. Sample dashboard loads correctly with test data

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Documentation is clear and complete

---

## PR 23: End-to-End Demo Script
**Branch:** `feature/end-to-end-demo`  
- [ ] Create `scripts/run_end_to_end_demo.sh`  
  * Trigger Fivetran sync  
  * Extract data from Postgres  
  * Transform and load to BigQuery  
  * Generate dashboard link  
  * Send email notification  
- [ ] Add comprehensive documentation

**Validation**
1. Script runs successfully in test environment  
2. All steps are properly logged and error-handled

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Script runs successfully
- [ ] Documentation is clear and complete

---

## Implementation Notes

### Architecture Changes

The key architectural changes in this plan are:

1. **Replacing Supermetrics with Fivetran**:
   - Fivetran provides more reliable and scalable data integration
   - Better support for Klaviyo data sources
   - More consistent schema handling

2. **Adding BigQuery as the data warehouse**:
   - Provides scalable analytics capabilities
   - Native integration with Looker Studio
   - Better performance for large datasets

3. **Adding S3 for data archiving**:
   - Reliable long-term storage
   - Enables data recovery and audit capabilities
   - Cost-effective for large volumes of historical data

### Implementation Order

Implement the PRs in the order listed above. Each PR builds on the previous one, so it's important to follow the sequence.

### Testing Strategy

- Unit tests should be included for all Python scripts
- Mock API responses for testing `fivetran_api_client.py`
- Use Docker for Postgres integration tests
- Use moto for S3 and SES testing
- End-to-end tests should validate the complete pipeline

> After each PR merge, assign a tester to follow the **Validation** steps. Once all PRs are merged and validated, the Fivetran + BigQuery integration is ready for demonstration. 🚀
