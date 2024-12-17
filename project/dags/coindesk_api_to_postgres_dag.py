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

    task_fetch_and_insert()
