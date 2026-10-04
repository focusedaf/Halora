"""Waterfall orchestrator.

    live check ──alive──────────────────────────────▶ health: alive
        │
        └─dead / blocked / error
              │
              ▼
        perma ─▶ wayback ─▶ arquivo ─▶ memento     (first hit wins,
              │                                      or collect all)
              ▼
        nothing found + page reachable + preserve=true
              ▶ save via perma (key) ─▶ wayback

Health values: alive | restricted | archived | dead | unreachable |
               unsafe | invalid
"""

import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.core.config import get_settings

from .archives import build_providers
from .live_check import check_live
from .safety import check_target, normalize_url

# Live statuses that should trigger the archive cascade.
ARCHIVE_TRIGGERS = {
    "dead", "soft_404", "redirected_to_root", "dns_error", "ssl_error",
    "timeout", "unreachable", "server_error", "too_many_redirects", "blocked",
}

URL_PATTERN = re.compile(r"https?://[^\s<>\"'\])}]+", re.IGNORECASE)

_cache = {}
_cache_lock = threading.Lock()


# -- cache -----------------------------------------------------------------

def _cache_get(key, ttl):
    if ttl <= 0:
        return None

    with _cache_lock:
        entry = _cache.get(key)

    if entry and time.time() - entry[0] < ttl:
        return entry[1]

    return None


def _cache_set(key, value, ttl):
    if ttl > 0:
        with _cache_lock:
            _cache[key] = (time.time(), value)


# -- helpers ---------------------------------------------------------------

def _timed(fn, *args):
    started = time.monotonic()
    result = fn(*args)
    return result, round((time.monotonic() - started) * 1000)


def _safe_call(provider, method, url):
    """A provider must never be able to break the cascade."""

    try:
        return _timed(getattr(provider, method), url)
    except Exception as exc:  # noqa: BLE001
        return (
            {"provider": provider.name, "status": "error", "snapshot_url": None,
             "captured_at": None, "http_status": None, "error": str(exc)[:200]},
            0,
        )


def _best(snapshots):
    """Most recent snapshot; cascade order breaks ties."""

    if not snapshots:
        return None

    return max(
        enumerate(snapshots),
        key=lambda pair: (pair[1].get("captured_at") or "", -pair[0]),
    )[1]


def list_providers():
    settings = get_settings()
    providers = build_providers(
        settings.urlhealth_archive_order,
        settings.urlhealth_timeout,
        settings.urlhealth_user_agent,
        settings,
    )

    return [
        {
            "name": p.name,
            "label": p.label,
            "supports_save": p.supports_save,
            "save_configured": bool(
                p.supports_save
                and (
                    getattr(settings, "perma_api_key", None)
                    if p.name == "perma"
                    else True
                )
            ),
        }
        for p in providers
    ]


# -- main entry points -----------------------------------------------------

