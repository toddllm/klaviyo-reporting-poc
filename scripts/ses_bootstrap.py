#!/usr/bin/env python3
import os
import sys
import argparse
import boto3
import json
from botocore.exceptions import ClientError

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import settings

# Constants
IAM_USER_NAME = "ses_poc_sender"
IAM_POLICY_NAME = "ses_poc_sender_policy"

def verify_domain(ses_client, domain, dry_run=False):
    """Verify a domain for SES if not already verified"""
    try:
        # Check if domain is already verified
        response = ses_client.get_identity_verification_attributes(
            Identities=[domain]
        )
        
        verification_attrs = response.get('VerificationAttributes', {})
        if domain in verification_attrs:
            status = verification_attrs[domain].get('VerificationStatus')
            if status == 'Success':
                print(f"✅ Domain {domain} is already verified")
                return True
            elif status == 'Pending':
                print(f"⏳ Domain {domain} verification is pending")
                print(f"Please check your DNS settings for the required records")
                return False
        
        if dry_run:
            print(f"[DRY RUN] Would verify domain: {domain}")
            return True
        
        # Verify the domain
        response = ses_client.verify_domain_identity(Domain=domain)
        verification_token = response['VerificationToken']
        
        print(f"🔍 Domain verification initiated for {domain}")
        print(f"\nPlease add the following TXT record to your DNS settings:")
        print(f"Domain: _amazonses.{domain}")
        print(f"Value: {verification_token}")
        
        return False
    except ClientError as e:
        print(f"❌ Error verifying domain: {e}")
        return False

def setup_dkim(ses_client, domain, dry_run=False):
    """Set up DKIM signing for a domain"""
    try:
        # Check if DKIM is already configured
        response = ses_client.get_identity_dkim_attributes(
            Identities=[domain]
        )
        
        dkim_attrs = response.get('DkimAttributes', {})
        if domain in dkim_attrs and dkim_attrs[domain].get('DkimEnabled', False):
            print(f"✅ DKIM is already enabled for {domain}")
            return True
        
        if dry_run:
            print(f"[DRY RUN] Would enable DKIM for domain: {domain}")
            return True
        
        # Enable DKIM for the domain
        response = ses_client.verify_domain_dkim(Domain=domain)
        dkim_tokens = response['DkimTokens']
        
        print(f"🔍 DKIM setup initiated for {domain}")
        print(f"\nPlease add the following CNAME records to your DNS settings:")
        for token in dkim_tokens:
            print(f"Domain: {token}._domainkey.{domain}")
            print(f"Value: {token}.dkim.amazonses.com")
        
        return True
    except ClientError as e:
        print(f"❌ Error setting up DKIM: {e}")
        return False

def verify_email(ses_client, email, dry_run=False):
    """Verify an email address for SES if not already verified"""
    try:
        # Check if email is already verified
        response = ses_client.get_identity_verification_attributes(
            Identities=[email]
        )
        
        verification_attrs = response.get('VerificationAttributes', {})
        if email in verification_attrs:
            status = verification_attrs[email].get('VerificationStatus')
            if status == 'Success':
                print(f"✅ Email {email} is already verified")
                return True
            elif status == 'Pending':
                print(f"⏳ Email {email} verification is pending")
                print(f"Please check your inbox for the verification email")
                return False
        
        if dry_run:
            print(f"[DRY RUN] Would verify email: {email}")
            return True
        
        # Verify the email
        ses_client.verify_email_identity(EmailAddress=email)
        
        print(f"🔍 Verification email sent to {email}")
        print(f"Please check your inbox and follow the verification link")
        
        return False
    except ClientError as e:
        print(f"❌ Error verifying email: {e}")
        return False

