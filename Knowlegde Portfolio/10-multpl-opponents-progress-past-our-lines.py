import pandas as pd
import matplotlib.pyplot as plt
from db_connection import get_connection

# === CONFIG ===
your_team_id = '1oyb7oym5nwzny8vxf03szd2h'
lost_game_ids = [
    '6aaebu7uj50ewu3irl3qmjg2c',
    '5ugfsw7je1y0lay7xdqe3pces',
    '5wofhz4hm81f0lk0ay8sumfis',
    '78nndczlbj2214zhtbfahs2s4',
    '6foamr1y4x3t549lo89xczuok',
    '6gfytd52ib44k8sm0pc8lohzo',
    '6uc41ha2woe8uz2y69t44j5ec',
    '5oc8drrbruovbuiriyhdyiyok'
]

conn = get_connection()

# === Prepare storage
all_zone_counts = {}

# === Loop through each match
for game_id in lost_game_ids:
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

    # Opponent team
    opponent_team_id = df[df['team_id'] != your_team_id]['team_id'].iloc[0]

    # Filter all opponent passes ending in our half
    passes = df[
        (df['team_id'] == opponent_team_id) &
        (df['action_type'] == '10') &  # Pass
        (df['end_x'].astype(float) > 52.5)  # our half (left-to-right assumed)
    ].copy()

    # Optional: keep only meaningful passes
    passes['pass_length'] = ((passes['end_x'] - passes['start_x'])**2 + 
                             (passes['end_y'] - passes['start_y'])**2) ** 0.5
    passes = passes[passes['pass_length'] > 5]

    # Classify by zone
    def classify_zone(x):
        if x < 35:
            return "Opponent Half"
        elif x < 70:
            return "Middle Third"
        else:
            return "Our Defensive Third"

    passes['target_zone'] = passes['end_x'].apply(classify_zone)
    zone_counts = passes['target_zone'].value_counts().reindex(
        ['Opponent Half', 'Middle Third', 'Our Defensive Third'], fill_value=0
    )

    all_zone_counts[game_id] = zone_counts

conn.close()

# === Create dataframe for plotting
zone_df = pd.DataFrame(all_zone_counts).T  # rows = games
zone_df.index.name = "Game ID"

# === Plot grouped bar chart
zone_df.plot(kind='bar', figsize=(10, 6), edgecolor='black')
plt.title("Opponent Pass Target Zones – Matches We Lost")
plt.ylabel("Number of Passes")
plt.xlabel("Match ID")
plt.xticks(rotation=45)
plt.legend(title="Zone")
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
