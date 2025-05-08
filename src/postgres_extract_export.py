#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import json
import uuid

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("Warning: psycopg2 not available, mock mode will be used for all queries")

logger = logging.getLogger(__name__)

# Default values
DEFAULT_TABLE = "klaviyo_campaigns"
DEFAULT_DATE_COLUMN = "created_at"
DEFAULT_LIMIT = 5
DEFAULT_OUTPUT_DIR = "data"

# Sample mock data for dry-run testing
def generate_mock_data(start_date=None, end_date=None, num_records=10):
    """Generate mock data for dry-run testing."""
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime.now() - timedelta(days=30)
    
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = datetime.now()
    
    # Calculate date range
    date_range = (end - start).days
    if date_range <= 0:
        date_range = 1
    
    # Campaign mock data
    if DEFAULT_TABLE == "klaviyo_campaigns" or "campaign" in DEFAULT_TABLE:
        return generate_mock_campaigns(start, end, num_records)
    
    # Event mock data
    elif "event" in DEFAULT_TABLE:
        return generate_mock_events(start, end, num_records)
    
    # List mock data
    elif "list" in DEFAULT_TABLE:
        return generate_mock_lists(start, end, num_records)
    
    # Generic mock data
    else:
        return generate_generic_mock_data(start, end, num_records)
    
