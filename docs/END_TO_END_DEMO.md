# End-to-End Demo Guide

## Overview

This document provides a comprehensive guide for running the end-to-end demo of the Klaviyo Reporting POC. The demo showcases the complete data pipeline from Fivetran to BigQuery to Looker Studio, demonstrating how Klaviyo campaign data can be automatically processed, stored, and visualized.

## Prerequisites

Before running the end-to-end demo, ensure you have:

1. Completed the setup of all components:
   - Fivetran connector configured and working
   - Postgres database accessible
   - AWS S3 bucket created with appropriate permissions
   - BigQuery project and dataset created
   - Looker Studio dashboard configured
   - AWS SES verified domain for sending emails

2. Set up all required environment variables in your `.env` file:
   - Fivetran credentials and configuration
   - Postgres connection details
   - AWS credentials and configuration
   - BigQuery project and dataset information
   - SES email configuration
   
   For a comprehensive guide on environment setup, see [Environment Setup Guide](setup.md).

3. Installed all required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Demo Script

The end-to-end demo is orchestrated by the `scripts/run_end_to_end_demo.sh` script, which performs the following steps:

1. **Fivetran Sync**: Triggers a Fivetran sync to pull the latest data from Klaviyo to Postgres
2. **ETL Process**: Extracts data from Postgres, transforms it using the field mapper, and saves it as a CSV
3. **S3 Upload**: Uploads the processed data to S3 for archiving
4. **BigQuery Load**: Loads the processed data into BigQuery for analytics
5. **Dashboard Link**: Generates a link to the Looker Studio dashboard with appropriate date filters
6. **Email Notification**: Sends an email notification with a summary and dashboard link

## Running the Demo

### Basic Usage

To run the demo with default settings (last 30 days of data):

```bash
./scripts/run_end_to_end_demo.sh
```

### Specifying Date Range

To run the demo for a specific date range:

```bash
./scripts/run_end_to_end_demo.sh --start-date 2025-04-01 --end-date 2025-04-30
```

### Dry Run Mode

To perform a dry run without making actual API calls or data changes:

```bash
./scripts/run_end_to_end_demo.sh --dry-run
```

### Sending Email Notifications

To send an email notification when the demo completes:

```bash
./scripts/run_end_to_end_demo.sh --notify-email recipient@example.com
```

### Skipping Steps

To skip specific steps in the pipeline:

```bash
# Skip Fivetran sync (use existing data in Postgres)
./scripts/run_end_to_end_demo.sh --skip-fivetran

# Skip BigQuery load (just extract and upload to S3)
./scripts/run_end_to_end_demo.sh --skip-bigquery

# Skip email notification
./scripts/run_end_to_end_demo.sh --skip-email
```

### Full Options

```bash
./scripts/run_end_to_end_demo.sh --help
```

This will display all available options:

```
Usage: ./scripts/run_end_to_end_demo.sh [options]

Options:
  --start-date YYYY-MM-DD   Start date for data extraction (default: 30 days ago)
  --end-date YYYY-MM-DD     End date for data extraction (default: today)
  --dry-run                 Run in dry-run mode without making actual API calls
  --skip-fivetran           Skip the Fivetran sync step
  --skip-bigquery          Skip the BigQuery load step
  --skip-email             Skip sending email notification
  --notify-email EMAIL     Email address to send notification to
  --report-type TYPE       Type of report to generate (campaign or events, default: campaign)
  --help                   Display this help message
```

## Demo Outputs

The demo produces the following outputs:

1. **Log File**: A detailed log of all operations in the `logs/` directory
2. **CSV Files**: Processed data files in the `data/` directory
3. **S3 Objects**: Archived data in the configured S3 bucket
4. **BigQuery Tables**: Data loaded into BigQuery tables
5. **Email Notification**: A summary email sent to the specified recipient
6. **Dashboard Link**: A URL to access the Looker Studio dashboard

## Monitoring and Troubleshooting

### Checking Demo Status

The demo script logs all operations to both the console and a log file. You can check the status of a running demo by examining the log file:

```bash
tail -f logs/end_to_end_demo_YYYYMMDD_HHMMSS.log
```

### Common Issues and Solutions

1. **Fivetran Sync Fails**
   - Check Fivetran API credentials
   - Verify that the connector and group IDs are correct
   - Check Fivetran connector status in the Fivetran dashboard

2. **Postgres Connection Fails**
   - Verify Postgres connection details
   - Check network connectivity to the Postgres server
   - Ensure the database user has appropriate permissions

3. **S3 Upload Fails**
   - Check AWS credentials
   - Verify that the S3 bucket exists and is accessible
   - Ensure the IAM user has appropriate permissions

4. **BigQuery Load Fails**
   - Check BigQuery credentials
   - Verify that the project and dataset exist
   - Ensure the service account has appropriate permissions

5. **Email Notification Fails**
   - Check AWS SES configuration
   - Verify that the sender email is verified in SES
   - Check SES sending limits and quotas

## Customizing the Demo

### Modifying the Dashboard

The demo uses the Looker Studio dashboard configured in the `LOOKER_REPORT_URL` environment variable. To customize the dashboard:

1. Create a new dashboard in Looker Studio
2. Connect it to your BigQuery dataset
3. Design the dashboard with appropriate charts and filters
4. Update the `LOOKER_REPORT_URL` environment variable with the new dashboard URL

### Adding Custom Metrics

To add custom metrics to the demo:

1. Modify the `src/postgres_extract_export.py` script to extract additional fields
2. Update the `src/lookml_field_mapper.py` script to map the new fields
3. Modify the BigQuery schema in `src/bq_loader.py` to include the new fields
4. Update the Looker Studio dashboard to visualize the new metrics

## Scheduling the Demo

To run the demo automatically on a schedule:

### Using Cron

Add a cron job to run the demo script at regular intervals:

```bash
# Run the demo every day at 2:00 AM
0 2 * * * /path/to/klaviyo-reporting-poc/scripts/run_end_to_end_demo.sh --notify-email admin@example.com >> /path/to/klaviyo-reporting-poc/logs/scheduled_demo.log 2>&1
```

### Using AWS Lambda

You can also deploy the demo as an AWS Lambda function with a CloudWatch Events trigger:

1. Package the demo code and dependencies
2. Create a Lambda function that calls the demo script
3. Set up a CloudWatch Events rule to trigger the Lambda function on a schedule

## Conclusion

The end-to-end demo showcases the complete Klaviyo Reporting POC pipeline, from data extraction to visualization. By running this demo, you can verify that all components of the system are working together correctly and demonstrate the value of the solution to stakeholders.

For more detailed information about individual components, refer to the following documentation:

- [Fivetran + BigQuery Integration PR Plan](FIVETRAN_BIGQUERY_PR_PLAN.md)
- [POC Overview](POC_OVERVIEW.md)
- [Looker Studio + BigQuery Setup Guide](looker_bigquery_setup.md)
