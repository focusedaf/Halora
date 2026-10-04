"""Stage 1: is the URL alive right now?

Follows redirects manually so every hop can be SSRF-checked, tries HEAD
first, falls back to GET, and detects soft-404s.
"""

import re
import time
from urllib.parse import urljoin, urlparse

import requests

from .safety import bare_host, check_target

MAX_REDIRECTS = 5
MAX_BODY_BYTES = 65536

BLOCKED_STATUS = {401, 403, 429, 451, 999}
REDIRECT_STATUS = {301, 302, 303, 307, 308}

SOFT_404_PATTERN = re.compile(
    r"(page|article|content|file|resource)?\s*"
    r"(not found|no longer available|does not exist|"
    r"can.?t be found|has been removed|404)",
    re.IGNORECASE,
)

TITLE_PATTERN = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_PATTERN = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)


def _result(status, url, **extra):
    result = {
        "status": status,
        "url": url,
        "final_url": extra.pop("final_url", url),
        "http_status": extra.pop("http_status", None),
        "redirects": extra.pop("redirects", []),
        "content_type": extra.pop("content_type", None),
        "title": extra.pop("title", None),
        "reason": extra.pop("reason", None),
        "latency_ms": extra.pop("latency_ms", None),
    }
    result.update(extra)
    return result


def _strip_tags(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def _detect_soft_404(body, original_url, final_url):
    """Return (title, reason). reason is None when the page looks real."""

    title = ""
    reason = None

    if body:
        match = TITLE_PATTERN.search(body)
        if match:
            title = _strip_tags(match.group(1))

        h1 = H1_PATTERN.search(body)
        h1_text = _strip_tags(h1.group(1)) if h1 else ""

        for candidate in (title, h1_text):
            if candidate and SOFT_404_PATTERN.search(candidate):
                reason = f'Page title/heading looks like an error page: "{candidate[:80]}"'
                break

    if reason is None:
        orig, final = urlparse(original_url), urlparse(final_url)
        same_host = bare_host(original_url) == bare_host(final_url)

        if same_host and orig.path.strip("/") and not final.path.strip("/"):
            reason = "Redirected to the site root (typical soft-404)."

    return title, reason


def _request(url, headers, timeout, method):
    return requests.request(
        method,
        url,
        headers=headers,
        timeout=timeout,
        allow_redirects=False,
        stream=True,
    )


def check_live(url, timeout=10, user_agent="URLHealth/1.0", allow_private=False):
    """Check a single URL and classify it.

    Statuses: alive, soft_404, redirected_to_root, blocked, dead,
    server_error, dns_error, ssl_error, timeout, unreachable,
    too_many_redirects, unsafe.
    """

    started = time.monotonic()
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    current = url
    chain = []

    def elapsed():
        return round((time.monotonic() - started) * 1000)

    try:
        for _ in range(MAX_REDIRECTS + 1):
            target = check_target(current, allow_private=allow_private)

            if target == "private":
                return _result(
                    "unsafe", url, final_url=current, redirects=chain,
                    reason="URL resolves to a private or reserved address.",
                    latency_ms=elapsed(),
                )

            if target == "dns_error":
                return _result(
                    "dns_error", url, final_url=current, redirects=chain,
                    reason="Domain name could not be resolved.",
                    latency_ms=elapsed(),
                )

            response = _request(current, headers, timeout, "HEAD")

            # Many servers reject or mishandle HEAD; retry once with GET.
            if response.status_code >= 400:
                response.close()
                response = _request(current, headers, timeout, "GET")

            code = response.status_code

            if code in REDIRECT_STATUS:
                location = response.headers.get("Location")
                response.close()

                if not location:
                    return _result(
                        "unreachable", url, final_url=current, http_status=code,
                        redirects=chain, reason="Redirect without Location header.",
                        latency_ms=elapsed(),
                    )

                chain.append({"from": current, "status": code})
                current = urljoin(current, location)
                continue

            content_type = (response.headers.get("Content-Type") or "").lower()

            if 200 <= code < 300:
                body = ""

                if "html" in content_type:
                    # HEAD has no body; fetch a small slice for soft-404 checks.
                    if response.request.method == "HEAD":
                        response.close()
                        response = _request(current, headers, timeout, "GET")

                    raw = next(response.iter_content(MAX_BODY_BYTES), b"")
                    body = raw.decode(response.encoding or "utf-8", errors="ignore")

                response.close()
                title, reason = _detect_soft_404(body, url, current)

                if reason:
                    status = (
                        "redirected_to_root"
                        if reason.startswith("Redirected")
                        else "soft_404"
                    )
                    return _result(
                        status, url, final_url=current, http_status=code,
                        redirects=chain, content_type=content_type,
                        title=title or None, reason=reason, latency_ms=elapsed(),
                    )

                return _result(
                    "alive", url, final_url=current, http_status=code,
                    redirects=chain, content_type=content_type,
                    title=title or None, latency_ms=elapsed(),
                )

            response.close()

            if code in BLOCKED_STATUS:
                status, reason = "blocked", f"Server refused automated access (HTTP {code})."
            elif code >= 500:
                status, reason = "server_error", f"Server error (HTTP {code})."
            else:
                status, reason = "dead", f"HTTP {code}."

            return _result(
                status, url, final_url=current, http_status=code,
                redirects=chain, content_type=content_type,
                reason=reason, latency_ms=elapsed(),
            )

        return _result(
            "too_many_redirects", url, final_url=current, redirects=chain,
            reason=f"More than {MAX_REDIRECTS} redirects.", latency_ms=elapsed(),
        )

    except requests.exceptions.SSLError as exc:
        return _result("ssl_error", url, final_url=current, redirects=chain,
                       reason=str(exc)[:200], latency_ms=elapsed())
    except requests.exceptions.Timeout:
        return _result("timeout", url, final_url=current, redirects=chain,
                       reason=f"No response within {timeout}s.", latency_ms=elapsed())
    except requests.exceptions.RequestException as exc:
        return _result("unreachable", url, final_url=current, redirects=chain,
                       reason=str(exc)[:200], latency_ms=elapsed())
