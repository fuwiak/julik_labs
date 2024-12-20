from sqlalchemy import Column, Integer, Text, TIMESTAMP, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class CoindeskInfo(Base):
    __tablename__ = 'coindesk_info'
    id = Column(Integer, primary_key=True)
    time_updated = Column(Text)
    time_updated_iso = Column(TIMESTAMP)
    time_updated_uk = Column(Text)
    disclaimer = Column(Text)
    chart_name = Column(Text)
    load_timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    bpi = relationship("CoindeskBPI", back_populates="info")

class CoindeskBPI(Base):
    __tablename__ = 'coindesk_bpi'
    id = Column(Integer, primary_key=True)
    coindesk_info_id = Column(Integer, ForeignKey('coindesk_info.id'))
    currency_code = Column(Text)
    currency_symbol = Column(Text)
    rate = Column(Text)
    description = Column(Text)
    rate_float = Column(Numeric)

    info = relationship("CoindeskInfo", back_populates="bpi")

# Таблицы для Optuna (лабораторная 5):
class OptunaRun(Base):
    __tablename__ = 'optuna_run'
    id = Column(Integer, primary_key=True)
    run_timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    best_value = Column(Numeric)
    best_params = Column(Text)

class OptunaTrial(Base):
    __tablename__ = 'optuna_trial'
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('optuna_run.id'))
    trial_number = Column(Integer)
    value = Column(Numeric)
    params = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

# Таблица для логирования вызовов функций (анализ текста, оптюна, CRUD)
class CallsLog(Base):
    __tablename__ = 'calls_log'
    id = Column(Integer, primary_key=True)
    endpoint = Column(Text)
    status = Column(Text)
    result = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
