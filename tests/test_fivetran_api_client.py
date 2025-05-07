import os
import pytest
import responses
from unittest.mock import patch
from src.fivetran_api_client import FivetranAPIClient, get_client_from_env

@pytest.fixture
def fivetran_client():
    return FivetranAPIClient("test_api_key", "test_api_secret")

@responses.activate
def test_get_groups(fivetran_client):
    # Mock the API response
    responses.add(
        responses.GET,
        "https://api.fivetran.com/v1/groups",
        json={
            "code": "Success",
            "data": {
                "items": [
                    {"id": "group1", "name": "Test Group 1"},
                    {"id": "group2", "name": "Test Group 2"}
                ]
            }
        },
        status=200
    )
    
    # Call the method
    groups = fivetran_client.get_groups()
    
    # Verify the response
    assert len(groups) == 2
    assert groups[0]["id"] == "group1"
    assert groups[0]["name"] == "Test Group 1"
    assert groups[1]["id"] == "group2"
    assert groups[1]["name"] == "Test Group 2"

@responses.activate
def test_get_connectors(fivetran_client):
    group_id = "test_group"
    
    # Mock the API response
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/groups/{group_id}/connectors",
        json={
            "code": "Success",
            "data": {
                "items": [
                    {"id": "conn1", "name": "Connector 1", "service": "klaviyo", "status": {"sync_state": "SYNC_SUCCEEDED"}},
                    {"id": "conn2", "name": "Connector 2", "service": "postgres", "status": {"sync_state": "SYNCING"}}
                ]
            }
        },
        status=200
    )
    
    # Call the method
    connectors = fivetran_client.get_connectors(group_id)
    
    # Verify the response
    assert len(connectors) == 2
    assert connectors[0]["id"] == "conn1"
    assert connectors[0]["name"] == "Connector 1"
    assert connectors[0]["service"] == "klaviyo"
    assert connectors[0]["status"]["sync_state"] == "SYNC_SUCCEEDED"

@responses.activate
def test_get_connector(fivetran_client):
    connector_id = "test_connector"
    
    # Mock the API response
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "service": "klaviyo",
                "status": {
                    "sync_state": "SYNC_SUCCEEDED",
                    "update_state": "READY"
                }
            }
        },
        status=200
    )
    
    # Call the method
    connector = fivetran_client.get_connector(connector_id)
    
    # Verify the response
    assert connector["id"] == connector_id
    assert connector["name"] == "Test Connector"
    assert connector["service"] == "klaviyo"
    assert connector["status"]["sync_state"] == "SYNC_SUCCEEDED"

@responses.activate
def test_trigger_sync(fivetran_client):
    connector_id = "test_connector"
    
    # Mock the API response
    responses.add(
        responses.POST,
        f"https://api.fivetran.com/v1/connectors/{connector_id}/sync",
        json={
            "code": "Success",
            "message": "Sync started"
        },
        status=200
    )
    
    # Call the method
    response = fivetran_client.trigger_sync(connector_id)
    
    # Verify the response
    assert response["code"] == "Success"
    assert response["message"] == "Sync started"

@responses.activate
def test_get_sync_status(fivetran_client):
    connector_id = "test_connector"
    
    # Mock the API response
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "status": {
                    "sync_state": "SYNCING",
                    "sync_error": None
                }
            }
        },
        status=200
    )
    
    # Call the method
    status, error = fivetran_client.get_sync_status(connector_id)
    
    # Verify the response
    assert status == "SYNCING"
    assert error is None

@responses.activate
def test_get_sync_status_with_error(fivetran_client):
    connector_id = "test_connector"
    
    # Mock the API response
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "status": {
                    "sync_state": "SYNC_FAILED",
                    "sync_error": "API authentication failed"
                }
            }
        },
        status=200
    )
    
    # Call the method
    status, error = fivetran_client.get_sync_status(connector_id)
    
    # Verify the response
    assert status == "SYNC_FAILED"
    assert error == "API authentication failed"

@responses.activate
def test_wait_for_sync_completion_success(fivetran_client):
    connector_id = "test_connector"
    
    # Mock the API response for the first call (SYNCING)
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "status": {
                    "sync_state": "SYNCING",
                    "sync_error": None
                }
            }
        },
        status=200
    )
    
    # Mock the API response for the second call (SYNC_SUCCEEDED)
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "status": {
                    "sync_state": "SYNC_SUCCEEDED",
                    "sync_error": None
                }
            }
        },
        status=200
    )
    
    # Call the method with a short poll interval
    with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up the test
        result = fivetran_client.wait_for_sync_completion(connector_id, poll_interval=1)
    
    # Verify the result
    assert result is True
    assert mock_sleep.call_count == 1  # Should sleep once between the two API calls

@responses.activate
def test_wait_for_sync_completion_failure(fivetran_client):
    connector_id = "test_connector"
    
    # Mock the API response for the first call (SYNCING)
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "status": {
                    "sync_state": "SYNCING",
                    "sync_error": None
                }
            }
        },
        status=200
    )
    
    # Mock the API response for the second call (SYNC_FAILED)
    responses.add(
        responses.GET,
        f"https://api.fivetran.com/v1/connectors/{connector_id}",
        json={
            "code": "Success",
            "data": {
                "id": connector_id,
                "name": "Test Connector",
                "status": {
                    "sync_state": "SYNC_FAILED",
                    "sync_error": "API authentication failed"
                }
            }
        },
        status=200
    )
    
    # Call the method with a short poll interval
    with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up the test
        result = fivetran_client.wait_for_sync_completion(connector_id, poll_interval=1)
    
    # Verify the result
    assert result is False
    assert mock_sleep.call_count == 1  # Should sleep once between the two API calls

@responses.activate
def test_rate_limit_handling(fivetran_client):
    # Mock the API response with a rate limit error
    responses.add(
        responses.GET,
        "https://api.fivetran.com/v1/groups",
        status=429,
        headers={"Retry-After": "1"}  # 1 second retry
    )
    
    # Mock the API response for the retry
    responses.add(
        responses.GET,
        "https://api.fivetran.com/v1/groups",
        json={
            "code": "Success",
            "data": {
                "items": [
                    {"id": "group1", "name": "Test Group 1"}
                ]
            }
        },
        status=200
    )
    
    # Call the method
    with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up the test
        groups = fivetran_client.get_groups()
    
    # Verify the response
    assert len(groups) == 1
    assert groups[0]["id"] == "group1"
    assert groups[0]["name"] == "Test Group 1"
    assert mock_sleep.call_count == 1  # Should sleep once for the rate limit

def test_get_client_from_env():
    # Mock environment variables
    with patch.dict(os.environ, {
        "FIVETRAN_API_KEY": "test_key",
        "FIVETRAN_API_SECRET": "test_secret"
    }):
        client = get_client_from_env()
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"

def test_get_client_from_env_missing_vars():
    # Mock environment variables (missing API secret)
    with patch.dict(os.environ, {
        "FIVETRAN_API_KEY": "test_key"
    }, clear=True):
        with pytest.raises(ValueError) as excinfo:
            get_client_from_env()
        assert "FIVETRAN_API_KEY and FIVETRAN_API_SECRET environment variables must be set" in str(excinfo.value)
