import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from db_connection import get_connection

# === CONFIG ===
your_team_id = '4dtif7outbuivua8umbwegoo5'

# Define match lists
clean_sheet_match_ids = [
    '5ow2wa823rjft38oh48b4ror8',
    '6j7t38109kev3yht9gfv7oopg',
    '6laud87o2272y9txxwvok2n84',
    '756u46khy7yhi4q7hljt6i8lw',
    '76pcoyeqglfmatz35cpaml0yc'
]

# Get matches where team conceded
def get_conceded_match_ids(team_id):
    conn = get_connection()
    query = f"""
    SELECT match_id FROM matches
    WHERE (
        (home_team_id = '{team_id}' AND away_score > 0)
        OR
        (away_team_id = '{team_id}' AND home_score > 0)
    )
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['match_id'].tolist()

conceded_match_ids = get_conceded_match_ids(your_team_id)

# === UTILS ===
def hms_to_seconds(hms_string):
    try:
        h, m, s = map(int, hms_string.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return None

def get_defensive_positions(match_ids, your_team_id):
    conn = get_connection()
    all_tracking = pd.DataFrame()

    for match_id in match_ids:
        # Tracking data
        query_tracking = f"""
        SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, 
               p.jersey_number, p.player_name, p.team_id
        FROM player_tracking pt
        JOIN players p ON pt.player_id = p.player_id
        WHERE pt.game_id = '{match_id}'
        """
        tracking_df = pd.read_sql_query(query_tracking, conn)
        tracking_df = tracking_df[tracking_df['player_name'] != 'Ball']
        tracking_df['seconds'] = tracking_df['timestamp'].apply(hms_to_seconds)
        tracking_df = tracking_df.dropna(subset=['seconds'])

        # Possession info
        query_possession = f"""
        SELECT seconds, team_id AS possessing_team
        FROM spadl_actions
        WHERE game_id = '{match_id}'
        """
        poss_df = pd.read_sql_query(query_possession, conn)
        defending_times = poss_df[poss_df['possessing_team'] != your_team_id]['seconds'].unique()

        # Match tracking seconds to possession time ±1s
        expanded_def_times = set()
        for t in defending_times:
            expanded_def_times.update([t - 1, t, t + 1])

        match_tracking = tracking_df[
            tracking_df['seconds'].round().astype(int).isin(expanded_def_times)
        ]

        match_tracking = match_tracking[match_tracking['team_id'] == your_team_id]
        all_tracking = pd.concat([all_tracking, match_tracking], ignore_index=True)

    conn.close()
    return all_tracking

# === Get both shapes ===
print("Processing clean-sheet matches...")
clean_df = get_defensive_positions(clean_sheet_match_ids, your_team_id)

print("Processing conceded-goal matches...")
conceded_df = get_defensive_positions(conceded_match_ids, your_team_id)

# === Averages ===
avg_clean = clean_df.groupby(['player_id', 'player_name', 'jersey_number']).agg({'x': 'mean', 'y': 'mean'}).reset_index()
avg_conceded = conceded_df.groupby(['player_id', 'player_name', 'jersey_number']).agg({'x': 'mean', 'y': 'mean'}).reset_index()

# === Plot ===
pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta', pitch_length=105, pitch_width=68)
fig, ax = pitch.draw(figsize=(12, 8))

# Clean-sheet in blue
pitch.scatter(avg_clean['x'], avg_clean['y'], ax=ax, s=500, color='skyblue', edgecolor='black', label='Clean Sheet')

# Conceded goals in red
pitch.scatter(avg_conceded['x'], avg_conceded['y'], ax=ax, s=500, color='red', edgecolor='black', alpha=0.6, label='Conceded')

# Annotate players from clean-sheet
for _, row in avg_clean.iterrows():
    ax.text(row['x'], row['y'] + 1, f"{row['jersey_number']}", ha='center', fontsize=9, color='black')

ax.set_title("Average Defensive Shape – Clean Sheet (Blue) vs Conceded (Red)", fontsize=16)
ax.legend(loc='upper center')
plt.tight_layout()
plt.show()
