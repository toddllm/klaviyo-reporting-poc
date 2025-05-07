# Looker Studio + BigQuery Setup Guide

## Overview

This document provides step-by-step instructions for connecting Looker Studio to BigQuery to visualize Klaviyo campaign data. The integration allows you to create interactive dashboards and reports based on the data loaded into BigQuery by the ETL pipeline.

## Prerequisites

Before you begin, ensure you have:

1. Completed the Fivetran + BigQuery integration setup
2. Successfully loaded Klaviyo data into BigQuery using the `bq_loader.py` script
3. A Google account with access to Looker Studio and the BigQuery project
4. Appropriate permissions to create BigQuery connections in Looker Studio

## Step 1: Access Looker Studio

1. Open your web browser and navigate to [Looker Studio](https://lookerstudio.google.com/)
2. Sign in with your Google account
3. Click on "Create" and select "Report" to create a new report

## Step 2: Connect to BigQuery

1. In the "Add data to report" dialog, select "BigQuery" as the data source
2. Choose "Custom query" as the connection method
3. Select your project from the dropdown menu
4. Enter the following SQL query to retrieve campaign data:

```sql
SELECT 
  campaign_name,
  campaign_id,
  send_time,
  open_rate,
  click_rate,
  conversion_rate,
  revenue,
  unsubscribe_rate,
  bounce_rate,
  date
FROM 
  `[PROJECT_ID].klaviyo_raw.events_campaign`
WHERE
  date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()
ORDER BY 
  date DESC
```

5. Replace `[PROJECT_ID]` with your actual Google Cloud project ID
6. Click "Connect" to establish the connection

## Step 3: Create a Dashboard

### Key Metrics Scorecard

1. From the "Add a chart" menu, select "Scorecard"
2. Add the following metrics as separate scorecards:
   - Average Open Rate
   - Average Click Rate
   - Average Conversion Rate
   - Total Revenue

### Campaign Performance Table

1. From the "Add a chart" menu, select "Table"
2. Add the following dimensions and metrics:
   - Dimensions: campaign_name, send_time, date
   - Metrics: open_rate, click_rate, conversion_rate, revenue

### Time Series Charts

1. From the "Add a chart" menu, select "Time series chart"
2. Create the following time series charts:
   - Open Rate Over Time
   - Click Rate Over Time
   - Revenue Over Time

### Campaign Comparison Bar Chart

1. From the "Add a chart" menu, select "Bar chart"
2. Add campaign_name as the dimension
3. Add open_rate, click_rate, and conversion_rate as metrics

## Step 4: Add Filters

1. From the "Add a control" menu, select "Date range control"
2. Connect it to the date field in your data source
3. Add a "Drop-down list" control for campaign_name to filter by specific campaigns

## Step 5: Format and Customize

1. Add a title and description to your dashboard
2. Organize charts into logical sections
3. Apply a theme that matches your brand
4. Add text boxes to provide context and explanations

## Step 6: Share the Dashboard

1. Click the "Share" button in the top-right corner
2. Set the appropriate sharing permissions:
   - "Anyone with the link" for public access
   - "Specific people" for restricted access
3. Enable or disable features like:
   - Downloading
   - Printing
   - Copying

## BigQuery Schema and Field Mappings

The following table describes the key fields available in the BigQuery tables and how they map to Klaviyo fields:

| BigQuery Field | Klaviyo Field | Description | Data Type |
|----------------|---------------|-------------|----------|
| campaign_id | id | Unique identifier for the campaign | STRING |
| campaign_name | name | Name of the campaign | STRING |
| send_time | send_time | Time when the campaign was sent | TIMESTAMP |
| open_rate | metrics.open_rate | Percentage of recipients who opened the email | FLOAT |
| click_rate | metrics.click_rate | Percentage of recipients who clicked a link | FLOAT |
| conversion_rate | metrics.conversion_rate | Percentage of recipients who completed a conversion | FLOAT |
| revenue | metrics.revenue | Total revenue attributed to the campaign | FLOAT |
| unsubscribe_rate | metrics.unsubscribe_rate | Percentage of recipients who unsubscribed | FLOAT |
| bounce_rate | metrics.bounce_rate | Percentage of emails that bounced | FLOAT |
| date | date | Date of the campaign metrics | DATE |

## Sample Looker Studio Dashboard Configuration

Below is a JSON configuration for a sample Looker Studio dashboard that you can import:

```json
{
  "dataSourceId": "BigQuery",
  "reportId": "klaviyo-campaign-dashboard",
  "charts": [
    {
      "type": "SCORECARD",
      "title": "Average Open Rate",
      "metric": "AVG(open_rate)",
      "position": {"x": 0, "y": 0, "width": 3, "height": 2}
    },
    {
      "type": "SCORECARD",
      "title": "Average Click Rate",
      "metric": "AVG(click_rate)",
      "position": {"x": 3, "y": 0, "width": 3, "height": 2}
    },
    {
      "type": "SCORECARD",
      "title": "Total Revenue",
      "metric": "SUM(revenue)",
      "position": {"x": 6, "y": 0, "width": 3, "height": 2}
    },
    {
      "type": "TABLE",
      "title": "Campaign Performance",
      "dimensions": ["campaign_name", "send_time", "date"],
      "metrics": ["open_rate", "click_rate", "conversion_rate", "revenue"],
      "position": {"x": 0, "y": 2, "width": 12, "height": 6}
    },
    {
      "type": "TIME_SERIES",
      "title": "Open Rate Over Time",
      "dimension": "date",
      "metric": "open_rate",
      "position": {"x": 0, "y": 8, "width": 6, "height": 4}
    },
    {
      "type": "TIME_SERIES",
      "title": "Click Rate Over Time",
      "dimension": "date",
      "metric": "click_rate",
      "position": {"x": 6, "y": 8, "width": 6, "height": 4}
    },
    {
      "type": "BAR",
      "title": "Campaign Comparison",
      "dimension": "campaign_name",
      "metrics": ["open_rate", "click_rate", "conversion_rate"],
      "position": {"x": 0, "y": 12, "width": 12, "height": 6}
    }
  ],
  "controls": [
    {
      "type": "DATE_RANGE",
      "title": "Date Range",
      "dimension": "date",
      "position": {"x": 0, "y": 18, "width": 6, "height": 2}
    },
    {
      "type": "FILTER",
      "title": "Campaign",
      "dimension": "campaign_name",
      "position": {"x": 6, "y": 18, "width": 6, "height": 2}
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Ensure you have the correct permissions to access the BigQuery project
   - Verify that the BigQuery dataset and tables exist
   - Check for typos in the SQL query

2. **No Data Showing**
   - Confirm that data has been loaded into BigQuery
   - Check the date range filter to ensure it covers the period when data exists
   - Verify that the field names in your charts match the BigQuery schema

3. **Performance Issues**
   - Consider adding date partitioning to your BigQuery tables
   - Optimize your SQL queries to filter data efficiently
   - Limit the amount of data being queried by using appropriate date filters

## Next Steps

After setting up your Looker Studio dashboard, consider the following next steps:

1. **Schedule Automatic Refreshes**: Configure your dashboard to refresh automatically at regular intervals
2. **Set Up Alerts**: Create alerts for key metrics to be notified of significant changes
3. **Embed the Dashboard**: Embed the dashboard in internal tools or websites for easier access
4. **Create Additional Views**: Develop specialized dashboards for different teams or use cases

## Conclusion

You have successfully connected Looker Studio to BigQuery and created a dashboard for visualizing Klaviyo campaign data. This integration provides a powerful way to analyze and share insights from your email marketing campaigns.
