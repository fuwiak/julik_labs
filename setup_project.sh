#!/bin/bash

# Define the directory structure
mkdir -p project/{dags,app,alembic/versions}

# Create placeholder files
touch project/dags/coindesk_api_to_postgres_dag.py

touch project/app/{main.py,database.py,models.py,schemas.py,crud.py,airflow_client.py,optuna_module.py,text_analysis.py,prometheus_metrics.py}

touch project/alembic/{env.py,alembic.ini}

touch project/{Dockerfile,Dockerfile.fastapi,docker-compose.yaml,requirements.txt}

# Add a message for the user
echo "Project structure created successfully."
