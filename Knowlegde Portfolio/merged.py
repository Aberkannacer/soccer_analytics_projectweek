import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from db_connection import get_connection

# Data ophalen uit de database voor een specifieke game
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

# Kies de gewenste player_id (vervang dit met een geldige id voor een verdediger)
player_id = 'awckr8ajqo4vstzghb59rkwkp'
player_df = tracking_df[tracking_df['player_id'] == player_id].copy()

if player_df.empty:
    print(f"Geen data voor speler met player_id: {player_id}")
else:
    # Converteer de timestamp-kolom naar timedelta (ervan uitgaande dat deze als '0 days 00:00:00' zijn)
    player_df['timestamp'] = pd.to_timedelta(player_df['timestamp'])
    # Sorteer op timestamp
    player_df = player_df.sort_values('timestamp').reset_index(drop=True)
    
    # Splits de data in eerste helft (<=45min) en tweede helft (>45min)
    first_half_df = player_df[player_df['timestamp'] <= pd.to_timedelta("45min")]
    second_half_df = player_df[player_df['timestamp'] > pd.to_timedelta("45min")]
    
    # Creëer een figuur met twee subplots (één voor elke helft)
    fig, axs = plt.subplots(1, 2, figsize=(24, 8))
    
    # Definieer een pitch met standaardafmetingen
    pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta', 
                  pitch_length=105, pitch_width=68)
    
    # Eerste helft (links)
    pitch.draw(ax=axs[0])
    sns.kdeplot(
        data=first_half_df,
        x='x',
        y='y',
        fill=True,
        alpha=0.6,
        thresh=0.05,
        cmap="Reds",
        bw_adjust=0.5,
        ax=axs[0]
    )
    axs[0].scatter(first_half_df['x'], first_half_df['y'], color='black', s=30, alpha=0.7, label=f"Player {player_id}")
    if not first_half_df.empty:
        start_point_first = first_half_df.iloc[0]
        axs[0].scatter(start_point_first['x'], start_point_first['y'], color='red', s=100, marker='o', label="Startpunt")
        axs[0].text(start_point_first['x']+2, start_point_first['y']+2, player_id, fontsize=10, color='red')
    axs[0].legend(loc='upper right')
    axs[0].set_title(f'Eerste Helft (0-45min)', fontsize=16)
    
    # Tweede helft (rechts)
    pitch.draw(ax=axs[1])
    sns.kdeplot(
        data=second_half_df,
        x='x',
        y='y',
        fill=True,
        alpha=0.6,
        thresh=0.05,
        cmap="Reds",
        bw_adjust=0.5,
        ax=axs[1]
    )
    axs[1].scatter(second_half_df['x'], second_half_df['y'], color='black', s=30, alpha=0.7, label=f"Player {player_id}")
    if not second_half_df.empty:
        start_point_second = second_half_df.iloc[0]
        axs[1].scatter(start_point_second['x'], start_point_second['y'], color='red', s=100, marker='o', label="Startpunt")
        axs[1].text(start_point_second['x']+2, start_point_second['y']+2, player_id, fontsize=10, color='red')
    axs[1].legend(loc='upper right')
    axs[1].set_title(f'Tweede Helft (>45min)', fontsize=16)
    
    plt.tight_layout()
    plt.show()
