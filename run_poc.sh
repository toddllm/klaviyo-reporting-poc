#!/bin/bash
set -euo pipefail

# Orchestration script for Klaviyo Reporting POC
# This script runs all the necessary steps in sequence

# Default values
DRY_RUN=false
MODE="live"
MAX_RETRIES=5
RETRY_DELAY=30

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    --max-retries=*)
      MAX_RETRIES="${1#*=}"
      shift
      ;;
    --retry-delay=*)
      RETRY_DELAY="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Set dry run flag for all scripts
DRY_RUN_FLAG=""
if [ "$DRY_RUN" = true ]; then
  DRY_RUN_FLAG="--dry-run"
  echo "Running in dry-run mode"
fi

# Set mode for all scripts
MODE_FLAG="--mode=$MODE"
echo "Running in $MODE mode"

# Function to run a command with polling for success
run_with_polling() {
  local cmd=$1
  local check_cmd=$2
  local retries=$MAX_RETRIES
  local delay=$RETRY_DELAY
  
  echo "Running: $cmd"
  eval "$cmd"
  
  if [ -n "$check_cmd" ]; then
    echo "Checking if operation completed successfully..."
    while [ $retries -gt 0 ]; do
      if eval "$check_cmd"; then
        echo "Operation completed successfully!"
        return 0
      else
        echo "Operation not yet complete. Retrying in $delay seconds... ($retries retries left)"
        sleep $delay
        retries=$((retries-1))
      fi
    done
    
    echo "Error: Operation did not complete after $MAX_RETRIES retries"
    exit 1
  fi
}

# Main execution flow
echo "Starting Klaviyo Reporting POC orchestration"

# Check if script exists and which arguments it supports
check_script() {
  local script=$1
  local check_type=$2  # 'exists' or 'mode'
  
  # Check if script exists
  if [ ! -f "$script" ]; then
    if [ "$check_type" = "exists" ]; then
      echo "false"
      return
    fi
  fi
  
  # If checking for mode support
  if [ "$check_type" = "mode" ]; then
    # Run the script with --help and check if it mentions mode
    if python "$script" --help 2>&1 | grep -q -- "--mode"; then
      echo "true"
    else
      echo "false"
    fi
  else
    # Just checking existence
    echo "true"
  fi
}

# Step 1: Seed profiles
# Check if seed_profiles.py exists and supports the mode flag
if [ "$(check_script seed_profiles.py exists)" = "true" ]; then
  if [ "$(check_script seed_profiles.py mode)" = "true" ]; then
    run_with_polling "python seed_profiles.py $DRY_RUN_FLAG $MODE_FLAG" ""
  else
    run_with_polling "python seed_profiles.py $DRY_RUN_FLAG" ""
  fi
else
  echo "Warning: seed_profiles.py not found, skipping this step"
fi

# Step 2: Create and send campaign
# Check if create_send_campaign.py exists and supports the mode flag
if [ "$(check_script create_send_campaign.py exists)" = "true" ]; then
  if [ "$(check_script create_send_campaign.py mode)" = "true" ]; then
    run_with_polling "python create_send_campaign.py $DRY_RUN_FLAG $MODE_FLAG" ""
  else
    run_with_polling "python create_send_campaign.py $DRY_RUN_FLAG" ""
  fi
else
  echo "Warning: create_send_campaign.py not found, skipping this step"
fi

# Step 3: Wait for metrics to be available and fetch them
# This step includes polling logic to wait for metrics to be ready
if [ "$(check_script fetch_metrics.py exists)" = "true" ]; then
  if [ "$(check_script fetch_metrics.py mode)" = "true" ]; then
    run_with_polling "python fetch_metrics.py $DRY_RUN_FLAG $MODE_FLAG" "python check_metrics_ready.py $MODE_FLAG"
  else
    run_with_polling "python fetch_metrics.py $DRY_RUN_FLAG" "python check_metrics_ready.py $MODE_FLAG"
  fi
else
  echo "Warning: fetch_metrics.py not found, skipping this step"
fi

# Step 4: Simulate events
if [ "$(check_script simulate_events.py exists)" = "true" ]; then
  if [ "$(check_script simulate_events.py mode)" = "true" ]; then
    run_with_polling "python simulate_events.py $DRY_RUN_FLAG $MODE_FLAG" ""
  else
    run_with_polling "python simulate_events.py $DRY_RUN_FLAG" ""
  fi
else
  echo "Warning: simulate_events.py not found, skipping this step"
fi

# Step 5: Push data to Google Sheets
if [ "$(check_script push_to_sheet.py exists)" = "true" ]; then
  if [ "$(check_script push_to_sheet.py mode)" = "true" ]; then
    run_with_polling "python push_to_sheet.py $DRY_RUN_FLAG $MODE_FLAG" ""
  else
    run_with_polling "python push_to_sheet.py $DRY_RUN_FLAG" ""
  fi
else
  echo "Warning: push_to_sheet.py not found, skipping this step"
fi

# Step 6: Generate AI insights
if [ "$(check_script ai_insights.py exists)" = "true" ]; then
  if [ "$(check_script ai_insights.py mode)" = "true" ]; then
    run_with_polling "python ai_insights.py $DRY_RUN_FLAG $MODE_FLAG" ""
  else
    run_with_polling "python ai_insights.py $DRY_RUN_FLAG" ""
  fi
else
  echo "Warning: ai_insights.py not found, skipping this step"
fi

# Step 7: Send Slack notification
if [ "$(check_script slack_integration.py exists)" = "true" ]; then
  if [ "$(check_script slack_integration.py mode)" = "true" ]; then
    run_with_polling "python slack_integration.py $DRY_RUN_FLAG $MODE_FLAG" ""
  else
    run_with_polling "python slack_integration.py $DRY_RUN_FLAG" ""
  fi
else
  echo "Warning: slack_integration.py not found, skipping this step"
fi

echo "Klaviyo Reporting POC orchestration completed successfully!"
exit 0
