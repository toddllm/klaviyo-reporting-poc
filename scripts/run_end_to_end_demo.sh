#!/bin/bash

# End-to-End Demo Script for Klaviyo Reporting POC
# This script runs the complete data pipeline from Fivetran to BigQuery to Looker Studio

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$ROOT_DIR/data"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/end_to_end_demo_$(date +%Y%m%d_%H%M%S).log"

# Default parameters
START_DATE=$(date -d "30 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)
DRY_RUN=false
SKIP_FIVETRAN=false
SKIP_BIGQUERY=false
SKIP_EMAIL=false
NOTIFY_EMAIL=""
REPORT_TYPE="campaign"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1"
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Function to display usage information
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --start-date YYYY-MM-DD   Start date for data extraction (default: 30 days ago)"
    echo "  --end-date YYYY-MM-DD     End date for data extraction (default: today)"
    echo "  --dry-run                 Run in dry-run mode without making actual API calls"
    echo "  --skip-fivetran           Skip the Fivetran sync step"
    echo "  --skip-bigquery          Skip the BigQuery load step"
    echo "  --skip-email             Skip sending email notification"
    echo "  --notify-email EMAIL     Email address to send notification to"
    echo "  --report-type TYPE       Type of report to generate (campaign or events, default: campaign)"
    echo "  --help                   Display this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --start-date)
            START_DATE="$2"
            shift 2
            ;;
        --end-date)
            END_DATE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-fivetran)
            SKIP_FIVETRAN=true
            shift
            ;;
        --skip-bigquery)
            SKIP_BIGQUERY=true
            shift
            ;;
        --skip-email)
            SKIP_EMAIL=true
            shift
            ;;
        --notify-email)
            NOTIFY_EMAIL="$2"
            shift 2
            ;;
        --report-type)
            REPORT_TYPE="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate dates
if ! date -d "$START_DATE" > /dev/null 2>&1; then
    log "Error: Invalid start date format. Use YYYY-MM-DD."
    exit 1
fi

if ! date -d "$END_DATE" > /dev/null 2>&1; then
    log "Error: Invalid end date format. Use YYYY-MM-DD."
    exit 1
fi

# Load environment variables
if [ -f "$ROOT_DIR/.env" ]; then
    log "Loading environment variables from .env file"
    source "$ROOT_DIR/.env"
else
    log "Warning: .env file not found. Make sure all required environment variables are set."
fi

# Check for required environment variables
required_vars=("FIVETRAN_API_KEY" "FIVETRAN_API_SECRET" "FIVETRAN_GROUP_ID" "FIVETRAN_CONNECTOR_ID" \
               "PG_HOST" "PG_PORT" "PG_DB" "PG_USER" "PG_PASSWORD" \
               "AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION" \
               "S3_BUCKET" "S3_PREFIX" "SES_FROM_EMAIL")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log "Error: Required environment variable $var is not set."
        exit 1
    fi
done

# Create timestamp for output files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CSV_OUTPUT="$DATA_DIR/klaviyo_export_${TIMESTAMP}.csv"
PROCESSED_CSV="$DATA_DIR/klaviyo_metrics_${TIMESTAMP}.csv"
S3_KEY="klaviyo-poc/klaviyo_metrics_${START_DATE}_${END_DATE}_${TIMESTAMP}.csv"
S3_URI="s3://$S3_BUCKET/$S3_KEY"

# Start the demo
log "Starting End-to-End Demo"
log "Parameters:"
log "  Start Date: $START_DATE"
log "  End Date: $END_DATE"
log "  Report Type: $REPORT_TYPE"
log "  Dry Run: $DRY_RUN"

# Step 1: Trigger Fivetran sync
if [ "$SKIP_FIVETRAN" = false ]; then
    log "Step 1: Triggering Fivetran sync"
    
    if [ "$DRY_RUN" = true ]; then
        log "[DRY RUN] Would trigger Fivetran sync for connector $FIVETRAN_CONNECTOR_ID in group $FIVETRAN_GROUP_ID"
    else
        log "Running Fivetran connector"
        python -m src.fivetran_connector_runner --group "$FIVETRAN_GROUP_ID" --connector "$FIVETRAN_CONNECTOR_ID"
        
        if [ $? -ne 0 ]; then
            log "Error: Fivetran sync failed"
            exit 1
        fi
        
        log "Fivetran sync completed successfully"
    fi
else
    log "Skipping Fivetran sync as requested"
fi

# Step 2: Run ETL process (extract from Postgres, transform, and load to CSV)
log "Step 2: Running ETL process"

ETL_CMD="python -m src.etl_runner --source fivetran --start $START_DATE --end $END_DATE --output $PROCESSED_CSV"

if [ "$DRY_RUN" = true ]; then
    ETL_CMD="$ETL_CMD --dry-run"
    log "[DRY RUN] Would run ETL process: $ETL_CMD"
