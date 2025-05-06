# Looker Studio Extract Setup Guide

## Overview

This guide provides step-by-step instructions for setting up a Looker Studio extract using the Klaviyo campaign performance data stored in BigQuery. The extract is configured to:

- Pull data from the last 90 days
- Aggregate metrics by Campaign ID and Date
- Refresh daily to ensure up-to-date reporting
- Create a cached dataset that stays under the 100MB limit

## Prerequisites

- Google Cloud Platform account with BigQuery access
- BigQuery project with `klaviyo_raw.events` table populated
- Permission to create extracts in Looker Studio
- `looker_extracts` dataset created in BigQuery (or another destination dataset)

## Setup Instructions

### 1. Prepare Your BigQuery Environment

1. Ensure your BigQuery instance has the `klaviyo_raw.events` table populated with Klaviyo campaign data
2. Create a destination dataset for the extract if it doesn't exist:

```sql
CREATE SCHEMA IF NOT EXISTS `looker_extracts`
OPTIONS(
  location="US"
);
```

### 2. Configure the Extract in Looker Studio

1. Log in to [Looker Studio](https://lookerstudio.google.com/)
2. Click **Create** > **Extract**

   ![Create Extract](img/looker_extract_create.png)

3. Select **BigQuery** as the data source

   ![Select BigQuery](img/looker_extract_select_bq.png)

4. Configure the source:
   - Project: `[YOUR_PROJECT_ID]`
   - Dataset: `klaviyo_raw`
   - Table: `events`

   ![Configure Source](img/looker_extract_source.png)

5. Configure the fields to extract:
   - Select all fields listed in the `looker_extract_klaviyo.json` template
   - Ensure field types match those specified in the template

   ![Configure Fields](img/looker_extract_fields.png)

6. Add a date filter for the last 90 days:
   - Field: `date`
   - Operator: `>=`
   - Value: `DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY)`

   ![Add Date Filter](img/looker_extract_date_filter.png)

7. Configure aggregation:
   - Dimensions: `campaign_id`, `date`
   - Metrics: Sum of `recipients`, `opens`, `clicks`, `unsubscribes`
   - Calculated Fields:
     - `open_rate`: `SUM(opens) / SUM(recipients)`
     - `click_rate`: `SUM(clicks) / SUM(recipients)`

   ![Configure Aggregation](img/looker_extract_aggregation.png)

8. Set the row limit to 10,000 (this should be more than enough for 90 days of data)

9. Configure the refresh schedule:
   - Frequency: Daily
   - Time: 4:00 AM
   - Timezone: America/New_York (or your preferred timezone)

   ![Configure Refresh](img/looker_extract_refresh.png)

10. Configure the destination:
    - Project: `[YOUR_PROJECT_ID]`
    - Dataset: `looker_extracts`
    - Table: `klaviyo_campaign_performance_90d`

    ![Configure Destination](img/looker_extract_destination.png)

11. Review and create the extract

### 3. Create a Report Using the Extract

1. In Looker Studio, click **Create** > **Report**

2. Add a data source by clicking **Add data**

3. Select **BigQuery** and navigate to your extract table:
   - Project: `[YOUR_PROJECT_ID]`
   - Dataset: `looker_extracts`
   - Table: `klaviyo_campaign_performance_90d`

4. Create visualizations using the extracted data:
   - Time series chart for open_rate and click_rate trends
   - Bar chart for campaign performance comparison
   - Add filters for date range and campaign_id

   ![Sample Report](img/looker_extract_report.png)

## Validation

### Size Validation

To verify that your extract stays under the 100MB limit:

1. After the extract has run, check the size of the destination table in BigQuery:

```sql
SELECT
  table_id,
  ROUND(size_bytes/1024/1024, 2) as size_mb
FROM
  `[YOUR_PROJECT_ID].looker_extracts.__TABLES__`
WHERE
  table_id = 'klaviyo_campaign_performance_90d'
```

2. The result should show a size well under 100MB

### Data Validation

To verify that the data in the extract matches the source:

1. Compare row counts between source and extract for a specific date range:

```sql
-- Source data count (aggregated)
SELECT
  COUNT(DISTINCT CONCAT(campaign_id, CAST(date AS STRING))) as row_count
FROM
  `[YOUR_PROJECT_ID].klaviyo_raw.events`
WHERE
  date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY);

-- Extract data count
SELECT
  COUNT(*) as row_count
FROM
  `[YOUR_PROJECT_ID].looker_extracts.klaviyo_campaign_performance_90d`;
```

2. The counts should match or be very close (allowing for any filtering in the extract)

## Troubleshooting

### Extract Fails to Run

1. Check BigQuery permissions
2. Verify that the source table exists and has data
3. Check for any syntax errors in filter expressions
4. Ensure the destination dataset exists and is writable

### Data Discrepancies

1. Verify that the date filter is correctly applied
2. Check for any data type mismatches between source and extract
3. Ensure calculated fields use the correct formulas

### Performance Issues

1. If the extract takes too long to run, consider adding partitioning to the source table
2. Reduce the date range if necessary
3. Add more specific filters to reduce the data volume

## Next Steps

- Consider creating additional extracts for different time periods or aggregation levels
- Set up alerts for extract failures
- Create scheduled email delivery of reports based on the extract
- Implement row-level security if needed
