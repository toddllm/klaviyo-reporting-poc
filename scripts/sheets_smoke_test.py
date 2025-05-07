import os
import gspread
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env
load_dotenv()

SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
SHEET_NAME = os.environ["GOOGLE_SHEET_NAME"]
RANGE_NAME = os.environ.get("GOOGLE_SHEET_RANGE_NAME", SHEET_NAME)

# Authenticate using service account
creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
gc = gspread.service_account(filename=creds_path)

# Open the sheet and worksheet
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.worksheet(SHEET_NAME)

# Prepare test data
now = datetime.utcnow().isoformat()
test_row = ["POC Smoke Test", now, "Success"]

# Write test data to the first empty row
worksheet.append_row(test_row)

print(f"✅ Successfully wrote to Google Sheet '{SHEET_NAME}' (ID: {SHEET_ID}) at {now}")
