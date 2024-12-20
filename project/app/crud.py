from models import CoindeskInfo
from sqlalchemy.orm import Session

def get_info(db: Session, info_id: int):
    return db.query(CoindeskInfo).filter(CoindeskInfo.id == info_id).first()

def create_info(db: Session, time_updated: str, disclaimer: str, chart_name: str):
    obj = CoindeskInfo(time_updated=time_updated, disclaimer=disclaimer, chart_name=chart_name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_info(db: Session, info_id: int, **fields):
    obj = db.query(CoindeskInfo).filter(CoindeskInfo.id == info_id).first()
    if not obj:
        return None
    for k,v in fields.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def delete_info(db: Session, info_id: int):
    obj = db.query(CoindeskInfo).filter(CoindeskInfo.id == info_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
