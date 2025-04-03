import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from db_connection import get_connection

# Step 1: Get player tracking data
conn = get_connection()
query_tracking = """
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
WHERE pt.game_id = '5uts2s7fl98clqz8uymaazehg'
"""
tracking_df = pd.read_sql_query(query_tracking, conn)

# 🔧 Convert 'timestamp' to total seconds
tracking_df['seconds'] = pd.to_timedelta(tracking_df['timestamp']).dt.total_seconds().round()

# Step 2: Get possession info to find defending frames
query_possession = """
SELECT 
    a.id, 
    a.period_id, 
    a.seconds,
    a.team_id AS possessing_team,
    LAG(a.team_id) OVER (ORDER BY a.period_id, a.seconds, a.id) AS prev_team_id
FROM spadl_actions a
WHERE a.game_id = '5uts2s7fl98clqz8uymaazehg'
"""
poss_df = pd.read_sql_query(query_possession, conn)
conn.close()

# Step 3: Identify your team
your_team_id = tracking_df['team_id'].unique()[0]

# Step 4: Get timestamps (seconds) when opponent has possession
defending_times = poss_df[poss_df['possessing_team'] != your_team_id]['seconds'].unique()

# Step 5: Filter tracking data to those defending moments
defending_tracking = tracking_df[tracking_df['seconds'].isin(defending_times.round())]

# Step 6: Keep only your team’s players
defending_tracking = defending_tracking[defending_tracking['team_id'] == your_team_id]

# Step 7: Compute average positions
avg_positions = defending_tracking.groupby(['player_id', 'player_name', 'jersey_number']).agg({
    'x': 'mean',
    'y': 'mean'
}).reset_index()

# Step 8: Plot
pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
              pitch_length=105, pitch_width=68)
fig, ax = pitch.draw(figsize=(12, 8))

pitch.scatter(
    avg_positions['x'],
    avg_positions['y'],
    ax=ax,
    s=500,
    color='skyblue',
    edgecolor='black'
)

# Add player numbers/names
for _, row in avg_positions.iterrows():
    ax.text(row['x'], row['y'] + 1, f"{row['jersey_number']} - {row['player_name']}", ha='center', fontsize=9)

    

ax.set_title('Average Player Positions While Defending (Out of Possession)', fontsize=16)
plt.tight_layout()
plt.show()
