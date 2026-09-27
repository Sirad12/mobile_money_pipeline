import pandas as pd
df = pd.read_csv("transactions_historique.csv")

print(df["montant"].describe())
print("-" * 50)

print(df["type_transaction"].value_counts(normalize=True))
print("-" * 50)

print(df["statut"].value_counts(normalize=True))