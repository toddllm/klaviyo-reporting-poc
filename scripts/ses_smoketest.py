#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

def validate_ses_env_vars():
    """Validate that all required SES environment variables are set"""
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "SES_FROM_EMAIL"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required AWS SES environment variables: {', '.join(missing_vars)}")

def send_email(to_address, subject, body, html_body=None, dry_run=False):
    """Send an email via AWS SES
    
    Args:
        to_address: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
        dry_run: If True, don't actually send the email
        
    Returns:
        Message ID if successful, None otherwise
    """
    # Validate environment variables
    validate_ses_env_vars()
    
    # Get sender email from environment
    sender = os.environ.get("SES_FROM_EMAIL")
    
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_address
    
    # Add reply-to if specified
    reply_to = os.environ.get("SES_REPLY_TO")
    if reply_to:
        msg['Reply-To'] = reply_to
    
    # Attach plain text part
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach HTML part if provided
    if html_body:
        msg.attach(MIMEText(html_body, 'html'))
    
    # Log the email details
    logger.info(f"Preparing to send email:\nFrom: {sender}\nTo: {to_address}\nSubject: {subject}")
    
    if dry_run:
        logger.info("DRY RUN: Email would be sent with the following content:")
        logger.info(f"Body:\n{body}")
        if html_body:
            logger.info(f"HTML Body:\n{html_body}")
        return "DRY-RUN-MESSAGE-ID"
    
    try:
        # Create SES client
        ses_client = boto3.client(
            'ses',
            region_name=os.environ.get("AWS_REGION")
        )
        
        # Send the email
        response = ses_client.send_raw_email(
            Source=sender,
            Destinations=[to_address],
            RawMessage={
                'Data': msg.as_string()
            }
        )
        
        message_id = response['MessageId']
        logger.info(f"Email sent! Message ID: {message_id}")
        return message_id
    
    except ClientError as e:
        logger.error(f"Error sending email: {e}")
        return None

def main():
    """Main function to send a test email via AWS SES"""
    parser = argparse.ArgumentParser(description="AWS SES Email Smoke Test")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", default="AWS SES Smoke Test", help="Email subject")
    parser.add_argument("--body", default="This is a test email sent via AWS SES.", help="Email body")
    parser.add_argument("--html", help="HTML email body (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send the email")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    try:
        # Send the email
        message_id = send_email(
            args.to,
            args.subject,
            args.body,
            args.html,
            args.dry_run
        )
        
        if message_id:
            print(f"Email {'would be ' if args.dry_run else ''}sent successfully! Message ID: {message_id}")
            return 0
        else:
            print("Failed to send email. Check the logs for details.")
            return 1
    
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