else
    log "Running ETL process: $ETL_CMD"
    eval $ETL_CMD
    
    if [ $? -ne 0 ]; then
        log "Error: ETL process failed"
        exit 1
    fi
    
    log "ETL process completed successfully"
    log "Processed data saved to $PROCESSED_CSV"
fi

# Step 3: Upload to S3
log "Step 3: Uploading processed data to S3"

S3_CMD="python -m src.etl_runner --source fivetran --start $START_DATE --end $END_DATE --output $PROCESSED_CSV --upload-s3 $S3_URI"

if [ "$DRY_RUN" = true ]; then
    S3_CMD="$S3_CMD --dry-run"
    log "[DRY RUN] Would upload to S3: $S3_CMD"
else
    log "Uploading to S3: $S3_CMD"
    eval $S3_CMD
    
    if [ $? -ne 0 ]; then
        log "Error: S3 upload failed"
        exit 1
    fi
    
    log "S3 upload completed successfully"
    log "Data uploaded to $S3_URI"
fi

# Step 4: Load to BigQuery
if [ "$SKIP_BIGQUERY" = false ]; then
    log "Step 4: Loading data to BigQuery"
    
    BQ_CMD="python -m src.bq_loader --file $PROCESSED_CSV --report-type $REPORT_TYPE"
    
    if [ "$DRY_RUN" = true ]; then
        BQ_CMD="$BQ_CMD --dry-run"
        log "[DRY RUN] Would load to BigQuery: $BQ_CMD"
    else
        log "Loading to BigQuery: $BQ_CMD"
        eval $BQ_CMD
        
        if [ $? -ne 0 ]; then
            log "Error: BigQuery load failed"
            exit 1
        fi
        
        log "BigQuery load completed successfully"
    fi
else
    log "Skipping BigQuery load as requested"
fi

# Step 5: Generate dashboard link
log "Step 5: Generating dashboard link"

# Get the dashboard URL from environment variable or use a default
DASHBOARD_URL=${LOOKER_REPORT_URL:-"https://lookerstudio.google.com/reporting/YOUR_REPORT_ID"}

# Add parameters to filter by date range
DASHBOARD_LINK="$DASHBOARD_URL?params=%7B%22date_range%22:%7B%22start%22:%22$START_DATE%22,%22end%22:%22$END_DATE%22%7D%7D"

log "Dashboard link: $DASHBOARD_LINK"

# Step 6: Send email notification
if [ "$SKIP_EMAIL" = false ] && [ -n "$NOTIFY_EMAIL" ]; then
    log "Step 6: Sending email notification"
    
    EMAIL_SUBJECT="Klaviyo Reporting POC: Data Pipeline Complete ($START_DATE to $END_DATE)"
    EMAIL_BODY="The Klaviyo Reporting POC data pipeline has completed successfully.\n\n"
    EMAIL_BODY+="Date Range: $START_DATE to $END_DATE\n"
    EMAIL_BODY+="Report Type: $REPORT_TYPE\n\n"
    EMAIL_BODY+="Steps Completed:\n"
    EMAIL_BODY+="1. Fivetran sync: ${SKIP_FIVETRAN:-Completed}\n"
    EMAIL_BODY+="2. ETL process: Completed\n"
    EMAIL_BODY+="3. S3 upload: Completed ($S3_URI)\n"
    EMAIL_BODY+="4. BigQuery load: ${SKIP_BIGQUERY:-Completed}\n\n"
    EMAIL_BODY+="Dashboard Link: $DASHBOARD_LINK\n\n"
    EMAIL_BODY+="For more details, please check the log file: $LOG_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        log "[DRY RUN] Would send email notification to $NOTIFY_EMAIL"
        log "[DRY RUN] Email subject: $EMAIL_SUBJECT"
        log "[DRY RUN] Email body: $EMAIL_BODY"
    else
        log "Sending email notification to $NOTIFY_EMAIL"
        python "$SCRIPT_DIR/ses_smoketest.py" --to "$NOTIFY_EMAIL" --subject "$EMAIL_SUBJECT" --body "$EMAIL_BODY"
        
        if [ $? -ne 0 ]; then
            log "Error: Email notification failed"
            # Continue even if email fails
        else
            log "Email notification sent successfully"
        fi
    fi
else
    log "Skipping email notification as requested or no email address provided"
fi

# Summary
log "End-to-End Demo Completed Successfully"
log "Summary:"
log "  Date Range: $START_DATE to $END_DATE"
log "  Report Type: $REPORT_TYPE"
log "  Processed Data: $PROCESSED_CSV"
log "  S3 URI: $S3_URI"
log "  Dashboard Link: $DASHBOARD_LINK"
log "  Log File: $LOG_FILE"

echo ""
echo "End-to-End Demo Completed Successfully"
echo "Dashboard Link: $DASHBOARD_LINK"
echo "For more details, check the log file: $LOG_FILE"

exit 0
