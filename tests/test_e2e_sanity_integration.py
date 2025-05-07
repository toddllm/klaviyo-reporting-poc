import os
import subprocess
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../scripts"))


class TestE2ESanityIntegration(unittest.TestCase):
    
    def setUp(self):
        # Set up environment variables for testing
        self.env_patcher = patch.dict("os.environ", {
            "BQ_PROJECT": "test-project",
            "BQ_DATASET": "test_dataset",
            "E2E_SANITY_TABLES": "test_table1,test_table2",
            "FIVETRAN_GROUP_ID": "test-group",
            "FIVETRAN_CONNECTOR_ID": "test-connector",
            "PG_HOST": "localhost",
            "PG_PORT": "5432",
            "PG_DB": "test",
            "PG_USER": "test",
            "PG_PASSWORD": "test",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_REGION": "us-east-1",
            "S3_BUCKET": "test-bucket",
            "S3_PREFIX": "test-prefix",
            "SES_FROM_EMAIL": "test@example.com"
        })
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()
    
    def test_e2e_script_calls_bq_sanity_check(self):
        # Run the end-to-end script with dry-run flag
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/run_end_to_end_demo.sh")
        result = subprocess.run(
            ["bash", script_path, "--dry-run"],
            capture_output=True,
            text=True,
            env=os.environ
        )
        
        # Check that the script ran successfully
        self.assertEqual(result.returncode, 0, f"Script failed with output: {result.stderr}")
        
        # Check that the output contains the BigQuery sanity check message
        self.assertIn("Would run BigQuery sanity check", result.stdout)
        
        # Check that the tables from E2E_SANITY_TABLES are mentioned
        self.assertIn("test_table1,test_table2", result.stdout)
    
    def test_e2e_script_uses_default_tables_when_env_not_set(self):
        # Remove E2E_SANITY_TABLES from environment
        if "E2E_SANITY_TABLES" in os.environ:
            del os.environ["E2E_SANITY_TABLES"]
        
        # Run the end-to-end script with dry-run flag
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/run_end_to_end_demo.sh")
        result = subprocess.run(
            ["bash", script_path, "--dry-run"],
            capture_output=True,
            text=True,
            env=os.environ
        )
        
        # Check that the script ran successfully
        self.assertEqual(result.returncode, 0, f"Script failed with output: {result.stderr}")
        
        # Check that the output contains the default tables
        self.assertIn("campaign,event,list", result.stdout)


if __name__ == "__main__":
    unittest.main()
