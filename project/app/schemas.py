from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, TIMESTAMP, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CoindeskInfo(Base):
    __tablename__ = 'coindesk_info'
    id = Column(Integer, primary_key=True, index=True)
    time_updated = Column(Text)
    time_updated_iso = Column(TIMESTAMP)
    time_updated_uk = Column(Text)
    disclaimer = Column(Text)
    chart_name = Column(Text)
    load_timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    bpi = relationship("CoindeskBPI", back_populates="info")


class CoindeskBPI(Base):
    __tablename__ = 'coindesk_bpi'
    id = Column(Integer, primary_key=True, index=True)
    coindesk_info_id = Column(Integer, ForeignKey('coindesk_info.id'))
    currency_code = Column(Text)
    currency_symbol = Column(Text)
    rate = Column(Text)
    description = Column(Text)
    rate_float = Column(Numeric)

    info = relationship("CoindeskInfo", back_populates="bpi")
