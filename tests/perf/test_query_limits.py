import os
import sys
import time
import csv
import pytest
import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.klaviyo_api_ingest import fetch_campaign_metrics
from src.supermetrics_klaviyo_pull import fetch_data

# Mark all tests in this file with the 'perf' marker
pytest.mark.perf = pytest.mark.perf

# Define test date ranges
TEST_RANGES = [
    ("1-day", 1),
    ("7-day", 7),
    ("30-day", 30)
]

# Output file for performance results
RESULTS_FILE = "perf_results.csv"


def setup_module(module):
    """Setup for the performance tests module"""
    # Create results file with headers if it doesn't exist
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "query_type", "date_range", "rows", "seconds", "success"])


def write_result(query_type, date_range, rows, seconds, success):
    """Write a test result to the CSV file"""
    timestamp = datetime.datetime.now().isoformat()
    with open(RESULTS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, query_type, date_range, rows, f"{seconds:.2f}", success])


@pytest.mark.perf
@pytest.mark.parametrize("range_name,days", TEST_RANGES)
def test_klaviyo_api_performance(range_name, days):
    """Test Klaviyo API fetch performance for different date ranges"""
    # Calculate date range
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Measure performance
    start_time = time.time()
    success = True
    rows = 0
    
    try:
        # Use dry_run=True to avoid actual API calls in test environment
        results = fetch_campaign_metrics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            dry_run=True
        )
        rows = len(results) if results else 0
    except Exception as e:
        print(f"Error in Klaviyo API test ({range_name}): {e}")
        success = False
    
    elapsed = time.time() - start_time
    
    # Write results
    write_result("klaviyo_api", range_name, rows, elapsed, success)
    
    # Assert performance thresholds
    if range_name == "1-day":
        assert elapsed < 60, f"1-day query took {elapsed:.2f}s, should be under 60s"
    elif range_name == "7-day":
        assert elapsed < 300, f"7-day query took {elapsed:.2f}s, should be under 300s"


@pytest.mark.perf
@pytest.mark.parametrize("range_name,days", TEST_RANGES)
def test_supermetrics_performance(range_name, days):
    """Test Supermetrics API fetch performance for different date ranges"""
    # Calculate date range
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Measure performance
    start_time = time.time()
    success = True
    rows = 0
    
    try:
        # Use dry_run=True to avoid actual API calls in test environment
        results = fetch_data(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            report_type="campaign",
            dry_run=True
        )
        rows = len(results) if results else 0
    except Exception as e:
        print(f"Error in Supermetrics test ({range_name}): {e}")
        success = False
    
    elapsed = time.time() - start_time
    
    # Write results
    write_result("supermetrics", range_name, rows, elapsed, success)
    
    # Assert performance thresholds
    if range_name == "1-day":
        assert elapsed < 60, f"1-day query took {elapsed:.2f}s, should be under 60s"
    elif range_name == "7-day":
        assert elapsed < 300, f"7-day query took {elapsed:.2f}s, should be under 300s"


@pytest.mark.perf
def test_combined_etl_performance():
    """Test the full ETL pipeline performance"""
    from src.etl_runner import run_etl
    
    # Measure performance
    start_time = time.time()
    success = True
    rows = 0
    
    try:
        # Use dry_run=True to avoid actual operations
        result = run_etl(dry_run=True)
        rows = result.get("rows_processed", 0) if result else 0
    except Exception as e:
        print(f"Error in ETL pipeline test: {e}")
        success = False
    
    elapsed = time.time() - start_time
    
    # Write results
    write_result("full_etl", "default", rows, elapsed, success)
    
    # Assert performance threshold for full ETL
    assert elapsed < 600, f"Full ETL took {elapsed:.2f}s, should be under 600s"


@pytest.mark.perf
def test_generate_summary():
    """Generate a summary of performance test results"""
    if not os.path.exists(RESULTS_FILE):
        pytest.skip(f"Results file {RESULTS_FILE} not found")
    
    # Read results
    results = []
    with open(RESULTS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    # Group by query type and date range
    summary = {}
    for result in results:
        key = (result["query_type"], result["date_range"])
        if key not in summary:
            summary[key] = {
                "count": 0,
                "success_count": 0,
                "total_time": 0,
                "avg_rows": 0,
                "max_time": 0,
                "min_time": float('inf')
            }
        
        s = summary[key]
        s["count"] += 1
        if result["success"] == "True":
            s["success_count"] += 1
        
        time_val = float(result["seconds"])
        rows_val = int(result["rows"]) if result["rows"].isdigit() else 0
        
        s["total_time"] += time_val
        s["avg_rows"] = ((s["avg_rows"] * (s["count"] - 1)) + rows_val) / s["count"]
        s["max_time"] = max(s["max_time"], time_val)
        s["min_time"] = min(s["min_time"], time_val)
    
    # Write summary to CSV
    summary_file = "perf_summary.csv"
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["query_type", "date_range", "runs", "success_rate", "avg_time", "min_time", "max_time", "avg_rows"])
        
        for (query_type, date_range), s in summary.items():
            success_rate = (s["success_count"] / s["count"]) * 100 if s["count"] > 0 else 0
            avg_time = s["total_time"] / s["count"] if s["count"] > 0 else 0
            
            writer.writerow([
                query_type,
                date_range,
                s["count"],
                f"{success_rate:.1f}%",
                f"{avg_time:.2f}",
                f"{s['min_time']:.2f}",
                f"{s['max_time']:.2f}",
                f"{s['avg_rows']:.1f}"
            ])
    
    print(f"Performance summary written to {summary_file}")
    return True
