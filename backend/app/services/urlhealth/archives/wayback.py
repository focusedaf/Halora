"""Internet Archive Wayback Machine.

Lookup: Availability API, then CDX API as a fallback (the availability
endpoint is known to miss captures that CDX has).
Save:   Save Page Now (anonymous GET, or SPN2 POST when IA keys are set).
"""

import requests

from .base import ArchiveProvider, parse_timestamp, snapshot_result

AVAILABILITY = "https://archive.org/wayback/available"
CDX = "https://web.archive.org/cdx/search/cdx"
SAVE = "https://web.archive.org/save"


def _https(url):
    return url.replace("http://", "https://", 1) if url else url


class WaybackProvider(ArchiveProvider):
    name = "wayback"
    label = "Wayback Machine"
    supports_save = True

    def lookup(self, url):
        errors = []

        try:
            response = self._get(AVAILABILITY, params={"url": url})
            response.raise_for_status()
            closest = (response.json().get("archived_snapshots") or {}).get("closest") or {}

            if closest.get("available") and str(closest.get("status", "200")).startswith("2"):
                return self._ok(
                    snapshot_url=_https(closest.get("url")),
                    captured_at=parse_timestamp(closest.get("timestamp")),
                    http_status=int(closest.get("status") or 200),
                )
        except (requests.exceptions.RequestException, ValueError) as exc:
            errors.append(exc)

        # Fallback: CDX, newest successful capture first.
        try:
            response = self._get(
                CDX,
                params={
                    "url": url,
                    "output": "json",
                    "fl": "timestamp,original,statuscode",
                    "filter": "statuscode:200",
                    "limit": -1,
                },
                timeout=self.timeout + 5,
            )
            response.raise_for_status()
            rows = response.json()

            # First row is the header.
            if isinstance(rows, list) and len(rows) > 1:
                timestamp, original, status = rows[-1][:3]
                return self._ok(
                    snapshot_url=f"https://web.archive.org/web/{timestamp}/{original}",
                    captured_at=parse_timestamp(timestamp),
                    http_status=int(status),
                )
        except (requests.exceptions.RequestException, ValueError) as exc:
            errors.append(exc)

        # Both endpoints failing is an error; both answering "none" is not_found.
        return self._error(errors[-1]) if len(errors) == 2 else self._missing()

    def save(self, url):
        access = getattr(self.settings, "ia_access_key", None)
        secret = getattr(self.settings, "ia_secret_key", None)

        try:
            if access and secret:
                # SPN2 is asynchronous: it returns a job id, not a snapshot.
                response = requests.post(
                    SAVE,
                    data={"url": url, "capture_all": 1},
                    headers=self._headers({"Authorization": f"LOW {access}:{secret}"}),
                    timeout=max(self.timeout, 30),
                )
                response.raise_for_status()
                job_id = response.json().get("job_id")

                if not job_id:
                    return self._error("Save Page Now returned no job id.")

                return snapshot_result(
                    self.name,
                    "pending",
                    job_id=job_id,
                    status_url=f"https://web.archive.org/save/status/{job_id}",
                )

            response = requests.get(
                f"{SAVE}/{url}",
                headers=self._headers(),
                timeout=max(self.timeout, 45),
                allow_redirects=True,
            )

            location = response.headers.get("Content-Location")

            if response.status_code < 400 and location:
                return snapshot_result(
                    self.name,
                    "created",
                    snapshot_url=f"https://web.archive.org{location}",
                )

            return self._error(f"Save Page Now returned HTTP {response.status_code}.")
        except (requests.exceptions.RequestException, ValueError) as exc:
            return self._error(exc)
