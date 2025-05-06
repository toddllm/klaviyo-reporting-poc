import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Define required environment variables
REQUIRED_VARS = {
    'SUPERMETRICS_API_KEY': 'Required for Supermetrics integration',
    'SUPERMETRICS_CLIENT_ID': 'Required for Supermetrics workspace/client ID',
    'AWS_ACCESS_KEY_ID': 'Required for S3 and SES access',
    'AWS_SECRET_ACCESS_KEY': 'Required for S3 and SES access',
    'AWS_REGION': 'Required, must support SES',
    'S3_BUCKET': 'Required for ETL outputs',
    'SES_DOMAIN': 'Required, verified domain in your AWS account',
    'SES_SENDER_EMAIL': 'Required, email address in the domain',
}

# Define optional environment variables with defaults
OPTIONAL_VARS = {
    'KLAVIYO_API_KEY': 'pk_placeholder',
    'SES_REPLY_TO': None,
    'DEFAULT_TIMEZONE': 'UTC',
    'AUDIENCE_ID': 'YdSN6t',
    'CAMPAIGN_ID': 'AbCdEf',
    'TEMPLATE_ID': 'WJ3kbV',
    'NUM_TEST_PROFILES': '5',
    'MODE': 'mock',
    'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/YOUR_WEBHOOK',
    'LOOKER_REPORT_URL': 'https://datastudio.google.com/reporting/YOUR_REPORT_ID',
    'GOOGLE_SHEET_ID': 'your_sheet_id_here',
    'GOOGLE_SHEET_NAME': 'Klaviyo Metrics',
    'GOOGLE_SHEET_RANGE_NAME': 'metrics_data',
    'KLAVIYO_API_VERSION': '2025-04-15',
}

@dataclass
class Settings:
    # Klaviyo API credentials
    klaviyo_api_key: str
    klaviyo_api_version: str
    
    # Supermetrics API credentials
    supermetrics_api_key: str
    supermetrics_client_id: str
    
    # AWS credentials and configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_bucket: str
    
    # AWS SES configuration
    ses_domain: str
    ses_sender_email: str
    ses_reply_to: Optional[str] = None
    
    # Timezone configuration
    default_timezone: str = 'UTC'
    
    # Campaign and audience IDs
    audience_id: str = 'YdSN6t'
    campaign_id: str = 'AbCdEf'
    template_id: str = 'WJ3kbV'
    
    # Test configuration
    num_test_profiles: int = 5
    mode: str = 'mock'
    
    # Integration endpoints
    slack_webhook_url: str = 'https://hooks.slack.com/services/YOUR_WEBHOOK'
    looker_report_url: str = 'https://datastudio.google.com/reporting/YOUR_REPORT_ID'
    
    # Google Sheets configuration
    google_sheet_id: str = 'your_sheet_id_here'
    google_sheet_name: str = 'Klaviyo Metrics'
    google_sheet_range_name: str = 'metrics_data'
    
    def dict(self) -> Dict[str, Any]:
        """Return the settings as a dictionary"""
        return asdict(self)

    def validate(self) -> None:
        """Validate the settings"""
        # Check mode is valid
        if self.mode not in ['mock', 'real']:
            raise ValueError(f"MODE must be 'mock' or 'real', got '{self.mode}'")
        
        # Check webhook URL format
        if self.slack_webhook_url != OPTIONAL_VARS['SLACK_WEBHOOK_URL'] and 'hooks.slack.com/services/' not in self.slack_webhook_url:
            raise ValueError(f"SLACK_WEBHOOK_URL must contain 'hooks.slack.com/services/', got '{self.slack_webhook_url}'")
        
        # Check Looker report URL format
        if self.looker_report_url != OPTIONAL_VARS['LOOKER_REPORT_URL'] and 'datastudio.google.com/reporting/' not in self.looker_report_url:
            raise ValueError(f"LOOKER_REPORT_URL must contain 'datastudio.google.com/reporting/', got '{self.looker_report_url}'")

