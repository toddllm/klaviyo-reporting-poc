import os
import sys
import time
import logging
import argparse
from typing import Optional

try:
    # When imported as a module
    from src.fivetran_api_client import get_client_from_env
except ImportError:
    # When run directly
    from fivetran_api_client import get_client_from_env

logger = logging.getLogger(__name__)

def run_connector(group_id: str, connector_id: str, timeout: int = 3600, 
                 poll_interval: int = 30, dry_run: bool = False) -> bool:
    """Trigger a sync for a connector and wait for it to complete.
    
    Args:
        group_id: The Fivetran group ID
        connector_id: The Fivetran connector ID
        timeout: Maximum time to wait in seconds (default: 1 hour)
        poll_interval: Time between status checks in seconds (default: 30 seconds)
        dry_run: If True, don't actually trigger the sync (for testing)
        
    Returns:
        True if sync completed successfully, False otherwise
    """
    if dry_run:
        message = f"DRY RUN: Would trigger sync for connector {connector_id} in group {group_id}"
        logger.info(message)
        print(message)
        return True
    
    try:
        client = get_client_from_env()
        
        # Verify the connector exists in the specified group
        connectors = client.get_connectors(group_id)
        connector_found = False
        
        for connector in connectors:
            if connector['id'] == connector_id:
                connector_found = True
                logger.info(f"Found connector {connector_id} in group {group_id}")
                break
        
        if not connector_found:
            logger.error(f"Connector {connector_id} not found in group {group_id}")
            return False
        
        # Trigger the sync
        logger.info(f"Triggering sync for connector {connector_id}")
        client.trigger_sync(connector_id)
        
        # Wait for completion
        logger.info(f"Waiting for sync to complete (timeout: {timeout}s, poll: {poll_interval}s)")
        return client.wait_for_sync_completion(
            connector_id, 
            timeout=timeout, 
            poll_interval=poll_interval
        )
    
    except Exception as e:
        logger.error(f"Error running connector: {e}")
        return False

def main():
    print("Starting Fivetran Connector Runner")
    parser = argparse.ArgumentParser(description="Fivetran Connector Runner")
    parser.add_argument("--group", required=True, help="Fivetran group ID")
    parser.add_argument("--connector", required=True, help="Fivetran connector ID")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds (default: 3600)")
    parser.add_argument("--poll-interval", type=int, default=30, 
                        help="Poll interval in seconds (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually trigger the sync")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", force=True)
    
    # Run the connector
    success = run_connector(
        args.group,
        args.connector,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
        dry_run=args.dry_run
    )
    
    # Exit with appropriate status code
    if success:
        message = "Connector sync completed successfully"
        logger.info(message)
        print(message)
        sys.exit(0)
    else:
        message = "Connector sync failed"
        logger.error(message)
        print(message)
        sys.exit(1)

if __name__ == "__main__":
    main()
