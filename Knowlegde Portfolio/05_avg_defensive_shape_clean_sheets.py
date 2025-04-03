import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from db_connection import get_connection

# === CONFIG ===
your_team_id = '4dtif7outbuivua8umbwegoo5'

# Clean-sheet matches (from previous output)
clean_sheet_match_ids = [
    '5ow2wa823rjft38oh48b4ror8',
    '6j7t38109kev3yht9gfv7oopg',
    '6laud87o2272y9txxwvok2n84',
    '756u46khy7yhi4q7hljt6i8lw',
    '76pcoyeqglfmatz35cpaml0yc'
]

# === FUNCTIONS ===

def hms_to_seconds(hms_string):
    try:
        h, m, s = map(int, hms_string.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return None

def get_defending_tracking_for_match(game_id, conn):
    # Get tracking data
    query_tracking = f"""
    SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, p.jersey_number, p.player_name, p.team_id
    FROM player_tracking pt
    JOIN players p ON pt.player_id = p.player_id
    WHERE pt.game_id = '{game_id}'
    """
    tracking_df = pd.read_sql_query(query_tracking, conn)
    tracking_df = tracking_df[tracking_df['player_name'] != 'Ball']
    tracking_df['seconds'] = tracking_df['timestamp'].apply(hms_to_seconds)
    tracking_df = tracking_df.dropna(subset=['seconds'])

    # Get possession info
    query_possession = f"""
    SELECT a.seconds, a.team_id AS possessing_team
    FROM spadl_actions a
    WHERE a.game_id = '{game_id}'
    """
    poss_df = pd.read_sql_query(query_possession, conn)
    defending_times = poss_df[poss_df['possessing_team'] != your_team_id]['seconds'].unique()

    # Expand defending seconds ±1s
    expanded_defending_seconds = set()
    for sec in defending_times:
        expanded_defending_seconds.update([sec - 1, sec, sec + 1])

    defending_tracking = tracking_df[
        tracking_df['seconds'].round().astype(int).isin(expanded_defending_seconds)
    ]

    # Keep only your players
    defending_tracking = defending_tracking[defending_tracking['team_id'] == your_team_id]

    return defending_tracking

# === PROCESS ALL MATCHES ===
conn = get_connection()

all_defending_tracking = pd.DataFrame()

for match_id in clean_sheet_match_ids:
    print(f"Processing match: {match_id}")
    df = get_defending_tracking_for_match(match_id, conn)
    all_defending_tracking = pd.concat([all_defending_tracking, df], ignore_index=True)

conn.close()

# === COMPUTE AVERAGE POSITIONS ===
avg_positions = all_defending_tracking.groupby(
    ['player_id', 'player_name', 'jersey_number']
).agg({'x': 'mean', 'y': 'mean'}).reset_index()

# === PLOT ===
pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
              pitch_length=105, pitch_width=68)
fig, ax = pitch.draw(figsize=(12, 8))

pitch.scatter(
    avg_positions['x'], avg_positions['y'],
    ax=ax, s=500, color='skyblue', edgecolor='black'
)

for _, row in avg_positions.iterrows():
    ax.text(row['x'], row['y'] + 1, f"{row['jersey_number']} - {row['player_name']}", 
            ha='center', fontsize=9)

ax.set_title("Average Defensive Shape (Clean Sheet Matches)", fontsize=16)
plt.tight_layout()
plt.show()
