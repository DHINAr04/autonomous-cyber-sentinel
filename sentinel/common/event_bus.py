import os
import threading
from queue import Queue, Empty
from typing import Dict, Any, Optional
from .config import bus_mode, redis_url

try:
    import redis as redis_py
except Exception:
    redis_py = None


class EventBus:
    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        raise NotImplementedError

    def subscribe(self, channel: str) -> "Subscriber":
        raise NotImplementedError


class BusFactory:
    @staticmethod
    def from_env() -> EventBus:
        mode = bus_mode()
        if mode == "redis" and redis_py is not None:
            url = redis_url()
            try:
                return RedisEventBus(url)
            except Exception:
                return InMemoryEventBus()
        return InMemoryEventBus()


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._queues: Dict[str, Queue] = {}
        self._lock = threading.Lock()

    def _get_queue(self, channel: str) -> Queue:
        with self._lock:
            if channel not in self._queues:
                self._queues[channel] = Queue()
            return self._queues[channel]

    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        q = self._get_queue(channel)
        q.put(message)

    def subscribe(self, channel: str) -> "Subscriber":
        return Subscriber(self._get_queue(channel))


class Subscriber:
    def __init__(self, queue: Queue) -> None:
        self._queue = queue

    def get(self, timeout: Optional[float] = 0.5) -> Optional[Dict[str, Any]]:
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None


class RedisEventBus(EventBus):
    def __init__(self, url: str) -> None:
        if redis_py is None:
            raise RuntimeError("redis-py not available")
        self._client = redis_py.Redis.from_url(url, decode_responses=True)

    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        # serialize as JSON-encoded string; simple repr for now
        import json
        self._client.publish(channel, json.dumps(message))

    def subscribe(self, channel: str) -> "Subscriber":
        return RedisSubscriber(self._client, channel)


class RedisSubscriber(Subscriber):
    def __init__(self, client: "redis_py.Redis", channel: str) -> None:
        self._pubsub = client.pubsub()
        self._pubsub.subscribe(channel)

    def get(self, timeout: Optional[float] = 0.5) -> Optional[Dict[str, Any]]:
        import json
        msg = self._pubsub.get_message(timeout=timeout)
        if msg and msg.get("type") == "message":
            try:
                return json.loads(msg.get("data", "{}"))
            except Exception:
                return None
        return None
