#!/bin/bash

set -e

# Default values
DRY_RUN=false
DASHBOARD_JSON="../config/looker_dashboard.json"
OUTPUT_JSON="../config/looker_studio_dashboard_config.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --dashboard-json)
      DASHBOARD_JSON="$2"
      shift 2
      ;;
    --output-json)
      OUTPUT_JSON="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --dry-run             Show what would be done without making changes"
      echo "  --dashboard-json PATH Path to the dashboard JSON template (default: ../config/looker_dashboard.json)"
      echo "  --output-json PATH    Path to save the updated JSON with document ID (default: ../config/looker_studio_dashboard_config.json)"
      echo "  --help                Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Ensure we're in the scripts directory
cd "$(dirname "$0")"

# Load environment variables
if [ -f "../.env" ]; then
  source "../.env"
fi

# Check for required environment variables
if [ -z "$BQ_PROJECT" ] || [ -z "$BQ_DATASET" ]; then
  echo "Error: BQ_PROJECT and BQ_DATASET environment variables must be set"
  echo "Please ensure these are defined in your .env file"
  exit 1
fi

# Read the dashboard JSON template
if [ ! -f "$DASHBOARD_JSON" ]; then
  echo "Error: Dashboard JSON template not found at $DASHBOARD_JSON"
  exit 1
fi

# Replace variables in the template
TEMP_JSON=$(mktemp)
cat "$DASHBOARD_JSON" | \
  sed "s/\${BQ_PROJECT}/$BQ_PROJECT/g" | \
  sed "s/\${BQ_DATASET}/$BQ_DATASET/g" > "$TEMP_JSON"

# If this is a dry run, just show what would be done
if [ "$DRY_RUN" = true ]; then
  echo "Dry run mode - would publish the following dashboard JSON:"
  cat "$TEMP_JSON"
  rm "$TEMP_JSON"
  exit 0
fi

# Create or update the Looker Studio document using the Google Drive API
echo "Publishing Looker Studio dashboard template..."

# Check if we have an existing document ID
DOCUMENT_ID=""
if [ -f "$OUTPUT_JSON" ]; then
  DOCUMENT_ID=$(grep -o '"documentId": "[^"]*"' "$OUTPUT_JSON" | cut -d '"' -f 4)
fi

# If we have a document ID, update it; otherwise create a new one
if [ -n "$DOCUMENT_ID" ]; then
  echo "Updating existing Looker Studio document with ID: $DOCUMENT_ID"
  # In a real implementation, this would use the Google Drive API to update the document
  # For this POC, we'll simulate the update by copying the template and adding the document ID
  cat "$TEMP_JSON" | jq '. + {"documentId": "'"$DOCUMENT_ID"'"}' > "$OUTPUT_JSON"
else
  echo "Creating new Looker Studio document"
  # In a real implementation, this would use the Google Drive API to create a new document
  # For this POC, we'll simulate the creation by generating a random document ID
  NEW_ID="looker-$(date +%Y%m%d%H%M%S)"
  cat "$TEMP_JSON" | jq '. + {"documentId": "'"$NEW_ID"'"}' > "$OUTPUT_JSON"
  DOCUMENT_ID="$NEW_ID"
fi

# Clean up temporary file
rm "$TEMP_JSON"

# Generate the "Make a copy" URL
COPY_URL="https://lookerstudio.google.com/reporting/create?c.reportId=$DOCUMENT_ID"

echo "Success! Looker Studio dashboard template published."
echo "Document ID: $DOCUMENT_ID"
echo "Make a copy URL: $COPY_URL"
echo "Updated configuration saved to: $OUTPUT_JSON"
