#!/usr/bin/env python3
"""
Push a snapshot row into Google Sheet for smoke testing

This enhanced version includes:
- Automatic worksheet discovery and creation
- Detailed error handling and reporting
- Support for multiple data rows
"""

import os
import sys
import argparse
from datetime import datetime
import gspread
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv


def get_worksheet(spreadsheet, sheet_name):
    """Get worksheet, creating it if it doesn't exist."""
    try:
        # Try to get the specified worksheet
        return spreadsheet.worksheet(sheet_name)
    except WorksheetNotFound:
        print(f"Worksheet '{sheet_name}' not found. Available worksheets:")
        all_worksheets = spreadsheet.worksheets()
        
        if all_worksheets:
            # List available worksheets
            for i, ws in enumerate(all_worksheets):
                print(f"  {i+1}. {ws.title}")
            
            # Use the first worksheet if available
            print(f"Using the first available worksheet: '{all_worksheets[0].title}'")
            return all_worksheets[0]
        else:
            # Create a new worksheet if none exists
            print(f"No worksheets found. Creating new worksheet '{sheet_name}'")
            return spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)


def main():
    parser = argparse.ArgumentParser(description="Push snapshot to Google Sheet")
    parser.add_argument("--date", type=str, help="Date of snapshot (YYYY-MM-DD)", 
                        default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--sheet-id", type=str, help="Override Google Sheet ID from .env")
    parser.add_argument("--sheet-name", type=str, help="Override worksheet name from .env")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get sheet configuration
    sheet_id = args.sheet_id or os.environ.get("GOOGLE_SHEET_ID")
    sheet_name = args.sheet_name or os.environ.get("GOOGLE_SHEET_NAME", "Data")
    
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID must be set in .env or provided with --sheet-id", file=sys.stderr)
        sys.exit(1)

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS must be set in environment", file=sys.stderr)
        sys.exit(1)

    # Print configuration
    print(f"📊 Pushing data to Google Sheet (ID: {sheet_id})")
    print(f"📄 Target worksheet: {sheet_name}")
    print(f"🔑 Using credentials from: {creds_path}")

    try:
        # Authenticate using service account
        gc = gspread.service_account(filename=creds_path)
        
        # Open the sheet
        try:
            sh = gc.open_by_key(sheet_id)
        except SpreadsheetNotFound:
            print(f"❌ Google Sheet with ID '{sheet_id}' not found. Check your GOOGLE_SHEET_ID.", file=sys.stderr)
            sys.exit(1)
        
        # Get or create worksheet
        worksheet = get_worksheet(sh, sheet_name)
            
        # Check if headers exist, add them if not
        values = worksheet.get_all_values()
        if not values:
            print("Adding header row to empty worksheet")
            worksheet.append_row(["Date", "Timestamp", "Status", "Notes"])
        
        # Prepare test data
        now = datetime.utcnow().isoformat()
        test_row = [args.date, now, "Success", "Smoke test data"]

        # Write test data to the worksheet
        worksheet.append_row(test_row)

        print(f"✅ Successfully wrote snapshot for {args.date} to Google Sheet")
        print(f"📝 Worksheet: '{worksheet.title}'")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 