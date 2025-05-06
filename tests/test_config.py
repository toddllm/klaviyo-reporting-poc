import sys
import os
import importlib
import pytest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new config module from src
from src import config as src_config
# Reload the module to ensure we get the latest version
importlib.reload(src_config)

# For backward compatibility, also test the root config module
import config
importlib.reload(config)

# Test the new src/config.py module
def test_src_config_defaults():
    # Test that settings object is created
    assert src_config.settings is not None
    # Test default values
    assert src_config.settings.klaviyo_api_key is not None
    assert src_config.settings.audience_id is not None
    assert src_config.settings.campaign_id is not None
    assert src_config.settings.template_id is not None
    assert src_config.settings.num_test_profiles > 0
    assert src_config.settings.mode in ['mock', 'real']
    assert src_config.settings.slack_webhook_url is not None
    assert src_config.settings.looker_report_url is not None
    assert src_config.settings.klaviyo_api_version == '2025-04-15'

def test_src_config_dict_method():
    # Test that dict() method returns a dictionary with all settings
    config_dict = src_config.settings.dict()
    assert isinstance(config_dict, dict)
    assert 'klaviyo_api_key' in config_dict
    assert 'supermetrics_api_key' in config_dict
    assert 'aws_access_key_id' in config_dict
    assert 'aws_region' in config_dict

@patch.dict(os.environ, {'MODE': 'invalid_mode'})
def test_src_config_validation_mode():
    # Test that validation fails with invalid mode
    with pytest.raises(ValueError, match="MODE must be 'mock' or 'real'"):
        # Skip the exit(1) by setting ALLOW_MISSING_ENV_VARS
        with patch.dict(os.environ, {'ALLOW_MISSING_ENV_VARS': 'true', 'SKIP_CONFIG_VALIDATION': 'false'}):
            importlib.reload(src_config)
            src_config.settings.validate()

@patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://invalid-url.com'})
def test_src_config_validation_slack_url():
    # Test that validation fails with invalid Slack webhook URL
    with pytest.raises(ValueError, match="SLACK_WEBHOOK_URL must contain 'hooks.slack.com/services/'"):
        # Skip the exit(1) by setting ALLOW_MISSING_ENV_VARS
        with patch.dict(os.environ, {'ALLOW_MISSING_ENV_VARS': 'true', 'SKIP_CONFIG_VALIDATION': 'false'}):
            importlib.reload(src_config)
            src_config.settings.validate()

@patch.dict(os.environ, {'LOOKER_REPORT_URL': 'https://invalid-url.com'})
def test_src_config_validation_looker_url():
    # Test that validation fails with invalid Looker report URL
    with pytest.raises(ValueError, match="LOOKER_REPORT_URL must contain 'datastudio.google.com/reporting/'"):
        # Skip the exit(1) by setting ALLOW_MISSING_ENV_VARS
        with patch.dict(os.environ, {'ALLOW_MISSING_ENV_VARS': 'true', 'SKIP_CONFIG_VALIDATION': 'false'}):
            importlib.reload(src_config)
            src_config.settings.validate()

# Test missing required environment variables
def test_src_config_missing_required_vars():
    # Test that load_settings exits when required variables are missing
    with patch.dict(os.environ, {}, clear=True):
        # We need to mock sys.exit to prevent the test from actually exiting
        with patch('sys.exit') as mock_exit:
            importlib.reload(src_config)
            mock_exit.assert_called_once_with(1)

# Test for backward compatibility with the root config module
def test_config_defaults():
    assert config.KLAVIYO_API_KEY is not None
    assert config.AUDIENCE_ID is not None
    assert config.CAMPAIGN_ID is not None
    assert config.TEMPLATE_ID is not None
    assert config.NUM_TEST_PROFILES > 0
    # Check if MODE is 'mock' or 'real', ignoring any comments
    assert config.MODE.strip().split('#')[0].strip() in ['mock', 'real']
    assert config.SLACK_WEBHOOK_URL is not None
    assert config.LOOKER_REPORT_URL is not None
    assert config.KLAVIYO_API_VERSION == '2025-04-15'

def test_slack_webhook_url():
    assert 'hooks.slack.com/services/' in config.SLACK_WEBHOOK_URL

def test_looker_report_url():
    assert 'datastudio.google.com/reporting/' in config.LOOKER_REPORT_URL
