"""Store tiny pricing-policy helpers used during discovery and compilation."""

from __future__ import annotations

from .types import GenerationRequest


def dial_pattern_for(request: GenerationRequest, relationship: str) -> int:
    """Return the default dial pattern for one relationship class."""
    if relationship in request.default_dial_patterns:
        return request.default_dial_patterns[relationship]
    return 0 if relationship == "local" else 3


def flags_for(request: GenerationRequest, relationship: str) -> int:
    """Return the default flag byte for one relationship class."""
    return request.default_flags.get(relationship, 0)


def band_id_for(request: GenerationRequest, relationship: str) -> str:
    """Return the configured price-band id for one relationship class."""
    if relationship not in request.relationship_map:
        raise ValueError(f"Missing pricing mapping for relationship: {relationship}")
    return request.relationship_map[relationship]


def relationship_override_for_npa(request: GenerationRequest, npa: int) -> str | None:
    """Return a policy-only override category for one NPA if configured."""
    for relationship in ("corridor", "extended", "misc"):
        if npa in request.special_npas.get(relationship, set()):
            return relationship
    return None
