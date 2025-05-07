# BigQuery Schema and Field Mappings

## Overview

This document provides a detailed mapping between Klaviyo API fields and the corresponding BigQuery schema fields. This mapping is essential for understanding how data flows from Klaviyo through the ETL pipeline and into BigQuery, and how it can be visualized in Looker Studio.

## Campaign Metrics Table

The `klaviyo_raw.events_campaign` table contains campaign performance metrics with the following schema:

| BigQuery Field | Klaviyo Field | Description | Data Type |
|----------------|---------------|-------------|----------|
| `campaign_id` | `id` | Unique identifier for the campaign | STRING |
| `campaign_name` | `name` | Name of the campaign | STRING |
| `subject` | `subject` | Email subject line | STRING |
| `from_email` | `from_email` | Sender email address | STRING |
| `from_name` | `from_name` | Sender name | STRING |
| `send_time` | `send_time` | Time when the campaign was sent | TIMESTAMP |
| `status` | `status` | Campaign status (e.g., sent, scheduled) | STRING |
| `num_recipients` | `stats.recipient_count` | Number of recipients | INTEGER |
| `open_count` | `stats.open_count` | Number of opens | INTEGER |
| `open_rate` | `metrics.open_rate` | Percentage of recipients who opened the email | FLOAT |
| `click_count` | `stats.click_count` | Number of clicks | INTEGER |
| `click_rate` | `metrics.click_rate` | Percentage of recipients who clicked a link | FLOAT |
| `conversion_count` | `stats.conversion_count` | Number of conversions | INTEGER |
| `conversion_rate` | `metrics.conversion_rate` | Percentage of recipients who completed a conversion | FLOAT |
| `revenue` | `metrics.revenue` | Total revenue attributed to the campaign | FLOAT |
| `unsubscribe_count` | `stats.unsubscribe_count` | Number of unsubscribes | INTEGER |
| `unsubscribe_rate` | `metrics.unsubscribe_rate` | Percentage of recipients who unsubscribed | FLOAT |
| `bounce_count` | `stats.bounce_count` | Number of bounces | INTEGER |
| `bounce_rate` | `metrics.bounce_rate` | Percentage of emails that bounced | FLOAT |
| `date` | Derived from `send_time` | Date of the campaign metrics | DATE |
| `created_at` | `created` | Time when the campaign was created | TIMESTAMP |
| `updated_at` | `updated` | Time when the campaign was last updated | TIMESTAMP |
| `etl_timestamp` | Generated during ETL | Time when the data was loaded into BigQuery | TIMESTAMP |

## Event Metrics Table

The `klaviyo_raw.events_events` table contains detailed event data with the following schema:

| BigQuery Field | Klaviyo Field | Description | Data Type |
|----------------|---------------|-------------|----------|
| `event_id` | `id` | Unique identifier for the event | STRING |
| `event_name` | `name` | Name of the event (e.g., Opened Email, Clicked Email) | STRING |
| `timestamp` | `timestamp` | Time when the event occurred | TIMESTAMP |
| `date` | Derived from `timestamp` | Date of the event | DATE |
| `campaign_id` | `campaign.id` | ID of the associated campaign | STRING |
| `campaign_name` | `campaign.name` | Name of the associated campaign | STRING |
| `profile_id` | `profile.id` | ID of the profile that triggered the event | STRING |
| `email` | `profile.email` | Email address of the profile | STRING |
| `first_name` | `profile.first_name` | First name of the profile | STRING |
| `last_name` | `profile.last_name` | Last name of the profile | STRING |
| `value` | `value` | Monetary value associated with the event | FLOAT |
| `url` | `properties.url` | URL that was clicked (for click events) | STRING |
| `subject` | `properties.subject` | Email subject line | STRING |
| `device_type` | `properties.device_type` | Type of device used (e.g., mobile, desktop) | STRING |
| `client_type` | `properties.client_type` | Type of client used (e.g., Gmail, Outlook) | STRING |
| `etl_timestamp` | Generated during ETL | Time when the data was loaded into BigQuery | TIMESTAMP |

## Profile Table

The `klaviyo_raw.events_profile` table contains customer profile data with the following schema:

