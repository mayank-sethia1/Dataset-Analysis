import pandas as pd
import sqlite3
import json
import argparse
import os
import matplotlib.pyplot as plt
import seaborn as sns

funnel ='''
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

intent ='''SELECT
  COALESCE(detected_intent, 'unknown') AS intent,
  COUNT(*) AS count,ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM messages), 2) AS pct_of_total
FROM messages
GROUP BY COALESCE(detected_intent, 'unknown')
ORDER BY count DESC;

'''
cancellation = """
WITH s AS (
  SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN canceled_at IS NOT NULL THEN 1 ELSE 0 END) AS canceled,
    SUM(CASE
        WHEN strftime('%s', canceled_at) - strftime('%s', created_at) > 3600
        THEN 1 ELSE 0
        END) AS violations
  FROM orders
)
SELECT
  total_orders,canceled,violations,
  CASE
    WHEN canceled = 0 THEN 0.0
    ELSE ROUND(100.0 * violations / canceled, 2)
  END AS violation_rate_pct
FROM s;
"""

def setup_database(events_path, messages_path, orders_path):

    db_connection = sqlite3.connect(':memory:')
    pd.read_csv(events_path).to_sql('events', db_connection)
    pd.read_csv(messages_path).to_sql('messages', db_connection)
    pd.read_csv(orders_path).to_sql('orders', db_connection)
    
    return db_connection

def run_analysis(db_connection):

    df_funnel = pd.read_sql_query(funnel, db_connection)
    df_intents = pd.read_sql_query(intent, db_connection)
    df_cancellation = pd.read_sql_query(cancellation, db_connection)
    return df_funnel, df_intents, df_cancellation

def create_visualizations(df_funnel, df_intents, out_dir):


    plt.figure(figsize=(12, 7))
    sns.barplot(data=df_funnel, x='step', y='users',hue='device')
    plt.title('Funnel Conversion by Device')
    plt.xlabel('Funnel Step')
    plt.ylabel('Number of Users')
    plt.tight_layout()
    funnel_chart_path = os.path.join(out_dir, 'funnel.png')
    plt.savefig(funnel_chart_path)
    plt.close()

    # Intent Chart (Top 10)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df_intents.head(10), x='pct_of_total', y='intent')
    plt.title('Top 10 Detected Intent Share')
    plt.xlabel('Percent of Total Messages (%)')
    plt.ylabel('Intent')
    intent_chart_path = os.path.join(out_dir, 'intents.png')
    plt.savefig(intent_chart_path)
    plt.close()

def generate_json_report(df_funnel, df_intents, df_cancellation, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        report_path = os.path.join(out_dir, 'report.json')
        
        report_data = {
            'funnel': df_funnel.to_dict(orient='records'),
            'intents': df_intents.to_dict(orient='records'),
            'cancellation_sla': df_cancellation.to_dict(orient='records')
        }
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
            

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--events')
    parser.add_argument('--messages')
    parser.add_argument('--orders')
    parser.add_argument('--out')
    
    args = parser.parse_args()
    
    output_directory = args.out
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)


    conn = setup_database(args.events, args.messages, args.orders)
    
    df_funnel, df_intents, df_cancellation = run_analysis(conn)
    conn.close() 

    generate_json_report(df_funnel, df_intents, df_cancellation, output_directory)
    create_visualizations(df_funnel, df_intents, output_directory)
    

if __name__ == '__main__':
    main()
