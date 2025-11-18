from fastapi.testclient import TestClient
from sentinel.dashboard.app import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_metrics():
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"alerts_total" in r.content
