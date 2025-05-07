import os
import csv
import pytest
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any

import psycopg2
from psycopg2.extras import RealDictCursor

# Test configuration
PG_TEST_HOST = "localhost"
PG_TEST_PORT = 5432
PG_TEST_DB = "postgres"
PG_TEST_USER = "postgres"
PG_TEST_PASSWORD = "postgres"
TEST_TABLE = "klaviyo_campaigns_test"

# Sample test data
TEST_DATA = [
    {
        "id": "campaign1",
        "name": "Test Campaign 1",
        "created_at": "2023-01-01",
        "updated_at": "2023-01-02",
        "status": "sent",
        "metrics": {"opens": 100, "clicks": 50}
    },
    {
        "id": "campaign2",
        "name": "Test Campaign 2",
        "created_at": "2023-02-01",
        "updated_at": "2023-02-02",
        "status": "sent",
        "metrics": {"opens": 200, "clicks": 75}
    },
    {
        "id": "campaign3",
        "name": "Test Campaign 3",
        "created_at": "2023-03-01",
        "updated_at": "2023-03-02",
        "status": "draft",
        "metrics": {"opens": 0, "clicks": 0}
    },
]


@pytest.fixture(scope="module")
def postgres_connection():
    """Create a connection to the test Postgres database."""
    # Skip test if we're not in a Docker environment with Postgres
    if os.environ.get("SKIP_INTEGRATION_TESTS"):
        pytest.skip("Skipping integration tests")
    
    # Try to connect to the test database
    try:
        conn = psycopg2.connect(
            host=PG_TEST_HOST,
            port=PG_TEST_PORT,
            dbname=PG_TEST_DB,
            user=PG_TEST_USER,
            password=PG_TEST_PASSWORD
        )
        yield conn
        conn.close()
    except psycopg2.Error:
        pytest.skip("Postgres test database not available")


@pytest.fixture(scope="module")
def setup_test_table(postgres_connection):
    """Set up a test table with sample data."""
    conn = postgres_connection
    
    # Create test table
    with conn.cursor() as cursor:
        # Drop table if it exists
        cursor.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")
        
        # Create table
        cursor.execute(f"""
        CREATE TABLE {TEST_TABLE} (
            id TEXT PRIMARY KEY,
            name TEXT,
            created_at DATE,
            updated_at DATE,
            status TEXT,
            metrics JSONB
        )
        """)
        
        # Insert test data
        for item in TEST_DATA:
            cursor.execute(
                f"INSERT INTO {TEST_TABLE} (id, name, created_at, updated_at, status, metrics) "
                f"VALUES (%s, %s, %s, %s, %s, %s)",
                (item["id"], item["name"], item["created_at"], item["updated_at"], 
                 item["status"], psycopg2.extras.Json(item["metrics"]))
            )
    
    conn.commit()
    yield
    
    # Clean up
    with conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")
    conn.commit()


@pytest.fixture
def output_file():
    """Fixture to generate a temporary output file path and clean it up after the test."""
    today = datetime.now().strftime("%Y%m%d")
    output_path = f"data/{TEST_TABLE}_export_{today}.csv"
    
    yield output_path
    
    # Clean up the output file
    if os.path.exists(output_path):
        os.remove(output_path)


def test_dry_run(setup_test_table):
    """Test the dry-run mode of the script."""
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "PG_HOST": PG_TEST_HOST,
        "PG_PORT": str(PG_TEST_PORT),
        "PG_DB": PG_TEST_DB,
        "PG_USER": PG_TEST_USER,
        "PG_PASSWORD": PG_TEST_PASSWORD
    })
    
    # Run the script in dry-run mode
    result = subprocess.run(
        [
            "python", "src/postgres_extract_export.py",
            "--table", TEST_TABLE,
            "--limit", "2",
            "--dry-run"
        ],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Check that the script ran successfully
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    
    # Check that the output contains sample rows
    assert "Sample of 2 rows from 3 total:" in result.stdout
    assert "Test Campaign 1" in result.stdout
    assert "Test Campaign 2" in result.stdout
    
    # Check that no file was created
    assert not os.path.exists(f"data/{TEST_TABLE}_export_{datetime.now().strftime('%Y%m%d')}.csv")


def test_date_filtering(setup_test_table):
    """Test that date filtering works correctly."""
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "PG_HOST": PG_TEST_HOST,
        "PG_PORT": str(PG_TEST_PORT),
        "PG_DB": PG_TEST_DB,
        "PG_USER": PG_TEST_USER,
        "PG_PASSWORD": PG_TEST_PASSWORD
    })
    
    # Run the script with date filtering
    result = subprocess.run(
        [
            "python", "src/postgres_extract_export.py",
            "--table", TEST_TABLE,
            "--start", "2023-02-01",
            "--end", "2023-02-28",
            "--dry-run"
        ],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Check that the script ran successfully
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    
    # Check that only the expected campaign is included
    assert "Test Campaign 2" in result.stdout
    assert "Test Campaign 1" not in result.stdout
    assert "Test Campaign 3" not in result.stdout


def test_csv_export(setup_test_table, output_file):
    """Test that data is correctly exported to CSV."""
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "PG_HOST": PG_TEST_HOST,
        "PG_PORT": str(PG_TEST_PORT),
        "PG_DB": PG_TEST_DB,
        "PG_USER": PG_TEST_USER,
        "PG_PASSWORD": PG_TEST_PASSWORD
    })
    
    # Run the script to export all data
    result = subprocess.run(
        [
            "python", "src/postgres_extract_export.py",
            "--table", TEST_TABLE
        ],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Check that the script ran successfully
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    
    # Check that the output file exists
    today = datetime.now().strftime("%Y%m%d")
    csv_file = f"data/{TEST_TABLE}_export_{today}.csv"
    assert os.path.exists(csv_file), f"CSV file {csv_file} was not created"
    
    # Read the CSV file and check its contents
    with open(csv_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Check that all rows were exported
    assert len(rows) == len(TEST_DATA), f"Expected {len(TEST_DATA)} rows, got {len(rows)}"
    
    # Check that the data matches
    for i, row in enumerate(rows):
        assert row["id"] in [d["id"] for d in TEST_DATA]
        assert row["name"] in [d["name"] for d in TEST_DATA]


def test_custom_date_column(setup_test_table):
    """Test that the custom date column parameter works correctly."""
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "PG_HOST": PG_TEST_HOST,
        "PG_PORT": str(PG_TEST_PORT),
        "PG_DB": PG_TEST_DB,
        "PG_USER": PG_TEST_USER,
        "PG_PASSWORD": PG_TEST_PASSWORD
    })
    
    # Run the script with a custom date column
    result = subprocess.run(
        [
            "python", "src/postgres_extract_export.py",
            "--table", TEST_TABLE,
            "--start", "2023-01-02",  # This should match updated_at for campaign 1
            "--end", "2023-02-02",    # This should match updated_at for campaign 2
            "--date-column", "updated_at",
            "--dry-run"
        ],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Check that the script ran successfully
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    
    # Check that both campaigns are included based on updated_at
    assert "Test Campaign 1" in result.stdout
    assert "Test Campaign 2" in result.stdout
    assert "Test Campaign 3" not in result.stdout
