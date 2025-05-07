import json
import os
import subprocess
import tempfile
from unittest import mock

import pytest

@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("BQ_PROJECT=test-project\n")
        f.write("BQ_DATASET=test_dataset\n")
        temp_path = f.name
    
    yield temp_path
    os.unlink(temp_path)

@pytest.fixture
def temp_dashboard_json():
    """Create a temporary dashboard JSON file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        json_content = {
            "reportName": "Test Dashboard",
            "dataSourceRef": {
                "sources": [{
                    "projectId": "${BQ_PROJECT}",
                    "datasetId": "${BQ_DATASET}",
                    "tableId": "v_email_metrics"
                }]
            }
        }
        json.dump(json_content, f)
        temp_path = f.name
    
    yield temp_path
    os.unlink(temp_path)

def test_publish_script_dry_run(temp_env_file, temp_dashboard_json, tmp_path):
    """Test the publish_looker_template.sh script in dry-run mode"""
    output_json = str(tmp_path / "output.json")
    
    # Create a temporary .env file in the script directory
    script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
    env_path = os.path.join(os.path.dirname(script_dir), ".env")
    with open(env_path, 'w') as f:
        f.write("BQ_PROJECT=test-project\n")
        f.write("BQ_DATASET=test_dataset\n")
    
    try:
        # Run the script in dry-run mode
        script_path = os.path.join(script_dir, "publish_looker_template.sh")
        
        result = subprocess.run(
            [script_path, "--dry-run", "--dashboard-json", temp_dashboard_json, 
             "--output-json", output_json],
            capture_output=True,
            text=True
        )
        
        # Check that the script ran successfully
        assert result.returncode == 0
        
        # Check that the output contains the expected text
        assert "Dry run mode" in result.stdout
        
        # Check that the output file was not created in dry-run mode
        assert not os.path.exists(output_json)
    finally:
        # Clean up the temporary .env file
        if os.path.exists(env_path):
            os.unlink(env_path)

def test_dashboard_json_structure():
    """Test that the dashboard JSON has the expected structure"""
    # Path to the dashboard JSON file
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config", "looker_studio_dashboard_config.json"
    )
    
    # Check that the file exists
    assert os.path.exists(json_path), f"Dashboard JSON file not found at {json_path}"
    
    # Load the JSON file
    with open(json_path, 'r') as f:
        dashboard_data = json.load(f)
    
    # Check that the required fields are present
    assert "reportName" in dashboard_data, "Dashboard JSON missing 'reportName' field"
    assert "components" in dashboard_data, "Dashboard JSON missing 'components' field"
    assert "dataSourceRef" in dashboard_data, "Dashboard JSON missing 'dataSourceRef' field"
    
    # Check that there are components of different types
    component_types = set()
    for component in dashboard_data["components"]:
        assert "type" in component, "Component missing 'type' field"
        component_types.add(component["type"])
    
    # Verify that we have at least a few different component types
    required_types = {"CHART", "SCORECARD", "TABLE"}
    for req_type in required_types:
        assert req_type in component_types, f"Dashboard missing '{req_type}' component"
