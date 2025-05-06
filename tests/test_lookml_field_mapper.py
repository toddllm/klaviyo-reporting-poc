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
    assert "engagement_score" in derived
    
    # Test the engagement score calculation
    test_record = {"open_rate": 0.6, "click_rate": 0.4}
    score = derived["engagement_score"](test_record)
    assert score == pytest.approx(0.6 * 0.7 + 0.4 * 0.3)

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
    assert "engagement_score" in normalized
    assert normalized["engagement_score"] == pytest.approx(0.45 * 0.7 + 0.20 * 0.3)

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
    assert "engagement_score" in normalized
    assert normalized["engagement_score"] == 0  # Default values are 0

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
