# Klaviyo Reporting POC: Smoke Test Checklist

## Quick Reference Checklist

Use this checklist for quick reference during smoke testing. For detailed instructions, refer to the [Manual Smoke Test Guide](./manual_smoke_test_guide.md).

### Tester Information
- **Name:** _________________
- **Date:** _________________
- **Environment:** _________________

### Phase 0: Pre-flight Checks
- [ ] Pull latest main branch
- [ ] Create fresh virtual environment
- [ ] Install dependencies
- [ ] Verify `.env` file contains all required keys

### Phase 1: Pipeline Trigger & Data Landing
- [ ] Run Fivetran connector in dry-run mode
- [ ] Run Fivetran connector in live mode
- [ ] Verify BigQuery tables exist and contain data

### Phase 2: ETL Runner Validation
- [ ] Run ETL in dry-run mode
- [ ] Run ETL in live mode
- [ ] Verify CSV file creation
- [ ] Confirm S3 upload success
- [ ] Check S3 console for file visibility

### Phase 3: BigQuery Reporting View
- [ ] Deploy reporting view
- [ ] Query view and verify data

### Phase 4: Looker Studio Dashboard
- [ ] Open Looker template and verify fields
- [ ] Test date range filtering
- [ ] Test campaign/list filters
- [ ] Export PDF and CSV

### Phase 5: Google Sheets Workbook
- [ ] Open Google Sheet
- [ ] Push snapshot to sheet
- [ ] Verify new rows
- [ ] Test sheet sharing

### Phase 6: Email (SES) Smoke Test (Optional)
- [ ] Send test email
- [ ] Verify email receipt and links

### Phase 7: Client-Facing Assets
- [ ] Review client deck PDF
- [ ] Review client demo markdown

### Phase 8: CI/CD & Lint
- [ ] Run pytest
- [ ] Run flake8

## Pass/Fail Summary

| Phase | Status (Pass/Fail) | Notes |
|-------|-------------------|-------|
| 0: Pre-flight | | |
| 1: Pipeline & Data | | |
| 2: ETL Runner | | |
| 3: BigQuery View | | |
| 4: Looker Dashboard | | |
| 5: Google Sheets | | |
| 6: Email Test | | |
| 7: Client Assets | | |
| 8: CI/CD & Lint | | |

## Critical Issues

1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

## Automated Testing

Run the automated smoke test agent:
```bash
python scripts/smoke_test_agent.py  # Full test
python scripts/smoke_test_agent.py --dry-run  # Dry run
```
