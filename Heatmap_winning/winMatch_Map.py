import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from mplsoccer import Pitch
from db_connection import get_connection

def plot_tracking_data(frame_df, minute, team_colors=None):
    """
    Plot één frame met spelerposities, in de stijl van je voorbeeldcode.
    frame_df: DataFrame met alle rijen voor dat ene frame (alle spelers).
    minute: de minuut (int) zodat we in de titel kunnen aangeven “Minuut X”.
    team_colors: optionele dict {team_id: color}, anders wordt TABLEAU_COLORS gebruikt.
    """
    pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
                  pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(12, 8))
    
    # Als er geen custom kleuren zijn doorgegeven, gebruik TABLEAU_COLORS
    if team_colors is None:
        colors = mpl.colors.TABLEAU_COLORS
        team_ids = frame_df['team_id'].unique()
        team_colors = {tid: c for tid, c in zip(team_ids, colors.values())}

    # Extract timestamp (bijvoorbeeld de eerste in dit frame)
    timestamp = frame_df['timestamp'].iloc[0]

    for _, row in frame_df.iterrows():
        x = row['x']
        y = row['y']
        player_name = row['player_name']
        team_id = row['team_id']
        jersey_no = row['jersey_number']
        
        # Plot bal
        if player_name == 'Ball':
            pitch.scatter(x, y, s=90, color='yellow', ax=ax, label='Ball')
        else:
            # Plot players
            pitch.scatter(x, y, s=100, color=team_colors.get(team_id, 'black'), ax=ax)
            # Annotatie
            ax.text(x + 2, y + 2, f"{player_name} ({jersey_no})", fontsize=8)
    
    ax.set_title(f"Frame snapshot in minuut {minute} (timestamp={timestamp})", fontsize=16)
    plt.tight_layout()
    return fig, ax

# -------------------------------
# HOOFDPROGRAMMA
# -------------------------------

# Parameters
game_id = '6mvh0ixx6p3frjttob5szqcr8'
output_folder = "minute_snapshots_frames"
os.makedirs(output_folder, exist_ok=True)

# Haal trackingdata op
conn = get_connection()
query = f"""
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y,
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
WHERE pt.game_id = '{game_id}';
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Converteer timestamp naar timedelta
df['timestamp'] = pd.to_timedelta(df['timestamp'])

# Eventueel bal uitsluiten als je dat wilt
# df = df[df['player_name'] != 'Ball']

# We nemen per minuut het LAATSTE frame (kun je ook veranderen in EERSTE)
for minute in range(10):
    start_int = pd.to_timedelta(f"{minute}min")
    end_int   = pd.to_timedelta(f"{minute+1}min")
    
    # Filter rijen in dit interval
    interval_df = df[(df['timestamp'] >= start_int) & (df['timestamp'] < end_int)]
    if interval_df.empty:
        print(f"Geen data in minuut {minute}")
        continue
    
    # Kies het LAATSTE frame_id in dit interval
    last_frame = interval_df['frame_id'].max()
    
    # Selecteer alleen de rijen van dat frame
    frame_df = interval_df[interval_df['frame_id'] == last_frame].copy()
    if frame_df.empty:
        print(f"Geen data voor het laatst beschikbare frame in minuut {minute}")
        continue
    
    # Plot dit frame
    fig, ax = plot_tracking_data(frame_df, minute)
    
    # Sla de figuur op
    output_path = os.path.join(output_folder, f"minute_{minute}_frame_{last_frame}.png")
    plt.savefig(output_path)
    plt.close(fig)
    print(f"Afbeelding opgeslagen: {output_path}")