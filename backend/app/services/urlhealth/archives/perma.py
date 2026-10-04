"""Perma.cc - Harvard LIL's permanent archive for legal/academic citations.

Lookup uses the public archives endpoint (no key needed). Saving requires
PERMA_API_KEY and consumes your account's monthly link quota, so it only
runs when preserve=true.
"""

import requests

from ..safety import url_key
from .base import ArchiveProvider, snapshot_result

PUBLIC_ARCHIVES = "https://api.perma.cc/v1/public/archives/"
ARCHIVES = "https://api.perma.cc/v1/archives/"


class PermaProvider(ArchiveProvider):
    name = "perma"
    label = "Perma.cc"
    supports_save = True

    @property
    def api_key(self):
        return getattr(self.settings, "perma_api_key", None)

    def _auth(self):
        return {"Authorization": f"ApiKey {self.api_key}"} if self.api_key else {}

    def lookup(self, url):
        try:
            response = self._get(
                PUBLIC_ARCHIVES,
                params={"url": url, "limit": 10},
                headers=self._auth(),
            )

            if response.status_code == 429:
                return self._error("Rate limited by Perma.cc (HTTP 429).")

            response.raise_for_status()
            objects = response.json().get("objects") or []
        except (requests.exceptions.RequestException, ValueError) as exc:
            return self._error(exc)

        wanted = url_key(url)

        # The list endpoint may ignore the filter, so always verify client-side.
        matches = [o for o in objects if url_key(o.get("url") or "") == wanted]

        if not matches:
            return self._missing()

        matches.sort(key=lambda o: o.get("creation_timestamp") or "", reverse=True)
        best = matches[0]
        guid = best.get("guid")

        if not guid:
            return self._missing()

        return self._ok(
            snapshot_url=f"https://perma.cc/{guid}",
            captured_at=best.get("creation_timestamp"),
            guid=guid,
            title=best.get("title"),
        )

    def save(self, url):
        if not self.api_key:
            return snapshot_result(
                self.name, "unsupported", error="PERMA_API_KEY is not configured."
            )

        try:
            response = requests.post(
                ARCHIVES,
                json={"url": url},
                headers=self._headers(
                    {**self._auth(), "Content-Type": "application/json"}
                ),
                timeout=max(self.timeout, 30),
            )

            if response.status_code not in (200, 201):
                return self._error(f"HTTP {response.status_code}: {response.text[:120]}")

            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as exc:
            return self._error(exc)

        guid = data.get("guid")

        if not guid:
            return self._error("Perma.cc did not return a GUID.")

        return snapshot_result(
            self.name,
            "created",
            snapshot_url=f"https://perma.cc/{guid}",
            captured_at=data.get("creation_timestamp"),
            guid=guid,
        )
