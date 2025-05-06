# Visualization Configuration

This directory contains configuration files for visualizing Klaviyo campaign metrics in Looker Studio.

## test_visualization_stub.json

This file provides a reference configuration for setting up visualizations in Looker Studio. It is not directly imported into Looker Studio but serves as a guide for manual setup.

### Purpose

The configuration defines:

1. A line chart showing open rate trends over time
2. A bar chart showing click rate by campaign
3. Filters for date range and list ID
4. A suggested layout for the dashboard

### Field Requirements

The configuration assumes the following fields are available in the data source:

- `date`: Campaign send date in YYYY-MM-DD format
- `campaign_name`: Name of the email campaign
- `send_time`: Exact time the campaign was sent in ISO 8601 format
- `open_rate`: Percentage of recipients who opened the email (as a decimal)
- `click_rate`: Percentage of recipients who clicked a link (as a decimal)
- `subject_line`: Email subject line
- `list_id`: ID of the recipient list

### Implementation Steps

1. Create a new Looker Studio report at [https://lookerstudio.google.com/](https://lookerstudio.google.com/)
2. Add a data source by uploading `mock_looker_dataset.csv` or connecting to the actual data source
3. Verify field types match those specified in the configuration
4. Add a line chart for "Open Rate Over Time" using `date` and `open_rate`
5. Add a bar chart for "Click Rate by Campaign" using `campaign_name` and `click_rate`
6. Add date range and `list_id` filters
7. Arrange the charts according to the layout section in the configuration

### Customization

The configuration can be customized to include additional charts or metrics as needed. Some suggestions:

- Add a table showing detailed campaign metrics
- Create a scatter plot comparing open rate and click rate
- Add a time series chart for revenue
- Create a pie chart showing campaign distribution by list

### Notes

- Looker Studio does not directly import JSON configuration files
- This file serves as a reference for manual setup
- Field names must match exactly between the data source and the configuration
- Date formats must be consistent for proper visualization