def check_url_health(
    url,
    mode="first_hit",
    providers=None,
    preserve=False,
    refresh=False,
):
    """Run the full waterfall for one URL.

    mode:      "first_hit" stops at the first archive with a snapshot;
               "all" queries every provider.
    providers: override cascade order (list of provider names).
    preserve:  if the page is live but has no snapshot, ask an archive to
               capture it (perma needs a key; wayback works anonymously).
    refresh:   bypass the in-memory cache.
    """

    settings = get_settings()
    checked_at = datetime.now(timezone.utc).isoformat()

    normalized = normalize_url(url)

    if not normalized:
        return {
            "url": url, "normalized_url": None, "health": "invalid",
            "live": None, "archive": {"checked": False, "best": None, "snapshots": []},
            "recommended": None, "cascade": [], "checked_at": checked_at,
            "error": "Not a valid http(s) URL.",
        }

    order = providers or settings.urlhealth_archive_order
    cache_key = (normalized, mode, tuple(order), preserve)

    if not refresh and not preserve:
        cached = _cache_get(cache_key, settings.urlhealth_cache_ttl)

        if cached:
            return {**cached, "url": url, "cached": True}

    trace = []

    # ---- Stage 1: live ----------------------------------------------------
    live = check_live(
        normalized,
        timeout=settings.urlhealth_timeout,
        user_agent=settings.urlhealth_user_agent,
        allow_private=settings.urlhealth_allow_private,
    )
    trace.append({
        "stage": "live", "status": live["status"],
        "detail": live.get("reason") or live.get("http_status"),
        "duration_ms": live.get("latency_ms"),
    })

    if live["status"] == "unsafe":
        return {
            "url": url, "normalized_url": normalized, "health": "unsafe",
            "live": live, "archive": {"checked": False, "best": None, "snapshots": []},
            "recommended": None, "cascade": trace, "checked_at": checked_at,
            "error": live.get("reason"),
        }

    # ---- Stage 2: archive cascade ----------------------------------------
    need_archive = live["status"] in ARCHIVE_TRIGGERS or preserve
    snapshots = []
    archive_providers = build_providers(
        order, settings.urlhealth_timeout, settings.urlhealth_user_agent, settings
    )

    if need_archive:
        for provider in archive_providers:
            result, ms = _safe_call(provider, "lookup", normalized)
            trace.append({
                "stage": provider.name, "status": result["status"],
                "detail": result.get("error") or result.get("snapshot_url"),
                "duration_ms": ms,
            })

            if result["status"] == "found":
                snapshots.append(result)

                if mode == "first_hit":
                    break

    # ---- Stage 3: preserve (opt-in) --------------------------------------
    created = None

    if (
        preserve
        and not snapshots
        and live["status"] in {"alive", "blocked"}
    ):
        for provider in archive_providers:
            if not provider.supports_save:
                continue

            result, ms = _safe_call(provider, "save", normalized)
            trace.append({
                "stage": f"{provider.name}:save", "status": result["status"],
                "detail": result.get("error") or result.get("snapshot_url") or result.get("status_url"),
                "duration_ms": ms,
            })

            if result["status"] in {"created", "pending"}:
                created = result
                if result["status"] == "created":
                    snapshots.append({**result, "status": "found", "newly_created": True})
                break

    best = _best(snapshots)

    # ---- Verdict ----------------------------------------------------------
    if live["status"] == "alive":
        health = "alive"
    elif live["status"] == "blocked":
        health = "restricted"
    elif best:
        health = "archived"
    elif live["status"] in {"timeout", "server_error", "unreachable", "ssl_error"}:
        health = "unreachable"
    else:
        health = "dead"

    if health in {"alive", "restricted"}:
        recommended = {"type": "live", "url": live["final_url"]}
    elif best:
        recommended = {"type": "archive", "url": best["snapshot_url"], "provider": best["provider"]}
    else:
        recommended = None

    result = {
        "url": url,
        "normalized_url": normalized,
        "health": health,
        "live": live,
        "archive": {
            "checked": need_archive,
            "best": best,
            "snapshots": snapshots,
            "preserve_job": created if created and created["status"] == "pending" else None,
        },
        "recommended": recommended,
        "cascade": trace,
        "checked_at": checked_at,
        "cached": False,
    }

    if not preserve:
        _cache_set(cache_key, result, settings.urlhealth_cache_ttl)

    return result


def check_urls_health(urls, **options):
    """Check many URLs concurrently. Duplicates are checked once."""

    settings = get_settings()
    ordered = list(dict.fromkeys(u for u in urls if isinstance(u, str) and u.strip()))

    if not ordered:
        return {"status": "success", "total": 0, "summary": {}, "results": []}

    workers = max(1, min(settings.urlhealth_max_workers, len(ordered)))

    def run(u):
        try:
            return check_url_health(u, **options)
        except Exception as exc:  # noqa: BLE001
            return {"url": u, "health": "unreachable", "error": str(exc)[:200],
                    "live": None, "archive": None, "recommended": None, "cascade": []}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(run, ordered))

    summary = {}

    for r in results:
        summary[r["health"]] = summary.get(r["health"], 0) + 1

    return {
        "status": "success",
        "total": len(results),
        "summary": summary,
        "results": results,
    }


def extract_urls(text):
    """Pull http(s) URLs out of free text (e.g. an LLM response)."""

    found = [u.rstrip(".,;:!?") for u in URL_PATTERN.findall(text or "")]

    return list(dict.fromkeys(found))


def check_text_urls(text, **options):
    """Extract every URL from a block of text and health-check them."""

    urls = extract_urls(text)
    result = check_urls_health(urls, **options)
    result["extracted_urls"] = urls

    return result
