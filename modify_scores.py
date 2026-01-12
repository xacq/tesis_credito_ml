import pandas as pd
import numpy as np

def assign_score(row):
    if row['score_interno'] == 'Analista':
        if row['dias_mora_prom'] > 10:
            return 'Rechazado'
        elif row['riesgo_real'] == 1:
            return 'A'
        else:
            # Randomly assign AAA or AA
            return 'AA' 
    return row['score_interno']

df = pd.read_csv('data/datos_credito_simulados.csv')

df['score_interno'] = df.apply(assign_score, axis=1)

df.to_csv('data/datos_credito_simulados.csv', index=False)

print("Processing complete. The file 'data/datos_credito_simulados.csv' has been updated.")
