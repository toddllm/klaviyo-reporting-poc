import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import push_to_sheet
from config import GOOGLE_SHEET_ID, GOOGLE_SHEET_NAME, GOOGLE_SHEET_RANGE_NAME

class TestPushToSheet(unittest.TestCase):
    
    @patch('push_to_sheet.authenticate_gspread')
    def test_push_to_sheet_dry_run(self, mock_auth):
        # Test dry run mode
        test_data = [['date', 'delivered', 'opened', 'clicked', 'revenue'], 
                     ['2025-05-01', '100', '45', '20', '250.00']]
        
        result = push_to_sheet.push_to_sheet(test_data, dry_run=True)
        
        # Verify dry run doesn't call authenticate_gspread
        mock_auth.assert_not_called()
        self.assertTrue(result)
    
    @patch('push_to_sheet.authenticate_gspread')
    def test_push_to_sheet_auth_failure(self, mock_auth):
        # Test authentication failure
        mock_auth.return_value = None
        test_data = [['date', 'delivered', 'opened', 'clicked', 'revenue']]
        
        result = push_to_sheet.push_to_sheet(test_data, dry_run=False)
        
        mock_auth.assert_called_once()
        self.assertFalse(result)
    
    @patch('push_to_sheet.authenticate_gspread')
    def test_push_to_sheet_success(self, mock_auth):
        # Mock the gspread client and worksheet
        mock_worksheet = MagicMock()
        mock_worksheet.id = '123456'
        
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        mock_auth.return_value = mock_client
        
        # Test data
        test_data = [['date', 'delivered', 'opened', 'clicked', 'revenue'], 
                     ['2025-05-01', '100', '45', '20', '250.00']]
        
        result = push_to_sheet.push_to_sheet(test_data, dry_run=False)
        
        # Verify the correct methods were called
        mock_auth.assert_called_once()
        mock_client.open_by_key.assert_called_once_with(GOOGLE_SHEET_ID)
        mock_spreadsheet.worksheet.assert_called_once_with(GOOGLE_SHEET_NAME)
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
        
        # Verify update was called with RAW value_input_option
        args, kwargs = mock_worksheet.update.call_args
        self.assertEqual(args[0], test_data)
        self.assertEqual(kwargs['value_input_option'], 'RAW')
        
        # Verify batch_update was called to set the named range
        mock_spreadsheet.batch_update.assert_called_once()
        
        # Verify the correct body structure for the named range
        args, kwargs = mock_spreadsheet.batch_update.call_args
        body = args[0]
        self.assertEqual(body['requests'][0]['addNamedRange']['namedRange']['name'], GOOGLE_SHEET_RANGE_NAME)
        self.assertEqual(body['requests'][0]['addNamedRange']['namedRange']['range']['sheetId'], '123456')
        
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
