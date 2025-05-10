# Superset Deployment: Findings & Solutions

## Overview

This document summarizes the results of our investigation into deploying Apache Superset on Google Cloud Platform (GCP) with organizational policy restrictions. We've identified core patterns that explain the deployment challenges and developed a working solution that follows the same successful approach used for the Klaviyo Looker Studio integration.

## Key Findings

### 1. The "Three Project IDs" Mystery Solved

GCP environments, especially free-tier projects with organizational policies, use three distinct identifiers that appear in different contexts:

| ID Type | Example | Used In | Notes |
|---------|---------|---------|-------|
| **Project ID** | `genial-shore-459316-d5` | Console URLs, CLI commands | Human-readable identifier |
| **Project Number** | `2606668430` | API resource paths, IAM bindings | Used in most back-end services |
| **Organization Reference** | `498256360637` | Error messages, parent references | Referenced in organizational policy errors |

Understanding this relationship helps diagnose permission and API enablement issues.

### 2. API Enablement Pattern Confirmed

We observed the exact "warm-up" pattern documented in our research:
- APIs show as "enabled" in `gcloud services list` output
- Yet return `SERVICE_DISABLED` errors on first use
- Require 2-5 minutes of propagation time after enablement
- Have higher permission requirements for first usage

### 3. Organizational Policy Restrictions

We encountered several policy restrictions:
- Cannot create new service accounts (403 errors)
- Cannot make resources publicly accessible (`allUsers` denied)
- Cannot enable certain APIs directly (permission boundaries)
- Cannot deploy with Terraform due to parallelism that races against API warm-up

## Successful Deployment Pattern

Based on our Hello World experiments and Superset deployment, we established a reliable pattern:

### 1. Authentication Approach

Use token-based authentication with existing service accounts:
```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token \
  --impersonate-service-account=klaviyo-ls-imperson-sa@genial-shore-459316-d5.iam.gserviceaccount.com \
  --audiences=https://SERVICE-URL)

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" https://SERVICE-URL
```

### 2. Deployment Approach

For complex applications like Superset:
1. **Custom Container Images**: Build with specific platform targeting (`--platform=linux/amd64`)
2. **Direct Deployment**: Use `gcloud run deploy` instead of Terraform to avoid race conditions
3. **Service Account Reuse**: Leverage the existing service account that worked for Looker Studio

### 3. Testing & Access

For browser-based access:
1. Use browser extensions like ModHeader to add the Authorization header with the identity token
2. Generate fresh tokens as needed (they expire after 1 hour)

## Current Superset Deployment

We successfully deployed Superset at:
`https://superset-klaviyo-2606668430.us-central1.run.app`

This deployment:
- Uses SQLite for database (simplicity)
- Contains initialized admin user (admin/admin)
- Is accessible via identity token authentication

## Relationship to Klaviyo Looker Studio Integration

This deployment follows the same successful pattern established with the Looker Studio integration:
- Both use the same service account (`klaviyo-ls-imperson-sa`)
- Both implement token-based authentication 
- Both avoid organizational policy restrictions by using existing resources

## Future Improvements

For production-ready Superset:
1. Replace SQLite with Cloud SQL for scalability and reliability
2. Set up proper user management and authentication
3. Configure BigQuery connections for data access
4. Implement SSL/TLS for secure connections

## Conclusion

We've established a proven pattern for deploying applications in GCP environments with organizational policy restrictions. By understanding the core mechanisms behind API enablement, project identities, and authentication patterns, we can reliably deploy various services following this approach.
