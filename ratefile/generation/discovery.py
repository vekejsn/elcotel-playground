"""Discover locality relationships for Elcotel generation requests."""

from __future__ import annotations

from pathlib import Path

from ..spec import load_raw_document
from ..types import HeaderSpec, PriceBandSpec, SurchargeSpec
from .lcg import (
    fetch_local_prefixes,
    fetch_ratecenters_by_lata,
    fetch_ratecenters_by_lir,
    lookup_prefix,
)
from .relationships import classify_exchange
from .sources import (
    ensure_default_exchange_paths,
    load_exchange_records,
    load_local_targets,
)
from .types import DiscoveryResult, GenerationRequest


def _load_price_bands(raw_bands: list[dict]) -> list[PriceBandSpec]:
    """Normalize price-band dictionaries from a discovery request document."""
    return [
        PriceBandSpec(
            band_id=entry["id"],
            category=entry["category"].strip().lower().replace("-", ""),
            initial_rate=int(entry["initial_rate"]),
            initial_time=int(entry["initial_time"]),
            additional_rate=int(entry["additional_rate"]),
            additional_time=int(entry["additional_time"]),
        )
        for entry in raw_bands
    ]


def _load_surcharges(raw_surcharges: dict) -> dict[str, SurchargeSpec]:
    """Normalize surcharge dictionaries from a discovery request document."""
    normalized: dict[str, SurchargeSpec] = {}
    for key, values in raw_surcharges.items():
        category = key.strip().lower().replace("-", "")
        normalized[category] = SurchargeSpec(
            coin=int(values.get("coin", 0)),
            paof_bell=int(values.get("paof_bell", 0)),
            paof_comm=int(values.get("paof_comm", 0)),
            paof_collect=int(values.get("paof_collect", 0)),
            paof_addtnl=int(values.get("paof_addtnl", 0)),
            chip_card=int(values.get("chip_card", 0)),
            spare_1=int(values.get("spare_1", 0)),
            spare_2=int(values.get("spare_2", 0)),
        )
    return normalized


def build_generation_request(
    *,
    home_npa: int,
    home_nxx: int,
    exchange_data: list[str],
    header: HeaderSpec | None = None,
    local_data: list[str] | None = None,
    discovery_mode: str = "offline",
    country: str = "US",
    state: str = "",
    template: str | None = None,
    cache_dir: str = "ratefile/cache",
    data_dir: str = "ratefile/data",
    cache_age_days: int = 14,
    use_offline_validation: bool = True,
    price_bands: list[PriceBandSpec] | None = None,
    relationship_map: dict[str, str] | None = None,
    default_dial_patterns: dict[str, int] | None = None,
    default_flags: dict[str, int] | None = None,
    special_npas: dict[str, set[int]] | None = None,
    surcharges: dict[str, SurchargeSpec] | None = None,
) -> GenerationRequest:
    """Build a generation request from direct CLI or test inputs."""
    return GenerationRequest(
        header=header or HeaderSpec(home_npa=str(home_npa), home_nxx=str(home_nxx)),
        home_npa=home_npa,
        home_nxx=home_nxx,
        discovery_mode=discovery_mode,
        exchange_data=exchange_data,
        local_data=local_data or [],
        country=country,
        state=state,
        template=template,
        cache_dir=cache_dir,
        data_dir=data_dir,
        cache_age_days=cache_age_days,
        use_offline_validation=use_offline_validation,
        price_bands=price_bands or [],
        relationship_map=relationship_map or {},
        default_dial_patterns=default_dial_patterns or {},
        default_flags=default_flags or {},
        special_npas=special_npas or {},
        surcharges=surcharges or {},
    )