def generate_mock_campaigns(start, end, num_records=8):
    """Generate mock campaign data."""
    campaign_names = [
        "Spring Sale Announcement",
        "New Collection Launch",
        "Limited Time Offer",
        "Weekly Newsletter",
        "Customer Appreciation",
        "Summer Clearance",
        "Product Spotlight",
        "Holiday Special"
    ]
    
    subjects = [
        "Don't Miss Out! 25% Off Everything",
        "New Arrivals Just Dropped",
        "48 Hours Only: BOGO Free",
        "This Week's Top Stories",
        "Thanks for Being a Loyal Customer",
        "Summer Items Up to 60% Off",
        "Featured Product of the Month",
        "Holiday Exclusive: Free Shipping"
    ]
    
    campaigns = []
    date_range = (end - start).days
    
    for i in range(min(num_records, len(campaign_names))):
        campaign_date = start + timedelta(days=(i * date_range // num_records))
        
        campaigns.append({
            "campaign_id": str(uuid.uuid4()),
            "campaign_name": campaign_names[i],
            "subject": subjects[i],
            "list_id": f"list_{(i % 3) + 1}",
            "created_at": campaign_date.strftime("%Y-%m-%d %H:%M:%S"),
            "sent_at": (campaign_date + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "sent"
        })
    
    return campaigns

def generate_mock_events(start, end, num_records=50):
    """Generate mock event data."""
    event_types = ["send", "open", "click", "bounce", "unsubscribe", "conversion"]
    event_weights = [0.5, 0.3, 0.1, 0.05, 0.03, 0.02]  # Probabilities
    
    campaign_ids = [str(uuid.uuid4()) for _ in range(5)]
    
    events = []
    date_range = (end - start).days
    
    for i in range(num_records):
        event_date = start + timedelta(days=(i * date_range // num_records), 
                                      hours=i % 24, 
                                      minutes=(i * 7) % 60)
        
        # Choose event type based on weights
        import random
        event_type = random.choices(event_types, weights=event_weights, k=1)[0]
        
        campaign_id = campaign_ids[i % len(campaign_ids)]
        revenue = 0
        if event_type == "conversion":
            revenue = round(random.uniform(25, 150), 2)
        
        events.append({
            "event_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "flow_id": None if i % 3 else str(uuid.uuid4()),
            "profile_id": f"profile_{(i % 100) + 1}",
            "event_type": event_type,
            "event_timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
            "revenue": revenue,
            "list_id": f"list_{(i % 3) + 1}"
        })
    
    return events

def generate_mock_lists(start, end, num_records=5):
    """Generate mock list data."""
    list_names = [
        "Newsletter Subscribers",
        "VIP Customers",
        "Abandoned Cart",
        "New Customers",
        "Inactive Customers"
    ]
    
    lists = []
    date_range = (end - start).days
    
    for i in range(min(num_records, len(list_names))):
        created_date = start + timedelta(days=(i * date_range // num_records))
        
        lists.append({
            "list_id": f"list_{i+1}",
            "list_name": list_names[i],
            "created_at": created_date.strftime("%Y-%m-%d %H:%M:%S"),
            "member_count": (i + 1) * 100 + 50,
            "active": True
        })
    
    return lists

def generate_generic_mock_data(start, end, num_records=10):
    """Generate generic mock data."""
    records = []
    date_range = (end - start).days
    
    for i in range(num_records):
        record_date = start + timedelta(days=(i * date_range // num_records))
        
        record = {
            "id": i+1,
            "name": f"Record {i+1}",
            "created_at": record_date.strftime("%Y-%m-%d %H:%M:%S"),
            "value": round((i+1) * 10.5, 2),
            "active": i % 2 == 0
        }
        
        records.append(record)
    
    return records

def get_connection():
    """Create a connection to the Postgres database using environment variables."""
    if not PSYCOPG2_AVAILABLE:
        logger.error("psycopg2 module not available")
        raise ImportError("psycopg2 module not available")
        
    try:
        return psycopg2.connect(
            host=os.environ["PG_HOST"],
            port=os.environ.get("PG_PORT", 5432),
            dbname=os.environ["PG_DB"],
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASSWORD"]
        )
    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}")
        raise
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to Postgres: {e}")
        raise


def build_query(table: str, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                date_column: str = DEFAULT_DATE_COLUMN, limit: Optional[int] = None) -> str:
    """Build a SQL query with optional date filters."""
    where_clauses = []
    
    if start_date:
        where_clauses.append(f"{date_column} >= '{start_date}'")
    
    if end_date:
        where_clauses.append(f"{date_column} <= '{end_date}'")
    
    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    limit_clause = f"LIMIT {limit}" if limit else ""
    order_clause = f"ORDER BY {date_column} ASC"
    
    return f"SELECT * FROM {table} {where_clause} {order_clause} {limit_clause};"


def build_last_n_days_query(table: str, days: int = 30, date_column: str = DEFAULT_DATE_COLUMN, 
                          limit: Optional[int] = None) -> str:
    """Build a SQL query to fetch data from the last N days."""
    where_clause = f"WHERE {date_column} >= CURRENT_DATE - INTERVAL '{days} days'"
    limit_clause = f"LIMIT {limit}" if limit else ""
    order_clause = f"ORDER BY {date_column} ASC"
    
    return f"SELECT * FROM {table} {where_clause} {order_clause} {limit_clause};"


def fetch_last_n_days(conn, table: str, days: int = 30, date_column: str = DEFAULT_DATE_COLUMN, 
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch data from the last N days as a fallback when date filters return no results."""
    query = build_last_n_days_query(table, days, date_column, limit)
    logger.info(f"Fetching data from last {days} days with query: {query}")
    return execute_query(conn, query)


def execute_query(conn, query: str) -> List[Dict[str, Any]]:
    """Execute a SQL query and return results as a list of dictionaries."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    except psycopg2.Error as e:
        logger.error(f"Query execution failed: {e}")
        raise


def write_to_csv(data: List[Dict[str, Any]], output_file: str) -> bool:
    """Write data to a CSV file."""
    if not data:
        logger.warning("No data to write to CSV")
        raise ValueError("Cannot write empty data to CSV")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Get all unique field names from the data
        fieldnames = set()
        for record in data:
            fieldnames.update(record.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        logger.info(f"Data written to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error writing to CSV: {e}")
        raise


def generate_output_filename(table: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Generate an output filename based on table name and date range."""
    today = datetime.now().strftime("%Y%m%d")
    
    if start_date and end_date:
        date_part = f"{start_date}_{end_date}"
    elif start_date:
        date_part = f"{start_date}_{today}"
    elif end_date:
        date_part = f"until_{end_date}"
    else:
        date_part = today
    
    return os.path.join(DEFAULT_OUTPUT_DIR, f"{table}_export_{date_part}.csv")


def fetch_to_dataframe(table: str = DEFAULT_TABLE, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None,
                     date_column: str = DEFAULT_DATE_COLUMN,
                     limit: Optional[int] = None,
                     dry_run: bool = False,
                     fallback_days: int = 30) -> List[Dict[str, Any]]:
    """Fetch data from Postgres and return as a list of dictionaries.
    
    This function can be imported and called directly from other modules.
    
    Args:
        table: Table name to query
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        date_column: Column name to use for date filtering
        limit: Maximum number of rows to return
        dry_run: If True, print query but don't execute it
        fallback_days: Number of days to use for fallback query if no results
        
    Returns:
        List of dictionaries representing the query results
    """
    # In dry-run mode, return mock data instead of connecting to the database
    if dry_run:
        logger.info(f"DRY RUN: Using mock data for {table}")
        mock_data = generate_mock_data(start_date, end_date)
        logger.info(f"Generated {len(mock_data)} mock records")
        
        # Print a sample of the mock data
        if mock_data:
            sample_size = min(3, len(mock_data))
            logger.info(f"Sample mock data (showing {sample_size} of {len(mock_data)} records):")
            for i in range(sample_size):
                logger.info(f"Record {i+1}: {json.dumps(dict(mock_data[i]), indent=2)}")
        
        return mock_data
    
    # For real database connections
    try:
        # Build the query
        query = build_query(table, start_date, end_date, date_column, limit)
        
        # Connect to the database and execute the query
        with get_connection() as conn:
            results = execute_query(conn, query)
            
            # If no results, try fallback to last N days
            if not results:
                logger.warning(f"⚠️  Extract returned 0 rows – falling back to last {fallback_days} days")
                results = fetch_last_n_days(conn, table, fallback_days, date_column, limit)
                if results:
                    logger.info(f"Fallback query returned {len(results)} rows")
                else:
                    logger.warning(f"Fallback query also returned 0 rows")
        
        logger.info(f"Fetched {len(results)} rows from {table}")
        return results
    
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        # In case of error, return mock data if psycopg2 is not available
        if not PSYCOPG2_AVAILABLE:
            logger.warning("Using mock data as fallback since psycopg2 is not available")
            return generate_mock_data(start_date, end_date)
        raise


def fetch_and_export_to_csv(table: str = DEFAULT_TABLE,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         date_column: str = DEFAULT_DATE_COLUMN,
                         output_file: Optional[str] = None,
                         dry_run: bool = False,
                         fallback_days: int = 30) -> str:
    """Fetch data from Postgres and export to CSV.
    
    This function can be imported and called directly from other modules.
    
    Args:
        table: Table name to query
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        date_column: Column name to use for date filtering
        output_file: Path to output file. If None, a default path is generated
        dry_run: If True, don't actually write to file
        fallback_days: Number of days to use for fallback query if no results
        
    Returns:
        Path to the output CSV file
    """
    # Fetch data with fallback for empty results
    results = fetch_to_dataframe(table, start_date, end_date, date_column, dry_run=dry_run, fallback_days=fallback_days)
    
    if not results:
        if dry_run:
            logger.warning("Mock data generation returned no results")
            return None
        else:
            logger.warning("Both primary and fallback queries returned no results")
            raise ValueError("Both primary and fallback queries returned no results")
    
    # Generate output filename if not provided
    if not output_file:
        output_file = generate_output_filename(table, start_date, end_date)
    
    # In dry-run mode, just return the output path
    if dry_run:
        logger.info(f"DRY RUN: Would write {len(results)} rows to {output_file}")
        return output_file
    
    # Write to CSV
    write_to_csv(results, output_file)
    logger.info(f"Exported {len(results)} rows to {output_file}")
    
    return output_file


def main(argv=None):
    """Main function to extract data from Postgres and export to CSV."""
    parser = argparse.ArgumentParser(description="Extract data from Postgres and export to CSV")
    parser.add_argument("--table", default=DEFAULT_TABLE, help=f"Table name (default: {DEFAULT_TABLE})")
    parser.add_argument("--start", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end", help="End date in YYYY-MM-DD format")
    parser.add_argument("--date-column", default=DEFAULT_DATE_COLUMN, 
                        help=f"Date column for filtering (default: {DEFAULT_DATE_COLUMN})")
    parser.add_argument("--limit", type=int, help="Limit the number of rows returned")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Print sample rows without writing to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--fallback-days", type=int, default=30, 
                        help="Number of days to use for fallback query if no results (default: 30)")
    
    args = parser.parse_args(argv)
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    try:
        # Fetch data with fallback for empty results
        results = fetch_to_dataframe(
            args.table, 
            args.start, 
            args.end, 
            args.date_column, 
            args.limit if args.dry_run else None,
            args.dry_run,
            args.fallback_days
        )
        
        if not results:
            logger.warning("Both primary and fallback queries returned no results")
            print("Both primary and fallback queries returned no results")
            return 1
        
        # In dry-run mode, print sample rows and exit
        if args.dry_run:
            limit = args.limit or DEFAULT_LIMIT
            print(f"Sample of {min(limit, len(results))} rows from {len(results)} total:")
            for i, row in enumerate(results[:limit]):
                print(f"\nRow {i+1}:")
                for key, value in row.items():
                    print(f"  {key}: {value}")
            return 0
        
        # Generate output filename and write to CSV
        output_file = args.output or generate_output_filename(args.table, args.start, args.end)
        write_to_csv(results, output_file)
        print(f"Exported {len(results)} rows to {output_file}")
        return 0
    
    except KeyError as e:
        if args.dry_run and "PG_" in str(e):
            # In dry-run mode, missing Postgres environment variables are not fatal
            logger.warning(f"Environment variable {e} missing, but using dry-run mode with mock data")
            print(f"Warning: Missing environment variable {e}, but continuing with mock data")
            results = generate_mock_data(args.start, args.end)
            print(f"Generated {len(results)} mock records")
            return 0
        else:
            logger.error(f"Environment variable error: {e}")
            print(f"Error: Missing environment variable {e}")
            return 1
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        print(f"Database error: {e}")
        return 1
    except ImportError as e:
        if args.dry_run:
            logger.warning(f"Import error: {e}, but using dry-run mode with mock data")
            print(f"Warning: {e}, but continuing with mock data")
            results = generate_mock_data(args.start, args.end)
            print(f"Generated {len(results)} mock records")
            return 0
        else:
            logger.error(f"Import error: {e}")
            print(f"Error: {e}")
            return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
