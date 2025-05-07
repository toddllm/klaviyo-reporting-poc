import json
import os
import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import httpretty

from src.google_sheets_export import get_credentials, get_email_metrics_data, export_to_sheets


class TestGoogleSheetsExport(unittest.TestCase):
    
    def setUp(self):
        # Create a sample DataFrame for testing
        self.sample_data = pd.DataFrame({
            'send_date': ['2025-05-01', '2025-05-02', '2025-05-03'],
            'campaign_id': ['c1', 'c2', 'c3'],
            'subject': ['Test Email 1', 'Test Email 2', 'Test Email 3'],
            'sends': [100, 200, 300],
            'unique_opens': [50, 120, 180],
            'unique_clicks': [20, 60, 90],
            'revenue': [100.50, 250.75, 300.25]
        })
        
        # Sample credentials dict
        self.credentials_dict = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEtest\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test-project.iam.gserviceaccount.com"
        }
        
        # Create a temporary credentials file for testing
        self.temp_credentials_file = 'test_credentials.json'
        with open(self.temp_credentials_file, 'w') as f:
            json.dump(self.credentials_dict, f)
    
    def tearDown(self):
        # Clean up the temporary credentials file
        if os.path.exists(self.temp_credentials_file):
            os.remove(self.temp_credentials_file)
    
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_get_credentials_from_file(self, mock_from_file):
        # Setup mock
        mock_credentials = MagicMock()
        mock_from_file.return_value = mock_credentials
        
        # Call the function
        result = get_credentials(self.temp_credentials_file)
        
        # Verify the result
        self.assertEqual(result, mock_credentials)
        mock_from_file.assert_called_once_with(
            self.temp_credentials_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
    
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_get_credentials_from_env_json(self, mock_from_info):
        # Setup mock
        mock_credentials = MagicMock()
        mock_from_info.return_value = mock_credentials
        
        # Set environment variable with JSON string
        os.environ['GOOGLE_CREDENTIALS_JSON'] = json.dumps(self.credentials_dict)
        
        # Call the function with a non-existent file
        result = get_credentials('non_existent_file.json')
        
        # Verify the result
        self.assertEqual(result, mock_credentials)
        mock_from_info.assert_called_once_with(
            self.credentials_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        
        # Clean up environment
        del os.environ['GOOGLE_CREDENTIALS_JSON']
    
    @patch('google.cloud.bigquery.Client')
    def test_get_email_metrics_data(self, mock_bq_client):
        # Setup mock
        mock_client = MagicMock()
        mock_bq_client.return_value = mock_client
        
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_query_job.to_dataframe.return_value = self.sample_data
        
        # Set environment variables
        os.environ['BQ_PROJECT'] = 'test-project'
        os.environ['BQ_DATASET'] = 'test-dataset'
        
        # Call the function
        result = get_email_metrics_data(7)
        
        # Verify the result
        pd.testing.assert_frame_equal(result, self.sample_data)
        mock_client.query.assert_called_once()
        mock_query_job.to_dataframe.assert_called_once()
        
        # Clean up environment
        del os.environ['BQ_PROJECT']
        del os.environ['BQ_DATASET']
    
    @patch('gspread.authorize')
    def test_export_to_sheets(self, mock_authorize):
        # Setup mocks
        mock_gc = MagicMock()
        mock_authorize.return_value = mock_gc
        
        mock_spreadsheet = MagicMock()
        mock_gc.open_by_key.return_value = mock_spreadsheet
        
        mock_worksheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.id = '123456'
        
        # Mock credentials
        mock_credentials = MagicMock()
        
        # Call the function
        sheet_id = 'test-sheet-id'
        range_name = 'test-range'
        result = export_to_sheets(self.sample_data, sheet_id, range_name, mock_credentials)
        
        # Verify the result
        expected_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={mock_worksheet.id}"
        self.assertEqual(result, expected_url)
        
        # Verify the calls
        mock_authorize.assert_called_once_with(mock_credentials)
        mock_gc.open_by_key.assert_called_once_with(sheet_id)
        mock_spreadsheet.worksheet.assert_called_once_with(range_name)
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
        self.assertEqual(mock_worksheet.format.call_count, 1)  # At least one format call for the header
    
    @patch('gspread.authorize')
    def test_export_to_sheets_worksheet_not_found(self, mock_authorize):
        # Setup mocks
        mock_gc = MagicMock()
        mock_authorize.return_value = mock_gc
        
        mock_spreadsheet = MagicMock()
        mock_gc.open_by_key.return_value = mock_spreadsheet
        
        # Simulate worksheet not found
        import gspread
        mock_spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound()
        
        mock_new_worksheet = MagicMock()
        mock_spreadsheet.add_worksheet.return_value = mock_new_worksheet
        mock_new_worksheet.id = '789012'
        
        # Mock credentials
        mock_credentials = MagicMock()
        
        # Call the function
        sheet_id = 'test-sheet-id'
        range_name = 'new-range'
        result = export_to_sheets(self.sample_data, sheet_id, range_name, mock_credentials)
        
        # Verify the result
        expected_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={mock_new_worksheet.id}"
        self.assertEqual(result, expected_url)
        
        # Verify the calls
        mock_authorize.assert_called_once_with(mock_credentials)
        mock_gc.open_by_key.assert_called_once_with(sheet_id)
        mock_spreadsheet.worksheet.assert_called_once_with(range_name)
        mock_spreadsheet.add_worksheet.assert_called_once()
        mock_new_worksheet.clear.assert_called_once()
        mock_new_worksheet.update.assert_called_once()
    
    @patch('src.google_sheets_export.get_credentials')
    @patch('src.google_sheets_export.get_email_metrics_data')
    @patch('src.google_sheets_export.export_to_sheets')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_function(self, mock_parse_args, mock_export, mock_get_data, mock_get_creds):
        # This test would be implemented to test the main function
        # It would mock the argument parsing and function calls
        pass


if __name__ == '__main__':
    unittest.main()
