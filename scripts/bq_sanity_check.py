#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

import dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Global args variable for easier testing
args = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BigQuery table sanity check")
    parser.add_argument(
        "--env", 
        help="Path to .env file",
        default=".env"
    )
    parser.add_argument(
        "--tables", 
        help="Comma-separated list of tables to check",
        default=""
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Print queries without executing them"
    )
    return parser.parse_args()


def load_env(env_path: str) -> None:
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)
    else:
        print(f"Warning: Environment file {env_path} not found")


def get_table_list() -> List[str]:
    tables_env = os.getenv("TABLE_LIST", "")
    if args and args.tables:
        return args.tables.split(",")
    elif tables_env:
        return tables_env.split(",")
    return ["campaign", "event", "list"]


def check_table(client: bigquery.Client, project_id: str, dataset_id: str, 
               table_id: str, dry_run: bool = False) -> Dict[str, Any]:
    full_table_id = f"{project_id}.{dataset_id}.{table_id}"
    result = {
        "table": table_id,
        "full_id": full_table_id,
        "exists": False,
        "row_count": 0,
        "latest_updated": None,
        "error": None
    }
    
    try:
        # Check if table exists
        if dry_run:
            print(f"[DRY RUN] Would check if table {full_table_id} exists")
            result["exists"] = True
            result["row_count"] = 100  # Fake count for dry run
            result["latest_updated"] = datetime.now().isoformat()
            return result
            
        # Get table to check if it exists
        table = client.get_table(full_table_id)
        result["exists"] = True
        
        # Count rows
        count_query = f"SELECT COUNT(*) as count FROM `{full_table_id}`"
        count_job = client.query(count_query)
        count_rows = list(count_job.result())
        if count_rows:
            result["row_count"] = count_rows[0].count
        
        # Check for updated_at column and get latest
        has_updated_at = any(field.name == "updated_at" for field in table.schema)
        
        if has_updated_at:
            latest_query = f"SELECT MAX(updated_at) as latest FROM `{full_table_id}`"
            latest_job = client.query(latest_query)
            latest_rows = list(latest_job.result())
            if latest_rows and latest_rows[0].latest:
                result["latest_updated"] = latest_rows[0].latest.isoformat()
    
    except NotFound:
        result["error"] = f"Table {full_table_id} not found"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def print_results(results: List[Dict[str, Any]]) -> None:
    print("\nBigQuery Sanity Check Results:")
    print("-" * 80)
    print(f"{'Table':<20} {'Exists':<10} {'Row Count':<15} {'Latest Updated':<30}")
    print("-" * 80)
    
    for result in results:
        exists = "✓" if result["exists"] else "✗"
        row_count = str(result["row_count"]) if result["exists"] else "N/A"
        latest = result["latest_updated"] or "N/A"
        print(f"{result['table']:<20} {exists:<10} {row_count:<15} {latest:<30}")
    
    print("-" * 80)
    
    # Print errors
    errors = [r for r in results if r["error"]]
    if errors:
        print("\nErrors:")
        for result in errors:
            print(f"  • {result['table']}: {result['error']}")


def check_for_issues(results: List[Dict[str, Any]]) -> bool:
    missing_tables = [r for r in results if not r["exists"]]
    empty_tables = [r for r in results if r["exists"] and r["row_count"] == 0]
    
    if missing_tables or empty_tables:
        print("\nIssues found:")
        
        if missing_tables:
            print("\nMissing tables:")
            for table in missing_tables:
                print(f"  • {table['full_id']}")
        
        if empty_tables:
            print("\nEmpty tables:")
            for table in empty_tables:
                print(f"  • {table['full_id']}")
        
        return True
    
    print("\nAll tables exist and contain data. ✓")
    return False


def main() -> int:
    global args
    project_id = os.getenv("BQ_PROJECT")
    dataset_id = os.getenv("BQ_DATASET")
    
    if not project_id or not dataset_id:
        print("Error: BQ_PROJECT and BQ_DATASET environment variables must be set")
        return 1
    
    print(f"Checking BigQuery tables in {project_id}.{dataset_id}")
    
    tables = get_table_list()
    if not tables:
        print("Error: No tables specified. Use --tables or set TABLE_LIST env var")
        return 1
    
    print(f"Tables to check: {', '.join(tables)}")
    
    dry_run = args.dry_run if args else False
    if dry_run:
        print("\n*** DRY RUN MODE - No queries will be executed ***\n")
        client = None
    else:
        client = bigquery.Client()
    
    results = []
    for table in tables:
        result = check_table(client, project_id, dataset_id, table, dry_run)
        results.append(result)
    
    print_results(results)
    
    has_issues = check_for_issues(results)
    return 1 if has_issues else 0


if __name__ == "__main__":
    args = parse_args()
    load_env(args.env)
    sys.exit(main())
