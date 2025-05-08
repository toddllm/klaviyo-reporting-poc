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
# Check if we're on macOS or Linux and set dates accordingly
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS date command
    START_DATE=$(date -v-30d +%Y-%m-%d)
    END_DATE=$(date +%Y-%m-%d)
else
    # Linux date command
    START_DATE=$(date -d "30 days ago" +%Y-%m-%d)
    END_DATE=$(date +%Y-%m-%d)
fi
DRY_RUN=false
SKIP_FIVETRAN=false
SKIP_BIGQUERY=false
SKIP_EMAIL=false
SKIP_SHEETS=false
SKIP_REPORTING_VIEW=false
SKIP_LOOKER_REFRESH=false
NOTIFY_EMAIL=""
REPORT_TYPE="campaign"
SINCE_DAYS=${DEMO_DEFAULT_SINCE_DAYS:-30}
MAX_FIVETRAN_WAIT_MINUTES=10

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
    echo "  --skip-bigquery           Skip the BigQuery load step"
    echo "  --skip-email              Skip sending email notification"
    echo "  --skip-sheets             Skip Google Sheets export"
    echo "  --skip-reporting-view     Skip deploying the BigQuery reporting view"
    echo "  --skip-looker-refresh     Skip refreshing the Looker Studio data source"
    echo "  --notify-email EMAIL      Email address to send notification to"
    echo "  --report-type TYPE        Type of report to generate (campaign or events, default: campaign)"
    echo "  --since-days DAYS         Number of days to look back for data (default: 30)"
    echo "  --max-wait MINUTES        Maximum minutes to wait for Fivetran sync (default: 10)"
    echo "  --help                    Display this help message"
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
        --skip-sheets)
            SKIP_SHEETS=true
            shift
            ;;
        --skip-reporting-view)
            SKIP_REPORTING_VIEW=true
            shift
            ;;
        --skip-looker-refresh)
            SKIP_LOOKER_REFRESH=true
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
        --since-days)
            SINCE_DAYS="$2"
            shift 2
            ;;
        --max-wait)
            MAX_FIVETRAN_WAIT_MINUTES="$2"
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
validate_date() {
    local date_str=$1
    # Extract year, month, and day
    local year=$(echo "$date_str" | cut -d'-' -f1)
    local month=$(echo "$date_str" | cut -d'-' -f2)
    local day=$(echo "$date_str" | cut -d'-' -f3)
    
    # Check if the format is correct
    if [[ ! "$date_str" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        return 1
    fi
    
    # Check if month and day are valid
    if [[ "$month" -lt 1 || "$month" -gt 12 || "$day" -lt 1 || "$day" -gt 31 ]]; then
        return 1
    fi
    
    return 0
}

if ! validate_date "$START_DATE"; then
    log "Error: Invalid start date format. Use YYYY-MM-DD."
    exit 1
fi

if ! validate_date "$END_DATE"; then
    log "Error: Invalid end date format. Use YYYY-MM-DD."
    exit 1
fi

# Load environment variables
if [ -f "$ROOT_DIR/.env" ]; then
    log "Loading environment variables from .env file"
    set -a
    source "$ROOT_DIR/.env"
    set +a
else
    log "Warning: .env file not found. Make sure all required environment variables are set."
fi

# Skip environment validation in dry-run
if [ "$DRY_RUN" = true ]; then
    log "Dry run mode: skipping environment variable validation"
else
    # Check for required environment variables
    required_vars=("FIVETRAN_GROUP_ID" "FIVETRAN_CONNECTOR_ID" \
                   "PG_HOST" "PG_PORT" "PG_DB" "PG_USER" "PG_PASSWORD" \
                   "AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION" \
                   "S3_BUCKET" "S3_PREFIX" "SES_FROM_EMAIL" \
                   "BQ_PROJECT" "BQ_DATASET")

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log "Error: Required environment variable $var is not set."
            exit 1
        fi
    done
fi

# Check for Fivetran authentication credentials
if [ -z "$FIVETRAN_API_KEY" ] && [ -z "$FIVETRAN_API_SECRET" ] && \
   [ -z "$FIVETRAN_SYSTEM_KEY" ] && [ -z "$FIVETRAN_SYSTEM_KEY_SECRET" ] && \
   [ -z "$FIVETRAN_SYSTEM_KEY_B64" ]; then
    log "Error: No Fivetran authentication credentials found. Set either:"
    log "  - FIVETRAN_API_KEY and FIVETRAN_API_SECRET (classic API key), or"
    log "  - FIVETRAN_SYSTEM_KEY and FIVETRAN_SYSTEM_KEY_SECRET (system key), or"
    log "  - FIVETRAN_SYSTEM_KEY_B64 (pre-encoded system key)"
    exit 1
fi

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

# Step 1: Prompt about Fivetran sync duration
if [ "$SKIP_FIVETRAN" = false ]; then
    echo -n "Fivetran sync may take up to $MAX_FIVETRAN_WAIT_MINUTES minutes. Proceed? [y/N]: "
    read -r PROCEED_SYNC
    if [[ ! "$PROCEED_SYNC" =~ ^[Yy] ]]; then
        SKIP_FIVETRAN=true
        log "User opted to skip Fivetran sync"
    fi
fi

log "  Dry Run: $DRY_RUN"

# Step 2: Trigger Fivetran sync and poll until completion
if [ "$SKIP_FIVETRAN" = false ]; then
    log "Step 1: Triggering and waiting for Fivetran sync"
    if [ "$DRY_RUN" = true ]; then
        log "[DRY RUN] Would trigger and wait for Fivetran sync for connector $FIVETRAN_CONNECTOR_ID"
    else
        python -m src.fivetran_api_client --trigger-sync "$FIVETRAN_CONNECTOR_ID" --wait --timeout $((MAX_FIVETRAN_WAIT_MINUTES*60)) --poll-interval 30
        if [ $? -ne 0 ]; then
            log " Error: Fivetran sync failed or timed out"
            exit 1
        fi
        log " Fivetran sync completed successfully"
    fi
else
    log "Skipping Fivetran sync as requested"
fi

# Step 2: Run ETL process (extract from Postgres, transform, and load to CSV)
log "Step 2: Running ETL process using source Postgres"
ETL_CMD="python -m src.etl_runner --source Postgres --start $START_DATE --end $END_DATE --output $PROCESSED_CSV"
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
S3_CMD="python -m src.etl_runner --source Postgres --start $START_DATE --end $END_DATE --output $PROCESSED_CSV --upload-to-s3 $S3_URI"

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
        
        # Get tables to check from environment or use default
        SANITY_TABLES=${E2E_SANITY_TABLES:-"campaign,event,list"}
        
        # Show what would be run in dry-run mode
        SANITY_CMD="python $SCRIPT_DIR/bq_sanity_check.py --env $ROOT_DIR/.env --tables $SANITY_TABLES --dry-run"
        log "[DRY RUN] Would run BigQuery sanity check: $SANITY_CMD"
        log "[DRY RUN] Would check tables: $SANITY_TABLES"
    else
        log "Loading to BigQuery: $BQ_CMD"
        eval $BQ_CMD
        
        if [ $? -ne 0 ]; then
            log " Error: BigQuery load failed"
            exit 1
        fi
        
        log " BigQuery load completed successfully"
        
        # Run BigQuery sanity check after successful load
        log "Running BigQuery sanity check"
        # Get tables to check from environment or use default
        SANITY_TABLES=${E2E_SANITY_TABLES:-"campaign,event,list"}
        
        SANITY_CMD="python $SCRIPT_DIR/bq_sanity_check.py --env $ROOT_DIR/.env --tables $SANITY_TABLES"
        log "Running BigQuery sanity check: $SANITY_CMD"
        eval $SANITY_CMD
        
        if [ $? -ne 0 ]; then
            log " Error: BigQuery sanity check failed. Some tables may be missing or empty."
            exit 1
        fi
        
        log " BigQuery sanity check completed successfully"
    fi
else
    log "Skipping BigQuery load as requested"
fi

# Step 5: Deploy BigQuery reporting view
if [ "$SKIP_REPORTING_VIEW" = false ]; then
    log "Step 5: Deploying BigQuery reporting view"
    
    if [ "$DRY_RUN" = true ]; then
        log "[DRY RUN] Would deploy BigQuery reporting view using $SCRIPT_DIR/deploy_reporting_view.sh --dry-run"
    else
        log "Deploying BigQuery reporting view"
        
        # Set environment variables for the deploy script if they're not already set
        export PROJECT_ID=${PROJECT_ID:-$BQ_PROJECT}
        export DATASET=${DATASET:-$BQ_DATASET}
        export LOOKER_SA=${LOOKER_SA:-$LOOKER_SA_EMAIL}
        
        # Run the deploy script
        "$SCRIPT_DIR/deploy_reporting_view.sh"
        
        if [ $? -ne 0 ]; then
            log " Error: Failed to deploy BigQuery reporting view"
            exit 1
        fi
        
        log " BigQuery reporting view deployed successfully"
    fi
else
    log "Skipping BigQuery reporting view deployment as requested"
fi

# Step 6: Refresh Looker Studio data source
if [ "$SKIP_LOOKER_REFRESH" = false ]; then
    log "Step 6: Refreshing Looker Studio data source"
    
    if [ "$DRY_RUN" = true ]; then
        log "[DRY RUN] Would refresh Looker Studio data source using $SCRIPT_DIR/publish_looker_template.sh --dry-run"
    else
        log "Refreshing Looker Studio data source"
        
        # Run the publish script
        "$SCRIPT_DIR/publish_looker_template.sh"
        
        if [ $? -ne 0 ]; then
            log "u274c Error: Failed to refresh Looker Studio data source"
            # Continue even if this fails, as it's not critical
            LOOKER_REFRESH_STATUS="failed"
        else
            log "u2705 Looker Studio data source refreshed successfully"
            LOOKER_REFRESH_STATUS="success"
        fi
    fi
else
    log "Skipping Looker Studio data source refresh as requested"
    LOOKER_REFRESH_STATUS="skipped"
fi

# Step 7: Generate dashboard link
log "Step 7: Generating dashboard link"

# Get the dashboard URL from environment variable or use a default
DASHBOARD_URL=${LOOKER_REPORT_URL:-"https://lookerstudio.google.com/reporting/YOUR_REPORT_ID"}

# Add parameters to filter by date range
DASHBOARD_LINK="$DASHBOARD_URL?params=%7B%22date_range%22:%7B%22start%22:%22$START_DATE%22,%22end%22:%22$END_DATE%22%7D%7D"

log "Dashboard link: $DASHBOARD_LINK"

# Step 8: Export to Google Sheets (Optional)
if [ "$SKIP_SHEETS" = false ]; then
    log "Step 8: Exporting data to Google Sheets"
    
    # Check if Google Sheet ID is set
    if [ -z "${GOOGLE_SHEET_ID}" ]; then
        log "Warning: GOOGLE_SHEET_ID environment variable is not set. Skipping Google Sheets export."
    else
        SHEETS_CMD="python -m src.google_sheets_export --sheet-id \"${GOOGLE_SHEET_ID}\" --since-days ${SINCE_DAYS}"
        
        if [ "$DRY_RUN" = true ]; then
            SHEETS_CMD="$SHEETS_CMD --dry-run"
            log "[DRY RUN] Would export to Google Sheets: $SHEETS_CMD"
        else
            log "Exporting to Google Sheets: $SHEETS_CMD"
            eval $SHEETS_CMD
            
            if [ $? -ne 0 ]; then
                log "Warning: Google Sheets export failed, but continuing with the demo"
                SHEETS_URL="N/A (export failed)"
            else
                SHEETS_URL="https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/edit"
                log "Google Sheets export completed successfully"
                log "Sheets URL: $SHEETS_URL"
            fi
        fi
    fi
else
    log "Skipping Google Sheets export as requested"
    SHEETS_URL="N/A (skipped)"
fi

# Step 9: Send email notification
if [ "$SKIP_EMAIL" = false ] && [ -n "$NOTIFY_EMAIL" ]; then
    log "Step 9: Sending email notification"
    
    EMAIL_SUBJECT="Klaviyo Reporting POC: Data Pipeline Complete ($START_DATE to $END_DATE)"
    EMAIL_BODY="The Klaviyo Reporting POC data pipeline has completed successfully.\n\n"
    EMAIL_BODY+="Date Range: $START_DATE to $END_DATE\n"
    EMAIL_BODY+="Report Type: $REPORT_TYPE\n\n"
    EMAIL_BODY+="Steps Completed:\n"
    EMAIL_BODY+="1. Fivetran sync: ${SKIP_FIVETRAN:-Completed}\n"
    EMAIL_BODY+="2. ETL process: Completed\n"
    EMAIL_BODY+="3. S3 upload: Completed\n"
    EMAIL_BODY+="4. BigQuery load: ${SKIP_BIGQUERY:-Completed}\n"
    EMAIL_BODY+="5. Reporting view: ${SKIP_REPORTING_VIEW:-Deployed}\n"
    EMAIL_BODY+="6. Looker refresh: ${LOOKER_REFRESH_STATUS:-Completed}\n"
    EMAIL_BODY+="7. Google Sheets export: ${SHEETS_URL:-N/A}\n\n"
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
log "  BigQuery Tables Checked: ${SANITY_TABLES:-"Not checked (dry run or skipped)"}"
log "  Reporting View: ${SKIP_REPORTING_VIEW:-"Deployed"}"
log "  Looker Refresh: ${LOOKER_REFRESH_STATUS:-"Not refreshed"}"
log "  Dashboard Link: $DASHBOARD_LINK"
log "  Google Sheets: ${SHEETS_URL:-"Not exported"}"
log "  Log File: $LOG_FILE"

# Define status indicators
FIVETRAN_STATUS=" Fivetran sync"
if [ "$SKIP_FIVETRAN" = true ]; then
    FIVETRAN_STATUS=" Fivetran sync (skipped)"
fi

ETL_STATUS=" ETL process"

S3_STATUS=" S3 upload"

BQ_STATUS=" BigQuery load"
if [ "$SKIP_BIGQUERY" = true ]; then
    BQ_STATUS=" BigQuery load (skipped)"
fi

VIEW_STATUS=" Reporting view"
if [ "$SKIP_REPORTING_VIEW" = true ]; then
    VIEW_STATUS=" Reporting view (skipped)"
fi

LOOKER_STATUS=" Looker refresh"
if [ "$SKIP_LOOKER_REFRESH" = true ]; then
    LOOKER_STATUS=" Looker refresh (skipped)"
elif [ "$LOOKER_REFRESH_STATUS" = "failed" ]; then
    LOOKER_STATUS=" Looker refresh (failed)"
fi

SHEETS_STATUS=" Sheets export"
if [ "$SKIP_SHEETS" = true ]; then
    SHEETS_STATUS=" Sheets export (skipped)"
elif [ "$SHEETS_URL" = "N/A (export failed)" ]; then
    SHEETS_STATUS=" Sheets export (failed)"
fi

echo ""
echo " End-to-End Demo Completed Successfully"
echo "----------------------------------"
echo "$FIVETRAN_STATUS"
echo "$ETL_STATUS"
echo "$S3_STATUS"
echo "$BQ_STATUS"
echo "$VIEW_STATUS"
echo "$LOOKER_STATUS"
echo "$SHEETS_STATUS"
echo "----------------------------------"
echo " Dashboard Link: $DASHBOARD_LINK"
if [ "$SKIP_SHEETS" = false ] && [ -n "$SHEETS_URL" ] && [ "$SHEETS_URL" != "N/A (skipped)" ] && [ "$SHEETS_URL" != "N/A (export failed)" ]; then
    echo " Google Sheets: $SHEETS_URL"
fi
echo " For more details, check the log file: $LOG_FILE"

exit 0
