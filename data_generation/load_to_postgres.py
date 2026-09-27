from sqlalchemy import create_engine
import pandas as pd
import os

DB_USER = "airflow"
DB_PASSWORD = "airflow"
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = "5432"
DB_NAME = "mobile_money_db"

def get_engine():
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_string)

def charger_transactions(df, table_name="transactions", schema="raw"):
    engine = get_engine()
    df.to_sql(
        table_name,
        engine,
        schema=schema,
        if_exists="append",
        index=False
    )
    print(f"{len(df)} lignes chargées dans {schema}.{table_name}")