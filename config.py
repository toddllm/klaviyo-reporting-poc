# This file is maintained for backward compatibility
# New code should import from src.config instead

import os
import sys
from dotenv import load_dotenv

# Add src directory to path if not already there
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Import from src.config
try:
    from src.config import (
        settings,
        KLAVIYO_API_KEY,
        AUDIENCE_ID,
        CAMPAIGN_ID,
        TEMPLATE_ID,
        NUM_TEST_PROFILES,
        MODE,
        SLACK_WEBHOOK_URL,
        LOOKER_REPORT_URL,
        GOOGLE_SHEET_ID,
        GOOGLE_SHEET_NAME,
        GOOGLE_SHEET_RANGE_NAME,
        KLAVIYO_API_VERSION,
        get_config
    )
    
    # If import succeeds, we're done
    
# Fallback to original implementation if src.config is not available
except ImportError:
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
    MODE = os.environ.get('MODE', 'mock')
    
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
