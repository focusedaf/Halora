"""Shared provider interface for web archives."""

from datetime import datetime, timezone

import requests


def parse_timestamp(ts):
    """Convert a 14-digit archive timestamp (YYYYMMDDhhmmss) to ISO-8601."""

    ts = str(ts or "").strip()

    try:
        return datetime.strptime(ts[:14].ljust(14, "0"), "%Y%m%d%H%M%S").replace(
            tzinfo=timezone.utc
        ).isoformat()
    except ValueError:
        return None


def snapshot_result(provider, status, **extra):
    """Uniform result shape for every archive lookup / save.

    status: found | not_found | error | created | pending | unsupported | skipped
    """

    return {
        "provider": provider,
        "status": status,
        "snapshot_url": extra.pop("snapshot_url", None),
        "captured_at": extra.pop("captured_at", None),
        "http_status": extra.pop("http_status", None),
        "error": extra.pop("error", None),
        **extra,
    }


class ArchiveProvider:
    """One archive in the waterfall. Subclasses implement lookup() and,
    optionally, save()."""

    name = "base"
    label = "Base"
    supports_save = False

    def __init__(self, timeout=10, user_agent="URLHealth/1.0", settings=None):
        self.timeout = timeout
        self.user_agent = user_agent
        self.settings = settings

    # -- helpers ---------------------------------------------------------

    def _headers(self, extra=None):
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        headers.update(extra or {})
        return headers

    def _get(self, url, params=None, headers=None, timeout=None):
        return requests.get(
            url,
            params=params,
            headers=self._headers(headers),
            timeout=timeout or self.timeout,
        )

    def _ok(self, **extra):
        return snapshot_result(self.name, "found", **extra)

    def _missing(self):
        return snapshot_result(self.name, "not_found")

    def _error(self, message):
        return snapshot_result(self.name, "error", error=str(message)[:200])

    # -- interface -------------------------------------------------------

    def lookup(self, url):
        raise NotImplementedError

    def save(self, url):
        return snapshot_result(self.name, "unsupported")
