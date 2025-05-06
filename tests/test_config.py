import sys
import os
import importlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
# Reload the module to ensure we get the latest version
importlib.reload(config)

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
