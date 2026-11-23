"""Per-tenant metrics and the guardrail hook.

SPIKE HOOK #2 - protect small tenants.
`check()` runs before every tenant endpoint. Our guardrail: a separate
"heavy report" budget per tenant (see REPORT_BUDGET below).
"""
import asyncio
import os
import re
import threading
from collections import defaultdict, deque

from fastapi import HTTPException, Request

WHALE_ID = 1
_PATH = re.compile(r"^/t/(\d+)/")

_lat: dict[int, deque] = defaultdict(lambda: deque(maxlen=1000))
_lock = threading.Lock()


def tenant_from_path(path: str):
    m = _PATH.match(path)
    return int(m.group(1)) if m else None


def record(tenant_id: int, ms: float, status: int) -> None:
    with _lock:
        _lat[tenant_id].append((ms, status))


# Heavy-report budget: how many month-end reports ONE tenant may run at the same time.
# Light work (listing and creating orders) is never limited.
REPORT_BUDGET = int(os.getenv("REPORT_BUDGET", "1"))
REPORT_WAIT_S = float(os.getenv("REPORT_WAIT_S", "30"))  # how long an extra report may wait in line
_budgets: dict[int, asyncio.Semaphore] = {}


async def check(tenant_id: int, request: Request):
    """FastAPI dependency: protect small tenants from one tenant's heavy reports.

    A tenant may run at most REPORT_BUDGET monthly reports at once. Extra reports
    wait in line (up to REPORT_WAIT_S seconds, then HTTP 429). Waiting happens
    without holding a server thread or a database connection, so one tenant's
    month-end cannot use up the capacity that other tenants need.
    """
    if not request.url.path.endswith("/reports/monthly"):
        yield tenant_id
        return
    budget = _budgets.setdefault(tenant_id, asyncio.Semaphore(REPORT_BUDGET))
    try:
        await asyncio.wait_for(budget.acquire(), timeout=REPORT_WAIT_S)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=429, detail="report budget reached, try again later")
    try:
        yield tenant_id
    finally:
        budget.release()


def _pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    return round(s[min(len(s) - 1, int(p / 100 * len(s)))], 1)


def _summ(samples: list[tuple[float, int]]) -> dict:
    ms = [m for m, _ in samples]
    return {
        "requests": len(ms),
        "errors": sum(1 for _, st in samples if st >= 400),
        "p50_ms": _pct(ms, 50),
        "p95_ms": _pct(ms, 95),
        "p99_ms": _pct(ms, 99),
    }


def snapshot() -> dict:
    """Latency summary: whale vs. all small tenants (last ~1000 requests per tenant)."""
    with _lock:
        whale = list(_lat.get(WHALE_ID, []))
        small = [s for tid, d in _lat.items() if tid != WHALE_ID for s in d]
        per_tenant = {tid: list(d) for tid, d in _lat.items() if tid != WHALE_ID}
    worst = sorted(
        ({"tenant_id": tid, **_summ(s)} for tid, s in per_tenant.items() if s),
        key=lambda x: x["p95_ms"] or 0,
        reverse=True,
    )[:5]
    return {"whale": _summ(whale), "small_tenants": _summ(small), "worst_small_tenants": worst}


def reset() -> None:
    with _lock:
        _lat.clear()