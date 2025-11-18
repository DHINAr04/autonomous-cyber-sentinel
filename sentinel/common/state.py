import threading
from typing import List, Dict, Any, Optional
from .persistence import Repository
from .metrics import inc_alerts, inc_investigations, inc_actions


class SharedState:
    def __init__(self, repo: Optional[Repository] = None) -> None:
        self.alerts: List[Dict[str, Any]] = []
        self.investigations: List[Dict[str, Any]] = []
        self.actions: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._repo = repo

    def add_alert(self, a: Dict[str, Any]) -> None:
        with self._lock:
            self.alerts.append(a)
            try:
                inc_alerts()
            except Exception:
                pass
            if self._repo:
                try:
                    self._repo.save_alert(a)
                except Exception:
                    pass

    def add_investigation(self, r: Dict[str, Any]) -> None:
        with self._lock:
            self.investigations.append(r)
            try:
                inc_investigations()
            except Exception:
                pass
            if self._repo:
                try:
                    self._repo.save_investigation(r)
                except Exception:
                    pass

    def add_action(self, act: Dict[str, Any]) -> None:
        with self._lock:
            self.actions.append(act)
            try:
                inc_actions()
            except Exception:
                pass
            if self._repo:
                try:
                    self._repo.save_action(act)
                except Exception:
                    pass
