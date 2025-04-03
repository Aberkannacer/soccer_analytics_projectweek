import pandas as pd
import matplotlib.pyplot as plt
from db_connection import get_connection

# CONFIG
your_team_id = '1oyb7oym5nwzny8vxf03szd2h' 
game_id = '6mvh0ixx6p3frjttob5szqcr8' # win 2-1
# game_id = '6aaebu7uj50ewu3irl3qmjg2c' # loss 2-4
# Defensive action types (as strings in your DB)
defensive_types = {
    '1': 'Tackle',
    '14': 'Duel',
    '17': 'Interception',
    '18': 'Clearance'
}

# Connect and load data
conn = get_connection()
query = f"""
SELECT action_type, seconds, team_id
FROM spadl_actions
WHERE game_id = '{game_id}' AND team_id = '{your_team_id}'
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Filter only defensive actions
df = df[df['action_type'].isin(defensive_types.keys())]
df['action_label'] = df['action_type'].map(defensive_types)

# === 3️⃣ Histogram of Defensive Action Types ===
type_counts = df['action_label'].value_counts().reindex(defensive_types.values(), fill_value=0)

plt.figure(figsize=(8, 5))
type_counts.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title("Count of Defensive Actions by Type")
plt.ylabel("Number of Actions")
plt.xlabel("Action Type")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# === 4️⃣ Line Graph: Defensive Actions Over Time (Minute bins) ===
df['minute'] = df['seconds'] // 60
actions_per_min = df.groupby('minute').size()

plt.figure(figsize=(10, 4))
actions_per_min.plot(kind='line', marker='o', color='darkgreen')
plt.title("Defensive Actions Per Minute")
plt.xlabel("Minute")
plt.ylabel("Number of Actions")
plt.grid(axis='both', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
