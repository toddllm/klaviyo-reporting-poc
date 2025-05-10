// Ultra Minimal Terraform for Apache Superset deployment using identity token authentication
// Based on the successful Hello World pattern using SQLite to avoid Cloud SQL permissions
// This is a simplification to work around organizational policy restrictions in free-tier GCP projects

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

// Define locals for reuse
locals {
  // Use the same service account that worked for the Looker Studio integration
  service_account_email = "klaviyo-ls-imperson-sa@${var.project}.iam.gserviceaccount.com"
}

// Deploy Superset using an existing public image with SQLite for simplicity
resource "google_cloud_run_v2_service" "superset" {
  name     = "superset-${var.tenant_slug}"
  location = var.region

  template {
    containers {
      // Use official Superset image
      image = "apache/superset:latest"
      
      env {
        name  = "SUPERSET_SECRET_KEY"
        value = "your-secret-key-here-please-change-in-production"
      }
      
      env {
        name  = "FEATURE_FLAGS"
        value = "{\"EMBEDDED_SUPERSET\": true}"
      }
      
      // Use SQLite for simplicity to avoid Cloud SQL permission issues
      env {
        name  = "SQLALCHEMY_DATABASE_URI"
        value = "sqlite:////var/lib/superset/superset.db"
      }
    }
    
    // Use existing service account that worked for Looker Studio integration
    service_account = local.service_account_email
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

// Grant the service account access to invoke the service (for same account access)
resource "google_cloud_run_service_iam_member" "self_invoker" {
  location = google_cloud_run_v2_service.superset.location
  service  = google_cloud_run_v2_service.superset.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${local.service_account_email}"
}

// Output the Superset URL
output "superset_url" {
  value = google_cloud_run_v2_service.superset.uri
}

// Output instructions for accessing Superset using identity token authentication
output "access_instructions" {
  value = <<-EOT
    To access Superset, use the identity token pattern that worked for our Hello World demo:
    
    1. Get an identity token for the service account:
       TOKEN=$(gcloud auth print-identity-token --impersonate-service-account=${local.service_account_email} --audiences=${google_cloud_run_v2_service.superset.uri})
    
    2. Access Superset using the token:
       curl -H "Authorization: Bearer $TOKEN" ${google_cloud_run_v2_service.superset.uri}
    
    3. For browser access, use a tool like ModHeader extension to add the Authorization header.
    
    IMPORTANT NOTE: This deployment uses SQLite instead of Cloud SQL to work around permission issues.
    For a production deployment, you'd need to request organization admin to grant your project
    the appropriate permissions for Cloud SQL.
  EOT
}
