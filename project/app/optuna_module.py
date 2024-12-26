import optuna
from datetime import datetime
from sqlalchemy.orm import Session
from models import OptunaRun, OptunaTrial

def run_optuna(db: Session, n_trials: int, low: float, high: float):
    """Запуск оптимизации и сохранение результатов в optuna_run/optuna_trial."""
    def objective(trial):
        x = trial.suggest_float('x', low, high)
        return (x - 2) ** 2

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    # Сохраняем "шапку" (оптимальный результат)
    run_obj = OptunaRun(
        best_value=study.best_value,
        best_params=str(study.best_params)
    )
    db.add(run_obj)
    db.commit()
    db.refresh(run_obj)  # чтобы получить run_obj.id

    # Сохраняем все trials
    for t in study.trials:
        trial_obj = OptunaTrial(
            run_id=run_obj.id,
            trial_number=t.number,
            value=t.value,
            params=str(t.params),
        )
        db.add(trial_obj)
    db.commit()
    return run_obj
