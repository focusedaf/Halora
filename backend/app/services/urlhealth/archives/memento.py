"""Memento Time Travel aggregator.

One call that fans out to many archives (archive.today, UK Web Archive,
national libraries, ...). Used as the broad net at the end of the cascade.
"""

from datetime import datetime, timezone

import requests

from .base import ArchiveProvider

TIME_TRAVEL = "https://timetravel.mementoweb.org/api/json"


class MementoProvider(ArchiveProvider):
    name = "memento"
    label = "Memento Time Travel"

    def lookup(self, url):
        now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

        try:
            response = self._get(f"{TIME_TRAVEL}/{now}/{url}")

            if response.status_code == 404:
                return self._missing()

            response.raise_for_status()
            mementos = response.json().get("mementos") or {}
        except (requests.exceptions.RequestException, ValueError) as exc:
            return self._error(exc)

        # Prefer the closest-to-now memento, fall back to the last one.
        for key in ("closest", "last"):
            entry = mementos.get(key) or {}
            uris = entry.get("uri") or []

            if isinstance(uris, str):
                uris = [uris]

            if uris:
                return self._ok(
                    snapshot_url=uris[0],
                    captured_at=entry.get("datetime"),
                )

        return self._missing()
