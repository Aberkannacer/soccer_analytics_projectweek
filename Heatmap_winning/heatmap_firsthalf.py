import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches
from db_connection import get_connection

# Data ophalen uit de database
conn = get_connection()
query = """
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y,
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE pt.game_id = '6mvh0ixx6p3frjttob5szqcr8';
"""
tracking_df = pd.read_sql_query(query, conn)
conn.close()

player_id = 'l6y4o9t2b0jxaxo85oztok45'

player_df = tracking_df[tracking_df['player_id'] == player_id].copy()

if player_df.empty:
    print(f"Geen data voor speler met player_id: {player_id}")
else:
    # Converteer timestamp naar timedelta
    player_df['timestamp'] = pd.to_timedelta(player_df['timestamp'])
    
    # Filter voor de eerste helft: data <= 45 minuten
    first_half_df = player_df[player_df['timestamp'] <= pd.to_timedelta("45min")]
    first_half_df = first_half_df.sort_values('timestamp').reset_index(drop=True)
    
    if first_half_df.empty:
        print("Geen data in de eerste helft van de match voor deze speler.")
    else:
        # Maak het voetbalveld aan (105 x 68 meter)
        pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
                      pitch_length=105, pitch_width=68)
        fig, ax = pitch.draw(figsize=(12, 8))
    
        # 1. Teken een meer gedetailleerde density plot (heatmap) met meerdere contour-levels
        heatmap_set = sns.kdeplot(
            data=first_half_df,
            x='x',
            y='y',
            fill=True,
            alpha=0.6,
            thresh=0.05,
            cmap="Reds",
            bw_adjust=0.5,
            levels=10,           # <--- MEER contour-levels
            # cbar=True,         # (optioneel, alleen als je seaborn-versie dit ondersteunt)
            # cbar_kws={"label": "Density"}  # (optioneel)
            ax=ax
        )
        if heatmap_set.collections:
            heatmap_set.collections[0].set_label("Heatmap")
    
        # 2. Plot de individuele posities met kleinere, transparantere stippen
        scat_positions = ax.scatter(
            first_half_df['x'],
            first_half_df['y'],
            color='black',
            s=20,        # <--- Kleiner
            alpha=0.5,   # <--- Transparanter
            zorder=2     # Zorgt dat het boven de heatmap komt
        )
    
        # 3. Markeer het startpunt (eerste rij in first_half_df) met een rode marker
        start_point = first_half_df.iloc[0]
        scat_start = ax.scatter(
            start_point['x'],
            start_point['y'],
            color='red',
            s=100,
            marker='o',
            zorder=3
        )
    
        # 4. Dead zones: bereken een density via gaussian_kde en markeer gebieden met lage dichtheid.
        x_vals = first_half_df['x'].values
        y_vals = first_half_df['y'].values
        values = np.vstack([x_vals, y_vals])
        kde = gaussian_kde(values, bw_method=0.5)
    
        # Gebruik de veldafmetingen: x: 0-105, y: 0-68
        xgrid = np.linspace(0, 100, 200)
        ygrid = np.linspace(0, 100, 200)
        X, Y = np.meshgrid(xgrid, ygrid)
        positions = np.vstack([X.ravel(), Y.ravel()])
        Z = np.reshape(kde(positions).T, X.shape)
    
        # Stel bijvoorbeeld het 30e percentiel in als drempel voor de dead zones
        deadzone_threshold = np.percentile(Z, 30)
    
        # Plot de dead zones als een contourf (lichtblauw)
        contour_dead = ax.contourf(
            X,
            Y,
            Z,
            levels=[0, deadzone_threshold],
            colors=['lightblue'],
            alpha=0.4
        )
        deadzone_patch = mpatches.Patch(color='lightblue', alpha=0.4, label='Dead Zones')
    
        # Bouw de legenda op met duidelijke labels
        ax.legend(
            handles=[
                heatmap_set.collections[0] if heatmap_set.collections else None,
                deadzone_patch,
                scat_positions,
                scat_start
            ],
            labels=[
                "Heatmap",
                "Dead Zones",
                f"B. Mechele",
                "Startpunt"
            ],
            loc='upper right'
        )
    
        ax.set_title(f'Positie Heatmap voor speler B. Mechele (1e helft, <=45 min) in game Club Brugge VS Anderlecht', fontsize=16)
        plt.tight_layout()
        plt.show()
