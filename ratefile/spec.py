"""Load and validate high-level explicit tariff specs for Elcotel generation."""

from __future__ import annotations

import json
from pathlib import Path

from .constants import (
    CATEGORY_ORDER,
    CATEGORY_TITLE_MAP,
    NPA_MAX,
    NPA_MIN,
    NXX_MAX,
    NXX_MIN,
)
from .types import (
    HeaderSpec,
    NpaDefaultRule,
    NxxOverrideRule,
    PriceBandSpec,
    RateFileSpec,
    SurchargeSpec,
    UnlistedRule,
)


def load_raw_document(path: str | Path) -> dict:
    return _load_raw(Path(path)) or {}


def _load_raw(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise ValueError("YAML input requires PyYAML to be installed.") from exc
    return yaml.safe_load(text)


def _normalize_category(category: str) -> str:
    normalized = category.strip().lower().replace("-", "")
    aliases = {
        "intralata": "intralata",
        "interlata": "interlata",
        "fcc": "interstate",
        "interstate": "interstate",
    }
    if normalized in CATEGORY_ORDER:
        return normalized
    if normalized in aliases:
        return aliases[normalized]
    raise ValueError(f"Unknown category: {category}")


def _require_three_digits(value: str | int, label: str) -> int:
    parsed = int(str(value))
    if label == "npa" and not (NPA_MIN <= parsed <= NPA_MAX):
        raise ValueError(f"NPA out of range: {parsed}")
    if label == "nxx" and not (NXX_MIN <= parsed <= NXX_MAX):
        raise ValueError(f"NXX out of range: {parsed}")
    return parsed


def _parse_range(values: list[str | int], label: str) -> tuple[int, int]:
    if len(values) != 2:
        raise ValueError(f"Expected two values for {label}_range")
    low = _require_three_digits(values[0], label)
    high = _require_three_digits(values[1], label)
    if low > high:
        raise ValueError(f"Invalid {label}_range: {low}>{high}")
    return low, high


def load_spec(path: str | Path) -> RateFileSpec:
    # Explicit spec mode expects the caller to already know the pricing bands and
    # NPA/NXX relationships that should be encoded into the file.
    raw = load_raw_document(path)
    header_raw = raw.get("header", {})
    header = HeaderSpec(
        description=header_raw.get("description", ""),
        home_npa=str(header_raw.get("home_npa", "")),
        home_nxx=str(header_raw.get("home_nxx", "")),
        is_ratefile=header_raw.get("is_ratefile", True),
    )
    price_bands = []
    for entry in raw.get("price_bands", []):
        price_bands.append(
            PriceBandSpec(
                band_id=entry["id"],
                category=_normalize_category(entry["category"]),
                initial_rate=int(entry["initial_rate"]),
                initial_time=int(entry["initial_time"]),
                additional_rate=int(entry["additional_rate"]),
                additional_time=int(entry["additional_time"]),
            )
        )
    npa_defaults = []
    for entry in raw.get("npa_defaults", []):
        npa_defaults.append(
            NpaDefaultRule(
                npa=_require_three_digits(entry["npa"], "npa")
                if "npa" in entry
                else None,
                npa_range=_parse_range(entry["npa_range"], "npa")
                if "npa_range" in entry
                else None,
                kind=entry.get("kind", "restricted"),
                band_id=entry.get("band"),
                raw_value=entry.get("raw_value"),
            )
        )
    nxx_overrides = []
    for entry in raw.get("nxx_overrides", []):
        nxx_overrides.append(
            NxxOverrideRule(
                npa=_require_three_digits(entry["npa"], "npa"),
                band_id=entry["band"],
                dial_pattern=int(entry["dial_pattern"]),
                flags=int(entry.get("flags", 0)),
                nxx=[
                    _require_three_digits(value, "nxx")
                    for value in entry.get("nxx", [])
                ],
                nxx_ranges=[
                    _parse_range(values, "nxx")
                    for values in entry.get("nxx_ranges", [])
                ],
            )
        )
    unlisted = []
    for entry in raw.get("unlisted", []):
        unlisted.append(
            UnlistedRule(
                npa=_require_three_digits(entry["npa"], "npa"),
                category=_normalize_category(entry["category"]),
                band_id=entry["band"],
                dial_pattern=int(entry["dial_pattern"]),
                flags=int(entry.get("flags", 0)),
            )
        )
    surcharges = {}
    for key, entry in raw.get("surcharges", {}).items():
        normalized = _normalize_category(key)
        surcharges[normalized] = SurchargeSpec(
            coin=int(entry.get("coin", 0)),
            paof_bell=int(entry.get("paof_bell", 0)),
            paof_comm=int(entry.get("paof_comm", 0)),
            paof_collect=int(entry.get("paof_collect", 0)),
            paof_addtnl=int(entry.get("paof_addtnl", 0)),
            chip_card=int(entry.get("chip_card", 0)),
            spare_1=int(entry.get("spare_1", 0)),
            spare_2=int(entry.get("spare_2", 0)),
        )
    spec = RateFileSpec(
        header=header,
        price_bands=price_bands,
        npa_defaults=npa_defaults,
        nxx_overrides=nxx_overrides,
        unlisted=unlisted,
        surcharges=surcharges,
    )
    validate_spec(spec)
    return spec


def validate_spec(spec: RateFileSpec) -> None:
    if not spec.price_bands:
        raise ValueError("Spec must define at least one price band.")
    band_ids = set()
    for band in spec.price_bands:
        if band.band_id in band_ids:
            raise ValueError(f"Duplicate price band id: {band.band_id}")
        band_ids.add(band.band_id)
    for rule in spec.npa_defaults:
        if rule.npa is None and rule.npa_range is None:
            raise ValueError("Each npa_default must define npa or npa_range.")
        if rule.kind == "price_band" and rule.band_id not in band_ids:
            raise ValueError(f"Unknown price band in npa_defaults: {rule.band_id}")
    unlisted_keys = {(entry.npa, entry.category) for entry in spec.unlisted}
    for override in spec.nxx_overrides:
        if override.band_id not in band_ids:
            raise ValueError(f"Unknown price band in nxx_overrides: {override.band_id}")
        if not override.nxx and not override.nxx_ranges:
            raise ValueError(f"NXX override for NPA {override.npa} has no NXX values.")
    for entry in spec.unlisted:
        if entry.band_id not in band_ids:
            raise ValueError(f"Unknown price band in unlisted: {entry.band_id}")
    band_categories = {band.band_id: band.category for band in spec.price_bands}
    for override in spec.nxx_overrides:
        category = band_categories[override.band_id]
        if (override.npa, category) not in unlisted_keys:
            raise ValueError(
                f"Missing unlisted rule for NPA {override.npa} category {category}."
            )
    for category in spec.surcharges:
        if category not in CATEGORY_ORDER:
            raise ValueError(f"Unknown surcharge category: {category}")


def surcharge_titles(spec: RateFileSpec) -> dict[str, SurchargeSpec]:
    return {CATEGORY_TITLE_MAP[key]: value for key, value in spec.surcharges.items()}
