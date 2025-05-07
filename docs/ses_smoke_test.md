# AWS SES Email Smoke Test

This document provides instructions for using the AWS SES Email Smoke Test utility to verify your AWS SES configuration.

## Overview

The SES Smoke Test utility allows you to send a test email via AWS SES to verify that your AWS credentials and SES configuration are working correctly. This is useful for testing the email notification functionality of the Klaviyo Reporting POC.

## Prerequisites

Before using the SES Smoke Test utility, ensure that you have:

1. Set up your AWS credentials in your environment variables or AWS credentials file
2. Verified your sender email address or domain in AWS SES
3. Configured the required environment variables (see below)

## Required Environment Variables

The following environment variables are required:

- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: The AWS region where your SES service is configured (e.g., `us-east-1`)
- `SES_FROM_EMAIL`: The verified sender email address

Optional environment variables:

- `SES_REPLY_TO`: An optional reply-to email address

## Usage

### Basic Usage

To send a test email:

```bash
python scripts/ses_smoketest.py --to recipient@example.com
```

This will send a test email with a default subject and body to the specified recipient.

### Dry Run

To perform a dry run without actually sending an email:

```bash
python scripts/ses_smoketest.py --to recipient@example.com --dry-run
```

This will log the email details without sending it.

### Custom Subject and Body

To customize the subject and body of the test email:

```bash
python scripts/ses_smoketest.py \
  --to recipient@example.com \
  --subject "Custom Test Subject" \
  --body "This is a custom test email body."
```

### HTML Email

To send an HTML email:

```bash
python scripts/ses_smoketest.py \
  --to recipient@example.com \
  --body "This is the plain text version." \
  --html "<html><body><h1>This is the HTML version</h1><p>With formatting.</p></body></html>"
```

### Verbose Logging

To enable verbose logging:

```bash
python scripts/ses_smoketest.py --to recipient@example.com --verbose
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Ensure all required environment variables are set.
2. **Unverified Email Address**: The sender email address must be verified in AWS SES.
3. **SES in Sandbox Mode**: If your AWS SES account is in sandbox mode, recipient email addresses must also be verified.
4. **IAM Permissions**: Ensure your AWS credentials have the `ses:SendEmail` and `ses:SendRawEmail` permissions.

### Checking SES Status

To check your SES verification status and sending limits:

```bash
aws ses get-send-quota
aws ses list-verified-email-addresses
```

## Integration with ETL Pipeline

The SES Smoke Test utility can be integrated into your ETL pipeline to send email notifications when the pipeline completes. For example:

```python
# At the end of your ETL script
import subprocess

def send_notification(success, output_file):
    subject = "ETL Pipeline Completed Successfully" if success else "ETL Pipeline Failed"
    body = f"The ETL pipeline has completed {'successfully' if success else 'with errors'}."
    if success:
        body += f"\n\nOutput file: {output_file}"
    
    subprocess.run([
        "python", "scripts/ses_smoketest.py",
        "--to", "recipient@example.com",
        "--subject", subject,
        "--body", body
    ])

# Call this function at the end of your ETL process
send_notification(success=True, output_file="/path/to/output.csv")
```

## Next Steps

After verifying that the SES Smoke Test works correctly, you can:

1. Integrate email notifications into your ETL pipeline
2. Set up automated email reports
3. Configure email alerts for pipeline failures

For more information on AWS SES, see the [AWS SES Documentation](https://docs.aws.amazon.com/ses/latest/dg/Welcome.html).
