"""Shared HTTP session with retries and polite rate limiting."""

from __future__ import annotations

import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 AuditDatasetBuilder/1.0"
)

_last_request: dict[str, float] = {}


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    retry = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = make_session()


def get(url: str, *, min_interval: float = 0.5, **kwargs) -> requests.Response:
    """GET with a per-host minimum interval between requests."""
    host = url.split("/", 3)[2]
    elapsed = time.monotonic() - _last_request.get(host, 0.0)
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    kwargs.setdefault("timeout", 60)
    resp = SESSION.get(url, **kwargs)
    _last_request[host] = time.monotonic()
    return resp
