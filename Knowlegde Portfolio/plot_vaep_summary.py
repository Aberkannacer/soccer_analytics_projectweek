import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("vaep_with_actions.csv")

# Top players by total VAEP
top_players = df.groupby('player_id').agg({
    'vaep': 'sum'
}).sort_values(by='vaep', ascending=False).head(5)

# Plot
top_players['vaep'].plot(kind='bar', color='teal', edgecolor='black')
plt.title("Top 5 Players by Total VAEP Value")
plt.xlabel("Player ID")
plt.ylabel("Total VAEP")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
