-- 1) Verify column order and names
WITH cols AS (
  SELECT STRING_AGG(column_name ORDER BY ordinal_position) AS col_list
  FROM `${PROJECT_ID}.${DATASET}.INFORMATION_SCHEMA.COLUMNS`
  WHERE table_name = 'v_email_metrics'
)
SELECT
  CASE
    WHEN col_list = 'send_date,campaign_id,campaign_name,subject,list_id,sends,unique_opens,unique_clicks,revenue,open_rate,click_rate'
    THEN 0 ELSE 1
  END AS column_mismatch
FROM cols;

-- 2) Verify row‐count parity with source aggregation
WITH src AS (
  SELECT
    DATE(e.event_timestamp) AS send_date,
    c.campaign_id,
    c.campaign_name,
    c.subject,
    COALESCE(l.list_id, '') AS list_id,
    COUNTIF(e.event_type = 'send') AS sends,
    COUNTIF(e.event_type = 'open') AS unique_opens,
    COUNTIF(e.event_type = 'click') AS unique_clicks,
    SUM(COALESCE(e.revenue, 0)) AS revenue,
    SAFE_DIVIDE(COUNTIF(e.event_type = 'open'), COUNTIF(e.event_type = 'send')) AS open_rate,
    SAFE_DIVIDE(COUNTIF(e.event_type = 'click'), COUNTIF(e.event_type = 'send')) AS click_rate
  FROM `${PROJECT_ID}.${DATASET}.email_events` AS e
  JOIN `${PROJECT_ID}.${DATASET}.email_campaigns` AS c
    ON e.campaign_id = c.campaign_id
  LEFT JOIN `${PROJECT_ID}.${DATASET}.email_lists` AS l
    ON c.list_id = l.list_id
  WHERE c.campaign_name NOT ILIKE '%test%'
  GROUP BY 1, 2, 3, 4, 5
),
vw AS (
  SELECT * FROM `${PROJECT_ID}.${DATASET}.v_email_metrics`
)
SELECT
  CASE
    WHEN (SELECT COUNT(*) FROM src) = (SELECT COUNT(*) FROM vw)
    THEN 0 ELSE 1
  END AS row_count_mismatch;
