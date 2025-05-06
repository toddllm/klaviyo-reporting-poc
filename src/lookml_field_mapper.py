#!/usr/bin/env python3
from datetime import datetime

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
    "engagement_score": lambda record: (record.get("open_rate", 0) * 0.7 + record.get("click_rate", 0) * 0.3)
}

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

if __name__ == "__main__":
    main()
