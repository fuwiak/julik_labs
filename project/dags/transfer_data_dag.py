from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'retries': 1
}

with DAG(
    dag_id='transfer_data',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False
) as dag:

    create_y_table = PostgresOperator(
        task_id='create_y_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS Y (
            id SERIAL PRIMARY KEY,
            num INTEGER NOT NULL,
            dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    transfer_data = PostgresOperator(
        task_id='transfer_data',
        postgres_conn_id='postgres_default',
        sql="""
        INSERT INTO Y (num, dt)
        SELECT num, CURRENT_TIMESTAMP
        FROM X;
        """
    )

    create_y_table >> transfer_data
