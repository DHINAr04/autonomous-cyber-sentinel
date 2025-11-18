from typing import Dict, Any, Optional
import time

try:
    import redis as redis_py
except Exception:
    redis_py = None


class Cache:
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def set(self, key: str, val: Dict[str, Any], ttl: float) -> None:
        raise NotImplementedError


class TTLCache(Cache):
    def __init__(self, ttl: float = 300.0) -> None:
        self.ttl = ttl
        self._store: Dict[str, tuple[float, Dict[str, Any]]] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        entry = self._store.get(key)
        if not entry:
            return None
        ts, val = entry
        if now - ts > self.ttl:
            self._store.pop(key, None)
            return None
        return val

    def set(self, key: str, val: Dict[str, Any], ttl: float) -> None:
        self._store[key] = (time.time(), val)


class RedisTTLCache(Cache):
    def __init__(self, url: str, ttl: float = 300.0) -> None:
        if redis_py is None:
            raise RuntimeError("redis-py not available")
        self.ttl = int(ttl)
        self._client = redis_py.Redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        import json
        try:
            raw = self._client.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except Exception:
            return None

    def set(self, key: str, val: Dict[str, Any], ttl: float) -> None:
        import json
        try:
            self._client.setex(key, int(ttl), json.dumps(val))
        except Exception:
            pass
