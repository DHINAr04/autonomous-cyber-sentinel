from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import uuid
import time


def _ts() -> float:
    return time.time()


def _id() -> str:
    return str(uuid.uuid4())


@dataclass
class AlertEvent:
    id: str
    ts: float
    src_ip: str
    dst_ip: str
    proto: str
    features: Dict[str, Any]
    model_score: float
    confidence: float
    severity: str
    sensor_id: str

    @staticmethod
    def synthetic(sensor_id: str, src_ip: str, dst_ip: str, score: float) -> "AlertEvent":
        severity = "high" if score >= 0.8 else ("medium" if score >= 0.5 else "low")
        return AlertEvent(
            id=_id(),
            ts=_ts(),
            src_ip=src_ip,
            dst_ip=dst_ip,
            proto="tcp",
            features={"bytes": int(5000 * score), "pkts": int(50 * score)},
            model_score=score,
            confidence=min(1.0, max(0.1, score)),
            severity=severity,
            sensor_id=sensor_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InvestigationReport:
    alert_id: str
    ts: float
    ioc_findings: Dict[str, Any]
    sources: List[str]
    risk_score: float
    verdict: str
    notes: str
    uncertainty: float
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResponseAction:
    action_id: str
    alert_id: str
    ts: float
    action_type: str
    target: str
    parameters: Dict[str, Any]
    result: str
    safety_gate: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
