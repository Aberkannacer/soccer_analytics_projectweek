import pandas as pd
from db_connection import get_connection
from socceraction.spadl import config as spadl_config
from socceraction.spadl.config import actiontypes
from socceraction.vaep import features, labels, formula
from socceraction.vaep.model import load_vaep_model

# === Load actions from your database ===
conn = get_connection()
query = """
SELECT * FROM spadl_actions
WHERE game_id = '6mvh0ixx6p3frjttob5szqcr8'
ORDER BY id
"""
actions = pd.read_sql_query(query, conn)
conn.close()

# === Drop unused or problematic columns ===
actions = actions.drop(columns=['bodypart'], errors='ignore')

# === Create features and labels (using built-in functions) ===
X = features.features(actions, spadl_config)
Y = labels.labels(actions, spadl_config)

# === Load pretrained VAEP models ===
scoring_model, conceding_model = model.load_vaep_model()

# === Predict probabilities ===
Pscores = scoring_model.predict_proba(X)[:, 1]
Pconcedes = conceding_model.predict_proba(X)[:, 1]

# === Compute VAEP values ===
vaep_values = formula.value(Pscores, Pconcedes)

# === Add values to dataframe ===
actions['Pscore'] = Pscores
actions['Pconcede'] = Pconcedes
actions['vaep'] = vaep_values

# === Add readable action type name (optional) ===
id_to_type = {i: name for i, name in enumerate(actiontypes.names)}
actions['action_name'] = actions['action_type'].map(id_to_type)

# === Save to CSV ===
actions.to_csv("vaep_with_actions.csv", index=False)
print("✅ VAEP values generated and saved to vaep_with_actions.csv")
