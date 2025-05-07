import pytest
import responses
from unittest.mock import patch, MagicMock

from src.fivetran_connector_runner import run_connector
from src.fivetran_api_client import FivetranAPIClient

@pytest.fixture
def mock_fivetran_client():
    client = MagicMock(spec=FivetranAPIClient)
    return client

def test_run_connector_dry_run():
    # Test dry run mode
    with patch('src.fivetran_connector_runner.get_client_from_env') as mock_get_client:
        result = run_connector("test_group", "test_connector", dry_run=True)
        
        # Verify the result
        assert result is True
        # Verify that get_client_from_env was not called
        mock_get_client.assert_not_called()

def test_run_connector_success():
    # Test successful connector run
    with patch('src.fivetran_connector_runner.get_client_from_env') as mock_get_client:
        # Setup the mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock the connector list
        mock_client.get_connectors.return_value = [
            {"id": "test_connector", "name": "Test Connector"}
        ]
        
        # Mock the trigger_sync and wait_for_sync_completion methods
        mock_client.trigger_sync.return_value = {"code": "Success"}
        mock_client.wait_for_sync_completion.return_value = True
        
        # Call the function
        result = run_connector("test_group", "test_connector")
        
        # Verify the result
        assert result is True
        
        # Verify the client method calls
        mock_client.get_connectors.assert_called_once_with("test_group")
        mock_client.trigger_sync.assert_called_once_with("test_connector")
        mock_client.wait_for_sync_completion.assert_called_once_with(
            "test_connector", timeout=3600, poll_interval=30
        )

def test_run_connector_not_found():
    # Test connector not found
    with patch('src.fivetran_connector_runner.get_client_from_env') as mock_get_client:
        # Setup the mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock the connector list (empty)
        mock_client.get_connectors.return_value = []
        
        # Call the function
        result = run_connector("test_group", "test_connector")
        
        # Verify the result
        assert result is False
        
        # Verify the client method calls
        mock_client.get_connectors.assert_called_once_with("test_group")
        mock_client.trigger_sync.assert_not_called()
        mock_client.wait_for_sync_completion.assert_not_called()

def test_run_connector_sync_failure():
    # Test sync failure
    with patch('src.fivetran_connector_runner.get_client_from_env') as mock_get_client:
        # Setup the mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock the connector list
        mock_client.get_connectors.return_value = [
            {"id": "test_connector", "name": "Test Connector"}
        ]
        
        # Mock the trigger_sync and wait_for_sync_completion methods
        mock_client.trigger_sync.return_value = {"code": "Success"}
        mock_client.wait_for_sync_completion.return_value = False
        
        # Call the function
        result = run_connector("test_group", "test_connector")
        
        # Verify the result
        assert result is False
        
        # Verify the client method calls
        mock_client.get_connectors.assert_called_once_with("test_group")
        mock_client.trigger_sync.assert_called_once_with("test_connector")
        mock_client.wait_for_sync_completion.assert_called_once_with(
            "test_connector", timeout=3600, poll_interval=30
        )

def test_run_connector_exception():
    # Test exception handling
    with patch('src.fivetran_connector_runner.get_client_from_env') as mock_get_client:
        # Setup the mock client to raise an exception
        mock_get_client.side_effect = Exception("Test exception")
        
        # Call the function
        result = run_connector("test_group", "test_connector")
        
        # Verify the result
        assert result is False

def test_run_connector_custom_params():
    # Test custom timeout and poll interval
    with patch('src.fivetran_connector_runner.get_client_from_env') as mock_get_client:
        # Setup the mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock the connector list
        mock_client.get_connectors.return_value = [
            {"id": "test_connector", "name": "Test Connector"}
        ]
        
        # Mock the trigger_sync and wait_for_sync_completion methods
        mock_client.trigger_sync.return_value = {"code": "Success"}
        mock_client.wait_for_sync_completion.return_value = True
        
        # Call the function with custom timeout and poll interval
        result = run_connector("test_group", "test_connector", timeout=1800, poll_interval=15)
        
        # Verify the result
        assert result is True
        
        # Verify the client method calls with custom parameters
        mock_client.wait_for_sync_completion.assert_called_once_with(
            "test_connector", timeout=1800, poll_interval=15
        )
