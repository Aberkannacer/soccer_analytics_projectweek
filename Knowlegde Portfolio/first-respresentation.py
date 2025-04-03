# turnover_heatmap.py
import pandas as pd
from db_connection import get_connection
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# Connect to DB and run the possession query
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

# Load the possession-ending actions
possession_df = pd.read_sql_query(query, conn)

# Close connection
conn.close()

# 🔥 Plot turnover heatmap for your team
your_team_id = possession_df['team_id'].unique()[0]  # You can adjust this

team_turnovers = possession_df[possession_df['team_id'] == your_team_id]

pitch = Pitch(pitch_color='grass', line_color='white', pitch_type='opta',
              pitch_length=105, pitch_width=68)
fig, ax = pitch.draw(figsize=(10, 7))

pitch.kdeplot(
    x=team_turnovers['start_x'],
    y=team_turnovers['start_y'],
    ax=ax,
    cmap='hot',
    fill=True,
    levels=100,
    alpha=0.7
)

ax.set_title('Turnover Heatmap - Where Possession Was Lost', fontsize=14)
plt.show()
