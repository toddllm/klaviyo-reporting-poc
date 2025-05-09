-- Creates (or replaces) a view that aggregates daily campaign KPIs
CREATE OR REPLACE VIEW `${PROJECT_ID}.${DATASET}.v_email_metrics` AS
SELECT
  DATE(e.timestamp) AS send_date,
  c.id AS campaign_id,
  c.name AS campaign_name,
  e.property_subject AS subject,
  COALESCE(l.id, '') AS list_id,
  COUNTIF(e.type = 'Sent Email') AS sends,
  COUNTIF(e.type = 'Opened Email') AS unique_opens,
  COUNTIF(e.type = 'Clicked Email') AS unique_clicks,
  SUM(COALESCE(e.property_total, 0)) AS revenue,
  SAFE_DIVIDE(COUNTIF(e.type = 'Opened Email'), COUNTIF(e.type = 'Sent Email')) AS open_rate,
  SAFE_DIVIDE(COUNTIF(e.type = 'Clicked Email'), COUNTIF(e.type = 'Sent Email')) AS click_rate
FROM `${PROJECT_ID}.${DATASET}.event` AS e
JOIN `${PROJECT_ID}.${DATASET}.campaign` AS c
  ON e.campaign_id = c.id
LEFT JOIN `${PROJECT_ID}.${DATASET}.list` AS l
  ON e.property_list_id = l.id
WHERE LOWER(c.name) NOT LIKE LOWER('%test%')
GROUP BY 1, 2, 3, 4, 5;
