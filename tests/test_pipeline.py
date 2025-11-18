import time
from sentinel.common.event_bus import InMemoryEventBus
from sentinel.common.state import SharedState
from sentinel.detection.engine import DetectionEngine
from sentinel.investigation.agent import InvestigationAgent
from sentinel.response.engine import ResponseEngine


def test_pipeline_runs_and_produces_items():
    state = SharedState()
    bus = InMemoryEventBus()
    d = DetectionEngine(bus, state, sensor_id="sensor-test")
    i = InvestigationAgent(bus, state)
    r = ResponseEngine(bus, state)
    d.start(); i.start(); r.start()
    time.sleep(2.5)
    d.stop(); i.stop(); r.stop()
    assert len(state.alerts) >= 2
    assert len(state.investigations) >= 2
    assert len(state.actions) >= 2
