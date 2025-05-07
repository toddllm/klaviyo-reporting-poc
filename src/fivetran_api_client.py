import os
import time
import logging
import requests
import base64
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class FivetranAPIClient:
    BASE_URL = "https://api.fivetran.com/v1"
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.auth = (self.api_key, self.api_secret)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
    @classmethod
    def from_auth_header(cls, auth_header: Dict[str, str]):
        """Create a client instance using an authorization header.
        
        Args:
            auth_header: Dictionary containing the Authorization header
            
        Returns:
            FivetranAPIClient instance configured with the provided auth header
        """
        client = cls("dummy_key", "dummy_secret")  # Keys won't be used with custom auth
        client.session.auth = None  # Disable basic auth
        client.session.headers.update(auth_header)  # Use the provided auth header
        return client
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response, including error cases."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._retry_request(response.request)
            
            error_msg = f"HTTP error: {e}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = f"API error: {error_data['error']}"
            except ValueError:
                pass
            
            logger.error(error_msg)
            raise
    
    def _retry_request(self, request) -> Dict[str, Any]:
        """Retry a failed request."""
        # If it's already a PreparedRequest, use it directly
        if hasattr(request, 'url'):
            response = self.session.send(request)
        else:
            # Otherwise, it's a Request object that needs to be prepared
            prepared_request = self.session.prepare_request(request)
            response = self.session.send(prepared_request)
        return self._handle_response(response)
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """Get all groups."""
        response = self.session.get(f"{self.BASE_URL}/groups")
        data = self._handle_response(response)
        return data.get("data", {}).get("items", [])
    
    def get_connectors(self, group_id: str) -> List[Dict[str, Any]]:
        """Get all connectors for a group."""
        response = self.session.get(f"{self.BASE_URL}/groups/{group_id}/connectors")
        data = self._handle_response(response)
        return data.get("data", {}).get("items", [])
    
    def get_connector(self, connector_id: str) -> Dict[str, Any]:
        """Get details for a specific connector."""
        response = self.session.get(f"{self.BASE_URL}/connectors/{connector_id}")
        data = self._handle_response(response)
        return data.get("data", {})
    
    def trigger_sync(self, connector_id: str) -> Dict[str, Any]:
        """Trigger a sync for a connector."""
        response = self.session.post(f"{self.BASE_URL}/connectors/{connector_id}/sync")
        return self._handle_response(response)
    
    def get_sync_status(self, connector_id: str) -> Tuple[str, Optional[str]]:
        """Get the current sync status for a connector.
        
        Returns:
            Tuple of (status, error_message)
        """
        connector_data = self.get_connector(connector_id)
        status = connector_data.get("status", {}).get("sync_state", "UNKNOWN")
        error = connector_data.get("status", {}).get("sync_error", None)
        return status, error
    
    def wait_for_sync_completion(self, connector_id: str, timeout: int = 3600, poll_interval: int = 30) -> bool:
        """Wait for a sync to complete.
        
        Args:
            connector_id: The connector ID
            timeout: Maximum time to wait in seconds (default: 1 hour)
            poll_interval: Time between status checks in seconds (default: 30 seconds)
            
        Returns:
            True if sync completed successfully, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status, error = self.get_sync_status(connector_id)
            
            if status == "SYNCING":
                logger.info(f"Connector {connector_id} is syncing. Waiting {poll_interval} seconds...")
                time.sleep(poll_interval)
                continue
                
            if status == "SYNC_SUCCEEDED":
                logger.info(f"Connector {connector_id} sync completed successfully.")
                return True
                
            if status in ["SYNC_FAILED", "ERROR"]:
                logger.error(f"Connector {connector_id} sync failed: {error}")
                return False
                
            logger.info(f"Connector {connector_id} status: {status}. Waiting {poll_interval} seconds...")
            time.sleep(poll_interval)
        
        logger.error(f"Timeout waiting for connector {connector_id} sync to complete.")
        return False


def _get_auth_header() -> Dict[str, str]:
    """Get the authentication header based on available environment variables.
    
    Priority: system key → classic key
    
    Returns:
        Dict containing the appropriate Authorization header
    
    Raises:
        RuntimeError: If no valid Fivetran credentials are found
    """
    # Check for system key authentication first
    sys_key = os.environ.get("FIVETRAN_SYSTEM_KEY")
    sys_secret = os.environ.get("FIVETRAN_SYSTEM_KEY_SECRET")
    sys_key_b64 = os.environ.get("FIVETRAN_SYSTEM_KEY_B64")
    
    # If we have a pre-encoded system key, use it directly
    if sys_key_b64:
        return {"Authorization": f"Basic {sys_key_b64}"}
    
    # If we have system key and secret, encode them
    if sys_key and sys_secret:
        token = base64.b64encode(f"{sys_key}:{sys_secret}".encode()).decode()
        return {"Authorization": f"Basic {token}"}
    
    # Fall back to classic API key authentication
    api_key = os.environ.get("FIVETRAN_API_KEY")
    api_secret = os.environ.get("FIVETRAN_API_SECRET")
    
    if api_key and api_secret:
        return {"Authorization": f"Bearer {api_key}"}
    
    # No valid credentials found
    raise RuntimeError(
        "No valid Fivetran credentials found. Set either FIVETRAN_SYSTEM_KEY and "
        "FIVETRAN_SYSTEM_KEY_SECRET, FIVETRAN_SYSTEM_KEY_B64, or FIVETRAN_API_KEY and "
        "FIVETRAN_API_SECRET environment variables."
    )

def get_client_from_env() -> FivetranAPIClient:
    """Create a Fivetran API client using environment variables.
    
    Supports both system key and classic API key authentication methods.
    """
    try:
        # Get the appropriate auth header based on available credentials
        auth_header = _get_auth_header()
        logger.info(f"Using Fivetran authentication: {list(auth_header.values())[0].split(' ')[0]}")
        return FivetranAPIClient.from_auth_header(auth_header)
    except RuntimeError as e:
        # Re-raise with more specific error message
        raise ValueError(str(e))


if __name__ == "__main__":
    import argparse
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Fivetran API Client")
    parser.add_argument("--list-groups", action="store_true", help="List all groups")
    parser.add_argument("--list-connectors", help="List all connectors for a group")
    parser.add_argument("--trigger-sync", help="Trigger a sync for a connector")
    parser.add_argument("--wait", action="store_true", help="Wait for sync to complete")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds")
    parser.add_argument("--poll-interval", type=int, default=30, help="Poll interval in seconds")
    
    args = parser.parse_args()
    
    try:
        client = get_client_from_env()
        
        if args.list_groups:
            groups = client.get_groups()
            for group in groups:
                print(f"Group: {group['name']} (ID: {group['id']})")
        
        elif args.list_connectors:
            connectors = client.get_connectors(args.list_connectors)
            for connector in connectors:
                print(f"Connector: {connector['name']} (ID: {connector['id']})")
                print(f"  Service: {connector['service']}")
                print(f"  Status: {connector['status']['sync_state']}")
                print("---")
        
        elif args.trigger_sync:
            print(f"Triggering sync for connector {args.trigger_sync}...")
            client.trigger_sync(args.trigger_sync)
            print("Sync triggered.")
            
            if args.wait:
                print(f"Waiting for sync to complete (timeout: {args.timeout}s, poll: {args.poll_interval}s)...")
                success = client.wait_for_sync_completion(
                    args.trigger_sync, 
                    timeout=args.timeout, 
                    poll_interval=args.poll_interval
                )
                if success:
                    print("Sync completed successfully.")
                    sys.exit(0)
                else:
                    print("Sync failed.")
                    sys.exit(1)
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
