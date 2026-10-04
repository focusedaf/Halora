"""URL normalization and SSRF protection.

This service fetches URLs supplied by users (or extracted from LLM output),
so every hop must be checked against private / loopback / link-local ranges.
"""

import ipaddress
import re
import socket
from urllib.parse import urlparse, urlunparse


def normalize_url(raw):
    """Return a clean http(s) URL, or None if it is unusable."""

    if not raw or not isinstance(raw, str):
        return None

    url = raw.strip().rstrip(".,;:)]}>\"'")

    if not url:
        return None

    if not re.match(r"^[a-z][a-z0-9+.\-]*://", url, re.IGNORECASE):
        # Reject scheme-only forms (javascript:, mailto:, data:) but allow host:port.
        if re.match(r"^[a-z][a-z0-9+.\-]*:(?!\d)", url, re.IGNORECASE):
            return None

        url = "https://" + url

    try:
        parsed = urlparse(url)
    except ValueError:
        return None

    if parsed.scheme.lower() not in {"http", "https"}:
        return None

    if not parsed.hostname:
        return None

    # Drop the fragment; it is never sent to the server.
    return urlunparse(parsed._replace(fragment=""))


def check_target(url, allow_private=False):
    """Classify the host a URL points at.

    Returns one of: "ok", "private", "dns_error".
    """

    host = urlparse(url).hostname

    if not host:
        return "dns_error"

    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError):
        return "dns_error"

    if allow_private:
        return "ok"

    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return "private"

        if not ip.is_global:
            return "private"

    return "ok"


def bare_host(url):
    """Lower-cased hostname without a leading "www."."""

    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""

    return host[4:] if host.startswith("www.") else host


def url_key(url):
    """Scheme/www/trailing-slash insensitive key for comparing URLs."""

    try:
        parsed = urlparse(url)
    except ValueError:
        return ""

    host = bare_host(url)
    path = parsed.path.rstrip("/")

    return f"{host}{path}?{parsed.query}" if parsed.query else f"{host}{path}"
