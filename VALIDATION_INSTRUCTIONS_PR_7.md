# Validation Instructions for PR 7: Simulate Events Script

## Overview

This PR implements the following requirements:

1. Rename `simulate_open.py` → `simulate_events.py`
2. Ensure payload includes `metric_id` inside `metric` object per API v2025-04-15
3. Provide helper `get_or_create_custom_metric(name)`

## Validation Steps

### 1. Verify Dry Run Mode Shows Correct Payload Structure

Run the script in dry-run mode to verify the payload structure:

```bash
python simulate_events.py --dry-run
```

Expected output should show a payload with `metric_id` inside the `metric` object:

```
[DRY-RUN] Would get or create metric with name: Opened Email
[DRY-RUN] Would POST to https://a.klaviyo.com/api/events/ with payload: {'data': {'type': 'event', 'attributes': {...}, 'relationships': {'profile': {'data': {'type': 'profile', 'id': '...'}}, 'metric': {'data': {'type': 'metric', 'id': '...'}}}}}}
Successfully simulated 1/1 events
```

### 2. Verify Custom Metric Creation

Run the script with a custom metric name:

```bash
python simulate_events.py --metric "Custom Test Event" --dry-run
```

Expected output should show the custom metric being created or retrieved:

```
[DRY-RUN] Would get or create metric with name: Custom Test Event
[DRY-RUN] Would POST to https://a.klaviyo.com/api/events/ with payload: {...}
Successfully simulated 1/1 events
```

### 3. Run Unit Tests

Verify that all unit tests pass:

```bash
python -m pytest tests/test_simulate_events.py -v
```

All tests should pass, confirming that:
- The `get_or_create_custom_metric` helper works correctly
- The event payload structure includes `metric_id` inside the `metric` object
- The main function handles different command-line arguments correctly

## Evidence of Successful Validation

Please include the following evidence in your PR:

1. Screenshot or copy of the dry-run output showing the correct payload structure
2. Test results showing all tests passing
