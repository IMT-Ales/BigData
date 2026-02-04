-- Ensure airflow user exists (if docker env vars dont cover it)
-- CREATE ROLE airflow WITH LOGIN PASSWORD 'airflow';
-- CREATE DATABASE rte_data;
-- GRANT ALL PRIVILEGES ON DATABASE rte_data TO airflow;
-- Actually, just minimal init if needed. Docker handles most.
SELECT 1; 
