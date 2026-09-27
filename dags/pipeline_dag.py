from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow/data_generation')

from generate_daily_transactions import generer_transactions_du_jour
from load_to_postgres import charger_transactions

default_args = {
    "owner": "Sira",
    "retries": 1, #Réessaie une fois en cas d'échec
    "retry_delay": timedelta(minutes=5), #Attend 5mn avant de réessayer
}

def tache_generer_et_charger(**context):
    date_execution = context["logical_date"] #Date que la dag est entrain de traiter
    df = generer_transactions_du_jour(date_execution)
    charger_transactions(df)


with DAG(
    dag_id="mobile_money_pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["mobile-money", "elt"],
) as dag:

    generer_et_charger = PythonOperator(
        task_id="generer_et_charger_transactions",
        python_callable=tache_generer_et_charger,
    )











