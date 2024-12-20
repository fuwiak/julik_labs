FROM apache/airflow:2.6.2-python3.9

USER root
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
USER airflow

RUN pip install --no-cache-dir requests psycopg2-binary optuna

COPY dags/ /opt/airflow/dags/

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
