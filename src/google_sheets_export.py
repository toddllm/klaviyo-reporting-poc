#!/usr/bin/env python3

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import gspread
import pandas as pd
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Export BigQuery v_email_metrics view to Google Sheets")
    parser.add_argument(
        "--sheet-id",
        help="Google Sheet ID to write to",
        default=os.environ.get("GOOGLE_SHEET_ID", ""),
    )
    parser.add_argument(
        "--range-name",
        help="Named range or sheet tab to write to",
        default=os.environ.get("GOOGLE_SHEET_RANGE_NAME", "metrics_data"),
    )
    parser.add_argument(
        "--since-days",
        type=int,
        help="Number of days to look back for data",
        default=int(os.environ.get("DEMO_DEFAULT_SINCE_DAYS", "30")),
    )
    parser.add_argument(
        "--credentials-file",
        help="Path to Google service account credentials JSON file",
        default=os.environ.get("GOOGLE_CREDENTIALS_JSON", ""),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print first 5 rows of data without writing to sheet",
    )
    return parser.parse_args()


def get_credentials(credentials_file: str) -> Credentials:
    """Get Google API credentials from file or environment variable."""
    if os.path.exists(credentials_file):
        return service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
        )
    
    # Try to get credentials from environment variable
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    if credentials_json:
        if os.path.exists(credentials_json):
            return service_account.Credentials.from_service_account_file(
                credentials_json,
                scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
            )
        try:
            # Try parsing as JSON string
            credentials_dict = json.loads(credentials_json)
            return service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
            )
        except json.JSONDecodeError:
            pass
    
    raise ValueError(
        "Google credentials not found. Provide either --credentials-file argument "
        "or set GOOGLE_CREDENTIALS_JSON environment variable."
    )


def get_email_metrics_data(since_days: int) -> pd.DataFrame:
    """Query BigQuery for email metrics data."""
    from google.cloud import bigquery
    
    # Get project and dataset from environment variables
    project_id = os.environ.get("BQ_PROJECT", "clara-blueprint-script-24")
    dataset_id = os.environ.get("BQ_DATASET", "klaviyopoc")
    
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=since_days)
    
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    
    # Query the v_email_metrics view
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.v_email_metrics`
    WHERE send_date >= '{start_date}'
    AND send_date <= '{end_date}'
    ORDER BY send_date DESC
    """
    
    # Run the query and convert to DataFrame
    df = client.query(query).to_dataframe()
    
    # Add calculated columns for sheets
    if 'unique_opens' in df.columns and 'sends' in df.columns:
        df['open_rate'] = df['unique_opens'] / df['sends']
    
    if 'unique_clicks' in df.columns and 'sends' in df.columns:
        df['click_rate'] = df['unique_clicks'] / df['sends']
    
    return df


def export_to_sheets(df: pd.DataFrame, sheet_id: str, range_name: str, credentials: Credentials) -> str:
    """Export DataFrame to Google Sheets."""
    # Connect to Google Sheets
    gc = gspread.authorize(credentials)
    
    try:
        # Open the spreadsheet
        spreadsheet = gc.open_by_key(sheet_id)
        
        # Try to get the worksheet by name
        try:
            worksheet = spreadsheet.worksheet(range_name)
        except gspread.exceptions.WorksheetNotFound:
            # Create a new worksheet if it doesn't exist
            worksheet = spreadsheet.add_worksheet(title=range_name, rows=df.shape[0] + 10, cols=df.shape[1] + 5)
        
        # Clear existing content
        worksheet.clear()
        
        # Convert DataFrame to list of lists (including header)
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Update the worksheet
        worksheet.update(data)
        
        # Format the header row
        worksheet.format('1:1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        # Format date columns
        date_col_index = df.columns.get_loc('send_date') + 1 if 'send_date' in df.columns else None
        if date_col_index:
            worksheet.format(f'{chr(64 + date_col_index)}2:{chr(64 + date_col_index)}{len(data)}', {
                'numberFormat': {'type': 'DATE', 'pattern': 'yyyy-mm-dd'}
            })
        
        # Format percentage columns
        for col_name in ['open_rate', 'click_rate']:
            if col_name in df.columns:
                col_index = df.columns.get_loc(col_name) + 1
                worksheet.format(f'{chr(64 + col_index)}2:{chr(64 + col_index)}{len(data)}', {
                    'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}
                })
        
        # Format currency columns
        if 'revenue' in df.columns:
            col_index = df.columns.get_loc('revenue') + 1
            worksheet.format(f'{chr(64 + col_index)}2:{chr(64 + col_index)}{len(data)}', {
                'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}
            })
        
        # Get the spreadsheet URL
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={worksheet.id}"
        return spreadsheet_url
    
    except Exception as e:
        raise RuntimeError(f"Error exporting to Google Sheets: {str(e)}")


def main():
    """Main function to export BigQuery data to Google Sheets."""
    args = parse_args()
    
    # Validate arguments
    if not args.sheet_id:
        print("Error: Google Sheet ID is required. Provide --sheet-id or set GOOGLE_SHEET_ID environment variable.")
        sys.exit(1)
    
    try:
        # Get credentials
        credentials = get_credentials(args.credentials_file)
        
        # Get data from BigQuery
        print(f"Fetching email metrics data for the last {args.since_days} days...")
        df = get_email_metrics_data(args.since_days)
        
        if df.empty:
            print("No data found for the specified date range.")
            sys.exit(0)
        
        # Print preview in dry-run mode
        if args.dry_run:
            print("\nDRY RUN MODE - Preview of data (first 5 rows):")
            print(df.head(5))
            print(f"\nTotal rows: {len(df)}")
            print("\nColumns:")
            for col in df.columns:
                print(f"  - {col}")
            print("\nNo data was written to Google Sheets.")
            sys.exit(0)
        
        # Export to Google Sheets
        print(f"Exporting {len(df)} rows to Google Sheets...")
        spreadsheet_url = export_to_sheets(df, args.sheet_id, args.range_name, credentials)
        
        print("\nExport completed successfully!")
        print(f"Spreadsheet URL: {spreadsheet_url}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
