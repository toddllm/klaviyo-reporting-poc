import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.postgres_extract_export import (
    build_query,
    generate_output_filename,
    write_to_csv,
    main
)


def test_build_query_no_filters():
    """Test building a query with no filters."""
    query = build_query("test_table")
    assert query == "SELECT * FROM test_table  ORDER BY created_at ASC ;"


def test_build_query_with_start_date():
    """Test building a query with a start date filter."""
    query = build_query("test_table", start_date="2023-01-01")
    assert query == "SELECT * FROM test_table WHERE created_at >= '2023-01-01' ORDER BY created_at ASC ;"


def test_build_query_with_end_date():
    """Test building a query with an end date filter."""
    query = build_query("test_table", end_date="2023-12-31")
    assert query == "SELECT * FROM test_table WHERE created_at <= '2023-12-31' ORDER BY created_at ASC ;"


def test_build_query_with_date_range():
    """Test building a query with both start and end date filters."""
    query = build_query("test_table", start_date="2023-01-01", end_date="2023-12-31")
    assert query == "SELECT * FROM test_table WHERE created_at >= '2023-01-01' AND created_at <= '2023-12-31' ORDER BY created_at ASC ;"


def test_build_query_with_custom_date_column():
    """Test building a query with a custom date column."""
    query = build_query("test_table", start_date="2023-01-01", date_column="updated_at")
    assert query == "SELECT * FROM test_table WHERE updated_at >= '2023-01-01' ORDER BY updated_at ASC ;"


def test_build_query_with_limit():
    """Test building a query with a limit."""
    query = build_query("test_table", limit=10)
    assert query == "SELECT * FROM test_table  ORDER BY created_at ASC LIMIT 10;"


def test_generate_output_filename_no_dates():
    """Test generating an output filename with no dates."""
    today = datetime.now().strftime("%Y%m%d")
    filename = generate_output_filename("test_table")
    assert filename == f"data/test_table_export_{today}.csv"


def test_generate_output_filename_with_start_date():
    """Test generating an output filename with a start date."""
    today = datetime.now().strftime("%Y%m%d")
    filename = generate_output_filename("test_table", start_date="2023-01-01")
    assert filename == f"data/test_table_export_2023-01-01_{today}.csv"


def test_generate_output_filename_with_end_date():
    """Test generating an output filename with an end date."""
    filename = generate_output_filename("test_table", end_date="2023-12-31")
    assert filename == "data/test_table_export_until_2023-12-31.csv"


def test_generate_output_filename_with_date_range():
    """Test generating an output filename with both start and end dates."""
    filename = generate_output_filename("test_table", start_date="2023-01-01", end_date="2023-12-31")
    assert filename == "data/test_table_export_2023-01-01_2023-12-31.csv"


def test_write_to_csv_empty_data():
    """Test writing empty data to CSV."""
    with pytest.raises(ValueError, match="Cannot write empty data to CSV"):
        write_to_csv([], "test_output.csv")


@patch("src.postgres_extract_export.get_connection")
@patch("src.postgres_extract_export.execute_query")
@patch("src.postgres_extract_export.write_to_csv")
@patch("src.postgres_extract_export.argparse.ArgumentParser.parse_args")
def test_main_success(mock_parse_args, mock_write_to_csv, mock_execute_query, mock_get_connection):
    """Test successful execution of the main function."""
    # Mock the connection and cursor
    mock_conn = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_conn
    
    # Mock the query results
    mock_execute_query.return_value = [
        {"id": "1", "name": "Test 1", "created_at": "2023-01-01"},
        {"id": "2", "name": "Test 2", "created_at": "2023-02-01"}
    ]
    
    # Mock the arguments
    mock_args = MagicMock()
    mock_args.table = "test_table"
    mock_args.start = None
    mock_args.end = None
    mock_args.date_column = "created_at"
    mock_args.limit = None
    mock_args.dry_run = False
    mock_args.verbose = False
    mock_parse_args.return_value = mock_args
    
    # Mock the CSV writing
    mock_write_to_csv.return_value = True
    
    # Set environment variables
    os.environ["PG_HOST"] = "localhost"
    os.environ["PG_PORT"] = "5432"
    os.environ["PG_DB"] = "postgres"
    os.environ["PG_USER"] = "postgres"
    os.environ["PG_PASSWORD"] = "postgres"
    
    # Run the main function
    result = main()
    
    # Check that the function returned success
    assert result == 0
    
    # Check that the query was executed
    mock_execute_query.assert_called_once()
    
    # Check that the CSV was written
    mock_write_to_csv.assert_called_once()


