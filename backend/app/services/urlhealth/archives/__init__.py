"""Archive provider registry. Add a new archive by dropping a module here and
registering it in PROVIDERS."""

from .arquivo import ArquivoProvider
from .base import ArchiveProvider, snapshot_result
from .memento import MementoProvider
from .perma import PermaProvider
from .wayback import WaybackProvider

PROVIDERS = {
    "perma": PermaProvider,
    "wayback": WaybackProvider,
    "arquivo": ArquivoProvider,
    "memento": MementoProvider,
}


def build_providers(order, timeout, user_agent, settings):
    """Instantiate providers in cascade order, skipping unknown names."""

    providers = []
    seen = set()

    for name in order:
        name = name.strip().lower()

        if name in PROVIDERS and name not in seen:
            providers.append(PROVIDERS[name](timeout, user_agent, settings))
            seen.add(name)

    return providers


__all__ = ["ArchiveProvider", "PROVIDERS", "build_providers", "snapshot_result"]
