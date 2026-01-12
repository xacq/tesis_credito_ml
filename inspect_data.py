import pandas as pd

# Load the dataset
df = pd.read_csv('data/datos_credito_simulados.csv')

# Get column names
print("Column names:")
print(df.columns)

# Get value counts for 'score_interno'
print("\nValue counts for 'score_interno':")
print(df['score_interno'].value_counts())

# Display a few rows for each score to understand the profile
print("\nSample rows for each 'score_interno':")
for score in df['score_interno'].unique():
    if score != 'Analista':
        print(f"\nScore: {score}")
        print(df[df['score_interno'] == score].head(2))

# Display a few rows for 'Analista'
print("\nScore: Analista")
print(df[df['score_interno'] == 'Analista'].head())
