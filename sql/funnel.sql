WITH
loaded AS (
  SELECT e.user_id,e.device,MIN(e.ts) AS t_loaded
  FROM events e
  WHERE e.event_name = 'Loaded'
  GROUP BY e.user_id, e.device
),

interact AS (
  SELECT l.user_id,l.device,MIN(e.ts) AS t_interact
  FROM loaded l
  JOIN events e 
  ON e.user_id = l.user_id AND e.device  = l.device AND e.event_name = 'Interact' AND e.ts >= l.t_loaded
  GROUP BY l.user_id, l.device
),

clicks AS (
  SELECT i.user_id,i.device,MIN(e.ts) AS t_click
  FROM interact i
  JOIN events e
  ON e.user_id = i.user_id AND e.device  = i.device AND e.event_name = 'Clicks' AND e.ts >= i.t_interact
  GROUP BY i.user_id, i.device
),

purchase AS (
  SELECT c.user_id,c.device,MIN(e.ts) AS t_purchase
  FROM clicks c
  JOIN events e
  ON e.user_id = c.user_id AND e.device  = c.device AND e.event_name = 'Purchase' AND e.ts >= c.t_click
  GROUP BY c.user_id, c.device
),

counts AS (
  SELECT l.device,COUNT(l.user_id) AS n_loaded,COUNT(i.user_id) AS n_interact,COUNT(c.user_id) AS n_click,COUNT(p.user_id) AS n_purchase
  FROM loaded l
  LEFT JOIN interact i ON l.user_id = i.user_id AND l.device = i.device
  LEFT JOIN clicks c ON l.user_id = c.user_id AND l.device = c.device
  LEFT JOIN purchase p ON l.user_id = p.user_id AND l.device = p.device
  GROUP BY l.device
)

SELECT step, users, conv_from_prev_pct, conv_from_start_pct, device
FROM (
  SELECT 'Loaded' AS step, n_loaded AS users,100.0 AS conv_from_prev_pct,100.0 AS conv_from_start_pct,device,1 AS step_order
  FROM counts
  UNION ALL
  SELECT 'Interact',n_interact,ROUND(100.0 * n_interact / n_loaded, 2),
  ROUND(100.0 * n_interact /n_loaded, 2),device,2
  FROM counts
  UNION ALL
  SELECT 'Clicks',n_click,ROUND(100.0 * n_click / n_interact, 2),ROUND(100.0 * n_click /n_loaded, 2),device,3
  FROM counts
  UNION ALL
  SELECT 'Purchase',n_purchase,ROUND(100.0 * n_purchase /n_click, 2),ROUND(100.0 * n_purchase /n_loaded, 2),device,4
  FROM counts
)
ORDER BY device, step_order;
'''
