# PR 2: LookML Field Mapper - Implementation Guide

This guide provides detailed instructions for implementing the `lookml_field_mapper.py` script as part of PR 2 in the Narrow Scope POC PR Plan.

## Overview

The `lookml_field_mapper.py` script is responsible for normalizing Klaviyo fields to match the expected schema for Looker Studio visualizations. It should:

1. Define a mapping dictionary from raw Klaviyo field names to reporting-ready field names
2. Provide functions to transform raw Klaviyo data to the normalized format
3. Include comprehensive unit tests
4. Be designed for reuse in the ETL pipeline or mock data setup

## Implementation Steps

### 1. Create the Basic Script Structure

Create a new file at `src/lookml_field_mapper.py` with the following structure:

```python
#!/usr/bin/env python3

# Field mapping dictionary
FIELD_MAP = {
    # Klaviyo field name -> Looker Studio field name
    "send_time": "date",
    "name": "campaign_name",
    "subject": "subject_line",
    "open_rate": "open_rate",
    "click_rate": "click_rate",
    "list_id": "list_id"
}

# Additional derived fields that need to be calculated
DERIVED_FIELDS = {
    # Derived field name -> Function to calculate it
    # Example: "engagement_score": lambda record: (record.get("open_rate", 0) * 0.7 + record.get("click_rate", 0) * 0.3)
}

def normalize_record(raw_record):
    """Normalize a single record from Klaviyo format to Looker Studio format"""
    # Implementation here

def normalize_records(raw_records):
    """Normalize a list of records from Klaviyo format to Looker Studio format"""
    # Implementation here

def get_field_mapping():
    """Return the field mapping dictionary"""
    return FIELD_MAP.copy()

def get_derived_fields():
    """Return the derived fields dictionary"""
    return DERIVED_FIELDS.copy()

# Main function for testing
def main():
    # Example usage
    import json
    
    # Sample Klaviyo record
    sample_record = {
        "id": "campaign_123",
        "name": "Test Campaign",
        "send_time": "2025-05-01T10:00:00Z",
        "subject": "Test Subject",
        "open_rate": 0.45,
        "click_rate": 0.20,
        "list_id": "list_123"
    }
    
    # Normalize the record
    normalized = normalize_record(sample_record)
    
    # Print the result
    print("Original record:")
    print(json.dumps(sample_record, indent=2))
    print("\nNormalized record:")
    print(json.dumps(normalized, indent=2))

if __name__ == "__main__":
    main()
```

### 2. Implement the Normalization Functions

Complete the normalization functions:

```python
def normalize_record(raw_record):
    """Normalize a single record from Klaviyo format to Looker Studio format"""
    if not raw_record:
        return {}
    
    normalized = {}
    
    # Map standard fields
    for klaviyo_field, looker_field in FIELD_MAP.items():
        if klaviyo_field in raw_record:
            normalized[looker_field] = raw_record[klaviyo_field]
    
    # Calculate derived fields
    for derived_field, calc_func in DERIVED_FIELDS.items():
        try:
            normalized[derived_field] = calc_func(raw_record)
        except Exception as e:
            print(f"Error calculating derived field {derived_field}: {e}")
    
    # Pass through any fields that aren't mapped but might be useful
    for field in raw_record:
        if field not in FIELD_MAP and field not in normalized:
            normalized[field] = raw_record[field]
    
    return normalized

def normalize_records(raw_records):
    """Normalize a list of records from Klaviyo format to Looker Studio format"""
    if not raw_records:
        return []
    
    return [normalize_record(record) for record in raw_records]
```

### 3. Add Date Formatting Helper (Optional)

Add a helper function to format dates consistently:

```python
from datetime import datetime

def format_date(date_str):
    """Format a date string to YYYY-MM-DD format"""
    if not date_str:
        return ""
    
    try:
        # Handle ISO format dates (e.g., "2025-05-01T10:00:00Z")
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        # If it's already in the right format or can't be parsed, return as is
        return date_str
```

Then update the `normalize_record` function to use this helper for date fields:

```python
def normalize_record(raw_record):
    """Normalize a single record from Klaviyo format to Looker Studio format"""
    if not raw_record:
        return {}
    
    normalized = {}
    
    # Map standard fields
    for klaviyo_field, looker_field in FIELD_MAP.items():
        if klaviyo_field in raw_record:
            # Apply special formatting for date fields
            if klaviyo_field == "send_time":
                normalized[looker_field] = format_date(raw_record[klaviyo_field])
            else:
                normalized[looker_field] = raw_record[klaviyo_field]
    
    # Rest of the function remains the same...
```

### 4. Create Unit Tests

Create a new file at `tests/test_lookml_field_mapper.py` with the following content:

