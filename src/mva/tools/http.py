"""Cached JSON HTTP helper shared by all database clients."""

from __future__ import annotations

import hashlib
import json
import time

import httpx

from mva import config

_TIMEOUT = 30.0


def _key(method: str, url: str, params, body) -> str:
    raw = json.dumps([method, url, params, body], sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def request_json(method: str, url: str, params: dict | None = None, body: dict | None = None):
    """GET/POST returning parsed JSON. Responses are cached on disk so reruns are reproducible."""
    path = config.CACHE_DIR / "http" / f"{_key(method, url, params, body)}.json"
    if path.exists():
        return json.loads(path.read_text())
    last = None
    for attempt in range(3):
        try:
            r = httpx.request(method, url, params=params, json=body, timeout=_TIMEOUT,
                              headers={"Accept": "application/json"}, follow_redirects=True)
            if r.status_code == 404:
                return {}
            r.raise_for_status()
            data = r.json()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
            return data
        except (httpx.HTTPError, ValueError) as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{url} failed: {last}")


def get_json(url: str, params: dict | None = None):
    return request_json("GET", url, params=params)


def post_json(url: str, body: dict):
    return request_json("POST", url, body=body)