@patch("src.postgres_extract_export.get_connection")
@patch("src.postgres_extract_export.execute_query")
@patch("src.postgres_extract_export.fetch_last_n_days")
@patch("src.postgres_extract_export.fetch_to_dataframe")
@patch("src.postgres_extract_export.argparse.ArgumentParser.parse_args")
def test_main_dry_run(mock_parse_args, mock_fetch_to_dataframe, mock_fetch_last_n_days, mock_execute_query, mock_get_connection):
    """Test dry-run mode of the main function."""
    # Mock the connection and cursor
    mock_conn = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_conn
    
    # Mock the fetch_to_dataframe to return data
    mock_fetch_to_dataframe.return_value = [
        {"id": "1", "name": "Test 1", "created_at": "2023-01-01"},
        {"id": "2", "name": "Test 2", "created_at": "2023-02-01"}
    ]
    
    # Mock the arguments
    mock_args = MagicMock()
    mock_args.table = "test_table"
    mock_args.start = None
    mock_args.end = None
    mock_args.date_column = "created_at"
    mock_args.limit = 5
    mock_args.dry_run = True
    mock_args.verbose = False
    mock_args.fallback_days = 30
    mock_parse_args.return_value = mock_args
    
    # Set environment variables
    os.environ["PG_HOST"] = "localhost"
    os.environ["PG_PORT"] = "5432"
    os.environ["PG_DB"] = "postgres"
    os.environ["PG_USER"] = "postgres"
    os.environ["PG_PASSWORD"] = "postgres"
    
    # Run the main function
    with patch("builtins.print") as mock_print:
        result = main()
    
    # Check that the function returned success
    assert result == 0
    
    # Check that fetch_to_dataframe was called
    mock_fetch_to_dataframe.assert_called_once()
    
    # Check that print was called with sample rows
    mock_print.assert_any_call("Sample of 2 rows from 2 total:")


@patch("src.postgres_extract_export.get_connection")
@patch("src.postgres_extract_export.argparse.ArgumentParser.parse_args")
def test_main_connection_error(mock_parse_args, mock_get_connection):
    """Test handling of connection errors."""
    # Mock the connection to raise an error
    mock_get_connection.side_effect = Exception("Connection error")
    
    # Mock the arguments
    mock_args = MagicMock()
    mock_args.table = "test_table"
    mock_args.start = None
    mock_args.end = None
    mock_args.date_column = "created_at"
    mock_args.limit = None
    mock_args.dry_run = False
    mock_args.verbose = False
    mock_parse_args.return_value = mock_args
    
    # Set environment variables
    os.environ["PG_HOST"] = "localhost"
    os.environ["PG_PORT"] = "5432"
    os.environ["PG_DB"] = "postgres"
    os.environ["PG_USER"] = "postgres"
    os.environ["PG_PASSWORD"] = "postgres"
    
    # Run the main function
    with patch("builtins.print") as mock_print:
        result = main()
    
    # Check that the function returned an error
    assert result == 1
    
    # Check that an error message was printed
    mock_print.assert_any_call("Error: Connection error")


@patch("src.postgres_extract_export.get_connection")
@patch("src.postgres_extract_export.execute_query")
@patch("src.postgres_extract_export.fetch_last_n_days")
@patch("src.postgres_extract_export.argparse.ArgumentParser.parse_args")
def test_main_no_results(mock_parse_args, mock_fetch_last_n_days, mock_execute_query, mock_get_connection):
    """Test handling of queries with no results."""
    # Mock the connection and cursor
    mock_conn = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_conn
    
    # Mock both queries to return no results
    mock_execute_query.return_value = []
    mock_fetch_last_n_days.return_value = []
    
    # Mock the arguments
    mock_args = MagicMock()
    mock_args.table = "test_table"
    mock_args.start = None
    mock_args.end = None
    mock_args.date_column = "created_at"
    mock_args.limit = None
    mock_args.dry_run = False
    mock_args.verbose = False
    mock_args.fallback_days = 30
    mock_parse_args.return_value = mock_args
    
    # Set environment variables
    os.environ["PG_HOST"] = "localhost"
    os.environ["PG_PORT"] = "5432"
    os.environ["PG_DB"] = "postgres"
    os.environ["PG_USER"] = "postgres"
    os.environ["PG_PASSWORD"] = "postgres"
    
    # Run the main function
    with patch("builtins.print") as mock_print:
        result = main()
    
    # Check that the function returned an error
    assert result == 1
    
    # Check that an error message was printed
    mock_print.assert_any_call("Both primary and fallback queries returned no results")
