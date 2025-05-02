# Validation Instructions for PR

Before merging this PR, the validation dev should verify the following changes:

## 1. Verify the `get_config()` function works correctly

Run the following test to ensure the config function returns the expected values:

```bash
python -c "from config import get_config; print(get_config())"  
```

Verify that the output contains all the expected configuration keys:
- KLAVIYO_API_KEY
- AUDIENCE_ID
- CAMPAIGN_ID
- TEMPLATE_ID
- MODE
- KLAVIYO_API_VERSION

## 2. Verify cache file generation in mock mode

Run the fetch_metrics script in mock mode:

```bash
python fetch_metrics.py
```

Verify that:
- The `.metric_ids.json` cache file is generated
- The file contains mock metric IDs for "Opened Email", "Clicked Email", and "Placed Order"
- The `metrics.csv` file is generated with mock data

## 3. Test metric window handling

Run the metric window tests to ensure they pass:

```bash
python -m pytest tests/test_metric_window.py -v
```

All tests should pass, confirming that:
- The date handling works correctly
- The caching of metric IDs works as expected
- The dry-run mode functions properly
- The mock mode generates appropriate test data

## 4. Test dry-run mode

Run the script in dry-run mode:

```bash
python fetch_metrics.py --dry-run
```

Verify that:
- It shows the correct UTC date format and date range
- No API calls are made (no errors should appear)
- No files are modified

## 5. Test with explicit date parameters

Run the script with explicit dates:

```bash
python fetch_metrics.py --start-date 2025-05-01 --end-date 2025-05-08
```

Verify that:
- The script runs successfully
- The metrics.csv file contains data for the specified date range
- The .metric_ids.json cache file is updated

The PR should only be merged when all these validation steps pass successfully.
