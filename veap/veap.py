import pandas as pd
import matplotlib.pyplot as plt

# Simuleer VAEP-scores voor B. Mechele per matchresultaat
data = {
    'Match Result': ['Win', 'Draw', 'Loss'],
    'VAEP Score': [0.45, 0.28, -0.12]  # voorbeeldwaarden – vervang door echte scores
}

df = pd.DataFrame(data)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(df['Match Result'], df['VAEP Score'], color=['green', 'orange', 'red'])

# Voeg labels toe boven de balken
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5 if height >= 0 else -15),
                textcoords='offset points',
                ha='center', va='bottom' if height >= 0 else 'top',
                fontsize=10, color='black')

# Titels en labels
ax.set_title('B. Mechele - VAEP Score per Match Result', fontsize=14)
ax.set_ylabel('VAEP Score')
ax.set_ylim(-0.2, 0.6)
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
