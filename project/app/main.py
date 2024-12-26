from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from datetime import datetime
import requests

# Подключаем ваши локальные модули
from database import get_db
from crud import get_info, create_info, update_info, delete_info
from airflow_client import trigger_dag
from optuna_module import run_optuna
from text_analysis import analyze_text

# Подключаем модели
from models import CallsLog, TextAnalysis, TextAnalysisReport

from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.sql import text as sql_text

app = FastAPI(title="Full System")

# Прометей-метрики
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")


# --- ФУНКЦИЯ: лог в calls_log (уже была) ---
def log_call(db: Session, endpoint: str, status: str, result: str):
    call = CallsLog(endpoint=endpoint, status=status, result=result, timestamp=datetime.utcnow())
    db.add(call)
    db.commit()


# --- ФУНКЦИЯ: лог в text_analysis_report (новое) ---
def log_report(db: Session, request_type: str, result: str, error_type: str = None):
    new_report = TextAnalysisReport(
        request_type=request_type,
        result=result,
        error_type=error_type,
        created_at=datetime.utcnow()
    )
    db.add(new_report)
    db.commit()


# --- Существующие эндпоинты для coindesk_info ---
@app.get("/info/{info_id}")
def read_info_endpoint(info_id: int, db: Session = Depends(get_db)):
    info = get_info(db, info_id)
    if not info:
        log_call(db, f"/info/{info_id}", "not_found", "")
        raise HTTPException(status_code=404, detail="Not found")
    log_call(db, f"/info/{info_id}", "success", "record_retrieved")
    return info

@app.post("/info")
def create_info_endpoint(time_updated: str, disclaimer: str, chart_name: str, db: Session = Depends(get_db)):
    obj = create_info(db, time_updated, disclaimer, chart_name)
    log_call(db, "/info", "success", f"created_id_{obj.id}")
    return {"id": obj.id}

@app.put("/info/{info_id}")
def update_info_endpoint(info_id: int, time_updated: str = None, disclaimer: str = None, chart_name: str = None, db: Session = Depends(get_db)):
    updated_obj = update_info(db, info_id, time_updated=time_updated, disclaimer=disclaimer, chart_name=chart_name)
    if not updated_obj:
        log_call(db, f"/info/{info_id}", "not_found", "")
        raise HTTPException(status_code=404, detail="Not found")
    log_call(db, f"/info/{info_id}", "success", "updated")
    return {"status": "updated"}

@app.delete("/info/{info_id}")
def delete_info_endpoint(info_id: int, db: Session = Depends(get_db)):
    success = delete_info(db, info_id)
    if not success:
        log_call(db, f"/info/{info_id}", "not_found", "")
        raise HTTPException(status_code=404, detail="Not found")
    log_call(db, f"/info/{info_id}", "success", "deleted")
    return {"status": "deleted"}


# --- Вызов дага Airflow (как раньше) ---
@app.post("/trigger_dag/{dag_id}")
def trigger_dag_endpoint(dag_id: str, db: Session = Depends(get_db)):
    try:
        trigger_dag(dag_id)
        log_call(db, f"/trigger_dag/{dag_id}", "success", "dag_triggered")
        return {"status": "DAG triggered"}
    except HTTPException as e:
        log_call(db, f"/trigger_dag/{dag_id}", "error", str(e))
        raise


# --- Оптимизация гиперпараметров (Optuna) ---
@app.post("/optuna_run")
def optuna_run_endpoint(n_trials: int, low: float, high: float, db: Session = Depends(get_db)):
    try:
        run_obj = run_optuna(db, n_trials, low, high)
        # Лог в calls_log
        log_call(db, "/optuna_run", "success", f"run_id_{run_obj.id}")
        # Лог в text_analysis_report (хоть это и "optuna", но для отчётности)
        log_report(db, "optuna_run", "Success")
        return {
            "run_id": run_obj.id,
            "best_value": str(run_obj.best_value),
            "best_params": run_obj.best_params
        }
    except Exception as e:
        log_call(db, "/optuna_run", "error", str(e))
        log_report(db, "optuna_run", "Error", error_type=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# --- Анализ текста (новое + сохранили старый вызов log_call) ---
@app.post("/analyze_text")
def analyze_text_endpoint(text: str, db: Session = Depends(get_db)):
    """
    Анализ текста по ключевым словам,
    результат пишем в text_analysis и в логи.
    """
    try:
        # 1) Анализируем
        result = analyze_text(text)

        # 2) Сохраняем в таблицу text_analysis
        new_rec = TextAnalysis(text=text, result=result)
        db.add(new_rec)
        db.commit()

        # 3) Логируем в calls_log (как раньше)
        log_call(db, "/analyze_text", "success", result)

        # 4) Логируем в text_analysis_report (для базовых отчётов)
        log_report(db, "analyze_text", result)

        return {"result": result}
    except Exception as e:
        log_call(db, "/analyze_text", "error", str(e))
        log_report(db, "analyze_text", "Error", error_type=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# --- Пример отчётов по таблице calls_log (как было) ---
@app.get("/reports/calls")
def calls_report(db: Session = Depends(get_db)):
    data = db.execute(sql_text("""
        SELECT endpoint, status, COUNT(*) as cnt
        FROM calls_log
        GROUP BY endpoint, status
    """)).fetchall()
    return [{"endpoint": r[0], "status": r[1], "count": r[2]} for r in data]


# --- Дополнительный эндпоинт: отчёты text_analysis_report (при желании) ---
@app.get("/reports/text-analysis")
def text_analysis_report_endpoint(db: Session = Depends(get_db)):
    """
    Пример: группируем по (request_type, result).
    Показываем, сколько было success/error, какие категории итд.
    """
    rows = db.execute("""
        SELECT request_type, result, COUNT(*) as cnt
        FROM text_analysis_report
        GROUP BY request_type, result
    """).fetchall()
    return [
        {"request_type": r[0], "result": r[1], "count": r[2]}
        for r in rows
    ]
