import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from db_connection import get_connection

# Maak verbinding en haal trackingdata op voor de gewenste game
conn = get_connection()
query = """
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, 
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE pt.game_id = '70wtfxx5kccxl5sxj1bvcd8us';
"""
tracking_df = pd.read_sql_query(query, conn)
conn.close()

# Debug: Bekijk de unieke team_id's in de trackingdata
print("Unieke team_id's:", tracking_df['team_id'].unique())

# Converteer de timestamp naar timedelta (ervan uitgaande dat de waarden als '0 days 00:00:00' zijn)
tracking_df['timestamp'] = pd.to_timedelta(tracking_df['timestamp'])

# Kies de gewenste team_id (bijvoorbeeld voor OH Leuven)
team_id = 'bw9wm8pqfzcchumhiwdt2w15c'
team_df = tracking_df[tracking_df['team_id'] == team_id].copy()

if team_df.empty:
    print(f"Geen data voor team met team_id: {team_id}")
else:
    # Voor elke speler binnen het team bepalen we het startpunt (laagste timestamp)
    start_positions = team_df.sort_values('timestamp').groupby('player_id').first().reset_index()
    
    # Maak het voetbalveld aan (105 x 68 meter) met mplsoccer
    pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta', 
                  pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(12, 8))
    
    # Plot de startposities als zwarte puntjes
    ax.scatter(start_positions['x'], start_positions['y'], color='black', s=50, label="Startpositie")
    
    # Voeg annotaties toe met spelernaam en rugnummer
    for idx, row in start_positions.iterrows():
        ax.text(row['x'] + 1, row['y'] + 1, f"{row['player_name']} ({row['jersey_number']})", 
                fontsize=10, color='red')
    
    ax.legend(loc='upper right')
    ax.set_title(f"Startposities Team {team_id}", fontsize=16)
    plt.tight_layout()
    plt.show()
