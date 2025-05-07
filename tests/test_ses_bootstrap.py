import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

# Mock the settings import
sys.modules['src.config'] = MagicMock()
sys.modules['src.config'].settings = MagicMock(
    ses_domain='example.com',
    ses_sender_email='test@example.com',
    aws_region='us-west-2'
)

# Import functions from ses_bootstrap.py
from ses_bootstrap import (
    verify_domain,
    setup_dkim,
    verify_email,
    create_iam_user,
    check_sandbox_status,
    request_production_access,
    IAM_USER_NAME,
    IAM_POLICY_NAME
)

@pytest.fixture
def mock_ses_client():
    return MagicMock()

@pytest.fixture
def mock_iam_client():
    return MagicMock()

@pytest.fixture
def mock_boto3():
    with patch('boto3.client') as mock_client:
        yield mock_client

# Test verify_domain function
def test_verify_domain_already_verified(mock_ses_client):
    # Setup mock response for already verified domain
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {
            'example.com': {
                'VerificationStatus': 'Success'
            }
        }
    }
    
    result = verify_domain(mock_ses_client, 'example.com')
    
    assert result is True
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_identity.assert_not_called()

def test_verify_domain_pending(mock_ses_client):
    # Setup mock response for pending domain verification
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {
            'example.com': {
                'VerificationStatus': 'Pending'
            }
        }
    }
    
    result = verify_domain(mock_ses_client, 'example.com')
    
    assert result is False
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_identity.assert_not_called()

def test_verify_domain_new(mock_ses_client):
    # Setup mock response for new domain
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {}
    }
    mock_ses_client.verify_domain_identity.return_value = {
        'VerificationToken': 'test-token'
    }
    
    result = verify_domain(mock_ses_client, 'example.com')
    
    assert result is False
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_identity.assert_called_once_with(Domain='example.com')

def test_verify_domain_dry_run(mock_ses_client):
    # Setup mock response for new domain with dry run
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {}
    }
    
    result = verify_domain(mock_ses_client, 'example.com', dry_run=True)
    
    assert result is True
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_identity.assert_not_called()

def test_verify_domain_error(mock_ses_client):
    # Setup mock error response
    mock_ses_client.get_identity_verification_attributes.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'GetIdentityVerificationAttributes'
    )
    
    result = verify_domain(mock_ses_client, 'example.com')
    
    assert result is False
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['example.com']
    )

# Test setup_dkim function
def test_setup_dkim_already_enabled(mock_ses_client):
    # Setup mock response for already enabled DKIM
    mock_ses_client.get_identity_dkim_attributes.return_value = {
        'DkimAttributes': {
            'example.com': {
                'DkimEnabled': True
            }
        }
    }
    
    result = setup_dkim(mock_ses_client, 'example.com')
    
    assert result is True
    mock_ses_client.get_identity_dkim_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_dkim.assert_not_called()

def test_setup_dkim_new(mock_ses_client):
    # Setup mock response for new DKIM setup
    mock_ses_client.get_identity_dkim_attributes.return_value = {
        'DkimAttributes': {}
    }
    mock_ses_client.verify_domain_dkim.return_value = {
        'DkimTokens': ['token1', 'token2', 'token3']
    }
    
    result = setup_dkim(mock_ses_client, 'example.com')
    
    assert result is True
    mock_ses_client.get_identity_dkim_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_dkim.assert_called_once_with(Domain='example.com')

def test_setup_dkim_dry_run(mock_ses_client):
    # Setup mock response for new DKIM setup with dry run
    mock_ses_client.get_identity_dkim_attributes.return_value = {
        'DkimAttributes': {}
    }
    
    result = setup_dkim(mock_ses_client, 'example.com', dry_run=True)
    
    assert result is True
    mock_ses_client.get_identity_dkim_attributes.assert_called_once_with(
        Identities=['example.com']
    )
    mock_ses_client.verify_domain_dkim.assert_not_called()

