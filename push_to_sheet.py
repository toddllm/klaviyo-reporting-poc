#!/usr/bin/env python3

import os
import csv
import argparse
import gspread
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials
from config import get_config, GOOGLE_SHEET_ID, GOOGLE_SHEET_NAME, GOOGLE_SHEET_RANGE_NAME

# Define the scopes for Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def authenticate_gspread():
    """Authenticate with Google Sheets API using service account credentials"""
    try:
        # Look for credentials file in the current directory or specified location
        creds_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
        creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def read_metrics_csv(file_path='metrics.csv'):
    """Read metrics data from CSV file"""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run fetch_metrics.py first.")
        return None
    
    data = []
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    
    return data

def push_to_sheet(data, dry_run=False):
    """Push data to Google Sheet and set up named range"""
    if dry_run:
        print(f"Would push {len(data)} rows of data to Google Sheet {GOOGLE_SHEET_ID}")
        print(f"Would set up named range '{GOOGLE_SHEET_RANGE_NAME}' for the data")
        return True
    
    # Authenticate with Google Sheets API
    client = authenticate_gspread()
    if not client:
        return False
    
    try:
        # Open the spreadsheet and worksheet
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Try to get the worksheet by name, create it if it doesn't exist
        try:
            worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(GOOGLE_SHEET_NAME, rows=100, cols=20)
        
        # Clear existing data
        worksheet.clear()
        
        # Update the worksheet with the data using RAW input option
        worksheet.update(data, value_input_option='RAW')
        
        # Calculate the range for the named range
        num_rows = len(data)
        num_cols = len(data[0]) if data else 0
        end_cell = rowcol_to_a1(num_rows, num_cols)
        range_a1 = f"A1:{end_cell}"
        
        # Set up the named range using the Google Sheets API directly
        # Since we don't have a1_range_to_grid_range in this version of gspread,
        # we'll create the grid range manually
        sheet_id = worksheet.id
        
        # Create a named range using the Google Sheets API
        body = {
            'requests': [{
                'addNamedRange': {
                    'namedRange': {
                        'name': GOOGLE_SHEET_RANGE_NAME,
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': num_rows,
                            'startColumnIndex': 0,
                            'endColumnIndex': num_cols
                        }
                    }
                }
            }]
        }
        
        spreadsheet.batch_update(body)
        
        print(f"Successfully pushed data to {GOOGLE_SHEET_NAME} and set up named range '{GOOGLE_SHEET_RANGE_NAME}'")
        print(f"View the sheet at: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
        return True
    
    except Exception as e:
        print(f"Error pushing data to sheet: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Push metrics data to Google Sheets")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without making API calls")
    parser.add_argument("--file", default="metrics.csv", help="Path to metrics CSV file (default: metrics.csv)")
    args = parser.parse_args()
    
    # Read metrics data from CSV
    data = read_metrics_csv(args.file)
    if not data:
        return 1
    
    # Push data to Google Sheet
    success = push_to_sheet(data, args.dry_run)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
