"""Compile discovery results into the normalized explicit spec used by R94 output."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ..types import NpaDefaultRule, NxxOverrideRule, RateFileSpec, UnlistedRule
from .discovery import discover_relationships
from .types import DiscoveryResult, GenerationRequest

DIRECT_DEFAULT_RELATIONSHIPS = {
    "intralata",
    "interlata",
    "interstate",
    "canadian",
    "corridor",
    "extended",
    "misc",
}


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


def load_template_header(path: str | None) -> bytes | None:
    """Load the fixed 268-byte header from a template file if one was supplied."""
    return Path(path).read_bytes()[:268] if path else None


def discovery_to_spec(result: DiscoveryResult) -> RateFileSpec:
    """Convert a discovery result into the explicit tariff spec consumed by R94 compilation."""
    request = result.request
    relationships_by_npa: dict[int, dict[str, set[int]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for relationship, records in result.relationships.items():
        if relationship == "invalid" or relationship not in request.relationship_map:
            continue
        for record in records:
            relationships_by_npa[record.npa][relationship].add(record.nxx)

    npa_defaults: list[NpaDefaultRule] = []
    nxx_overrides: list[NxxOverrideRule] = []
    unlisted_rules: list[UnlistedRule] = []

    for npa, relationship_sets in sorted(relationships_by_npa.items()):
        if len(relationship_sets) == 1:
            relationship = next(iter(relationship_sets))
            if relationship in DIRECT_DEFAULT_RELATIONSHIPS:
                npa_defaults.append(
                    NpaDefaultRule(
                        npa=npa,
                        kind="price_band",
                        band_id=band_id_for(request, relationship),
                    )
                )
                continue

        npa_defaults.append(NpaDefaultRule(npa=npa, kind="nxx_specific"))
        for relationship, nxx_values in sorted(relationship_sets.items()):
            band_id = band_id_for(request, relationship)
            nxx_overrides.append(
                NxxOverrideRule(
                    npa=npa,
                    band_id=band_id,
                    dial_pattern=dial_pattern_for(request, relationship),
                    flags=flags_for(request, relationship),
                    nxx=sorted(nxx_values),
                )
            )
            unlisted_rules.append(
                UnlistedRule(
                    npa=npa,
                    category=next(
                        b.category for b in request.price_bands if b.band_id == band_id
                    ),
                    band_id=band_id,
                    dial_pattern=dial_pattern_for(request, relationship),
                    flags=flags_for(request, relationship),
                )
            )

    deduped_unlisted = {(entry.npa, entry.category): entry for entry in unlisted_rules}
    return RateFileSpec(
        header=request.header,
        price_bands=request.price_bands,
        npa_defaults=npa_defaults,
        nxx_overrides=nxx_overrides,
        unlisted=list(deduped_unlisted.values()),
        surcharges=request.surcharges,
    )


def request_to_spec(request: GenerationRequest) -> RateFileSpec:
    """Discover relationships for a request and compile them into an explicit spec."""
    return discovery_to_spec(discover_relationships(request))
