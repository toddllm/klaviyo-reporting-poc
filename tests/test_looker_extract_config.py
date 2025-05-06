import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_looker_extract_config_structure():
    """Test that the Looker extract config file has the expected structure"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config',
        'looker_extract_klaviyo.json'
    )
    
    # Check file exists
    assert os.path.exists(config_path), "Looker extract config file not found"
    
    # Load and validate JSON structure
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check top-level keys
    assert "extractConfig" in config, "Missing extractConfig section"
    assert "visualizationConfig" in config, "Missing visualizationConfig section"
    assert "implementationNotes" in config, "Missing implementationNotes section"
    
    # Check extract config structure
    extract_config = config["extractConfig"]
    assert "name" in extract_config, "Missing name in extractConfig"
    assert "source" in extract_config, "Missing source in extractConfig"
    assert "extract" in extract_config, "Missing extract in extractConfig"
    assert "destination" in extract_config, "Missing destination in extractConfig"
    
    # Check source config
    source = extract_config["source"]
    assert "type" in source, "Missing type in source"
    assert source["type"] == "BIGQUERY", "Source type should be BIGQUERY"
    assert "projectId" in source, "Missing projectId in source"
    assert "datasetId" in source, "Missing datasetId in source"
    assert "tableId" in source, "Missing tableId in source"
    
    # Check extract fields
    extract = extract_config["extract"]
    assert "fields" in extract, "Missing fields in extract"
    assert "filters" in extract, "Missing filters in extract"
    assert "aggregation" in extract, "Missing aggregation in extract"
    assert "refreshSchedule" in extract, "Missing refreshSchedule in extract"
    
    # Check fields have required properties
    for field in extract["fields"]:
        assert "name" in field, "Missing name in field"
        assert "type" in field, "Missing type in field"
    
    # Check destination config
    destination = extract_config["destination"]
    assert "type" in destination, "Missing type in destination"
    assert destination["type"] == "BIGQUERY", "Destination type should be BIGQUERY"
    assert "projectId" in destination, "Missing projectId in destination"
    assert "datasetId" in destination, "Missing datasetId in destination"
    assert "tableId" in destination, "Missing tableId in destination"

def test_looker_extract_config_content():
    """Test specific content requirements for the Looker extract config"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config',
        'looker_extract_klaviyo.json'
    )
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    extract_config = config["extractConfig"]
    extract = extract_config["extract"]
    
    # Check that we have date field for filtering
    field_names = [field["name"] for field in extract["fields"]]
    assert "date" in field_names, "Missing date field"
    
    # Check that we have campaign_id field for aggregation
    assert "campaign_id" in field_names, "Missing campaign_id field"
    
    # Check that we have required metrics
    assert "open_rate" in field_names, "Missing open_rate field"
    assert "click_rate" in field_names, "Missing click_rate field"
    
    # Check date filter exists
    has_date_filter = False
    for filter_item in extract["filters"]:
        if filter_item.get("fieldName") == "date":
            has_date_filter = True
            break
    assert has_date_filter, "Missing date filter"
    
    # Check aggregation dimensions
    agg = extract["aggregation"]
    assert "dimensions" in agg, "Missing dimensions in aggregation"
    assert "campaign_id" in agg["dimensions"], "campaign_id should be a dimension"
    assert "date" in agg["dimensions"], "date should be a dimension"
    
    # Check refresh schedule
    refresh = extract["refreshSchedule"]
    assert "frequency" in refresh, "Missing frequency in refreshSchedule"
    assert refresh["frequency"] in ["DAILY", "WEEKLY", "MONTHLY"], "Invalid refresh frequency"
