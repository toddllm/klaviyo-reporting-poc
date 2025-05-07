import os
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Import the module directly from scripts
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.ses_smoketest import validate_ses_env_vars, send_email


def test_validate_ses_env_vars_success():
    # Test with all required environment variables set
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1",
        "SES_FROM_EMAIL": "test@example.com"
    }):
        # This should not raise an exception
        validate_ses_env_vars()


def test_validate_ses_env_vars_missing():
    # Test with missing environment variables
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret"
        # Missing AWS_REGION and SES_FROM_EMAIL
    }, clear=True):
        with pytest.raises(ValueError) as excinfo:
            validate_ses_env_vars()
        assert "Missing required AWS SES environment variables" in str(excinfo.value)
        assert "AWS_REGION" in str(excinfo.value)
        assert "SES_FROM_EMAIL" in str(excinfo.value)


def test_send_email_dry_run():
    # Test dry run mode
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1",
        "SES_FROM_EMAIL": "test@example.com"
    }):
        result = send_email(
            "recipient@example.com",
            "Test Subject",
            "Test Body",
            dry_run=True
        )
        assert result == "DRY-RUN-MESSAGE-ID"


def test_send_email_success():
    # Test successful email sending
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1",
        "SES_FROM_EMAIL": "test@example.com",
        "SES_REPLY_TO": "reply@example.com"  # Test reply-to header
    }):
        # Mock the boto3 client
        mock_client = MagicMock()
        mock_client.send_raw_email.return_value = {"MessageId": "test-message-id"}
        
        with patch("boto3.client", return_value=mock_client):
            result = send_email(
                "recipient@example.com",
                "Test Subject",
                "Test Body",
                html_body="<p>Test HTML Body</p>"
            )
            
            # Verify the result
            assert result == "test-message-id"
            
            # Verify the client was called correctly
            mock_client.send_raw_email.assert_called_once()
            call_args = mock_client.send_raw_email.call_args[1]
            assert call_args["Source"] == "test@example.com"
            assert call_args["Destinations"] == ["recipient@example.com"]
            assert "Test Subject" in call_args["RawMessage"]["Data"]
            assert "Test Body" in call_args["RawMessage"]["Data"]
            assert "<p>Test HTML Body</p>" in call_args["RawMessage"]["Data"]
            assert "reply@example.com" in call_args["RawMessage"]["Data"]


def test_send_email_error():
    # Test error handling
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-east-1",
        "SES_FROM_EMAIL": "test@example.com"
    }):
        # Mock the boto3 client to raise an exception
        mock_client = MagicMock()
        mock_client.send_raw_email.side_effect = ClientError(
            {"Error": {"Code": "MessageRejected", "Message": "Email address is not verified"}},
            "SendRawEmail"
        )
        
        with patch("boto3.client", return_value=mock_client):
            result = send_email(
                "recipient@example.com",
                "Test Subject",
                "Test Body"
            )
            
            # Verify the result
            assert result is None
            
            # Verify the client was called
            mock_client.send_raw_email.assert_called_once()
