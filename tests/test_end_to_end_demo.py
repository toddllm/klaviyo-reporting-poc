import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEndToEndDemo(unittest.TestCase):
    """Test the end-to-end demo script"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts",
            "run_end_to_end_demo.sh"
        )
        
        # Ensure the script exists and is executable
        self.assertTrue(os.path.exists(self.script_path), "Demo script does not exist")
        self.assertTrue(os.access(self.script_path, os.X_OK), "Demo script is not executable")
    
    @patch('subprocess.run')
    def test_dry_run_mode(self, mock_run):
        """Test that the script runs in dry-run mode without errors"""
        # Configure the mock to return a successful CompletedProcess
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout=b'', stderr=b'')
        
        # Run the script in dry-run mode
        result = subprocess.run(
            [self.script_path, "--dry-run"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check that the script exited successfully
        self.assertEqual(result.returncode, 0, f"Script failed with error: {result.stderr}")
        
        # Check that the output contains expected messages
        self.assertIn("Starting End-to-End Demo", result.stdout)
        self.assertIn("[DRY RUN]", result.stdout)
    
    def test_help_option(self):
        """Test that the --help option displays usage information"""
        # Run the script with --help
        result = subprocess.run(
            [self.script_path, "--help"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check that the output contains usage information
        self.assertIn("Usage:", result.stdout)
        self.assertIn("Options:", result.stdout)
        self.assertIn("--start-date", result.stdout)
        self.assertIn("--end-date", result.stdout)
        self.assertIn("--dry-run", result.stdout)
    
    def test_script_structure(self):
        """Test that the script contains all required sections"""
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Check for key sections
        self.assertIn("Step 1: Triggering Fivetran sync", script_content)
        self.assertIn("Step 2: Running ETL process", script_content)
        self.assertIn("Step 3: Uploading processed data to S3", script_content)
        self.assertIn("Step 4: Loading data to BigQuery", script_content)
        self.assertIn("Step 5: Generating dashboard link", script_content)
        self.assertIn("Step 6: Sending email notification", script_content)

if __name__ == '__main__':
    unittest.main()
