# BigQuery Sanity Check

This document provides information about the BigQuery sanity check functionality implemented in the Klaviyo Reporting POC. The sanity check verifies that required BigQuery tables exist and contain data, ensuring the data pipeline is functioning correctly.

## Overview

The BigQuery sanity check script (`scripts/bq_sanity_check.py`) performs the following checks:

1. Verifies that specified BigQuery tables exist
2. Counts the number of rows in each table
3. Retrieves the latest `updated_at` timestamp (if the column exists)
4. Flags empty or missing tables with a non-zero exit code

This script can be run:
- Locally during development
- As part of the end-to-end demo script
- In CI via a scheduled GitHub Action

## Usage

### Command Line Usage

```bash
python scripts/bq_sanity_check.py --env .env --tables campaign,event,flow,list
```

### Options

- `--env PATH`: Path to the .env file containing BigQuery credentials (default: `.env`)
- `--tables LIST`: Comma-separated list of tables to check (overrides `TABLE_LIST` environment variable)
- `--dry-run`: Print queries without executing them (useful for testing)

### Environment Variables

The script requires the following environment variables:

- `BQ_PROJECT`: The BigQuery project ID
- `BQ_DATASET`: The BigQuery dataset name
- `TABLE_LIST`: (Optional) Comma-separated list of tables to check (default: `campaign,event,flow,list`)
- `E2E_SANITY_TABLES`: (Optional) Used by the end-to-end demo script (default: `campaign,event,flow,list`)

### Authentication

The script uses Google Cloud's Application Default Credentials for authentication. You can set up authentication in one of the following ways:

1. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to a service account key file
2. Use `gcloud auth application-default login` for local development
3. In CI environments, use service account credentials provided by the environment

## Integration with End-to-End Demo

The BigQuery sanity check is integrated into the end-to-end demo script (`scripts/run_end_to_end_demo.sh`). After loading data into BigQuery, the script runs the sanity check to verify that all required tables exist and contain data.

You can customize which tables are checked by setting the `E2E_SANITY_TABLES` environment variable.

## CI Integration

A GitHub Actions workflow runs the BigQuery sanity check nightly at 03:00 UTC. The workflow is defined in `.github/workflows/bq_sanity.yml`.

The workflow:
1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Decrypts secrets (if available)
5. Runs the BigQuery sanity check
6. Sends a Slack notification on failure

## Troubleshooting

### Common Issues

#### Missing Tables

If the sanity check reports missing tables, verify:
- The Fivetran connector is properly configured and syncing
- The BigQuery dataset exists and has the correct permissions
- The table names match what's expected by the script

#### Empty Tables

If tables exist but are empty:
- Check that the Fivetran connector is successfully syncing data
- Verify that the ETL process is correctly loading data into BigQuery
- Check for any filters that might be excluding all data

#### Authentication Errors

If you encounter authentication errors:
- Verify that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly
- Check that the service account has the necessary permissions on the BigQuery dataset
- Ensure the service account key hasn't expired

## Extending the Sanity Check

The sanity check can be extended to perform additional validations:

- Check for specific columns in tables
- Verify data quality (e.g., no null values in critical columns)
- Add time-based checks (e.g., data freshness)
- Implement custom business logic validations

To extend the script, modify `scripts/bq_sanity_check.py` and add your custom validation logic to the `check_table` function.
