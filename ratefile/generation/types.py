"""Define the discovery-side dataclasses used by Elcotel generation workflows."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..types import HeaderSpec, PriceBandSpec, SurchargeSpec


@dataclass
class ExchangeRecord:
    """Represent one normalized NPA-NXX record from a source dataset or API."""

    npa: int
    nxx: int
    country: str = "US"
    state: str = ""
    rate_center: str = ""
    lata: str = ""
    status: str = "assigned"

    @property
    def key(self) -> tuple[int, int]:
        """Return the `(NPA, NXX)` tuple used by relationship sets."""
        return (self.npa, self.nxx)

    @property
    def is_assigned(self) -> bool:
        """Return whether the exchange should be considered dialable."""
        return self.status == "assigned"


@dataclass
class GenerationRequest:
    """Collect every input needed to generate an R94 from discovery data."""

    header: HeaderSpec
    home_npa: int
    home_nxx: int
    discovery_mode: str = "offline"
    exchange_data: list[str] = field(default_factory=list)
    local_data: list[str] = field(default_factory=list)
    country: str = "US"
    state: str = ""
    template: str | None = None
    cache_dir: str = "elcotel-playground/ratefile/cache"
    data_dir: str = "elcotel-playground/ratefile/data"
    cache_age_days: int = 14
    use_offline_validation: bool = True
    price_bands: list[PriceBandSpec] = field(default_factory=list)
    relationship_map: dict[str, str] = field(default_factory=dict)
    default_dial_patterns: dict[str, int] = field(default_factory=dict)
    default_flags: dict[str, int] = field(default_factory=dict)
    special_npas: dict[str, set[int]] = field(default_factory=dict)
    surcharges: dict[str, SurchargeSpec] = field(default_factory=dict)


@dataclass
class DiscoveryResult:
    """Store the classified locality data produced from one generation request."""

    request: GenerationRequest
    home_exchange: ExchangeRecord
    records: list[ExchangeRecord]
    local_targets: set[tuple[int, int]] = field(default_factory=set)
    lata_targets: set[tuple[int, int]] = field(default_factory=set)
    metadata: dict[str, str] = field(default_factory=dict)
    relationships: dict[str, list[ExchangeRecord]] = field(default_factory=dict)
