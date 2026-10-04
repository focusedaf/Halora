"""Response typing helpers.

The verification pipeline intentionally returns a nested JSON object whose
shape can evolve as the research implementation grows, so the API currently
returns the pipeline dictionary directly instead of enforcing a rigid schema.
"""

from typing import Any, TypeAlias

VerificationResult: TypeAlias = dict[str, Any]
