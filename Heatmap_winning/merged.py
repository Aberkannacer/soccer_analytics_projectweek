import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches
from db_connection import get_connection

# Gebruik het juiste game_id
game_id = '6mvh0ixx6p3frjttob5szqcr8'
player_id = 'l6y4o9t2b0jxaxo85oztok45'

# Database connectie en trackingdata ophalen
conn = get_connection()
query = f"""
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y,
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE pt.game_id = '{game_id}';
"""
tracking_df = pd.read_sql_query(query, conn)
conn.close()

# Filter op specifieke speler
player_df = tracking_df[tracking_df['player_id'] == player_id].copy()

if player_df.empty:
    print(f"Geen data voor speler met player_id: {player_id}")
else:
    player_df['timestamp'] = pd.to_timedelta(player_df['timestamp'])
    both_halves_df = player_df.sort_values('timestamp').reset_index(drop=True)

    if both_halves_df.empty:
        print("Geen data voor de volledige match.")
    else:
        pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
                      pitch_length=105, pitch_width=68)
        fig, ax = pitch.draw(figsize=(12, 8))

        # 1. Heatmap
        heatmap_set = sns.kdeplot(
            data=both_halves_df,
            x='x', y='y',
            fill=True,
            alpha=0.6,
            thresh=0.05,
            cmap="Reds",
            bw_adjust=0.5,
            levels=10,
            ax=ax
        )
        if heatmap_set.collections:
            heatmap_set.collections[0].set_label("Heatmap")

        # 2. Posities
        scat_positions = ax.scatter(
            both_halves_df['x'], both_halves_df['y'],
            color='black', s=20, alpha=0.5, zorder=2
        )

        # 3. Startpunt
        start_point = both_halves_df.iloc[0]
        scat_start = ax.scatter(
            start_point['x'], start_point['y'],
            color='red', s=100, marker='o', zorder=3
        )

        # 4. Dead zones
        x_vals = both_halves_df['x'].values
        y_vals = both_halves_df['y'].values
        values = np.vstack([x_vals, y_vals])
        kde = gaussian_kde(values, bw_method=0.5)

        xgrid = np.linspace(0, 100, 200)
        ygrid = np.linspace(0, 100, 200)
        X, Y = np.meshgrid(xgrid, ygrid)
        positions = np.vstack([X.ravel(), Y.ravel()])
        Z = np.reshape(kde(positions).T, X.shape)

        deadzone_threshold = np.percentile(Z, 30)

        contour_dead = ax.contourf(
            X, Y, Z,
            levels=[0, deadzone_threshold],
            colors=['lightblue'],
            alpha=0.4
        )
        deadzone_patch = mpatches.Patch(color='lightblue', alpha=0.4, label='Dead Zones')

        # Legenda
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
                "B. Mechele",
                "Startpunt"
            ],
            loc='upper right'
        )

        ax.set_title("Gecombineerde Positie Heatmap voor B. Mechele (Volledige Match) in game Club Brugge VS Anderlecht", fontsize=16)
        plt.tight_layout()
        plt.show()
