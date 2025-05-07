#!/usr/bin/env python3
"""
Push a snapshot row into Google Sheet for smoke testing
"""

import os
import sys
import argparse
from datetime import datetime
import gspread
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Push snapshot to Google Sheet")
    parser.add_argument("--date", type=str, required=True, help="Date of snapshot (YYYY-MM-DD)")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    sheet_name = os.environ.get("GOOGLE_SHEET_NAME")
    if not sheet_id or not sheet_name:
        print("❌ GOOGLE_SHEET_ID and GOOGLE_SHEET_NAME must be set in .env", file=sys.stderr)
        sys.exit(1)

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS must be set in environment", file=sys.stderr)
        sys.exit(1)

    # Authenticate using service account
    gc = gspread.service_account(filename=creds_path)

    # Open the sheet and worksheet
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.worksheet(sheet_name)

    # Prepare test data
    now = datetime.utcnow().isoformat()
    test_row = [args.date, now, "Success"]

    # Write test data to the first empty row
    worksheet.append_row(test_row)

    print(f"✅ Successfully wrote snapshot {args.date} to Google Sheet '{sheet_name}' (ID: {sheet_id}) at {now}")

if __name__ == "__main__":
    main() 