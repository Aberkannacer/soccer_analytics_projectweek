import pandas as pd
from db_connection import get_connection

# Data ophalen uit de database en de keeper uitsluiten (keeper = jersey_number 33)
conn = get_connection()
query = """
SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, 
       p.jersey_number, p.player_name, p.team_id
FROM player_tracking pt
JOIN players p ON pt.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
WHERE pt.game_id = '5uts2s7fl98clqz8uymaazehg'
  AND p.jersey_number <> 33;
"""
tracking_df = pd.read_sql_query(query, conn)
conn.close()

# Converteer de timestamp-kolom naar timedelta zodat we ermee kunnen rekenen
tracking_df['timestamp'] = pd.to_timedelta(tracking_df['timestamp'])

# Bepaal het allereerste moment in de wedstrijd (bijv. timestamp = 0)
start_time = tracking_df['timestamp'].min()
start_df = tracking_df[tracking_df['timestamp'] == start_time].copy()

# Stel de doelpositie in; hier nemen we als voorbeeld de linkerzijde, midden in de hoogte (0,34)
goal_x, goal_y = 0, 34

# Bereken de Euclidische afstand tot het doel voor elk datapunt in het beginmoment
start_df['distance_to_goal'] = ((start_df['x'] - goal_x)**2 + (start_df['y'] - goal_y)**2)**0.5

# Zoek het datapunt (en daarmee de speler) met de minimale afstand tot het doel
defender_candidate = start_df.loc[start_df['distance_to_goal'].idxmin()]

print("Defender candidate:")
print(defender_candidate[['player_id', 'player_name', 'jersey_number', 'distance_to_goal']])
