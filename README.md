# Создание проекта

```bash 
docker-compose up --build -d

```

```markdown
- Проверка Airflow DAG: [http://localhost:8080](http://localhost:8080)
- Проверка FastAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Проверка Prometheus: [http://localhost:9090](http://localhost:9090)
- Проверка Grafana: [http://localhost:3000](http://localhost:3000)
```

```markdown

доги для проверки ошибок
     docker-compose logs airflow-webserver
     docker-compose logs airflow-scheduler
     docker-compose logs postgres
     docker-compose logs fastapi
     docker-compose logs prometheus
     docker-compose logs grafana

```


## Лабораторная 2 Инструменты анализа данных


```bash
docker-compose exec postgres bash
psql -U airflow -d airflow
SELECT * FROM coindesk_info LIMIT 10;
```

Проверка на наличие данныхSELECT * FROM coindesk_info LIMIT 10; в таблицы

```sql


```


## Лабораторная 3 Инструменты анализа данных «FastApi и запуск Dag-ов Airflow»

```markdown
Связанные файлы
- airflow_client.py
- crud.py
- database.py
- main.py
- models.py
- schemas.py

```

## Лабораторная 4 Инструменты анализа данных «Настройка мониторинга: Grafana+Prometheus»
- prometheus_metrics.py

## Лабораторная 5 Инструменты анализа данных «Анализ системы и подбора гиперпараметров»

```markdown
optuna_module.py
```





