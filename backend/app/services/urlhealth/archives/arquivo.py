"""Arquivo.pt - Portuguese Web Archive (CDX server API, no key needed).

Strongest for .pt and Portuguese-language content, but crawls globally.
"""

import json

import requests

from .base import ArchiveProvider, parse_timestamp

CDX = "https://arquivo.pt/wayback/cdx"


class ArquivoProvider(ArchiveProvider):
    name = "arquivo"
    label = "Arquivo.pt"

    def lookup(self, url):
        try:
            response = self._get(
                CDX,
                params={"url": url, "output": "json", "limit": 25},
                timeout=self.timeout + 5,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            return self._error(exc)

        # CDX JSON output is one JSON object per line.
        rows = []

        for line in response.text.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                rows.append(json.loads(line))
            except ValueError:
                continue

        good = [
            r for r in rows
            if isinstance(r, dict)
            and str(r.get("status", "")).startswith("2")
            and r.get("timestamp")
        ]

        if not good:
            return self._missing()

        best = max(good, key=lambda r: str(r["timestamp"]))

        return self._ok(
            snapshot_url=f"https://arquivo.pt/wayback/{best['timestamp']}/{best.get('url') or url}",
            captured_at=parse_timestamp(best["timestamp"]),
            http_status=int(best["status"]),
        )
