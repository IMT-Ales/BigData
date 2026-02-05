from airflow import DAG, Dataset
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

sys.path.append("/opt/airflow/src")

from process_data import run_spark_job

db_name = os.getenv("MONGO_DB_NAME", "rte")
collection_name = os.getenv("MONGO_COLLECTION", "eco2mix_regional_tr")
dataset_uri = f"mongodb://{db_name}/{collection_name}"

RTE_DATASET = Dataset(dataset_uri)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

with DAG(
    'rte_processing',
    default_args=default_args,
    description='Process RTE data from MongoDB to Postgres using Spark',
    schedule=[RTE_DATASET],
    start_date=days_ago(1),
    catchup=False,
    tags=['spark', 'postgres', 'gte'],
) as dag:

    process_task = PythonOperator(
        task_id='process_rte_data_spark',
        python_callable=run_spark_job
    )

    process_task
