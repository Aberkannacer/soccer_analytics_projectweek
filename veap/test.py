import pandas as pd
from db_connection import get_connection

conn = get_connection()
query = """
SELECT DISTINCT action_type
FROM spadl_actions
WHERE player_id = (
    SELECT player_id FROM players WHERE player_name = 'B. Mechele'
);
"""
action_types_df = pd.read_sql_query(query, conn)
conn.close()

print(action_types_df)
