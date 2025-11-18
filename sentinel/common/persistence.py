import os
from typing import Any, Dict
from sqlalchemy import create_engine, Column, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import sentinel_db


Base = declarative_base()


class AlertRow(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True)
    ts = Column(Float)
    src_ip = Column(String)
    dst_ip = Column(String)
    proto = Column(String)
    severity = Column(String)
    payload = Column(Text)


class InvestigationRow(Base):
    __tablename__ = "investigations"
    id = Column(String, primary_key=True)
    alert_id = Column(String)
    ts = Column(Float)
    verdict = Column(String)
    risk_score = Column(Float)
    payload = Column(Text)


class ActionRow(Base):
    __tablename__ = "actions"
    id = Column(String, primary_key=True)
    alert_id = Column(String)
    ts = Column(Float)
    action_type = Column(String)
    result = Column(String)
    safety_gate = Column(String)
    payload = Column(Text)


class Repository:
    def __init__(self, db_path: str | None = None) -> None:
        path = db_path or sentinel_db()
        self._engine = create_engine(path, future=True)
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine, expire_on_commit=False, future=True)

    def save_alert(self, data: Dict[str, Any]) -> None:
        from json import dumps
        with self._Session() as s:
            row = AlertRow(
                id=str(data.get("id")),
                ts=float(data.get("ts", 0.0)),
                src_ip=str(data.get("src_ip", "")),
                dst_ip=str(data.get("dst_ip", "")),
                proto=str(data.get("proto", "")),
                severity=str(data.get("severity", "")),
                payload=dumps(data),
            )
            s.add(row)
            s.commit()

    def save_investigation(self, data: Dict[str, Any]) -> None:
        from json import dumps
        with self._Session() as s:
            row = InvestigationRow(
                id=str(data.get("alert_id")),
                alert_id=str(data.get("alert_id")),
                ts=float(data.get("ts", 0.0)),
                verdict=str(data.get("verdict", "")),
                risk_score=float(data.get("risk_score", 0.0)),
                payload=dumps(data),
            )
            s.add(row)
            s.commit()

    def save_action(self, data: Dict[str, Any]) -> None:
        from json import dumps
        with self._Session() as s:
            row = ActionRow(
                id=str(data.get("action_id")),
                alert_id=str(data.get("alert_id")),
                ts=float(data.get("ts", 0.0)),
                action_type=str(data.get("action_type", "")),
                result=str(data.get("result", "")),
                safety_gate=str(data.get("safety_gate", "")),
                payload=dumps(data),
            )
            s.add(row)
            s.commit()
