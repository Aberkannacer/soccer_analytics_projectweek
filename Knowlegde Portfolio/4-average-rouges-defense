import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from db_connection import get_connection

# === CONFIGURATION ===
game_id = '5ugfsw7je1y0lay7xdqe3pces'
your_team_id = '1oyb7oym5nwzny8vxf03szd2h'

# === HELPER FUNCTION ===
def hms_to_seconds(hms):
    try:
        h, m, s = map(int, hms.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return None

# === 1. LOAD TRACKING DATA ===
conn = get_connection()
query_tracking = f"""
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, 
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
WHERE pt.game_id = '{game_id}'
"""
tracking_df = pd.read_sql_query(query_tracking, conn)
tracking_df = tracking_df[tracking_df['player_name'] != 'Ball']
tracking_df['seconds'] = tracking_df['timestamp'].apply(hms_to_seconds)
tracking_df.dropna(subset=['seconds'], inplace=True)

# === 2. LOAD POSSESSION DATA ===
query_possession = f"""
SELECT a.seconds, a.team_id AS possessing_team
FROM spadl_actions a
WHERE a.game_id = '{game_id}'
"""
poss_df = pd.read_sql_query(query_possession, conn)
conn.close()

# === 3. IDENTIFY DEFENSIVE SECONDS ===
defending_secs = poss_df[poss_df['possessing_team'] != your_team_id]['seconds'].unique()

# Expand each second to ±1 for matching
expanded_secs = {int(sec + offset) for sec in defending_secs for offset in [-1, 0, 1]}

# === 4. FILTER DEFENSIVE TRACKING FRAMES ===
defending_tracking = tracking_df[
    (tracking_df['team_id'] == your_team_id) &
    (tracking_df['seconds'].round().astype(int).isin(expanded_secs))
]

# === 5. CALCULATE AVERAGE POSITIONS ===
avg_positions = defending_tracking.groupby(
    ['player_id', 'player_name', 'jersey_number']
)[['x', 'y']].mean().reset_index()

# === 6. PLOT ===
pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
              pitch_length=105, pitch_width=68)
fig, ax = pitch.draw(figsize=(12, 8))

pitch.scatter(avg_positions['x'], avg_positions['y'], ax=ax, s=500,
              color='skyblue', edgecolor='black')

for _, row in avg_positions.iterrows():
    ax.text(row['x'], row['y'] + 1, f"{row['jersey_number']} - {row['player_name']}",
            ha='center', fontsize=9)

ax.set_title('Average Player Positions While Defending (Out of Possession)', fontsize=16)
plt.tight_layout()
plt.show()
