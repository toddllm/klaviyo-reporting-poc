#!/usr/bin/env python3
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the src directory to the path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bq_loader import (
    get_credentials,
    create_bigquery_client,
    ensure_dataset_exists,
    get_table_id,
    load_json_to_bigquery,
    load_csv_to_bigquery,
    main
)

class TestBQLoader(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create sample JSON data
        self.sample_json_data = [
            {
                "campaign_id": "campaign_123",
                "campaign_name": "Test Campaign 1",
                "send_time": "2025-05-01T10:00:00Z",
                "subject_line": "Test Subject 1",
                "open_rate": 0.45,
                "click_rate": 0.20,
                "delivered": 1000,
                "opened": 450,
                "clicked": 200,
                "date": "2025-05-01"
            },
            {
                "campaign_id": "campaign_456",
                "campaign_name": "Test Campaign 2",
                "send_time": "2025-05-02T10:00:00Z",
                "subject_line": "Test Subject 2",
                "open_rate": 0.50,
                "click_rate": 0.25,
                "delivered": 800,
                "opened": 400,
                "clicked": 200,
                "date": "2025-05-02"
            }
        ]
        
        # Create sample JSON file
        self.json_file = os.path.join(self.temp_dir.name, "supermetrics_raw_campaign_20250506.json")
        with open(self.json_file, "w") as f:
            json.dump(self.sample_json_data, f)
        
        # Create sample CSV file
        self.csv_file = os.path.join(self.temp_dir.name, "supermetrics_raw_campaign_20250506.csv")
        with open(self.csv_file, "w") as f:
            f.write("campaign_id,campaign_name,send_time,subject_line,open_rate,click_rate,delivered,opened,clicked,date\n")
            f.write("campaign_123,Test Campaign 1,2025-05-01T10:00:00Z,Test Subject 1,0.45,0.20,1000,450,200,2025-05-01\n")
            f.write("campaign_456,Test Campaign 2,2025-05-02T10:00:00Z,Test Subject 2,0.50,0.25,800,400,200,2025-05-02\n")
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    @patch("os.path.exists")
    @patch("os.getenv")
    @patch("google.oauth2.service_account.Credentials.from_service_account_file")
    def test_get_credentials(self, mock_from_file, mock_getenv, mock_exists):
        # Test with service account path
        mock_from_file.return_value = "mock_credentials"
        mock_exists.return_value = True
        
        # Case 1: Service account path provided
        creds = get_credentials("path/to/service_account.json")
        self.assertEqual(creds, "mock_credentials")
        mock_from_file.assert_called_with("path/to/service_account.json", scopes=["https://www.googleapis.com/auth/bigquery"])
        
        # Case 2: Service account from environment variable
        mock_getenv.return_value = "env/path/to/service_account.json"
        creds = get_credentials()
        self.assertEqual(creds, "mock_credentials")
        mock_from_file.assert_called_with("env/path/to/service_account.json", scopes=["https://www.googleapis.com/auth/bigquery"])
        
        # Case 3: No service account available
        mock_getenv.return_value = None
        creds = get_credentials()
        self.assertIsNone(creds)
    
    @patch("src.bq_loader.get_credentials")
    @patch("google.cloud.bigquery.Client")
    def test_create_bigquery_client(self, mock_client, mock_get_credentials):
        mock_get_credentials.return_value = "mock_credentials"
        mock_client.return_value = "mock_bq_client"
        
        client = create_bigquery_client("path/to/service_account.json")
        self.assertEqual(client, "mock_bq_client")
        mock_get_credentials.assert_called_with("path/to/service_account.json")
        mock_client.assert_called_with(credentials="mock_credentials")
    
    def test_ensure_dataset_exists(self):
        mock_client = MagicMock()
        mock_dataset_ref = MagicMock()
        mock_client.dataset.return_value = mock_dataset_ref
        
        # Case 1: Dataset exists
        mock_client.get_dataset.return_value = MagicMock()
        ensure_dataset_exists(mock_client, "test_dataset")
        mock_client.dataset.assert_called_with("test_dataset")
        mock_client.get_dataset.assert_called_with(mock_dataset_ref)
        mock_client.create_dataset.assert_not_called()
        
        # Case 2: Dataset doesn't exist
        mock_client.reset_mock()
        mock_client.dataset.return_value = mock_dataset_ref
        mock_client.get_dataset.side_effect = Exception("Dataset not found")
        ensure_dataset_exists(mock_client, "test_dataset")
        mock_client.create_dataset.assert_called()
    
    def test_get_table_id(self):
        mock_client = MagicMock()
        mock_client.project = "test_project"
        
        # Case 1: With date suffix
        table_id = get_table_id(mock_client, "test_dataset", "events", "campaign", "20250506")
        self.assertEqual(table_id, "test_project.test_dataset.events_campaign_20250506")
        
        # Case 2: Without date suffix
        table_id = get_table_id(mock_client, "test_dataset", "events", "campaign")
        self.assertEqual(table_id, "test_project.test_dataset.events_campaign")
    
    @patch("src.bq_loader.get_table_id")
    def test_load_json_to_bigquery_dry_run(self, mock_get_table_id):
        mock_client = MagicMock()
        mock_get_table_id.return_value = "test_project.test_dataset.events_campaign_20250506"
        
        # Test dry run
        table_id, row_count = load_json_to_bigquery(
            mock_client, self.json_file, "test_dataset", "events", "campaign", True, True
        )
        
        self.assertEqual(table_id, "test_project.test_dataset.events_campaign_20250506")
        self.assertEqual(row_count, 2)  # 2 rows in sample data
        mock_client.load_table_from_file.assert_not_called()
    
    @patch("src.bq_loader.get_table_id")
    def test_load_csv_to_bigquery_dry_run(self, mock_get_table_id):
        mock_client = MagicMock()
        mock_get_table_id.return_value = "test_project.test_dataset.events_campaign_20250506"
        
        # Test dry run
        table_id, row_count = load_csv_to_bigquery(
            mock_client, self.csv_file, "test_dataset", "events", "campaign", True, True
        )
        
        self.assertEqual(table_id, "test_project.test_dataset.events_campaign_20250506")
        self.assertEqual(row_count, 2)  # 2 rows in sample data
        mock_client.load_table_from_file.assert_not_called()
    
    @patch("sys.argv", ["bq_loader.py", "--file", "test.json", "--report-type", "campaign", "--dry-run"])
    @patch("os.path.exists")
    @patch("src.bq_loader.create_bigquery_client")
    @patch("src.bq_loader.ensure_dataset_exists")
    @patch("src.bq_loader.load_json_to_bigquery")
    def test_main_json(self, mock_load_json, mock_ensure_dataset, mock_create_client, mock_exists):
        mock_exists.return_value = True
        mock_create_client.return_value = MagicMock()
        mock_load_json.return_value = ("test_table_id", 2)
        
        result = main()
        self.assertEqual(result, 0)
        mock_load_json.assert_called_once()
    
    @patch("sys.argv", ["bq_loader.py", "--file", "test.csv", "--report-type", "campaign", "--dry-run"])
    @patch("os.path.exists")
    @patch("src.bq_loader.create_bigquery_client")
    @patch("src.bq_loader.ensure_dataset_exists")
    @patch("src.bq_loader.load_csv_to_bigquery")
    def test_main_csv(self, mock_load_csv, mock_ensure_dataset, mock_create_client, mock_exists):
        mock_exists.return_value = True
        mock_create_client.return_value = MagicMock()
        mock_load_csv.return_value = ("test_table_id", 2)
        
        result = main()
        self.assertEqual(result, 0)
        mock_load_csv.assert_called_once()
    
    @patch("sys.argv", ["bq_loader.py", "--file", "test.txt", "--report-type", "campaign", "--dry-run"])
    @patch("os.path.exists")
    @patch("src.bq_loader.create_bigquery_client")
    @patch("src.bq_loader.ensure_dataset_exists")
    def test_main_unsupported_file(self, mock_ensure_dataset, mock_create_client, mock_exists):
        mock_exists.return_value = True
        mock_create_client.return_value = MagicMock()
        
        result = main()
        self.assertEqual(result, 1)  # Should return error code

if __name__ == "__main__":
    unittest.main()
