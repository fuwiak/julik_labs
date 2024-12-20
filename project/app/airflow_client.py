import requests
from fastapi import HTTPException

AIRFLOW_API_URL = "http://airflow-webserver:8080/api/v1"

def trigger_dag(dag_id: str):
    # Предполагается, что Airflow API доступен без аутентификации или настроен соответствующим образом
    url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"
    response = requests.post(url, json={"conf": {}}, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return True
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
