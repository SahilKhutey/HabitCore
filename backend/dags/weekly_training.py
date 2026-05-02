from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from scripts.model_training import train_behavioral_models

default_args = {
    "owner": "habitcore",
    "retries": 1,
    "retry_delay": timedelta(hours=1),
}

with DAG(
    "weekly_model_training_v2",
    default_args=default_args,
    description="Retrains behavioral models on a weekly basis",
    schedule_interval="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ml", "training"],
) as dag:

    train_task = PythonOperator(
        task_id="train_behavioral_models",
        python_callable=train_behavioral_models,
    )
