SELECT
  COALESCE(detected_intent, 'unknown') AS intent,
  COUNT(*) AS count,ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM messages), 2) AS pct_of_total
FROM messages
GROUP BY COALESCE(detected_intent, 'unknown')
ORDER BY count DESC;


WITH msgs AS (
  SELECT DISTINCT session_id, COALESCE(NULLIF(detected_intent, ''), 'unknown') AS intent
  FROM messages
),
purchases AS (
  SELECT DISTINCT session_id
  FROM events
  WHERE event_name = 'Purchase'
)
SELECT
  m.intent,COUNT(DISTINCT m.session_id) AS sessions_with_intent,COUNT(DISTINCT p.session_id) AS sessions_with_purchase,
  ROUND(100.0 * COUNT(DISTINCT p.session_id) / COUNT(DISTINCT m.session_id), 2) AS purchase_rate_pct
FROM msgs m
LEFT JOIN purchases p ON p.session_id = m.session_id
GROUP BY m.intent
ORDER BY purchase_rate_pct DESC, sessions_with_intent DESC
LIMIT 2;