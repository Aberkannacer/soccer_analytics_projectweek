import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches
from db_connection import get_connection

# Data ophalen uit de database voor game_id '5wofhz4hm81f0lk0ay8sumfis'
conn = get_connection()
query = """
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y,
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE pt.game_id = '6aaebu7uj50ewu3irl3qmjg2c';
"""
tracking_df = pd.read_sql_query(query, conn)
conn.close()

player_id = 'l6y4o9t2b0jxaxo85oztok45'
player_df = tracking_df[tracking_df['player_id'] == player_id].copy()

if player_df.empty:
    print(f"Geen data voor speler met player_id: {player_id}")
else:
    # Converteer de timestamp naar timedelta (aangenomen dat de waarden als '0 days 00:00:00' zijn)
    player_df['timestamp'] = pd.to_timedelta(player_df['timestamp'])
    
    # Filter voor de tweede helft: data > 45 minuten
    second_half_df = player_df[player_df['timestamp'] > pd.to_timedelta("45min")]
    second_half_df = second_half_df.sort_values('timestamp').reset_index(drop=True)
    
    if second_half_df.empty:
        print("Geen data in de tweede helft van de match voor deze speler.")
    else:
        # Maak het voetbalveld aan (105 x 68 meter)
        pitch = Pitch(
            pitch_color='grass', 
            line_color='white',
            pitch_type='opta',
            pitch_length=105, 
            pitch_width=68
        )
        fig, ax = pitch.draw(figsize=(12, 8))
    
        # 1. HEATMAP (density plot) van de posities
        heatmap_set = sns.kdeplot(
            data=second_half_df,
            x='x', 
            y='y', 
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
    
        # 2. Plot de individuele posities als zwarte stippen (kleiner en transparanter)
        scat_positions = ax.scatter(
            second_half_df['x'], 
            second_half_df['y'], 
            color='black', 
            s=20, 
            alpha=0.5,
            zorder=2
        )
    
        # 3. Markeer het startpunt (eerste rij in second_half_df) met een rode marker
        start_point = second_half_df.iloc[0]
        scat_start = ax.scatter(
            start_point['x'], 
            start_point['y'], 
            color='red', 
            s=100, 
            marker='o',
            zorder=3
        )
    
        # 4. Dead zones: bereken de dichtheidsfunctie via gaussian_kde en markeer gebieden met lage dichtheid.
        x_vals = second_half_df['x'].values
        y_vals = second_half_df['y'].values
        values = np.vstack([x_vals, y_vals])
        kde = gaussian_kde(values, bw_method=0.5)
    
        # Gebruik veldafmetingen: x: 0-105, y: 0-68
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
    
        ax.set_title(f'Positie Heatmap voor speler B. Mechele (2e helft, >45 min) in game Club Brugge VS Gent', fontsize=16)
        plt.tight_layout()
        plt.show()
