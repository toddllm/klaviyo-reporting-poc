# Automated Smoke Test Agent Guide

## Overview

The automated smoke test agent is a tool that runs through all phases of the Klaviyo Reporting POC smoke test automatically. It executes each step, captures outputs, takes screenshots, and generates a comprehensive report.

## Prerequisites

Before running the automated smoke test agent, ensure:

1. Your `.env` file contains all required environment variables:
   - FIVETRAN_SYSTEM_KEY, FIVETRAN_SYSTEM_KEY_SECRET, FIVETRAN_GROUP_ID, FIVETRAN_CONNECTOR_ID
   - BQ_PROJECT, BQ_DATASET
   - GOOGLE_SHEET_ID, GOOGLE_SHEET_NAME, GOOGLE_SHEET_RANGE_NAME
   - LOOKER_SA_EMAIL, LOOKER_DASHBOARD_URL, GOOGLE_SHEET_URL
   - AWS credentials (if SES testing is enabled)

2. You have installed all required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. You have proper permissions for all services (BigQuery, Google Sheets, Looker, AWS).

## Running the Automated Smoke Test

### Full Test

To run the complete smoke test that performs all operations:

```bash
python scripts/smoke_test_agent.py
```

### Dry Run

To run in dry-run mode (skips live operations that would modify data):

```bash
python scripts/smoke_test_agent.py --dry-run
```

## Test Phases

The automated smoke test agent runs through the following phases:

1. **Pre-flight Checks**
   - Verifies environment variables
   - Checks for required credentials

2. **Pipeline Trigger & Data Landing**
   - Triggers Fivetran connector
   - Verifies BigQuery tables

3. **ETL Runner Validation**
   - Runs ETL process
   - Verifies CSV output and S3 upload

4. **BigQuery Reporting View**
   - Deploys and queries reporting view

5. **Looker Studio Dashboard**
   - Takes screenshot of dashboard
   - Verifies data visibility

6. **Google Sheets Workbook**
   - Pushes snapshot to sheet
   - Takes screenshot of updated sheet

7. **Additional Checks**
   - CI/CD verification
   - Asset validation

## Test Output

After running the test, you'll find:

1. **Detailed Log File**
   - Location: `logs/smoke_test_log_<timestamp>.md`
   - Contains command outputs, status of each phase, and error details if any

2. **Screenshots**
   - Location: `logs/screens/`
   - Includes screenshots of Looker dashboard and Google Sheets

## Interpreting Results

The test log will clearly indicate:

- ✅ **PASS**: Step completed successfully
- ⚠️ **WARNING**: Non-critical issue detected
- ❌ **FAIL**: Critical error that prevented completion

The summary at the end of the log will show which phases passed or failed.

## Troubleshooting

If the automated test fails:

1. Check the log file for specific error messages
2. Verify all environment variables are correctly set
3. Ensure you have proper permissions for all services
4. Try running individual components manually to isolate the issue

## Example Log Output

```markdown
# Smoke Test Report: 2025-05-07 12:16:21

## Phase 0: Pre-flight Checks
✅ Environment variables verified
✅ Credentials validated

## Phase 1: Pipeline Trigger & Data Landing
✅ Fivetran connector triggered successfully
✅ BigQuery tables verified

...

## Summary
Total Phases: 7
Passed: 7
Warnings: 0
Failed: 0

Smoke test completed successfully!
```

## Manual Fallback

If you need to run the smoke test manually, refer to the [Manual Smoke Test Guide](./manual_smoke_test_guide.md) for step-by-step instructions.
