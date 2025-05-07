# Google Sheets Setup for Klaviyo Reporting POC

## 1. Enable Google Sheets API

Enable the API for your GCP project:
```sh
gcloud services enable sheets.googleapis.com --project=clara-blueprint-script-24
```

## 2. Create the Google Sheet

- Go to [Google Sheets](https://sheets.new) and create a new sheet.
- Name it something like "Klaviyo Metrics".

## 3. Get Sheet ID and Range
- The **Sheet ID** is found in the URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
- The **Sheet Name** is the tab at the bottom (e.g., "Sheet1" or your custom name).
- The **Range Name** is typically the sheet name or a range like `Sheet1!A1:Z1000`.

## 4. Share the Sheet with Your Service Account
- Share the sheet with your service account email (e.g. `bigquery-poc@clara-blueprint-script-24.iam.gserviceaccount.com`) with **Editor** permissions.

## 5. Update Your `.env`
```ini
GOOGLE_SHEET_ID=<your_sheet_id_here>
GOOGLE_SHEET_NAME=<your_sheet_name>
GOOGLE_SHEET_RANGE_NAME=<metrics_data or desired range>
```

## 6. Test Access (Optional)
- Use a Python script with `gspread` or the Google Sheets API to verify access.

---

**Note:** There is no `gcloud` command to create a Google Sheet directly; use the web UI or Sheets API.

---

_This file documents the required steps for Google Sheets integration in the POC pipeline._
