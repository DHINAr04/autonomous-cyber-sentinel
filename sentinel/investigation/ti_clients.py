import os
import time
import hashlib
from typing import Dict, Any, Optional
import requests
from sentinel.common.config import vt_api_key, abuseipdb_api_key, otx_api_key, redis_url, offline_mode
from .cache import TTLCache, RedisTTLCache, Cache


def _make_cache() -> Cache:
    url = redis_url()
    try:
        return RedisTTLCache(url)
    except Exception:
        return TTLCache()


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:12]


class VirusTotalClient:
    def __init__(self, cache: Cache) -> None:
        self.api_key = vt_api_key()
        self.cache = cache

    def ip_report(self, ip: str) -> Dict[str, Any]:
        key = f"vt:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        if offline_mode() or not self.api_key:
            val = int(_hash(ip), 16) % 101
            data = {"source": "vt", "ip": ip, "reputation": val, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"x-apikey": self.api_key}
        r = requests.get(url, headers=headers, timeout=5)
        rep = r.json().get("data", {}).get("attributes", {}).get("reputation", 0)
        data = {"source": "vt", "ip": ip, "reputation": rep}
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data


class AbuseIPDBClient:
    def __init__(self, cache: Cache) -> None:
        self.api_key = abuseipdb_api_key()
        self.cache = cache

    def ip_check(self, ip: str) -> Dict[str, Any]:
        key = f"abuse:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        if offline_mode() or not self.api_key:
            val = int(_hash(ip), 16) % 101
            data = {"source": "abuseipdb", "ip": ip, "abuse_score": val, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": self.api_key, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        r = requests.get(url, headers=headers, params=params, timeout=5)
        score = r.json().get("data", {}).get("abuseConfidenceScore", 0)
        data = {"source": "abuseipdb", "ip": ip, "abuse_score": score}
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data


class OTXClient:
    def __init__(self, cache: Cache) -> None:
        self.api_key = otx_api_key()
        self.cache = cache

    def ip_info(self, ip: str) -> Dict[str, Any]:
        key = f"otx:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        if offline_mode() or not self.api_key:
            pulse_count = int(_hash(ip), 16) % 5
            data = {"source": "otx", "ip": ip, "pulses": pulse_count, "mocked": True}
            self.cache.set(key, data, 300.0)
            time.sleep(0.1)
            return data
        headers = {"X-OTX-API-KEY": self.api_key}
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            pulse_count = len(r.json().get("pulse_info", {}).get("pulses", []))
        except Exception:
            pulse_count = 0
        data = {"source": "otx", "ip": ip, "pulses": pulse_count}
        self.cache.set(key, data, 300.0)
        time.sleep(0.5)
        return data
