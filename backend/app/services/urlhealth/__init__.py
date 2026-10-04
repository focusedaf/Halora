"""URL health checking with a waterfall cascade.

Stage 1: live check            -> is the URL still reachable?
Stage 2: archive cascade       -> perma.cc -> Wayback -> Arquivo.pt -> Memento
Stage 3: preserve (opt-in)     -> ask an archive to capture a live page
"""

from .cascade import (
    check_url_health,
    check_urls_health,
    check_text_urls,
    extract_urls,
    list_providers,
)

__all__ = [
    "check_url_health",
    "check_urls_health",
    "check_text_urls",
    "extract_urls",
    "list_providers",
]
