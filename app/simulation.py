"""Month-end simulation: the whale's finance team runs reports all at once.

Workers call the API over HTTP, like real users would, so everything between
the browser and the database applies to them too.
"""
import os
import threading

import httpx

API_URL = os.getenv("SIM_API_URL", "http://127.0.0.1:8000")
WORKERS = int(os.getenv("SIM_WHALE_WORKERS", "40"))

_stop = threading.Event()
_threads: list[threading.Thread] = []


def _worker() -> None:
    with httpx.Client(base_url=API_URL, timeout=60) as client:
        while not _stop.is_set():
            try:
                client.get("/t/1/reports/monthly", params={"year": 2026})
            except httpx.HTTPError:
                _stop.wait(0.5)


def running() -> bool:
    return any(t.is_alive() for t in _threads)


def start() -> None:
    if running():
        return
    _stop.clear()
    _threads.clear()
    for _ in range(WORKERS):
        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        _threads.append(t)


def stop() -> None:
    _stop.set()