```python
import pytest
from src.lookml_field_mapper import (
    normalize_record,
    normalize_records,
    get_field_mapping,
    get_derived_fields,
    format_date
)

# Test field mapping
def test_get_field_mapping():
    mapping = get_field_mapping()
    assert isinstance(mapping, dict)
    assert "send_time" in mapping
    assert mapping["send_time"] == "date"
    assert "name" in mapping
    assert mapping["name"] == "campaign_name"

# Test derived fields
def test_get_derived_fields():
    derived = get_derived_fields()
    assert isinstance(derived, dict)

# Test normalize_record with complete data
def test_normalize_record_complete():
    raw_record = {
        "id": "campaign_123",
        "name": "Test Campaign",
        "send_time": "2025-05-01T10:00:00Z",
        "subject": "Test Subject",
        "open_rate": 0.45,
        "click_rate": 0.20,
        "list_id": "list_123"
    }
    
    normalized = normalize_record(raw_record)
    
    assert normalized["campaign_name"] == "Test Campaign"
    assert normalized["date"] == "2025-05-01"
    assert normalized["subject_line"] == "Test Subject"
    assert normalized["open_rate"] == 0.45
    assert normalized["click_rate"] == 0.20
    assert normalized["list_id"] == "list_123"
    assert "id" in normalized  # Unmapped fields should be passed through

# Test normalize_record with missing fields
def test_normalize_record_missing_fields():
    raw_record = {
        "id": "campaign_123",
        "name": "Test Campaign"
        # Missing other fields
    }
    
    normalized = normalize_record(raw_record)
    
    assert normalized["campaign_name"] == "Test Campaign"
    assert "date" not in normalized
    assert "subject_line" not in normalized
    assert "id" in normalized  # Unmapped fields should be passed through

# Test normalize_record with empty input
def test_normalize_record_empty():
    assert normalize_record({}) == {}
    assert normalize_record(None) == {}

# Test normalize_records with multiple records
def test_normalize_records():
    raw_records = [
        {
            "id": "campaign_1",
            "name": "Test Campaign 1",
            "send_time": "2025-05-01T10:00:00Z"
        },
        {
            "id": "campaign_2",
            "name": "Test Campaign 2",
            "send_time": "2025-05-02T10:00:00Z"
        }
    ]
    
    normalized = normalize_records(raw_records)
    
    assert len(normalized) == 2
    assert normalized[0]["campaign_name"] == "Test Campaign 1"
    assert normalized[0]["date"] == "2025-05-01"
    assert normalized[1]["campaign_name"] == "Test Campaign 2"
    assert normalized[1]["date"] == "2025-05-02"

# Test normalize_records with empty input
def test_normalize_records_empty():
    assert normalize_records([]) == []
    assert normalize_records(None) == []

# Test date formatting
def test_format_date():
    assert format_date("2025-05-01T10:00:00Z") == "2025-05-01"
    assert format_date("2025-05-01") == "2025-05-01"  # Already in correct format
    assert format_date("") == ""
    assert format_date(None) == ""
```

### 5. Update the Main Function for Testing

Complete the `main` function to demonstrate usage:

```python
def main():
    # Example usage
    import json
    
    # Sample Klaviyo records
    sample_records = [
        {
            "id": "campaign_123",
            "name": "Test Campaign 1",
            "send_time": "2025-05-01T10:00:00Z",
            "subject": "Test Subject 1",
            "open_rate": 0.45,
            "click_rate": 0.20,
            "list_id": "list_123"
        },
        {
            "id": "campaign_456",
            "name": "Test Campaign 2",
            "send_time": "2025-05-08T10:00:00Z",
            "subject": "Test Subject 2",
            "open_rate": 0.50,
            "click_rate": 0.25,
            "list_id": "list_123"
        }
    ]
    
    # Normalize the records
    normalized = normalize_records(sample_records)
    
    # Print the result
    print("Original records:")
    print(json.dumps(sample_records, indent=2))
    print("\nNormalized records:")
    print(json.dumps(normalized, indent=2))
    
    # Print field mapping
    print("\nField mapping:")
    for k, v in get_field_mapping().items():
        print(f"  {k} -> {v}")
```

## Validation Steps

### For Developers

1. Ensure the `src` and `tests` directories exist:
   ```bash
   mkdir -p src tests
   ```

2. Implement the `lookml_field_mapper.py` script as described above.

3. Implement the unit tests as described above.

4. Run the script to verify it works correctly:
   ```bash
   python src/lookml_field_mapper.py
   ```

5. Run the unit tests to verify they pass:
   ```bash
   pytest tests/test_lookml_field_mapper.py -v
   ```

### For Reviewers

1. Verify that the script follows the project's coding standards.

2. Check that the field mapping is complete and covers all required fields.

3. Verify that the normalization functions handle edge cases correctly (missing fields, null values, etc.).

4. Ensure that the date formatting is consistent and follows the expected format for Looker Studio.

5. Run the unit tests to verify they pass:
   ```bash
   pytest tests/test_lookml_field_mapper.py -v
   ```

## Next Steps

After implementing and validating PR 2, proceed to PR 3: Mock Looker Dataset.
