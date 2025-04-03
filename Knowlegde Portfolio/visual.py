import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib as mpl
from db_connection import get_connection  # Importeer de connectie functie

# Data ophalen
conn = get_connection()
query = """
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE pt.game_id = '5uts2s7fl98clqz8uymaazehg';
"""
tracking_df = pd.read_sql_query(query, conn)
conn.close()

def plot_tracking_data(tracking_data, frame_id):
    """
    Plot de spelersposities op een voetbalveld voor een specifieke frame_id.
    tracking_data: DataFrame met kolommen [frame_id, timestamp, x, y, player_name, jersey_number, team_id]
    frame_id: het specifieke frame dat je wilt plotten.
    """
    # Filter de data voor de gekozen frame_id
    data_frame = tracking_data[tracking_data['frame_id'] == frame_id]

    # Check of er wel data is voor deze frame_id
    if data_frame.empty:
        print(f"Geen data gevonden voor frame_id: {frame_id}")
        return

    # We gaan ervan uit dat elke rij in deze frame dezelfde timestamp heeft
    timestamp = data_frame['timestamp'].iloc[0]

    # Krijg de unieke teams
    team_names = data_frame['team_id'].unique()
    
    # Definieer een kleurenmap voor elk team (hier gebruiken we TABLEAU_COLORS als voorbeeld)
    colors = mpl.colors.TABLEAU_COLORS
    color_map = {team: color for team, color in zip(team_names, colors.values())}
    
    # Maak een Pitch-object aan (105 x 68 is een gangbare maat)
    pitch = Pitch(
        pitch_color='grass', 
        line_color='white',
        pitch_type='opta',
        pitch_length=105, 
        pitch_width=68
    )
    fig, ax = pitch.draw(figsize=(12, 8))

    # Plot de spelers
    for _, row in data_frame.iterrows():
        x = row['x']
        y = row['y']
        player_name = row['player_name']
        team_name = row['team_id']
        jersey_no = row['jersey_number']

        # Plot de speler
        pitch.scatter(x, y, s=100, color=color_map[team_name], ax=ax)

        # Schrijf de naam en rugnummer bij de speler (iets verschoven)
        ax.text(x + 1, y + 1, f"{player_name} ({jersey_no})", fontsize=8, color='white')
    
    # Titel boven de plot
    ax.set_title(f'Player Positions at Event Timestamp: {timestamp}', fontsize=16)
    plt.tight_layout()
    plt.show()

# Kies een frame_id die je wilt bekijken, bijvoorbeeld het eerste unieke frame:
unique_frames = tracking_df['frame_id'].unique()
frame_id_example = unique_frames[0]

# Roep de plotfunctie aan
plot_tracking_data(tracking_df, frame_id_example)