# Initialize settings
def load_settings() -> Settings:
    """Load settings from environment variables with validation"""
    # Check for required environment variables
    missing_vars = []
    for var_name, description in REQUIRED_VARS.items():
        if not os.environ.get(var_name):
            missing_vars.append(f"{var_name}: {description}")
    
    # If any required variables are missing, print error and exit
    if missing_vars and os.environ.get('ALLOW_MISSING_ENV_VARS') != 'true':
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See .env.example for a template.")
        sys.exit(1)
    
    # Load settings
    settings = Settings(
        # Klaviyo API credentials
        klaviyo_api_key=os.environ.get('KLAVIYO_API_KEY', OPTIONAL_VARS['KLAVIYO_API_KEY']),
        klaviyo_api_version=os.environ.get('KLAVIYO_API_VERSION', OPTIONAL_VARS['KLAVIYO_API_VERSION']),
        
        # Supermetrics API credentials
        supermetrics_api_key=os.environ.get('SUPERMETRICS_API_KEY', ''),
        supermetrics_client_id=os.environ.get('SUPERMETRICS_CLIENT_ID', ''),
        
        # AWS credentials and configuration
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', ''),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
        aws_region=os.environ.get('AWS_REGION', ''),
        s3_bucket=os.environ.get('S3_BUCKET', ''),
        
        # AWS SES configuration
        ses_domain=os.environ.get('SES_DOMAIN', ''),
        ses_sender_email=os.environ.get('SES_SENDER_EMAIL', ''),
        ses_reply_to=os.environ.get('SES_REPLY_TO', OPTIONAL_VARS['SES_REPLY_TO']),
        
        # Timezone configuration
        default_timezone=os.environ.get('DEFAULT_TIMEZONE', OPTIONAL_VARS['DEFAULT_TIMEZONE']),
        
        # Campaign and audience IDs
        audience_id=os.environ.get('AUDIENCE_ID', OPTIONAL_VARS['AUDIENCE_ID']),
        campaign_id=os.environ.get('CAMPAIGN_ID', OPTIONAL_VARS['CAMPAIGN_ID']),
        template_id=os.environ.get('TEMPLATE_ID', OPTIONAL_VARS['TEMPLATE_ID']),
        
        # Test configuration
        num_test_profiles=int(os.environ.get('NUM_TEST_PROFILES', OPTIONAL_VARS['NUM_TEST_PROFILES'])),
        mode=os.environ.get('MODE', OPTIONAL_VARS['MODE']),
        
        # Integration endpoints
        slack_webhook_url=os.environ.get('SLACK_WEBHOOK_URL', OPTIONAL_VARS['SLACK_WEBHOOK_URL']),
        looker_report_url=os.environ.get('LOOKER_REPORT_URL', OPTIONAL_VARS['LOOKER_REPORT_URL']),
        
        # Google Sheets configuration
        google_sheet_id=os.environ.get('GOOGLE_SHEET_ID', OPTIONAL_VARS['GOOGLE_SHEET_ID']),
        google_sheet_name=os.environ.get('GOOGLE_SHEET_NAME', OPTIONAL_VARS['GOOGLE_SHEET_NAME']),
        google_sheet_range_name=os.environ.get('GOOGLE_SHEET_RANGE_NAME', OPTIONAL_VARS['GOOGLE_SHEET_RANGE_NAME']),
    )
    
    # Validate settings
    if os.environ.get('SKIP_CONFIG_VALIDATION') != 'true':
        settings.validate()
    
    return settings

# Create settings instance
settings = load_settings()

# For backward compatibility with existing code
KLAVIYO_API_KEY = settings.klaviyo_api_key
KLAVIYO_API_VERSION = settings.klaviyo_api_version
AUDIENCE_ID = settings.audience_id
CAMPAIGN_ID = settings.campaign_id
TEMPLATE_ID = settings.template_id
NUM_TEST_PROFILES = settings.num_test_profiles
MODE = settings.mode
SLACK_WEBHOOK_URL = settings.slack_webhook_url
LOOKER_REPORT_URL = settings.looker_report_url
GOOGLE_SHEET_ID = settings.google_sheet_id
GOOGLE_SHEET_NAME = settings.google_sheet_name
GOOGLE_SHEET_RANGE_NAME = settings.google_sheet_range_name

def get_config() -> Dict[str, Any]:
    """Return configuration as a dictionary (for backward compatibility)"""
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