def create_iam_user(iam_client, dry_run=False):
    """Create or update an IAM user for SES SMTP access"""
    try:
        # Check if user already exists
        try:
            iam_client.get_user(UserName=IAM_USER_NAME)
            print(f"✅ IAM user {IAM_USER_NAME} already exists")
            user_exists = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                user_exists = False
            else:
                raise
        
        if not user_exists:
            if dry_run:
                print(f"[DRY RUN] Would create IAM user: {IAM_USER_NAME}")
            else:
                iam_client.create_user(UserName=IAM_USER_NAME)
                print(f"✅ Created IAM user {IAM_USER_NAME}")
        
        # Create SES policy
        ses_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ses:SendEmail",
                        "ses:SendRawEmail"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        if dry_run:
            print(f"[DRY RUN] Would attach SES policy to user: {IAM_USER_NAME}")
            return True
        
        # Check if policy exists and update it, or create new
        try:
            iam_client.get_user_policy(
                UserName=IAM_USER_NAME,
                PolicyName=IAM_POLICY_NAME
            )
            # Update existing policy
            iam_client.put_user_policy(
                UserName=IAM_USER_NAME,
                PolicyName=IAM_POLICY_NAME,
                PolicyDocument=json.dumps(ses_policy)
            )
            print(f"✅ Updated policy {IAM_POLICY_NAME} for user {IAM_USER_NAME}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # Create new policy
                iam_client.put_user_policy(
                    UserName=IAM_USER_NAME,
                    PolicyName=IAM_POLICY_NAME,
                    PolicyDocument=json.dumps(ses_policy)
                )
                print(f"✅ Created policy {IAM_POLICY_NAME} for user {IAM_USER_NAME}")
            else:
                raise
        
        # Create SMTP credentials
        try:
            response = iam_client.create_access_key(UserName=IAM_USER_NAME)
            access_key = response['AccessKey']
            
            print(f"\n🔑 SMTP Credentials for {IAM_USER_NAME}:")
            print(f"SMTP Username: {access_key['AccessKeyId']}")
            print(f"SMTP Password: {access_key['SecretAccessKey']}")
            print("\n⚠️  IMPORTANT: Save these credentials securely. You won't be able to retrieve the secret key again.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'LimitExceeded':
                print(f"⚠️  User {IAM_USER_NAME} already has the maximum number of access keys")
                print(f"Please delete an existing key before creating a new one")
            else:
                raise
        
        return True
    except ClientError as e:
        print(f"❌ Error creating IAM user: {e}")
        return False

def check_sandbox_status(ses_client):
    """Check if the SES account is in sandbox mode"""
    try:
        response = ses_client.get_account_sending_enabled()
        sending_enabled = response.get('Enabled', False)
        
        if sending_enabled:
            print("✅ SES account is out of sandbox mode")
            return False
        else:
            print("⚠️  SES account is in sandbox mode")
            return True
    except ClientError as e:
        print(f"❌ Error checking sandbox status: {e}")
        return True

def request_production_access(ses_client, region, dry_run=False):
    """Provide instructions for requesting production access"""
    if dry_run:
        print("[DRY RUN] Would provide instructions for requesting production access")
        return
    
    print("\n📝 To request production access (move out of sandbox):\n")
    print(f"1. Go to: https://{region}.console.aws.amazon.com/ses/home?region={region}#/account")
    print("2. Click 'Request production access'")
    print("3. Fill out the form with your use case details")
    print("4. Submit the request and wait for AWS approval")

def main():
    parser = argparse.ArgumentParser(description="Set up AWS SES for sending emails")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without making changes")
    args = parser.parse_args()
    
    # Get settings from config
    domain = settings.ses_domain
    sender_email = settings.ses_sender_email
    region = settings.aws_region
    
    if not domain or not sender_email or not region:
        print("❌ Missing required environment variables. Please set SES_DOMAIN, SES_SENDER_EMAIL, and AWS_REGION.")
        sys.exit(1)
    
    # Initialize AWS clients
    try:
        ses_client = boto3.client('ses', region_name=region)
        iam_client = boto3.client('iam', region_name=region)
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Setting up AWS SES for {domain} and {sender_email}\n")
    
    # Verify domain
    domain_verified = verify_domain(ses_client, domain, args.dry_run)
    
    # Set up DKIM
    dkim_setup = setup_dkim(ses_client, domain, args.dry_run)
    
    # Verify sender email
    email_verified = verify_email(ses_client, sender_email, args.dry_run)
    
    # Create IAM user for SMTP
    iam_user_created = create_iam_user(iam_client, args.dry_run)
    
    # Check sandbox status
    in_sandbox = check_sandbox_status(ses_client)
    if in_sandbox:
        request_production_access(ses_client, region, args.dry_run)
    
    # Summary
    print("\n📋 SES Setup Summary:")
    print(f"Domain verification: {'Pending' if not domain_verified else 'Complete'}")
    print(f"DKIM setup: {'Pending' if not dkim_setup else 'Complete'}")
    print(f"Email verification: {'Pending' if not email_verified else 'Complete'}")
    print(f"IAM user setup: {'Pending' if not iam_user_created else 'Complete'}")
    print(f"Sandbox status: {'In sandbox' if in_sandbox else 'Production ready'}")
    
    if domain_verified and dkim_setup and email_verified and iam_user_created:
        print("\n✅ SES setup complete!")
        if in_sandbox:
            print("⚠️  Note: Your account is still in sandbox mode. Follow the instructions above to request production access.")
    else:
        print("\n⚠️  SES setup is incomplete. Please address the pending items above.")

if __name__ == "__main__":
    main()
