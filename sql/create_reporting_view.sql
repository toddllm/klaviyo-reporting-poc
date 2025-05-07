-- Creates (or replaces) a view that aggregates daily campaign KPIs
CREATE OR REPLACE VIEW `${PROJECT_ID}.${DATASET}.v_email_metrics` AS
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
GROUP BY 1, 2, 3, 4, 5;