def test_setup_dkim_error(mock_ses_client):
    # Setup mock error response
    mock_ses_client.get_identity_dkim_attributes.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'GetIdentityDkimAttributes'
    )
    
    result = setup_dkim(mock_ses_client, 'example.com')
    
    assert result is False
    mock_ses_client.get_identity_dkim_attributes.assert_called_once_with(
        Identities=['example.com']
    )

# Test verify_email function
def test_verify_email_already_verified(mock_ses_client):
    # Setup mock response for already verified email
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {
            'test@example.com': {
                'VerificationStatus': 'Success'
            }
        }
    }
    
    result = verify_email(mock_ses_client, 'test@example.com')
    
    assert result is True
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['test@example.com']
    )
    mock_ses_client.verify_email_identity.assert_not_called()

def test_verify_email_pending(mock_ses_client):
    # Setup mock response for pending email verification
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {
            'test@example.com': {
                'VerificationStatus': 'Pending'
            }
        }
    }
    
    result = verify_email(mock_ses_client, 'test@example.com')
    
    assert result is False
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['test@example.com']
    )
    mock_ses_client.verify_email_identity.assert_not_called()

def test_verify_email_new(mock_ses_client):
    # Setup mock response for new email
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {}
    }
    
    result = verify_email(mock_ses_client, 'test@example.com')
    
    assert result is False
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['test@example.com']
    )
    mock_ses_client.verify_email_identity.assert_called_once_with(EmailAddress='test@example.com')

def test_verify_email_dry_run(mock_ses_client):
    # Setup mock response for new email with dry run
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {}
    }
    
    result = verify_email(mock_ses_client, 'test@example.com', dry_run=True)
    
    assert result is True
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['test@example.com']
    )
    mock_ses_client.verify_email_identity.assert_not_called()

def test_verify_email_error(mock_ses_client):
    # Setup mock error response
    mock_ses_client.get_identity_verification_attributes.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'GetIdentityVerificationAttributes'
    )
    
    result = verify_email(mock_ses_client, 'test@example.com')
    
    assert result is False
    mock_ses_client.get_identity_verification_attributes.assert_called_once_with(
        Identities=['test@example.com']
    )

# Test create_iam_user function
def test_create_iam_user_exists(mock_iam_client):
    # Setup mock response for existing user
    mock_iam_client.get_user.return_value = {
        'User': {
            'UserName': IAM_USER_NAME
        }
    }
    mock_iam_client.get_user_policy.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchEntity', 'Message': 'Policy not found'}},
        'GetUserPolicy'
    )
    
    result = create_iam_user(mock_iam_client)
    
    assert result is True
    mock_iam_client.get_user.assert_called_once_with(UserName=IAM_USER_NAME)
    mock_iam_client.create_user.assert_not_called()
    mock_iam_client.put_user_policy.assert_called_once()

def test_create_iam_user_new(mock_iam_client):
    # Setup mock response for new user
    mock_iam_client.get_user.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchEntity', 'Message': 'User not found'}},
        'GetUser'
    )
    mock_iam_client.get_user_policy.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchEntity', 'Message': 'Policy not found'}},
        'GetUserPolicy'
    )
    mock_iam_client.create_access_key.return_value = {
        'AccessKey': {
            'AccessKeyId': 'test-access-key',
            'SecretAccessKey': 'test-secret-key'
        }
    }
    
    result = create_iam_user(mock_iam_client)
    
    assert result is True
    mock_iam_client.get_user.assert_called_once_with(UserName=IAM_USER_NAME)
    mock_iam_client.create_user.assert_called_once_with(UserName=IAM_USER_NAME)
    mock_iam_client.put_user_policy.assert_called_once()
    mock_iam_client.create_access_key.assert_called_once_with(UserName=IAM_USER_NAME)

