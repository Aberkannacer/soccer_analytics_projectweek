import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from db_connection import get_connection

# === CONFIG ===
your_team_id = '4dtif7outbuivua8umbwegoo5'
game_id = '5uts2s7fl98clqz8uymaazehg'

# Map action_type IDs to names
action_names = {
    '1': 'Tackle',
    '17': 'Interception',
    '18': 'Clearance',
    '14': 'Duel'
}
defensive_ids = list(action_names.keys())

# Connect
conn = get_connection()





ids_for_sql = ",".join(f"'{i}'" for i in defensive_ids)

# === Step 1: Get defensive actions by your team ===
query = f"""
SELECT 
    s.action_type, s.result,
    s.start_x, s.start_y, s.team_id, s.seconds,
    p.player_name, t.team_name
FROM spadl_actions s
JOIN players p ON s.player_id = p.player_id
JOIN teams t ON s.team_id = t.team_id
WHERE s.game_id = '{game_id}' 
  AND s.team_id = '{your_team_id}'
  AND s.action_type IN ({ids_for_sql})
"""
actions_df = pd.read_sql_query(query, conn)

# === Step 2: Get opponent possession seconds ===
query_poss = f"""
SELECT seconds, team_id as possessing_team
FROM spadl_actions
WHERE game_id = '{game_id}'
"""
poss_df = pd.read_sql_query(query_poss, conn)
conn.close()

# === Step 3: Filter to moments when we are out of possession ===
oppo_poss_secs = poss_df[poss_df['possessing_team'] != your_team_id]['seconds'].unique()
actions_df = actions_df[actions_df['seconds'].round().isin(pd.Series(oppo_poss_secs).round())]

# Map action_type numbers to readable labels
actions_df['action_label'] = actions_df['action_type'].map(action_names)

# === Step 4: Plot ===
pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta', pitch_length=105, pitch_width=68)
fig, ax = pitch.draw(figsize=(12, 8))

for label, group in actions_df.groupby('action_label'):
    pitch.scatter(
        group['start_x'], group['start_y'],
        ax=ax, s=120, label=label,
        alpha=0.7, edgecolor='black'
    )

ax.set_title("Defensive Actions Map – Out of Possession", fontsize=16)
ax.legend()
plt.tight_layout()
plt.show()
