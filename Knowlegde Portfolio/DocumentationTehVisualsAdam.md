# ⚽ Defensive Analysis Project – Out of Possession Behavior

This document provides an overview of the Python scripts used to analyze our team's **defensive behavior**, **structure**, and **vulnerabilities**, particularly when **out of possession**.

---

## 📂 File Overview

| File                                               | Description                                                        |
| -------------------------------------------------- | ------------------------------------------------------------------ |
| `01_initial_visual_test.py`                        | First experiment in visualizing data – used for sandboxing         |
| `02_defensive_turnover_zones.py`                   | Histogram of where we lost the ball across zones                   |
| `03_avg_defensive_positions_single_game.py`        | Average player positions during defense (one match)                |
| `04_rogue_defensive_shape.py`                      | _(Clarify purpose — appears to analyze irregular defensive shape)_ |
| `05_avg_defensive_shape_clean_sheets.py`           | Defensive shape in matches with clean sheets                       |
| `06_avg_defensive_shape_conceded.py`               | Defensive shape in matches where we conceded                       |
| `07_compare_defensive_shapes_clean_vs_conceded.py` | Overlay comparison of average defensive shape (clean vs conceded)  |
| `08_scatter_defensive_actions.py`                  | Scatter plot of tackles, interceptions, clearances, duels          |
| `09_opponent_progress_single_game.py`              | Opponent pass progression in one match                             |
| `10_opponent_progress_multiple_games.py`           | Same as above but across multiple matches                          |
| `11_defensive_losses_histogram_line.py`            | Histogram & line chart of lost defensive actions                   |
| `12_defensive_wins_line_histogram.py`              | Line & histogram of successful defensive actions                   |

---

## 🔍 Individual Script Summaries

### `01_turnover_heatmap.py`

**Purpose**:  
Generates a **heatmap of turnover locations** after possession sequences. Helps visualize where our team most often loses the ball on the pitch.

- Identifies turnovers using SQL window functions and possession grouping.
- Filters to only meaningful sequences (3+ actions before turnover).
- Uses `mplsoccer.Pitch` to plot a KDE heatmap of start positions of turnovers.

**Output**:  
🔥 Heatmap of where our team lost possession on the field.

```python
pitch.kdeplot(
    x=team_turnovers['start_x'],
    y=team_turnovers['start_y'],
    cmap='hot'
)
```

---

### **`02_defensive_turnover_zones.py`**

**Purpose**: Shows in which zones (third + side) the team lost possession.

**Output**: Bar chart showing counts per zone.

```python

team_turnovers['zone'] = team_turnovers['third'] + ' - ' + team_turnovers['side']

```

---

### `03_avg_defensive_positions_single_game.py`

**Purpose**: Computes and plots average positions of defenders during a single game’s defensive phases.

**Tech**: Uses `mplsoccer.Pitch`

---

### `04_rogue_defensive_shape.py`

**Purpose**: (To be clarified) Appears to analyze moments where defensive structure deviates significantly from average.

**Suggestion**: Define what "rogue" means in your tactical framework.

---

### `05_avg_defensive_shape_clean_sheets.py`

**Purpose**: Shows average defensive shape in matches with **zero goals conceded** (clean sheets).

**Output**: Player position map (blue)

---

### `06_avg_defensive_shape_conceded.py`

**Purpose**: Same as above but for matches where we conceded goals.

**Output**: Player position map (red)

---

### `07_compare_defensive_shapes_clean_vs_conceded.py`

**Purpose**: Overlay clean-sheet and conceded-shape positions for comparison.

**Output**: Blue (clean) vs Red (conceded) on same pitch

---

### `08_scatter_defensive_actions.py`

**Purpose**: Scatter plot of **defensive actions** (tackles, duels, clearances) during opponent possession.

**Logic**: Filters for out-of-possession moments only.

---

### `09_opponent_progress_single_game.py`

**Purpose**: Detects and visualizes how often opponents reached midfield or deeper in a single game.

**Zones**: Midfield / Defensive Third

---

### `10_opponent_progress_multiple_games.py`

**Purpose**: Same as #09 but across multiple **lost matches**.

**Output**: Grouped bar chart comparing each match

---

### `11_defensive_losses_histogram_line.py`

**Purpose**:

Analyzes **defensive actions in a match we lost**. Focuses on the **quantity and timing** of tackles, duels, interceptions, and clearances.

- **Histogram**: Counts of each defensive action type.

- **Line Graph**: Total defensive actions per minute.

```python

actions_per_min = df.groupby('minute').size()

```

**Visuals**:

- Bar chart of action types

- Line chart of actions across match time

---

### `12_defensive_wins_line_histogram.py`

**Purpose**:

Same analysis as above, but for a **match we won**. Helps compare volume and timing of successful defensive actions.

- Same plots: histogram by type, line chart by time
- Useful for identifying intensity or drop-off moments
  **Match result in script**: Win 2–1

---

## 🧪 Running the Project

1. Make sure `db_connection.py` is configured to your local or remote match data.

2. Install dependencies:

```bash

pip install pandas matplotlib mplsoccer

```

3. Run any script:

```bash

python 08_scatter_defensive_actions.py

```

---

## 📝 Suggestions

- Modularize shared logic (e.g., possession filter, tracking cleaner)

- Rename “rogue” for clarity if presenting to staff/analysts

- Use consistent plotting styles for comparison clarity

- Use image exports to include snapshots in match reports

---

## ✍️ Author

**Adam Bakhmadov**, 2025

_Data-driven tactical insights for team improvement._
