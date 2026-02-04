from airflow import DAG, Dataset
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import requests
import pymongo
import os
import json
from datetime import timedelta

RTE_API_URL = "https://reseaux-energies-rte.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/records"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "rte")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "eco2mix_regional_tr")

dataset_uri = f"mongodb://{DB_NAME}/{COLLECTION_NAME}"
RTE_DATASET = Dataset(dataset_uri)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_and_store_data(**kwargs):
    limit = 100
    offset = 0
    total_count = 0
    
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    collection.delete_many({})
    print(f"Cleared collection {COLLECTION_NAME}")

    while True:
        # Limit from our api
        if offset + limit > 10000:
            print("Reached API limit of 10000 records.")
            break

        params = {
            "limit": limit,
            "offset": offset
        }
        
        print(f"Fetching offset {offset}...")
        response = requests.get(RTE_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            break

        collection.insert_many(results)
        count = len(results)
        total_count += count
        print(f"Inserted {count} records.")
        
        if count < limit:
            break
            
        offset += limit

    print(f"Total records ingested: {total_count}")
    client.close()

with DAG(
    'rte_ingestion',
    default_args=default_args,
    description='Ingest RTE eCO2mix Regional data to MongoDB',
    schedule='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['rte', 'mongodb'],
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_rte_data',
        python_callable=fetch_and_store_data,
        outlets=[RTE_DATASET]
    )

    ingest_task
