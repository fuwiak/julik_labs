from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from .database import get_db
from .crud import get_info, create_info, update_info, delete_info
from .airflow_client import trigger_dag
from .optuna_module import run_optuna
from .text_analysis import analyze_text
from .models import CallsLog
from datetime import datetime
import requests

app = FastAPI(title="Full System")

def log_call(db: Session, endpoint: str, status: str, result: str):
    call = CallsLog(endpoint=endpoint, status=status, result=result, timestamp=datetime.utcnow())
    db.add(call)
    db.commit()

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
    updated = update_info(db, info_id, time_updated=time_updated, disclaimer=disclaimer, chart_name=chart_name)
    if not updated:
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

@app.post("/trigger_dag/{dag_id}")
def trigger_dag_endpoint(dag_id: str, db: Session = Depends(get_db)):
    try:
        trigger_dag(dag_id)
        log_call(db, f"/trigger_dag/{dag_id}", "success", "dag_triggered")
        return {"status": "DAG triggered"}
    except HTTPException as e:
        log_call(db, f"/trigger_dag/{dag_id}", "error", str(e))
        raise

@app.post("/optuna_run")
def optuna_run_endpoint(n_trials: int, low: float, high: float, db: Session = Depends(get_db)):
    run = run_optuna(db, n_trials, low, high)
    log_call(db, "/optuna_run", "success", f"run_id_{run.id}")
    return {"run_id": run.id, "best_value": str(run.best_value), "best_params": run.best_params}

@app.post("/analyze_text")
def analyze_text_endpoint(text: str, db: Session = Depends(get_db)):
    result = analyze_text(text)
    log_call(db, "/analyze_text", "success", result)
    return {"result": result}

@app.get("/reports/calls")
def calls_report(db: Session = Depends(get_db)):
    # Отчёт по вызовам — count by status, endpoint
    from .models import CallsLog
    data = db.execute("""
        SELECT endpoint, status, COUNT(*) as cnt
        FROM calls_log
        GROUP BY endpoint, status
    """).fetchall()
    return [{"endpoint": r[0], "status": r[1], "count": r[2]} for r in data]