def test_create_iam_user_dry_run(mock_iam_client):
    # Setup mock response for new user with dry run
    mock_iam_client.get_user.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchEntity', 'Message': 'User not found'}},
        'GetUser'
    )
    
    result = create_iam_user(mock_iam_client, dry_run=True)
    
    assert result is True
    mock_iam_client.get_user.assert_called_once_with(UserName=IAM_USER_NAME)
    mock_iam_client.create_user.assert_not_called()
    mock_iam_client.put_user_policy.assert_not_called()
    mock_iam_client.create_access_key.assert_not_called()

def test_create_iam_user_error(mock_iam_client):
    # Setup mock error response
    mock_iam_client.get_user.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'GetUser'
    )
    
    result = create_iam_user(mock_iam_client)
    
    assert result is False
    mock_iam_client.get_user.assert_called_once_with(UserName=IAM_USER_NAME)

# Test check_sandbox_status function
def test_check_sandbox_status_in_sandbox(mock_ses_client):
    # Setup mock response for sandbox account
    mock_ses_client.get_account_sending_enabled.return_value = {
        'Enabled': False
    }
    
    result = check_sandbox_status(mock_ses_client)
    
    assert result is True
    mock_ses_client.get_account_sending_enabled.assert_called_once()

def test_check_sandbox_status_production(mock_ses_client):
    # Setup mock response for production account
    mock_ses_client.get_account_sending_enabled.return_value = {
        'Enabled': True
    }
    
    result = check_sandbox_status(mock_ses_client)
    
    assert result is False
    mock_ses_client.get_account_sending_enabled.assert_called_once()

def test_check_sandbox_status_error(mock_ses_client):
    # Setup mock error response
    mock_ses_client.get_account_sending_enabled.side_effect = ClientError(
        {'Error': {'Code': 'TestException', 'Message': 'Test error'}},
        'GetAccountSendingEnabled'
    )
    
    result = check_sandbox_status(mock_ses_client)
    
    assert result is True
    mock_ses_client.get_account_sending_enabled.assert_called_once()

# Test request_production_access function
def test_request_production_access(capsys):
    # Test that instructions are printed
    request_production_access(None, 'us-west-2')
    captured = capsys.readouterr()
    
    assert 'To request production access' in captured.out
    assert 'https://us-west-2.console.aws.amazon.com/ses/home?region=us-west-2#/account' in captured.out

def test_request_production_access_dry_run(capsys):
    # Test that dry run message is printed
    request_production_access(None, 'us-west-2', dry_run=True)
    captured = capsys.readouterr()
    
    assert '[DRY RUN]' in captured.out
    assert 'Would provide instructions' in captured.out

# Test main function
@patch('sys.argv', ['ses_bootstrap.py', '--dry-run'])
@patch('boto3.client')
def test_main_dry_run(mock_boto3, capsys):
    # Setup mock clients
    mock_ses_client = MagicMock()
    mock_iam_client = MagicMock()
    mock_boto3.side_effect = lambda service, region_name: {
        'ses': mock_ses_client,
        'iam': mock_iam_client
    }[service]
    
    # Setup mock responses
    mock_ses_client.get_identity_verification_attributes.return_value = {
        'VerificationAttributes': {}
    }
    mock_ses_client.get_identity_dkim_attributes.return_value = {
        'DkimAttributes': {}
    }
    mock_ses_client.get_account_sending_enabled.return_value = {
        'Enabled': False
    }
    mock_iam_client.get_user.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchEntity', 'Message': 'User not found'}},
        'GetUser'
    )
    
    # Run main function
    from ses_bootstrap import main
    main()
    
    # Check output
    captured = capsys.readouterr()
    assert '[DRY RUN]' in captured.out
    assert 'Setting up AWS SES' in captured.out
    
    # Verify mock calls
    mock_ses_client.verify_domain_identity.assert_not_called()
    mock_ses_client.verify_domain_dkim.assert_not_called()
    mock_ses_client.verify_email_identity.assert_not_called()
    mock_iam_client.create_user.assert_not_called()
