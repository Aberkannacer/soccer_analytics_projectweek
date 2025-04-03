import pandas as pd
from db_connection import get_connection

# Stel de gewenste team_id in
team_id = '1oyb7oym5nwzny8vxf03szd2h'

# Maak verbinding met de database
conn = get_connection()

# Haal de wedstrijden op, inclusief teamnamen voor thuis en uit
query = f"""
SELECT m.match_id,
       m.home_team_id,
       ht.team_name AS home_team_name,
       m.away_team_id,
       at.team_name AS away_team_name,
       m.home_score,
       m.away_score
FROM matches m
LEFT JOIN teams ht ON m.home_team_id = ht.team_id
LEFT JOIN teams at ON m.away_team_id = at.team_id
WHERE m.home_team_id = '{team_id}'
   OR m.away_team_id = '{team_id}';
"""

matches_df = pd.read_sql_query(query, conn)
conn.close()

# Definieer een functie om het resultaat voor het team te bepalen (Win, Loss of Draw)
def determine_result(row, team_id):
    if row['home_team_id'] == team_id:
        if row['home_score'] > row['away_score']:
            return 'Win'
        elif row['home_score'] < row['away_score']:
            return 'Loss'
        else:
            return 'Draw'
    elif row['away_team_id'] == team_id:
        if row['away_score'] > row['home_score']:
            return 'Win'
        elif row['away_score'] < row['home_score']:
            return 'Loss'
        else:
            return 'Draw'
    else:
        return 'N/A'

# Voeg de kolom 'result' toe aan de DataFrame
matches_df['result'] = matches_df.apply(lambda row: determine_result(row, team_id), axis=1)

# Optioneel: herschik de kolommen voor een duidelijk overzicht
columns_order = ['match_id', 'home_team_id', 'home_team_name',
                 'away_team_id', 'away_team_name', 'home_score', 'away_score', 'result']
matches_df = matches_df[columns_order]

# Toon de resultaten
print(matches_df)
