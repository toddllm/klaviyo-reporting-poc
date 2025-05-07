#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Default values
DEFAULT_TABLE = "klaviyo_campaigns"
DEFAULT_DATE_COLUMN = "created_at"
DEFAULT_LIMIT = 5
DEFAULT_OUTPUT_DIR = "data"


def get_connection():
    """Create a connection to the Postgres database using environment variables."""
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
    try:
        # Build the query
        query = build_query(table, start_date, end_date, date_column, limit)
        
        if dry_run:
            logger.info(f"DRY RUN: Would execute query: {query}")
            return []
        
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
    
    if not results and not dry_run:
        logger.warning("Both primary and fallback queries returned no results")
        raise ValueError("Both primary and fallback queries returned no results")
    
    # Generate output filename if not provided
    if not output_file:
        output_file = generate_output_filename(table, start_date, end_date)
    
    # In dry-run mode, just return the output path
    if dry_run:
        logger.info(f"DRY RUN: Would write {len(results) if results else 0} rows to {output_file}")
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
        logger.error(f"Environment variable error: {e}")
        print(f"Error: Missing environment variable {e}")
        return 1
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        print(f"Database error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
