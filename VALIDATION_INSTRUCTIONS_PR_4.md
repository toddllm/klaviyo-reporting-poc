# Validation Instructions for PR 4

Before merging this PR, the validation dev should verify:

1. Run the dry-run mode to check the correct UTC window:
   ```bash
   python fetch_metrics.py --dry-run
   ```
   Verify that it shows the correct UTC date format and date range.

2. Run the metric window tests to ensure they pass:
   ```bash
   pytest -k test_metric_window
   ```
   All tests should pass, confirming that:
   - The date handling works correctly
   - The caching of metric IDs works as expected
   - The dry-run mode functions properly
   - The mock mode generates appropriate test data

3. Run the script with actual dates to verify it works with explicit parameters:
   ```bash
   python fetch_metrics.py --start-date 2025-05-01 --end-date 2025-05-08
   ```
   
4. Check that the `.metric_ids.json` cache file is generated correctly and contains the expected metric IDs.

5. Verify that the `metrics.csv` output file contains both the general metrics and the separate revenue metrics.

The PR should only be merged when all these validation steps pass successfully.
