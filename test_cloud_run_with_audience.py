#!/usr/bin/env python3
"""
Updated test script to access a Cloud Run service using token-based authentication
with proper audience parameter.

This follows the same pattern that worked for the Klaviyo Looker Studio integration.
"""

import os
import subprocess
import requests

# Cloud Run service URL
SERVICE_URL = "https://hello-world-2606668430.us-central1.run.app"

# Service account to impersonate (using the same one that worked for Looker Studio)
SERVICE_ACCOUNT = "klaviyo-ls-imperson-sa@genial-shore-459316-d5.iam.gserviceaccount.com"

def get_identity_token():
    """Get an identity token by impersonating the service account with proper audience"""
    try:
        result = subprocess.run(
            [
                "gcloud", "auth", "print-identity-token",
                "--impersonate-service-account", SERVICE_ACCOUNT,
                "--audiences", SERVICE_URL
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting token: {e}")
        print(f"Error output: {e.stderr}")
        return None

def access_cloud_run_service(token):
    """Access the Cloud Run service using the token"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Accessing {SERVICE_URL} with identity token auth...")
    response = requests.get(SERVICE_URL, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.text)
    
    return response

def main():
    """Main entry point"""
    # Get the identity token by impersonating the service account
    token = get_identity_token()
    
    if not token:
        print("Failed to get identity token. Cannot proceed.")
        return
    
    # Use the token to access the Cloud Run service
    access_cloud_run_service(token)

if __name__ == "__main__":
    main()
