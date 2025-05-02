import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Klaviyo API credentials
KLAVIYO_API_KEY = os.environ.get('KLAVIYO_API_KEY', 'pk_placeholder')

# Campaign and audience IDs
AUDIENCE_ID = os.environ.get('AUDIENCE_ID', 'YdSN6t')
CAMPAIGN_ID = os.environ.get('CAMPAIGN_ID', 'AbCdEf')
TEMPLATE_ID = os.environ.get('TEMPLATE_ID', 'WJ3kbV')

# Test configuration
NUM_TEST_PROFILES = int(os.environ.get('NUM_TEST_PROFILES', '5'))
MODE = os.environ.get('MODE', 'mock')  # Use 'real' for actual API calls

# Integration endpoints
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/YOUR_WEBHOOK')
LOOKER_REPORT_URL = os.environ.get('LOOKER_REPORT_URL', 'https://datastudio.google.com/reporting/YOUR_REPORT_ID')

# Google Sheets configuration
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', 'your_sheet_id_here')
GOOGLE_SHEET_NAME = os.environ.get('GOOGLE_SHEET_NAME', 'Klaviyo Metrics')
GOOGLE_SHEET_RANGE_NAME = os.environ.get('GOOGLE_SHEET_RANGE_NAME', 'metrics_data')

# API version
KLAVIYO_API_VERSION = '2025-04-15'

def get_config():
    """Return configuration as a dictionary"""
    return {
        'KLAVIYO_API_KEY': KLAVIYO_API_KEY,
        'AUDIENCE_ID': AUDIENCE_ID,
        'CAMPAIGN_ID': CAMPAIGN_ID,
        'TEMPLATE_ID': TEMPLATE_ID,
        'MODE': MODE,
        'KLAVIYO_API_VERSION': KLAVIYO_API_VERSION,
        'GOOGLE_SHEET_ID': GOOGLE_SHEET_ID,
        'GOOGLE_SHEET_NAME': GOOGLE_SHEET_NAME,
        'GOOGLE_SHEET_RANGE_NAME': GOOGLE_SHEET_RANGE_NAME
    }
