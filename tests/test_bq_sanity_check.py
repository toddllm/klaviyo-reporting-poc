import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../scripts"))

import bq_sanity_check
from google.cloud.exceptions import NotFound


class TestBQSanityCheck(unittest.TestCase):
    
    def setUp(self):
        # Mock environment variables
        self.env_patcher = patch.dict("os.environ", {
            "BQ_PROJECT": "test-project",
            "BQ_DATASET": "test_dataset",
            "TABLE_LIST": "table1,table2,table3"
        })
        self.env_patcher.start()
        
        # Create a mock args object
        mock_args = MagicMock()
        mock_args.tables = ""
        mock_args.dry_run = False
        mock_args.env = ".env"
        
        # Set the global args variable
        bq_sanity_check.args = mock_args
    
    def tearDown(self):
        self.env_patcher.stop()
        # Reset the global args variable
        bq_sanity_check.args = None
    
    def test_get_table_list_from_env(self):
        # Test getting tables from environment variable
        bq_sanity_check.args.tables = ""
        tables = bq_sanity_check.get_table_list()
        self.assertEqual(tables, ["table1", "table2", "table3"])
    
    def test_get_table_list_from_args(self):
        # Test getting tables from command line arguments
        bq_sanity_check.args.tables = "arg1,arg2"
        tables = bq_sanity_check.get_table_list()
        self.assertEqual(tables, ["arg1", "arg2"])
    
    def test_get_table_list_default(self):
        # Test default table list
        self.env_patcher.stop()
        self.env_patcher = patch.dict("os.environ", {
            "BQ_PROJECT": "test-project",
            "BQ_DATASET": "test_dataset"
        })
        self.env_patcher.start()
        bq_sanity_check.args.tables = ""
        
        tables = bq_sanity_check.get_table_list()
        self.assertEqual(tables, ["campaign", "event", "flow", "list"])
    
    def test_check_table_exists(self):
        # Create a direct mock for the client
        client = MagicMock()
        
        # Mock the get_table method
        mock_table = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "updated_at"
        mock_table.schema = [mock_field]
        client.get_table.return_value = mock_table
        
        # Mock the count query result
        mock_count_row = MagicMock()
        mock_count_row.count = 100
        mock_count_job = MagicMock()
        mock_count_job.result.return_value = [mock_count_row]
        
        # Mock the latest timestamp query result
        mock_latest_row = MagicMock()
        mock_latest_row.latest = datetime(2025, 5, 1, 12, 0, 0)
        mock_latest_job = MagicMock()
        mock_latest_job.result.return_value = [mock_latest_row]
        
        # Set up the query method to return different results for different calls
        client.query = MagicMock()
        client.query.side_effect = [mock_count_job, mock_latest_job]
        
        # Call the function under test
        result = bq_sanity_check.check_table(
            client, "test-project", "test_dataset", "test_table"
        )
        
        # Verify the results
        self.assertTrue(result["exists"])
        self.assertEqual(result["row_count"], 100)
        self.assertEqual(result["latest_updated"], "2025-05-01T12:00:00")
        self.assertIsNone(result["error"])
    
    @patch("bq_sanity_check.bigquery.Client")
    def test_check_table_not_found(self, mock_client):
        # Mock a table that doesn't exist
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_table.side_effect = NotFound("Table not found")
        
        result = bq_sanity_check.check_table(
            mock_client_instance, "test-project", "test_dataset", "missing_table"
        )
        
        self.assertFalse(result["exists"])
        self.assertEqual(result["row_count"], 0)
        self.assertIsNone(result["latest_updated"])
        self.assertIn("not found", result["error"])
    
    @patch("bq_sanity_check.check_for_issues")
    @patch("bq_sanity_check.print_results")
    @patch("bq_sanity_check.check_table")
    @patch("bq_sanity_check.bigquery.Client")
    def test_main_success(self, mock_client, mock_check_table, 
                          mock_print_results, mock_check_for_issues):
        # Mock successful table checks
        mock_check_table.return_value = {
            "table": "test_table",
            "full_id": "test-project.test_dataset.test_table",
            "exists": True,
            "row_count": 100,
            "latest_updated": "2025-05-01T12:00:00",
            "error": None
        }
        mock_check_for_issues.return_value = False
        
        # Set up args for this test
        bq_sanity_check.args.dry_run = False
        
        exit_code = bq_sanity_check.main()
        
        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_check_table.call_count, 3)  # For table1, table2, table3
        mock_print_results.assert_called_once()
        mock_check_for_issues.assert_called_once()
    
    @patch("bq_sanity_check.check_for_issues")
    @patch("bq_sanity_check.print_results")
    @patch("bq_sanity_check.check_table")
    @patch("bq_sanity_check.bigquery.Client")
    def test_main_with_issues(self, mock_client, mock_check_table, 
                             mock_print_results, mock_check_for_issues):
        # Mock table checks with issues
        mock_check_table.return_value = {
            "table": "test_table",
            "full_id": "test-project.test_dataset.test_table",
            "exists": True,
            "row_count": 0,  # Empty table
            "latest_updated": None,
            "error": None
        }
        mock_check_for_issues.return_value = True  # Issues found
        
        # Set up args for this test
        bq_sanity_check.args.dry_run = False
        
        exit_code = bq_sanity_check.main()
        
        self.assertEqual(exit_code, 1)  # Should return non-zero exit code
        self.assertEqual(mock_check_table.call_count, 3)  # For table1, table2, table3
        mock_print_results.assert_called_once()
        mock_check_for_issues.assert_called_once()
    
    def test_main_missing_env_vars(self):
        # Test behavior when environment variables are missing
        self.env_patcher.stop()
        self.env_patcher = patch.dict("os.environ", {})
        self.env_patcher.start()
        
        # Make sure args is set up
        bq_sanity_check.args.dry_run = False
        
        exit_code = bq_sanity_check.main()
        
        self.assertEqual(exit_code, 1)  # Should return non-zero exit code


if __name__ == "__main__":
    unittest.main()
