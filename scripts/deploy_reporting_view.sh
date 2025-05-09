#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy_reporting_view.sh [--dry-run]
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# Set default values and validate required environment variables
: "${PROJECT_ID:=your-project-id}"
: "${DATASET:=klaviyopoc}"
: "${LOOKER_SA:=looker_sa@your-project-id.iam.gserviceaccount.com}"

SQL_FILE="sql/create_reporting_view.sql"
VIEW="${PROJECT_ID}.${DATASET}.v_email_metrics"

# Create a temp file with variables substituted
TMP_SQL_FILE=$(mktemp)
trap 'rm -f "$TMP_SQL_FILE"' EXIT

# Replace variables in SQL
sed -e "s/\${PROJECT_ID}/${PROJECT_ID}/g" -e "s/\${DATASET}/${DATASET}/g" "${SQL_FILE}" > "${TMP_SQL_FILE}"

if $DRY_RUN; then
  echo "=== DRY RUN: View DDL with substituted variables ==="
  cat "${TMP_SQL_FILE}"
  echo ""
  echo "=== DRY RUN: IAM Grant ==="
  echo "gcloud projects add-iam-policy-binding ${PROJECT_ID} \\"
  echo "  --member=serviceAccount:${LOOKER_SA} \\"
  echo "  --role=roles/bigquery.dataViewer"
  
  # In dry-run mode, just simulate success
  echo "[DRY RUN] View would be created and permissions granted"
  exit 0
fi

echo "Deploying view ${VIEW}"
bq query --nouse_legacy_sql --use_legacy_sql=false --replace \
  --project_id="${PROJECT_ID}" < "${TMP_SQL_FILE}"

# Skip permission granting if Looker SA doesn't exist
if gcloud iam service-accounts describe "${LOOKER_SA}" > /dev/null 2>&1; then
  echo "Granting Looker SA viewer on dataset ${DATASET}"
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${LOOKER_SA}" \
    --role="roles/bigquery.dataViewer"
else
  echo "Warning: Looker SA ${LOOKER_SA} does not exist, skipping permission grant"
fi

echo "Deployment completed successfully!"
