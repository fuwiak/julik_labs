import optuna
from sqlalchemy.orm import Session
from .models import OptunaRun, OptunaTrial

def run_optuna(db: Session, n_trials: int, low: float, high: float):
    def objective(trial):
        x = trial.suggest_float('x', low, high)
        return (x - 2)**2

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    # Сохраняем результаты
    run = OptunaRun(best_value=study.best_value, best_params=str(study.best_params))
    db.add(run)
    db.commit()
    db.refresh(run)

    for t in study.trials:
        trial_record = OptunaTrial(
            run_id=run.id,
            trial_number=t.number,
            value=t.value,
            params=str(t.params)
        )
        db.add(trial_record)
    db.commit()
    return run
