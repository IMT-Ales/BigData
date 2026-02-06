#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE DATABASE rte_data;
	GRANT ALL PRIVILEGES ON DATABASE rte_data TO airflow;
EOSQL
