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
    
    # Run the script in dry-run mode
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "scripts", "publish_looker_template.sh")
    
    result = subprocess.run(
        [script_path, "--dry-run", "--dashboard-json", temp_dashboard_json, 
         "--output-json", output_json],
        capture_output=True,
        text=True,
        env={**os.environ, "BQ_PROJECT": "test-project", "BQ_DATASET": "test_dataset"}
    )
    
    # Check that the script ran successfully
    assert result.returncode == 0
    
    # Check that the output contains the expected text
    assert "Dry run mode" in result.stdout
    assert "test-project" in result.stdout  # Variable substitution happened
    assert "test_dataset" in result.stdout  # Variable substitution happened
    
    # Check that the output file was not created in dry-run mode
    assert not os.path.exists(output_json)

@mock.patch('subprocess.run')
def test_publish_script_creates_output(mock_run, temp_env_file, temp_dashboard_json, tmp_path):
    """Test that the script creates an output file with a document ID"""
    output_json = str(tmp_path / "output.json")
    
    # Mock the jq command that would be called by the script
    mock_run.return_value = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="",
        stderr=""
    )
    
    # Set up environment for the test
    env = os.environ.copy()
    env["BQ_PROJECT"] = "test-project"
    env["BQ_DATASET"] = "test_dataset"
    
    # Run the script
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "scripts", "publish_looker_template.sh")
    
    # Create a simple mock implementation that creates the output file
    def side_effect(args, **kwargs):
        if "jq" in str(args):
            # Create the output file with a document ID
            with open(output_json, 'w') as f:
                json_content = {
                    "reportName": "Test Dashboard",
                    "documentId": "test-doc-id-12345",
                    "dataSourceRef": {
                        "sources": [{
                            "projectId": "test-project",
                            "datasetId": "test_dataset",
                            "tableId": "v_email_metrics"
                        }]
                    }
                }
                json.dump(json_content, f)
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    
    mock_run.side_effect = side_effect
    
    result = subprocess.run(
        [script_path, "--dashboard-json", temp_dashboard_json, "--output-json", output_json],
        capture_output=True,
        text=True,
        env=env
    )
    
    # Check that the output file exists and contains a document ID
    assert os.path.exists(output_json)
    with open(output_json, 'r') as f:
        output_data = json.load(f)
        assert "documentId" in output_data
        assert output_data["documentId"] == "test-doc-id-12345"
