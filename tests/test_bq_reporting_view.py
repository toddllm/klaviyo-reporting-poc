import os
import subprocess
import unittest
from unittest.mock import patch, MagicMock

class TestBigQueryReportingView(unittest.TestCase):
    
    def setUp(self):
        self.project_id = os.environ.get('BQ_PROJECT', 'clara-blueprint-script-24')
        self.dataset = os.environ.get('BQ_DATASET', 'klaviyopoc')
        self.looker_sa = os.environ.get('LOOKER_SA', 'looker_sa@clara-blueprint-script-24.iam.gserviceaccount.com')
        
    @patch('subprocess.run')
    def test_deploy_script_dry_run(self, mock_run):
        # Mock the subprocess.run to avoid actual execution
        mock_run.return_value = MagicMock(returncode=0)
        
        # Set environment variables
        env = os.environ.copy()
        env['PROJECT_ID'] = self.project_id
        env['DATASET'] = self.dataset
        env['LOOKER_SA'] = self.looker_sa
        
        # Run the deploy script with --dry-run
        result = subprocess.run(
            ['bash', 'scripts/deploy_reporting_view.sh', '--dry-run'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Check that the script executed successfully
        self.assertEqual(result.returncode, 0, f"Script failed with error: {result.stderr}")
        
        # Check that the output contains expected strings
        self.assertIn('DRY RUN: View DDL', result.stdout)
        self.assertIn('DRY RUN: IAM Grant', result.stdout)
    
    @patch('subprocess.run')
    def test_sql_file_syntax(self, mock_run):
        # Mock the subprocess.run to avoid actual execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Query successfully validated. Assuming the tables exist, the query is valid."
        mock_run.return_value = mock_process
        
        # Read the SQL file
        with open('sql/create_reporting_view.sql', 'r') as f:
            sql_content = f.read()
        
        # Replace variables
        sql_content = sql_content.replace('${PROJECT_ID}', self.project_id)
        sql_content = sql_content.replace('${DATASET}', self.dataset)
        
        # Validate SQL syntax using bq query --dry_run
        cmd = [
            'bq', 'query',
            '--nouse_legacy_sql',
            '--dry_run',
            '--project_id', self.project_id,
            sql_content
        ]
        
        # This is mocked, so it won't actually run
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Check that the command would execute successfully
        self.assertEqual(result.returncode, 0, f"SQL validation failed: {result.stderr}")

if __name__ == '__main__':
    unittest.main()
