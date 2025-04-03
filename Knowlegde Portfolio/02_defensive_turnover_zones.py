import pandas as pd
import matplotlib.pyplot as plt
from db_connection import get_connection

# Connect and fetch turnover data again
conn = get_connection()
query = """
WITH action_changes AS (
    SELECT
        a.*,
        LAG(a.team_id) OVER (ORDER BY a.period_id, a.seconds, a.id) AS prev_team_id,
        LEAD(a.team_id) OVER (ORDER BY a.period_id, a.seconds, a.id) AS next_team_id
    FROM
        spadl_actions a
    WHERE
        a.game_id = '5uts2s7fl98clqz8uymaazehg'
),

possession_markers AS (
    SELECT
        *,
        CASE WHEN prev_team_id IS NULL OR team_id != prev_team_id THEN 1 ELSE 0 END AS is_new_possession
    FROM
        action_changes
),

possession_sequences AS (
    SELECT
        *,
        SUM(is_new_possession) OVER (ORDER BY period_id, seconds, id) AS possession_group
    FROM
        possession_markers
),

possession_stats AS (
    SELECT
        possession_group,
        team_id,
        COUNT(*) AS action_count,
        MAX(id) AS last_action_id
    FROM
        possession_sequences
    GROUP BY
        possession_group, team_id
)

SELECT
    a.id AS action_id,
    a.game_id,
    a.period_id,
    a.seconds AS time_seconds,
    p.player_name,
    t.team_name AS team_losing_possession,
    nt.team_name AS team_gaining_possession,
    a.action_type AS type_name,
    a.result AS result_name,
    ps.action_count AS consecutive_team_actions,
    a.start_x,
    a.start_y,
    a.end_x,
    a.end_y,
    a.id AS original_event_id,
    a.team_id
FROM
    possession_sequences a
JOIN
    possession_stats ps ON a.possession_group = ps.possession_group 
                        AND a.team_id = ps.team_id
                        AND a.id = ps.last_action_id  
JOIN
    players p ON a.player_id = p.player_id
JOIN
    teams t ON a.team_id = t.team_id
LEFT JOIN
    teams nt ON a.next_team_id = nt.team_id
WHERE
    ps.action_count >= 3  
    AND a.team_id != a.next_team_id  
    AND a.next_team_id IS NOT NULL  
ORDER BY
    a.period_id,
    a.seconds,
    a.id;
"""

possession_df = pd.read_sql_query(query, conn)
conn.close()

# Filter your team
your_team_id = possession_df['team_id'].unique()[0]
team_turnovers = possession_df[possession_df['team_id'] == your_team_id]

# Define zones (you can tweak boundaries)
def classify_zone(x, y):
    if x < 35:
        return 'Defensive Third'
    elif x < 70:
        return 'Middle Third'
    else:
        return 'Attacking Third'

def classify_side(y):
    if y < 22.6:
        return 'Left'
    elif y < 45.3:
        return 'Center'
    else:
        return 'Right'

team_turnovers['third'] = team_turnovers['start_x'].apply(lambda x: classify_zone(x, 0))
team_turnovers['side'] = team_turnovers['start_y'].apply(classify_side)

# Combine zones
team_turnovers['zone'] = team_turnovers['third'] + ' - ' + team_turnovers['side']

# Count zones
zone_counts = team_turnovers['zone'].value_counts().sort_values(ascending=False)

# Plot bar chart
plt.figure(figsize=(10, 6))
zone_counts.plot(kind='bar', color='teal', edgecolor='black')
plt.title('Turnovers by Field Zone')
plt.xlabel('Zone of Possession Loss')
plt.ylabel('Number of Turnovers')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(True)
plt.show()