| BigQuery Field | Klaviyo Field | Description | Data Type |
|----------------|---------------|-------------|----------|
| `profile_id` | `id` | Unique identifier for the profile | STRING |
| `email` | `email` | Email address | STRING |
| `first_name` | `first_name` | First name | STRING |
| `last_name` | `last_name` | Last name | STRING |
| `phone_number` | `phone_number` | Phone number | STRING |
| `location_city` | `location.city` | City | STRING |
| `location_region` | `location.region` | Region/state | STRING |
| `location_country` | `location.country` | Country | STRING |
| `location_zip` | `location.zip` | ZIP/postal code | STRING |
| `created_at` | `created` | Time when the profile was created | TIMESTAMP |
| `updated_at` | `updated` | Time when the profile was last updated | TIMESTAMP |
| `last_activity` | `last_activity` | Time of the profile's last activity | TIMESTAMP |
| `subscribed_to_email` | `subscribed_to_email` | Whether the profile is subscribed to emails | BOOLEAN |
| `etl_timestamp` | Generated during ETL | Time when the data was loaded into BigQuery | TIMESTAMP |

## List Membership Table

The `klaviyo_raw.events_list_membership` table contains data about which profiles belong to which lists:

| BigQuery Field | Klaviyo Field | Description | Data Type |
|----------------|---------------|-------------|----------|
| `list_id` | `list.id` | ID of the list | STRING |
| `list_name` | `list.name` | Name of the list | STRING |
| `profile_id` | `profile.id` | ID of the profile | STRING |
| `email` | `profile.email` | Email address of the profile | STRING |
| `subscribed_at` | `subscribed_at` | Time when the profile was subscribed to the list | TIMESTAMP |
| `etl_timestamp` | Generated during ETL | Time when the data was loaded into BigQuery | TIMESTAMP |

## Data Transformation Notes

### Date Partitioning

All tables in BigQuery are partitioned by the `date` field to optimize query performance. When querying these tables, always include a date filter to limit the amount of data scanned.

### Derived Fields

Some fields in the BigQuery schema are derived during the ETL process:

- `date`: Extracted from the timestamp fields to enable date partitioning
- `etl_timestamp`: Added to track when the data was loaded into BigQuery
- Calculated rates (e.g., `open_rate`, `click_rate`): Computed from the raw count fields

### Field Mapping Process

The field mapping process occurs in the following steps:

1. Raw data is extracted from Klaviyo via Fivetran
2. The data is stored in Postgres with minimal transformation
3. The ETL runner extracts the data from Postgres
4. The field mapper normalizes the field names and formats
5. The normalized data is loaded into BigQuery

## Using This Schema in Looker Studio

When creating reports in Looker Studio, you can use this schema as a reference for available fields. The most commonly used fields for campaign performance dashboards are:

- `campaign_name`
- `send_time`
- `date`
- `open_rate`
- `click_rate`
- `conversion_rate`
- `revenue`

For more detailed event analysis, you can use the fields from the `events_events` table, joining with the campaign table as needed.

## Example Queries

### Campaign Performance Overview

```sql
SELECT
  campaign_name,
  send_time,
  num_recipients,
  open_rate,
  click_rate,
  conversion_rate,
  revenue
FROM
  `[PROJECT_ID].klaviyo_raw.events_campaign`
WHERE
  date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()
ORDER BY
  send_time DESC
```

### Daily Performance Metrics

```sql
SELECT
  date,
  COUNT(DISTINCT campaign_id) AS campaigns_sent,
  AVG(open_rate) AS avg_open_rate,
  AVG(click_rate) AS avg_click_rate,
  SUM(revenue) AS total_revenue
FROM
  `[PROJECT_ID].klaviyo_raw.events_campaign`
WHERE
  date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()
GROUP BY
  date
ORDER BY
  date
```

### Campaign Revenue by Device Type

```sql
SELECT
  c.campaign_name,
  e.device_type,
  COUNT(DISTINCT e.profile_id) AS unique_users,
  SUM(e.value) AS revenue
FROM
  `[PROJECT_ID].klaviyo_raw.events_events` e
JOIN
  `[PROJECT_ID].klaviyo_raw.events_campaign` c
ON
  e.campaign_id = c.campaign_id
WHERE
  e.event_name = 'Placed Order'
  AND e.date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND CURRENT_DATE()
GROUP BY
  c.campaign_name,
  e.device_type
ORDER BY
  c.campaign_name,
  revenue DESC
```

## Conclusion

This document provides a comprehensive mapping between Klaviyo fields and BigQuery schema fields. Use this as a reference when creating queries, reports, and dashboards to ensure you're using the correct field names and data types.
