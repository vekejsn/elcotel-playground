"""Classify exchanges into locality relationships for Elcotel generation."""

from __future__ import annotations

from .types import ExchangeRecord, GenerationRequest
from .policy import relationship_override_for_npa


# Relationship precedence mixes discovered facts with policy-driven overrides:
# invalid/unassigned -> local -> special policy buckets -> national geography ->
# LATA-based toll classes. This keeps policy-only categories like corridor and
# misc from overriding genuinely local destinations.
def classify_exchange(
    home: ExchangeRecord,
    candidate: ExchangeRecord,
    request: GenerationRequest,
    local_targets: set[tuple[int, int]],
    lata_targets: set[tuple[int, int]],
) -> str:
    if not candidate.is_assigned:
        return "invalid"
    if candidate.key == home.key:
        return "local"
    if candidate.key in local_targets:
        return "local"
    if (
        home.rate_center
        and candidate.rate_center
        and home.rate_center == candidate.rate_center
    ):
        return "local"

    override = relationship_override_for_npa(request, candidate.npa)
    if override is not None:
        return override

    if candidate.country == "CA" and home.country != "CA":
        return "canadian"
    if home.country != candidate.country:
        return "interstate"
    if home.state and candidate.state and home.state != candidate.state:
        return "interstate"
    if candidate.key in lata_targets:
        return "intralata"
    if home.lata and candidate.lata:
        return "intralata" if home.lata == candidate.lata else "interlata"
    return "interlata"
