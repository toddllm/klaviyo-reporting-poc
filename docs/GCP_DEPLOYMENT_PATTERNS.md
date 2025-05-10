# GCP Deployment Patterns with Organizational Policy Restrictions

This document summarizes our findings and provides a proven pattern for deploying applications in GCP environments with free-tier organizational policy restrictions.

## Key Findings

### The Three Project IDs Mystery Solved

We've confirmed the relationship between the three different project identifiers:

1. **Project ID** (human-readable): `genial-shore-459316-d5`
   - Used in Google Cloud Console URLs
   - Used in `gcloud config get-value project`
   - Visible in error toast messages

2. **Project Number** (numeric): `2606668430`
   - Used in API resource paths (`projects/2606668430/services/...`)
   - Used in IAM bindings
   - Used by Google back-end services

3. **Internal Reference ID**: `498256360637`
   - Referenced in some organizational policy error messages
   - Used in parent-child relationships

All three reference the same project but are used in different contexts within GCP.

### API Enablement Pattern

We've confirmed that all necessary APIs are already enabled:
- Service Usage API
- Cloud Resource Manager API
- IAM API
- IAM Credentials API
- Cloud Run API
- Artifact Registry API
- SQL Component API
- SQL Admin API

The "warm-up" pattern is critical:
1. APIs must be enabled (already done)
2. There is a propagation delay (2-5 minutes) after enabling
3. First use has higher permission requirements
4. Subsequent uses have lower permission thresholds

### Authentication Pattern

We've established a working authentication pattern:

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │     │                     │
│  YOUR APPLICATION   │────▶│  IDENTITY TOKEN     │────▶│  GCP RESOURCE       │
│                     │     │  WITH AUDIENCE      │     │  (Cloud Run, etc.)  │
│                     │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      │
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │                     │
                            │  SERVICE ACCOUNT    │
                            │  (klaviyo-ls-imper  │
                            │   son-sa)           │
                            │                     │
                            └─────────────────────┘
```

## The Proven Pattern

Our Hello World demonstration proved this pattern works:

1. **Service Account**: Use the existing `klaviyo-ls-imperson-sa@genial-shore-459316-d5.iam.gserviceaccount.com`
2. **Role Assignments**: The service account has necessary roles (run.admin, cloudsql.client, etc.)
3. **Identity Tokens**: Use identity tokens with proper audience parameter for authentication

### Authentication Flow

```python
# Python example of the authentication flow
import subprocess
import requests

# Get identity token for service account
token = subprocess.run([
    "gcloud", "auth", "print-identity-token",
    "--impersonate-service-account", 
    "klaviyo-ls-imperson-sa@genial-shore-459316-d5.iam.gserviceaccount.com",
    "--audiences", "https://your-service-url"
], capture_output=True, text=True).stdout.strip()

# Use token to access service
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://your-service-url", headers=headers)
```

## Superset Deployment

We've applied this pattern to Superset deployment:

1. **Infrastructure**: Cloud SQL database + Cloud Run service
2. **Service Account**: Reusing `klaviyo-ls-imperson-sa` that worked for Looker Studio
3. **Access Pattern**: Identity tokens with audience parameter

### Terraform Implementation

The Terraform configuration in `minimal_superset.tf` implements this pattern:

```hcl
# Key elements of the configuration:

locals {
  service_account_email = "klaviyo-ls-imperson-sa@${var.project}.iam.gserviceaccount.com"
}

resource "google_cloud_run_v2_service" "superset" {
  # ...
  template {
    # ...
    service_account = local.service_account_email
  }
}

resource "google_cloud_run_service_iam_member" "self_invoker" {
  # ...
  member = "serviceAccount:${local.service_account_email}"
}
```

## Deployment Steps

1. The `apply_superset.sh` script handles deployment and testing:
   - Initializes and applies Terraform
   - Creates Cloud SQL database and Cloud Run service
   - Tests access using identity token authentication

## Browser Access

For browser access to deployed services:
1. Install ModHeader extension for Chrome/Firefox
2. Add an `Authorization` header with value `Bearer <token>`
3. Navigate to the service URL

## Relationship to Klaviyo Looker Studio Integration

This pattern is the same one that worked for the Klaviyo Looker Studio integration:
- Using an existing service account
- Token-based impersonation
- Direct access to resources

By following this pattern consistently, we can deploy multiple services in this GCP environment despite organizational policy restrictions.
