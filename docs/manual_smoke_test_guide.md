# Klaviyo Reporting POC: Manual Smoke Test Guide

## Overview

This document provides step-by-step instructions for manually testing the Klaviyo Reporting POC end-to-end. Follow each phase in order and document all command outputs, errors, and observations.

## Test Environment Setup

Before beginning the test, ensure you have:

- Access to the repository
- Proper credentials in your `.env` file
- Permissions for all required services (BigQuery, Google Sheets, Looker, AWS if applicable)

## Test Log Template

Create a test log file with the following format:

```
Klaviyo Reporting POC - Manual Smoke Test
Tester: [Your Name]
Date: [YYYY-MM-DD]
Environment: [Dev/Staging/Prod]

[Copy each phase and step below, adding command outputs and observations]
```

## Smoke Test Phases

### Phase 0: Pre-flight Checks

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 0.1 | `git checkout main && git pull` | Latest code pulled successfully | | |
| 0.2 | `python -m venv venv && source venv/bin/activate` | Virtual environment created and activated | | |
| 0.3 | `pip install -r requirements.txt` | All dependencies installed without errors | | |
| 0.4 | Verify `.env` file contains all required keys | All keys present without quotes or whitespace:<br>- FIVETRAN_SYSTEM_KEY / SECRET / GROUP_ID / CONNECTOR_ID<br>- BQ_PROJECT, BQ_DATASET<br>- GOOGLE_SHEET_ID / GOOGLE_SHEET_NAME / GOOGLE_SHEET_RANGE_NAME<br>- LOOKER_SA_EMAIL<br>- AWS vars (if SES test enabled) | | |

### Phase 1: Pipeline Trigger & Data Landing

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 1.1 | `python src/fivetran_connector_runner.py --dry-run` | Dry run completes without errors | | |
| 1.2 | `python src/fivetran_connector_runner.py` | Live run completes with `"sync_completed": "success"` in JSON output | | |
| 1.3 | `python scripts/bq_sanity_check.py` | All four tables exist with row counts > 0 and latest timestamp < 1 hour old | | |

### Phase 2: ETL Runner Validation

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 2.1 | `python src/etl_runner.py --source fivetran --start $(date -v-7d +%F) --end $(date +%F) --dry-run` | Dry run shows `[DRY RUN]` lines with no exceptions | | |
| 2.2 | `python src/etl_runner.py --source fivetran --start $(date -v-7d +%F) --end $(date +%F)` | Live run completes successfully | | |
| 2.3 | Check for CSV file | `data/exports/klaviyo_<yyyymmdd>.csv` exists and has rows | | |
| 2.4 | Verify S3 upload | S3 upload message shows 200 OK or equivalent success | | |
| 2.5 | Check S3 console | File visible in S3 console under expected key prefix | | |

### Phase 3: BigQuery Reporting View

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 3.1 | `bash scripts/deploy_reporting_view.sh` | "View created or already exists" message | | |
| 3.2 | ```bq query --nouse_legacy_sql "SELECT campaign_name, sent, opens, clicks, revenue FROM \`${BQ_PROJECT}.${BQ_DATASET}.v_email_metrics\` ORDER BY send_date DESC LIMIT 5"``` | Query returns rows with non-null metrics | | |

### Phase 4: Looker Studio Dashboard

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 4.1 | Open Looker template link | View fields resolve with no red error fields | | |
| 4.2 | Change date range to past 7 days | Charts populate with data | | |
| 4.3 | Test filters (campaign/list) | Filters work correctly | | |
| 4.4 | Export PDF & CSV from Looker | Downloads complete successfully | | |

### Phase 5: Google Sheets Workbook

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 5.1 | Open sheet using GOOGLE_SHEET_ID | Sheet opens successfully | | |
| 5.2 | `python scripts/sheets_push_snapshot.py --date $(date +%F)` | Script runs without errors | | |
| 5.3 | Check sheet for new rows | New rows appended in the named range | | |
| 5.4 | Test sheet sharing | Sheet is shareable in view-only mode | | |

### Phase 6: Email (SES) Smoke Test (Optional)

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 6.1 | `python scripts/send_test_email.py --to your@email.com --csv data/exports/klaviyo_<date>.csv` | Command completes without errors | | |
| 6.2 | Check email inbox | Email received with working links to Looker & sheet | | |

### Phase 7: Client-Facing Assets

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 7.1 | Open client_deck.pdf | 6 slides present with no missing images, QR codes scan to correct URLs | | |
| 7.2 | Review client_demo.md | All links valid, screenshots load, no TODO markers | | |

### Phase 8: CI/CD & Lint

| Step | Command/Action | Expected Result | Actual Result | Status ✅/⚠️/❌ |
|------|---------------|-----------------|--------------|----------------|
| 8.1 | `pytest` | All tests pass | | |
| 8.2 | `flake8 src tests` | No linting errors | | |

## Test Summary

| Phase | Status | Notes |
|-------|--------|-------|
| 0: Pre-flight | | |
| 1: Pipeline & Data | | |
| 2: ETL Runner | | |
| 3: BigQuery View | | |
| 4: Looker Dashboard | | |
| 5: Google Sheets | | |
| 6: Email Test | | |
| 7: Client Assets | | |
| 8: CI/CD & Lint | | |

## Issues Found

*List any issues found during testing with the following format:*

1. **Issue**: [Brief description]
   - **Phase/Step**: [e.g., 2.3]
   - **Severity**: [High/Medium/Low]
   - **Reproduction Steps**: [Steps to reproduce]
   - **Expected vs. Actual**: [What was expected vs. what happened]
   - **Screenshots/Logs**: [If applicable]

## Recommendations

*Provide any recommendations for fixing issues or improving the system.*

## Automated Testing

To run the automated smoke test agent (if available):

```bash
# Run the full smoke test
python scripts/smoke_test_agent.py

# Run in dry-run mode (skips live operations)
python scripts/smoke_test_agent.py --dry-run
```

The agent will generate a detailed markdown report in `logs/smoke_test_log_<timestamp>.md` and capture screenshots in `logs/screens/`.