def load_generation_request(path: str | Path) -> GenerationRequest:
    """Load a discovery request document from JSON or YAML."""
    raw = load_raw_document(path)
    pricing = raw.get("pricing", {})
    header_raw = raw.get("header", {})
    header = HeaderSpec(
        description=header_raw.get("description", ""),
        home_npa=str(header_raw.get("home_npa", raw.get("home_npa", ""))),
        home_nxx=str(header_raw.get("home_nxx", raw.get("home_nxx", ""))),
        is_ratefile=header_raw.get("is_ratefile", True),
    )
    special_npas = {
        key.strip().lower().replace("-", ""): {int(value) for value in values}
        for key, values in pricing.get("special_npas", {}).items()
    }
    sources = raw.get("sources", {})
    exchange_data = sources.get("exchange_data", [])
    if isinstance(exchange_data, str):
        exchange_data = [exchange_data]
    local_data = sources.get("local_data", []) or sources.get("lir_data", [])
    if isinstance(local_data, str):
        local_data = [local_data]
    return build_generation_request(
        home_npa=int(raw.get("home_npa", header.home_npa)),
        home_nxx=int(raw.get("home_nxx", header.home_nxx)),
        exchange_data=exchange_data,
        local_data=local_data,
        header=header,
        discovery_mode=raw.get("discovery_mode", "offline"),
        country=raw.get("country", sources.get("country", "US")),
        state=raw.get("state", sources.get("state", "")),
        template=raw.get("template"),
        cache_dir=raw.get("cache_dir", "ratefile/cache"),
        data_dir=raw.get("data_dir", "ratefile/data"),
        cache_age_days=int(raw.get("cache_age_days", 14)),
        use_offline_validation=bool(raw.get("use_offline_validation", True)),
        price_bands=_load_price_bands(pricing.get("bands", [])),
        relationship_map={
            key.strip().lower().replace("-", ""): value
            for key, value in pricing.get("relationship_map", {}).items()
        },
        default_dial_patterns={
            key.strip().lower().replace("-", ""): int(value)
            for key, value in pricing.get("default_dial_patterns", {}).items()
        },
        default_flags={
            key.strip().lower().replace("-", ""): int(value)
            for key, value in pricing.get("default_flags", {}).items()
        },
        special_npas=special_npas,
        surcharges=_load_surcharges(
            raw.get("surcharges", pricing.get("surcharges", {}))
        ),
    )


def _load_api_targets(
    request: GenerationRequest,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]], dict[str, str]]:
    """Expand LocalCallingGuide results into local and LATA/LIR target sets."""
    prefix = lookup_prefix(
        request.home_npa,
        request.home_nxx,
        request.cache_dir,
        request.cache_age_days,
    )
    local_targets: set[tuple[int, int]] = set()
    lata_targets: set[tuple[int, int]] = set()

    exchange = prefix.get("exch", "")
    if exchange:
        for item in fetch_local_prefixes(
            exchange, request.cache_dir, request.cache_age_days
        ):
            npa = item.get("npa")
            nxx = item.get("nxx")
            if npa and nxx:
                local_targets.add((int(npa), int(nxx)))

    if request.discovery_mode == "api-lata" and prefix.get("lata"):
        ratecenters = fetch_ratecenters_by_lata(
            prefix["lata"], request.cache_dir, request.cache_age_days
        )
    elif request.discovery_mode == "api-lir" and prefix.get("lir"):
        ratecenters = fetch_ratecenters_by_lir(
            prefix["lir"], request.cache_dir, request.cache_age_days
        )
    else:
        ratecenters = []

    for ratecenter in ratecenters:
        exchange_name = ratecenter.get("exch", "")
        see_exch = ratecenter.get("see_exch", "")
        if not exchange_name or (see_exch and see_exch != "None"):
            continue
        for item in fetch_local_prefixes(
            exchange_name, request.cache_dir, request.cache_age_days
        ):
            npa = item.get("npa")
            nxx = item.get("nxx")
            if npa and nxx:
                lata_targets.add((int(npa), int(nxx)))

    return local_targets, lata_targets, prefix


def discover_relationships(request: GenerationRequest) -> DiscoveryResult:
    """Classify all relevant exchanges for one generation request."""
    exchange_paths = list(request.exchange_data)
    if request.use_offline_validation and not exchange_paths:
        exchange_paths = ensure_default_exchange_paths(request.data_dir)
    records = load_exchange_records(exchange_paths)

    home_exchange = next(
        (
            record
            for record in records
            if record.npa == request.home_npa and record.nxx == request.home_nxx
        ),
        None,
    )
    if home_exchange is None:
        raise ValueError(
            f"Home exchange {request.home_npa}-{request.home_nxx} was not found in the exchange data."
        )

    if request.discovery_mode in {"api-lata", "api-lir"}:
        local_targets, lata_targets, metadata = _load_api_targets(request)
        if metadata.get("state") and not home_exchange.state:
            home_exchange.state = metadata["state"]
        if metadata.get("lata") and not home_exchange.lata:
            home_exchange.lata = metadata["lata"]
    else:
        local_targets = load_local_targets(
            request.local_data, request.home_npa, request.home_nxx
        )
        lata_targets = set()
        metadata = {}

    relationships: dict[str, list] = {}
    for record in records:
        relationship = classify_exchange(
            home_exchange, record, request, local_targets, lata_targets
        )
        relationships.setdefault(relationship, []).append(record)

    return DiscoveryResult(
        request=request,
        home_exchange=home_exchange,
        records=records,
        local_targets=local_targets,
        lata_targets=lata_targets,
        metadata=metadata,
        relationships=relationships,
    )
