import pandas as pd
import matplotlib.pyplot as plt
from db_connection import get_connection

# CONFIG
your_team_id = '1oyb7oym5nwzny8vxf03szd2h'
game_id = '6rulhyb9xa5yczi1jntilsr9w'

conn = get_connection()

# === Step 1: Load all actions ===
query = f"""
SELECT s.action_type, s.start_x, s.start_y, s.end_x, s.end_y,
       s.team_id, s.seconds, s.result,
       p.player_name, t.team_name
FROM spadl_actions s
JOIN players p ON s.player_id = p.player_id
JOIN teams t ON s.team_id = t.team_id
WHERE s.game_id = '{game_id}'
"""
df = pd.read_sql_query(query, conn)
conn.close()

# === Step 2: Get opponent team ID
opponent_team_id = df[df['team_id'] != your_team_id]['team_id'].iloc[0]

# === Step 3: All opponent passes into your half
passes_into_our_half = df[
    (df['team_id'] == opponent_team_id) &
    (df['action_type'] == '10') &  # 10 = pass
    (df['end_x'].astype(float) > 52.5)  # assuming you defend left to right
].copy()

# Optional: calculate pass length to remove short/sideways passes
passes_into_our_half['pass_length'] = ((passes_into_our_half['end_x'] - passes_into_our_half['start_x'])**2 +
                                       (passes_into_our_half['end_y'] - passes_into_our_half['start_y'])**2) ** 0.5
passes_into_our_half = passes_into_our_half[passes_into_our_half['pass_length'] > 5]

# === Step 4: Classify where the pass ends (zones)
def classify_zone(x):
    if x < 35:
        return "Opponent Half"
    elif x < 70:
        return "Middle Third"
    else:
        return "Our Defensive Third"

passes_into_our_half['target_zone'] = passes_into_our_half['end_x'].apply(classify_zone)

# === Step 5: Count per zone
zone_counts = passes_into_our_half['target_zone'].value_counts().reindex(
    ['Opponent Half', 'Middle Third', 'Our Defensive Third'], fill_value=0
)

# === Step 6: Debug print
print("Opponent passes into our half found:", len(passes_into_our_half))
print(passes_into_our_half[['start_x', 'end_x', 'target_zone']].head())

# === Step 7: Plot
zone_counts.plot(kind='bar', color='orangered', edgecolor='black')
plt.title("Opponent Pass Targets Into Our Half")
plt.ylabel("Number of Passes")
plt.xlabel("Zone Where Pass Ended")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
