import os
import sys
import pytest
from unittest.mock import patch, mock_open

# Add the parent directory to sys.path to import ai_insights
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_insights


def test_ai_summary():
    # Mock metrics data
    mock_metrics = {
        "date": "2025-05-02",
        "campaign_id": "test_campaign_123",
        "delivered": 100,
        "opened": 50,
        "clicked": 25,
        "revenue": 500.0
    }
    
    # Test the mock_insight function
    bullets = ai_insights.mock_insight(mock_metrics)
    
    # Assert that the bullets contain expected content
    assert any("Open rate" in bullet for bullet in bullets)
    assert any("Click rate" in bullet for bullet in bullets)
    assert any("Average revenue per recipient" in bullet for bullet in bullets)
    
    # Test HTML generation
    html_summary = ai_insights.generate_html_summary(bullets, mock_metrics)
    
    # Assert that the HTML contains the meta charset tag
    assert '<meta charset="utf-8">' in html_summary
    
    # Assert that the HTML contains the bullet points
    for bullet in bullets:
        assert bullet in html_summary


def test_load_metrics_from_csv():
    # Mock CSV data
    csv_data = "date,campaign_id,delivered,opened,clicked,revenue\n2025-05-02,test_campaign_123,100,50,25,500.0\n"
    
    # Mock the open function to return our test data
    with patch("builtins.open", mock_open(read_data=csv_data)):
        metrics = ai_insights.load_metrics_from_csv()
    
    # Assert that the metrics were loaded correctly
    assert metrics["date"] == "2025-05-02"
    assert metrics["campaign_id"] == "test_campaign_123"
    assert int(metrics["delivered"]) == 100
    assert int(metrics["opened"]) == 50
    assert int(metrics["clicked"]) == 25
    assert float(metrics["revenue"]) == 500.0


def test_main_function():
    # Mock metrics data
    mock_metrics = {
        "date": "2025-05-02",
        "campaign_id": "test_campaign_123",
        "delivered": 100,
        "opened": 50,
        "clicked": 25,
        "revenue": 500.0
    }
    
    # Mock the load_metrics_from_csv function to return our test data
    with patch("ai_insights.load_metrics_from_csv", return_value=mock_metrics):
        # Mock the open function for writing the HTML file
        with patch("builtins.open", mock_open()) as mock_file:
            # Mock print to avoid output during tests
            with patch("builtins.print"):
                # Run the main function
                ai_insights.main()
    
    # Assert that the HTML file was written
    mock_file.assert_called_with('summary.html', 'w')
