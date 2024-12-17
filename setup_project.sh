#!/usr/bin/env bash
set -e

# Создаем директорию проекта и подпапку для DAG'ов
mkdir -p project/dags

# Создаем Dockerfile
cat > project/Dockerfile <<EOF
FROM apache/airflow:2.6.2-python3.9

USER root
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
USER airflow

RUN pip install --no-cache-dir requests psycopg2-binary

COPY dags/ /opt/airflow/dags/

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
EOF

# Создаем docker-compose.yaml
cat > project/docker-compose.yaml <<EOF
version: '3.9'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airflow -d airflow"]
      interval: 5s
      timeout: 5s
      retries: 5

  airflow-webserver:
    build: .
    restart: always
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__FERNET_KEY: 'somethingrandom12345'
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'false'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    ports:
      - "8080:8080"
    command: >
      bash -c "
      airflow db upgrade &&
      airflow users create --username admin --password admin --firstname Air --lastname Flow --role Admin --email admin@example.com &&
      airflow webserver
      "

  airflow-scheduler:
    build: .
    restart: always
    depends_on:
      - postgres
      - airflow-webserver
    environment:
      AIRFLOW__CORE__FERNET_KEY: 'somethingrandom12345'
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    command: >
      bash -c "
      airflow scheduler
      "
EOF

# Создаем DAG файл
cat > project/dags/coindesk_api_to_postgres_dag.py <<EOF
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
import requests
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1
}

def fetch_and_insert(**context):
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(url)
    data = response.json()

    time_data = data.get('time', {})
    disclaimer = data.get('disclaimer')
    chart_name = data.get('chartName')
    bpi_data = data.get('bpi', {})

    time_updated_str = time_data.get('updated')
    time_updated_iso_str = time_data.get('updatedISO')
    time_updated_iso = datetime.fromisoformat(time_updated_iso_str.replace('Z', '+00:00')) if time_updated_iso_str else None
    time_updated_uk = time_data.get('updateduk')

    pg_hook = PostgresHook(postgres_conn_id='postgres_default')

    insert_info_sql = """
        INSERT INTO coindesk_info (time_updated, time_updated_iso, time_updated_uk, disclaimer, chart_name)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    info_id = pg_hook.get_first(insert_info_sql, parameters=(time_updated_str, time_updated_iso, time_updated_uk, disclaimer, chart_name))[0]

    insert_bpi_sql = """
        INSERT INTO coindesk_bpi (coindesk_info_id, currency_code, currency_symbol, rate, description, rate_float)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    for currency_code, currency_info in bpi_data.items():
        pg_hook.run(insert_bpi_sql, parameters=(
            info_id,
            currency_info.get('code'),
            currency_info.get('symbol'),
            currency_info.get('rate'),
            currency_info.get('description'),
            currency_info.get('rate_float')
        ))

with DAG(
    'coindesk_api_to_postgres',
    default_args=default_args,
    description='DAG для получения данных из Coindesk API и сохранения в Postgres',
    schedule_interval='@hourly',
    catchup=False
) as dag:

    task_fetch_and_insert = PythonOperator(
        task_id='fetch_and_insert_data',
        python_callable=fetch_and_insert,
        provide_context=True
    )

    task_fetch_and_insert
EOF

echo "Project structure created successfully."
