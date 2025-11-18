from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from typing import Dict, Any
from sentinel.common.state import SharedState
import os
from sentinel.common.event_bus import BusFactory
from sentinel.detection.engine import DetectionEngine
from sentinel.investigation.agent import InvestigationAgent
from sentinel.response.engine import ResponseEngine
from sentinel.common.persistence import Repository
from sentinel.common.metrics import latest


repo = Repository()
state = SharedState(repo=repo)
bus = BusFactory.from_env()
detection = DetectionEngine(bus, state, sensor_id="sensor-1")
investigator = InvestigationAgent(bus, state)
responder = ResponseEngine(bus, state)

app = FastAPI()


@app.on_event("startup")
def _startup() -> None:
    detection.start()
    investigator.start()
    responder.start()


@app.on_event("shutdown")
def _shutdown() -> None:
    detection.stop()
    investigator.stop()
    responder.stop()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.get("/alerts")
def alerts() -> Dict[str, Any]:
    return {"items": state.alerts}


@app.get("/investigations")
def investigations() -> Dict[str, Any]:
    return {"items": state.investigations}


@app.get("/actions")
def actions() -> Dict[str, Any]:
    return {"items": state.actions}


@app.websocket("/stream")
async def stream(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            payload = {
                "alerts": len(state.alerts),
                "investigations": len(state.investigations),
                "actions": len(state.actions),
            }
            await ws.send_json(payload)
            import asyncio
            await asyncio.sleep(1.0)
    finally:
        await ws.close()


@app.get("/metrics")
def metrics() -> Response:
    body, ctype = latest()
    return Response(content=body, media_type=ctype)
