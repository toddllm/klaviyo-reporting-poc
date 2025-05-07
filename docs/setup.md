# Environment Setup Guide

This document provides a comprehensive guide for setting up the environment for the Klaviyo Reporting POC. It includes a checklist of required environment variables and instructions for configuring each component of the system.

## Environment Variables Checklist

The following environment variables are required for the Klaviyo Reporting POC to function properly. You can use the `.env.example` file as a template for creating your own `.env` file.

### Core Configuration

- [ ] `BQ_PROJECT` - Your Google Cloud project ID for BigQuery
- [ ] `BQ_DATASET` - The BigQuery dataset name (e.g., `klaviyopoc`)
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Path to your Google Cloud service account JSON file

### Fivetran Configuration

- [ ] `FIVETRAN_GROUP_ID` - Your Fivetran group ID
- [ ] `FIVETRAN_CONNECTOR_ID` - Your Fivetran connector ID

Choose ONE authentication method:

**Option 1: Classic API key authentication**
- [ ] `FIVETRAN_API_KEY` - Your Fivetran API key
- [ ] `FIVETRAN_API_SECRET` - Your Fivetran API secret

**Option 2: System key authentication**
- [ ] `FIVETRAN_SYSTEM_KEY` - Your Fivetran system key
- [ ] `FIVETRAN_SYSTEM_KEY_SECRET` - Your Fivetran system key secret

### Postgres Configuration (Fivetran destination)

- [ ] `PG_HOST` - Your Postgres host
- [ ] `PG_PORT` - Your Postgres port (default: 5432)
- [ ] `PG_DB` - Your Postgres database name
- [ ] `PG_USER` - Your Postgres username
- [ ] `PG_PASSWORD` - Your Postgres password

### AWS Configuration

- [ ] `AWS_ACCESS_KEY_ID` - Your AWS access key ID
- [ ] `AWS_SECRET_ACCESS_KEY` - Your AWS secret access key
- [ ] `AWS_REGION` - Your AWS region (must support SES)
- [ ] `S3_BUCKET` - Your S3 bucket name
- [ ] `S3_PREFIX` - Your S3 prefix for file organization

### AWS SES Configuration

- [ ] `SES_DOMAIN` - Your verified domain in AWS SES
- [ ] `SES_SENDER_EMAIL` - Your sender email address
- [ ] `SES_FROM_EMAIL` - Your from email address
- [ ] `SES_REPLY_TO` - Your reply-to email address (optional)

### Google Sheets Configuration (Optional)

- [ ] `GOOGLE_SHEET_ID` - Your Google Sheet ID
- [ ] `GOOGLE_SHEET_NAME` - Your Google Sheet name
- [ ] `GOOGLE_SHEET_RANGE_NAME` - Your Google Sheet range name

### BigQuery Sanity Check Configuration

- [ ] `TABLE_LIST` - Comma-separated list of tables to check (default: `campaign,event,flow,list`)
- [ ] `E2E_SANITY_TABLES` - Comma-separated list of tables to check in end-to-end tests

## Setup Instructions

### 1. Google Cloud Setup

1. Create a Google Cloud project or use an existing one
2. Enable the BigQuery API
3. Create a service account with BigQuery Admin permissions
4. Download the service account JSON key file
5. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the JSON key file

### 2. Fivetran Setup

1. Create a Fivetran account or use an existing one
2. Create a new connector for Klaviyo
3. Configure the connector to sync to your destination (Postgres or BigQuery)
4. Get your Fivetran group ID and connector ID
5. Generate API credentials (API key or system key)

### 3. AWS Setup

1. Create an AWS account or use an existing one
2. Create an IAM user with S3 and SES permissions
3. Generate access keys for the IAM user
4. Create an S3 bucket for storing ETL outputs
5. Verify your domain in SES

### 4. Postgres Setup (if using Postgres as Fivetran destination)

1. Set up a Postgres database
2. Create a user with appropriate permissions
3. Configure Fivetran to sync to this database

### 5. Environment File

1. Copy the `.env.example` file to `.env`
2. Fill in all the required environment variables
3. Keep the `.env` file secure and do not commit it to version control

## Validation

To validate your environment setup, run the following commands:

```bash
# Check BigQuery connection
python scripts/bq_sanity_check.py --dry-run

# Check Fivetran connection
python src/fivetran_api_client.py --test-connection

# Run the ETL process with a small date range
python src/etl_runner.py --source fivetran --start 2025-01-01 --end 2025-01-02
```

If all commands run successfully, your environment is properly configured.

## Troubleshooting

### Common Issues

1. **BigQuery Authentication Errors**
   - Ensure the `GOOGLE_APPLICATION_CREDENTIALS` path is correct
   - Verify the service account has the necessary permissions

2. **Fivetran Connection Errors**
   - Check that your Fivetran credentials are correct
   - Ensure the connector is properly configured

3. **Postgres Connection Errors**
   - Verify the Postgres connection details
   - Check that the user has the necessary permissions

4. **AWS S3/SES Errors**
   - Confirm your AWS credentials are correct
   - Ensure the IAM user has the required permissions
   - Verify that your domain is properly verified in SES

### Getting Help

If you encounter issues that you cannot resolve, please contact the project maintainers for assistance.
