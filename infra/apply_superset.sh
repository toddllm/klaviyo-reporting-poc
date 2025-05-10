#!/bin/bash
# Apply the Superset deployment using the successful pattern from our Hello World demo

set -e

CURRENT_DIR=$(pwd)
BASE_DIR=$(dirname "$0")

cd "${BASE_DIR}"

echo "=== Step 1: Initializing Terraform ==="
terraform init

echo "=== Step 2: Validating Configuration ==="
terraform validate

echo "=== Step 3: Applying Terraform Configuration ==="
echo "This will create Cloud SQL and Cloud Run resources"
terraform apply -auto-approve

echo "=== Step 4: Deployment Complete ==="
echo "Getting deployment information:"
terraform output

echo ""
echo "=== Step 5: Testing Access ==="
echo "Testing access to Superset using identity token authentication:"

# Get the Superset URL
SUPERSET_URL=$(terraform output -raw superset_url)

# Get an identity token for the service account
echo "Getting identity token..."
TOKEN=$(gcloud auth print-identity-token \
  --impersonate-service-account=klaviyo-ls-imperson-sa@$(terraform output -raw project).iam.gserviceaccount.com \
  --audiences=${SUPERSET_URL})

echo "Testing access with token..."
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer ${TOKEN}" ${SUPERSET_URL}

echo ""
echo "For browser access, install the ModHeader extension and add:"
echo "Header name: Authorization"
echo "Header value: Bearer <token>"

cd "${CURRENT_DIR}"
