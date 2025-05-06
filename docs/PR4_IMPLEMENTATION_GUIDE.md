# PR 4: Test Visualization Stub - Implementation Guide

This guide provides detailed instructions for creating the `test_visualization_stub.json` file as part of PR 4 in the Narrow Scope POC PR Plan.

## Overview

The `test_visualization_stub.json` file is a sample Looker Studio JSON configuration that references the mock data fields. It should:

1. Define one line chart (open rate over time)
2. Define one bar chart (click rate by campaign)
3. Include comments explaining field requirements and naming assumptions
4. Be formatted correctly for reference during Looker Studio setup

## Implementation Steps

### 1. Create the Directory Structure

Create the `config` directory if it doesn't exist:

```bash
mkdir -p config
```

### 2. Create the Visualization Stub

Create a new file at `config/test_visualization_stub.json` with the following content:

```json
{
  "_comment": "This is a reference configuration for Looker Studio visualizations. It is not directly imported but serves as a guide for manual setup.",
  "dataSource": {
    "name": "Klaviyo Campaign Metrics",
    "type": "FILE_UPLOAD",
    "fileType": "CSV",
    "filePath": "mock_looker_dataset.csv"
  },
  "fields": {
    "_comment": "These fields must match the column names in the CSV file. Field types are inferred by Looker Studio but can be manually set.",
    "date": {
      "type": "DATE",
      "description": "Campaign send date (YYYY-MM-DD)"
    },
    "campaign_name": {
      "type": "TEXT",
      "description": "Name of the email campaign"
    },
    "send_time": {
      "type": "DATETIME",
      "description": "Exact time the campaign was sent (ISO 8601)"
    },
    "open_rate": {
      "type": "NUMBER",
      "description": "Percentage of recipients who opened the email (decimal)"
    },
    "click_rate": {
      "type": "NUMBER",
      "description": "Percentage of recipients who clicked a link (decimal)"
    },
    "subject_line": {
      "type": "TEXT",
      "description": "Email subject line"
    },
    "list_id": {
      "type": "TEXT",
      "description": "ID of the recipient list"
    }
  },
  "charts": [
    {
      "_comment": "Line chart showing open rate trends over time",
      "type": "LINE",
      "title": "Open Rate Over Time",
      "dimensions": ["date"],
      "metrics": ["open_rate"],
      "settings": {
        "xAxis": {
          "label": "Date"
        },
        "yAxis": {
          "label": "Open Rate",
          "format": "PERCENT"
        },
        "legend": {
          "position": "TOP"
        },
        "lineStyles": [
          {
            "series": "open_rate",
            "color": "#4285F4",
            "lineWeight": 2,
            "pointRadius": 3
          }
        ]
      }
    },
    {
      "_comment": "Bar chart showing click rate by campaign",
      "type": "BAR",
      "title": "Click Rate by Campaign",
      "dimensions": ["campaign_name"],
      "metrics": ["click_rate"],
      "settings": {
        "xAxis": {
          "label": "Campaign"
        },
        "yAxis": {
          "label": "Click Rate",
          "format": "PERCENT"
        },
        "legend": {
          "position": "NONE"
        },
        "barStyles": [
          {
            "series": "click_rate",
            "color": "#34A853"
          }
        ],
        "orientation": "VERTICAL",
        "sortByMetric": true,
        "sortOrder": "DESCENDING"
      }
    }
  ],
  "filters": [
    {
      "_comment": "Date range filter for all charts",
      "type": "DATE_RANGE",
      "field": "date",
      "defaultValues": {
        "start": "2025-04-01",
        "end": "2025-06-30"
      }
    },
    {
      "_comment": "List filter to segment by recipient list",
      "type": "LIST",
      "field": "list_id",
      "allowMultiple": true
    }
  ],
  "layout": {
    "_comment": "This is a suggested layout for the dashboard",
    "sections": [
      {
        "title": "Campaign Performance Overview",
        "elements": [
          {
            "type": "FILTER_GROUP",
            "position": {
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 1
            }
          },
          {
            "type": "CHART",
            "chartIndex": 0,
            "position": {
              "x": 0,
              "y": 1,
              "width": 12,
              "height": 4
            }
          },
          {
            "type": "CHART",
            "chartIndex": 1,
            "position": {
              "x": 0,
              "y": 5,
              "width": 12,
              "height": 4
            }
          }
        ]
      }
    ]
  },
  "implementationNotes": {
    "_comment": "These notes provide guidance for implementing this configuration in Looker Studio",
    "steps": [
      "1. Create a new Looker Studio report",
      "2. Add a data source by uploading mock_looker_dataset.csv",
      "3. Verify field types match those specified in the 'fields' section",
      "4. Add a line chart for 'Open Rate Over Time' using date and open_rate",
      "5. Add a bar chart for 'Click Rate by Campaign' using campaign_name and click_rate",
      "6. Add date range and list_id filters",
      "7. Arrange the charts according to the layout section"
    ],
    "fieldRequirements": [
      "date: Must be in YYYY-MM-DD format",
      "open_rate: Must be a decimal (e.g., 0.42 for 42%)",
      "click_rate: Must be a decimal (e.g., 0.18 for 18%)",
      "campaign_name: Should be unique and descriptive",
      "list_id: Used for filtering, should be consistent across related campaigns"
    ]
  }
}
```

### 3. Create Documentation

Create a new file at `config/README.md` with the following content:

```markdown
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
```

## Validation Steps

### For Developers

1. Create the `config` directory if it doesn't exist:
   ```bash
   mkdir -p config
   ```

2. Create the `test_visualization_stub.json` file as described above.

3. Create the documentation in `config/README.md` as described above.

4. Verify that the JSON file is valid:
   ```bash
   python -c "import json; json.load(open('config/test_visualization_stub.json'))"
   ```

### For Reviewers

1. Verify that the JSON file is valid and well-formatted.

2. Check that the configuration includes:
   - A line chart for open rate over time
   - A bar chart for click rate by campaign
   - Clear comments explaining field requirements and naming assumptions

3. Verify that the field names in the configuration match those in the mock dataset:
   - `date`
   - `campaign_name`
   - `send_time`
   - `open_rate`
   - `click_rate`
   - `subject_line`
   - `list_id`

4. Check that the documentation in `config/README.md` is clear and complete.

5. (Optional) Follow the implementation steps in the documentation to create a Looker Studio dashboard using the mock dataset and verify that it works as expected.

## Next Steps

After implementing and validating PR 4, proceed to PR 5: ETL Runner.
