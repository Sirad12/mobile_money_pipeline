import pandas as pd
from load_to_postgres import charger_transactions

df = pd.read_csv("../transactions_historique.csv")
charger_transactions(df)