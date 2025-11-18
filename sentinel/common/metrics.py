from prometheus_client import Counter, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST


registry = CollectorRegistry()

alerts_total = Counter("alerts_total", "Total alerts generated", registry=registry)
investigations_total = Counter("investigations_total", "Total investigations generated", registry=registry)
actions_total = Counter("actions_total", "Total actions executed", registry=registry)


def inc_alerts() -> None:
    alerts_total.inc()


def inc_investigations() -> None:
    investigations_total.inc()


def inc_actions() -> None:
    actions_total.inc()


def latest() -> tuple[bytes, str]:
    return generate_latest(registry), CONTENT_TYPE_LATEST
