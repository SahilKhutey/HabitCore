from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from scripts.feature_engineering import compute_daily_features
from scripts.pattern_detection import detect_patterns
from scripts.insights import generate_insights

default_args = {
    "owner": "habitcore",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def run_features(**context):
    # Airflow data_interval_start is the logical date
    run_date = context["data_interval_start"].strftime('%Y-%m-%d')
    compute_daily_features(run_date)

def run_patterns(**context):
    run_date = context["data_interval_start"].strftime('%Y-%m-%d')
    detect_patterns(run_date)

def run_insights(**context):
    run_date = context["data_interval_start"].strftime('%Y-%m-%d')
    generate_insights(run_date)

with DAG(
    "daily_behavior_pipeline_v2",
    default_args=default_args,
    description="Core behavioral intelligence pipeline",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=True, # Enable backfilling
    max_active_runs=1, # Prevent concurrency issues during backfill
    tags=["intelligence", "production"],
) as dag:

    t1 = PythonOperator(
        task_id="extract_features",
        python_callable=run_features,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id="detect_patterns",
        python_callable=run_patterns,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id="generate_insights",
        python_callable=run_insights,
        provide_context=True,
    )

    t1 >> t2 >> t3
