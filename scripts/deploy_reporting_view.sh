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
: "${PROJECT_ID:=clara-blueprint-script-24}"
: "${DATASET:=klaviyopoc}"
: "${LOOKER_SA:=looker_sa@clara-blueprint-script-24.iam.gserviceaccount.com}"

SQL_FILE="sql/create_reporting_view.sql"
VIEW="${PROJECT_ID}.${DATASET}.v_email_metrics"

# Replace variables in SQL file
SQL_CONTENT=$(cat "${SQL_FILE}" | sed "s/\${PROJECT_ID}/${PROJECT_ID}/g" | sed "s/\${DATASET}/${DATASET}/g")

if $DRY_RUN; then
  echo "=== DRY RUN: View DDL ==="
  echo "$SQL_CONTENT"
  echo ""
  echo "=== DRY RUN: IAM Grant ==="
  echo "gcloud bigquery datasets add-iam-policy-binding ${DATASET} \\"
  echo "  --project=${PROJECT_ID} \\"
  echo "  --member=serviceAccount:${LOOKER_SA} \\"
  echo "  --role=roles/bigquery.dataViewer"
  exit 0
fi

echo "Deploying view ${VIEW}"
bq query --nouse_legacy_sql --use_legacy_sql=false --replace \
  --project_id="${PROJECT_ID}" "${SQL_CONTENT}"

echo "Granting Looker SA viewer on dataset ${DATASET}"
gcloud bigquery datasets add-iam-policy-binding "${DATASET}" \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${LOOKER_SA}" \
  --role="roles/bigquery.dataViewer"

echo "Deployment completed successfully!"
