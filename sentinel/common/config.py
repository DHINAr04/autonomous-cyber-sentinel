import os


def bus_mode() -> str:
    return os.getenv("BUS", "memory").strip().lower()


def redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


def sentinel_db() -> str:
    return os.getenv("SENTINEL_DB", "sqlite:///sentinel.db")


def live_capture_enabled() -> bool:
    return os.getenv("LIVE_CAPTURE", "0") == "1"


def capture_iface() -> str | None:
    return os.getenv("CAPTURE_IFACE")


def vt_api_key() -> str | None:
    return os.getenv("VT_API_KEY")


def abuseipdb_api_key() -> str | None:
    return os.getenv("ABUSEIPDB_API_KEY")


def otx_api_key() -> str | None:
    return os.getenv("OTX_API_KEY")


def offline_mode() -> bool:
    return os.getenv("OFFLINE", "0") == "1"


def model_path() -> str | None:
    return os.getenv("MODEL_PATH")


def score_weights() -> dict:
    return {"bytes": 0.5, "pkts": 0.3, "iat_inv": 0.2}


def severity_thresholds() -> dict:
    return {"high": 0.8, "medium": 0.6}


def _get_setting(key: str, default: object) -> object:
    return default
