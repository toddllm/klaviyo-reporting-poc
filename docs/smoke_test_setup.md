# Klaviyo Reporting POC: Smoke Test Setup Guide

This guide explains how to set up all the necessary credentials and environment variables for running the full end-to-end smoke test with real services.

## Overview

The smoke test verifies the entire data pipeline from:
1. Fivetran data sync
2. BigQuery table population
3. ETL process
4. Reporting view
5. Looker dashboard
6. Google Sheets export

## Environment Variables Setup

All configuration is managed through environment variables in a `.env` file. Below is a step-by-step guide for setting up each section.

### BigQuery Settings

```
BQ_PROJECT=your-gcp-project-id
BQ_DATASET=klaviyopoc
BQ_TABLE_CAMPAIGNS=klaviyo_campaigns
BQ_TABLE_EVENTS=klaviyo_events
```

**How to obtain:**
1. **Project ID**: Log into [Google Cloud Console](https://console.cloud.google.com/). Your project ID is visible at the top of the console or in the project selector.
2. **Dataset and tables**: These should be configured by Fivetran to match your configuration.

### Fivetran Settings

```
FIVETRAN_SYSTEM_KEY=your_fivetran_system_key
FIVETRAN_SECRET=your_fivetran_secret
FIVETRAN_GROUP_ID=your_fivetran_group_id
FIVETRAN_CONNECTOR_ID=your_fivetran_connector_id
```

**How to obtain:**
1. Log into [Fivetran](https://fivetran.com/dashboard)
2. Go to "Account Settings" (gear icon) > API Configuration
3. Generate or view your API key and secret
4. For Group ID: Navigate to the group containing your Klaviyo connector - the ID is in the URL `/groups/{GROUP_ID}/connectors`
5. For Connector ID: Click on your Klaviyo connector - the ID is in the URL `/groups/{GROUP_ID}/connectors/{CONNECTOR_ID}`

### Google Service Account 

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**How to obtain:**
1. In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Create a new service account or use an existing one (must have BigQuery and Sheets permissions)
3. Create a new key (JSON format)
4. Download and store the key securely in your project directory
5. Set the path to this JSON file in your .env

### Google Sheets Settings

```
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_NAME=Klaviyo Metrics
GOOGLE_SHEET_RANGE_NAME=metrics_data
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/your_sheet_id
```

**How to obtain:**
1. Create a new Google Sheet or use an existing one
2. From the sheet URL `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`, extract the SHEET_ID
3. Share the sheet with your service account email (read/write permissions)
4. Create a worksheet/tab with name matching GOOGLE_SHEET_NAME

### Looker Studio Settings

```
LOOKER_SA_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
LOOKER_DASHBOARD_URL=https://lookerstudio.google.com/your_dashboard_id
```

**How to obtain:**
1. Use the same service account email as your Google credentials
2. Create a Looker Studio report connected to your BigQuery dataset
3. From the report URL, copy the full dashboard URL

### AWS Settings (for S3 and SES)

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET=your-klaviyo-bucket
SES_DOMAIN=yourdomain.com
SES_SENDER_EMAIL=reports@yourdomain.com
```

**How to obtain:**
1. **AWS Keys**: In AWS Console, go to "IAM" > "Users" > create or select a user > "Security credentials" > "Create access key"
2. **Region**: Choose a region that supports both S3 and SES services
3. **S3 Bucket**: In S3 Console, create a new bucket or use an existing one
4. **SES Domain**: In SES Console:
   - Go to "Domains" > "Verify a New Domain"
   - Follow DNS verification instructions
   - After verification, create an email address in that domain

### Supermetrics Settings (if using)

```
SUPERMETRICS_API_KEY=your_supermetrics_key
SUPERMETRICS_CLIENT_ID=your_supermetrics_client_id
```

**How to obtain:**
1. Sign up for [Supermetrics](https://supermetrics.com/)
2. Get API credentials from their developer portal

### Other Settings

```
ALLOW_MISSING_ENV_VARS=false
KLAVIYO_API_KEY=pk_your_klaviyo_key
KLAVIYO_API_VERSION=2025-04-15
AUDIENCE_ID=your_audience_id
CAMPAIGN_ID=your_campaign_id
TEMPLATE_ID=your_template_id
NUM_TEST_PROFILES=5
MODE=real
```

**How to obtain:**
- **Klaviyo API Key**: [Klaviyo account settings](https://www.klaviyo.com/account) > API Keys
- **IDs**: These are specific to your Klaviyo account campaigns/audiences

## Running the Smoke Test

Once you have populated all required credentials:

1. First run in dry-run mode to verify configuration:
   ```
   python scripts/smoke_test_agent.py --dry-run
   ```

2. Then run the complete live test:
   ```
   python scripts/smoke_test_agent.py
   ```

## Troubleshooting

### Common Issues

1. **Fivetran sync fails**:
   - Verify your Fivetran API credentials
   - Check that connector is properly configured

2. **BigQuery access denied**:
   - Ensure service account has proper permissions
   - Verify project and dataset names

3. **Google Sheets access issues**:
   - Confirm sheet is shared with service account email
   - Check sheet ID is correct

4. **Looker screenshot fails**:
   - Verify dashboard URL is accessible
   - Check browser automation dependencies are installed

5. **AWS operations fail**:
   - Confirm IAM user has S3 and SES permissions
   - For SES, ensure domain is verified

## Security Notes

- Never commit your `.env` file to version control
- Consider using a secrets manager for production deployments
- Rotate API keys periodically
- Use minimal permissions for service accounts and IAM users 