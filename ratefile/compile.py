"""Compile explicit Elcotel tariff specs into ordered R94 structures."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .constants import (
    CATEGORY_ORDER,
    NPA_MAX,
    NPA_MIN,
    NXX_SPECIFIC_TOKEN,
    RESTRICTED_TOKEN,
    UNLIMITED_TOKEN,
)
from .types import (
    CompiledGroupRow,
    CompiledNpaPrice,
    CompiledNxxTable,
    CompiledPriceBand,
    CompiledRateFile,
    NxxOverrideRule,
    RateFileSpec,
    SurchargeSpec,
)
from .parser import RateFile, read_ratefile


def _expand_npa_rule(rule) -> list[int]:
    if rule.npa is not None:
        return [rule.npa]
    if rule.npa_range is None:
        return []
    return list(range(rule.npa_range[0], rule.npa_range[1] + 1))


def _expand_nxx_rule(rule: NxxOverrideRule) -> set[int]:
    values = set(rule.nxx)
    for low, high in rule.nxx_ranges:
        values.update(range(low, high + 1))
    return values


def _compile_price_bands(
    spec: RateFileSpec,
) -> tuple[list[CompiledPriceBand], dict[str, CompiledPriceBand]]:
    # R94 does not tag each band with a category. Instead the category is inferred
    # from its position in the ordered band list, so we must emit them grouped in
    # the original local -> intralata -> ... -> misc order.
    by_category = defaultdict(list)
    for band in spec.price_bands:
        by_category[band.category].append(band)
    compiled = []
    band_lookup = {}
    band_index = 1
    for category in CATEGORY_ORDER:
        for group_sequence, band in enumerate(by_category[category], start=1):
            compiled_band = CompiledPriceBand(
                band_id=band.band_id,
                band_index=band_index,
                category=category,
                group_sequence=group_sequence,
                initial_rate=band.initial_rate,
                initial_time=band.initial_time,
                additional_rate=band.additional_rate,
                additional_time=band.additional_time,
            )
            compiled.append(compiled_band)
            band_lookup[band.band_id] = compiled_band
            band_index += 1
    return compiled, band_lookup


def _compile_npa_prices(
    spec: RateFileSpec,
    band_lookup: dict[str, CompiledPriceBand],
    template: RateFile | None,
) -> list[CompiledNpaPrice]:
    # The top-level NPA table acts as the default for each area code. Any NPA that
    # receives explicit NXX tables must also be marked as NXX-specific here.
    if template is not None:
        raw_values = {entry.npa: entry.raw_value for entry in template.npa_prices}
    else:
        raw_values = {npa: RESTRICTED_TOKEN for npa in range(NPA_MIN, NPA_MAX + 1)}
    for rule in spec.npa_defaults:
        if rule.raw_value is not None:
            value = rule.raw_value
        elif rule.kind == "restricted":
            value = RESTRICTED_TOKEN
        elif rule.kind == "unlimited":
            value = UNLIMITED_TOKEN
        elif rule.kind == "nxx_specific":
            value = NXX_SPECIFIC_TOKEN
        elif rule.kind == "price_band":
            value = band_lookup[rule.band_id].band_index
        else:
            raise ValueError(f"Unsupported npa_default kind: {rule.kind}")
        for npa in _expand_npa_rule(rule):
            raw_values[npa] = value
    for override in spec.nxx_overrides:
        raw_values[override.npa] = NXX_SPECIFIC_TOKEN
    return [
        CompiledNpaPrice(npa=npa, raw_value=raw_values[npa])
        for npa in range(NPA_MIN, NPA_MAX + 1)
    ]


def _compile_nxx_groups(
    spec: RateFileSpec, band_lookup: dict[str, CompiledPriceBand]
) -> tuple[list[CompiledGroupRow], list[CompiledNxxTable]]:
    # One group row is emitted per NPA per category bucket. That means the same NPA
    # can appear multiple times when it has, for example, both local and intralata
    # NXX-specific overrides.
    unlisted_lookup = {(entry.npa, entry.category): entry for entry in spec.unlisted}
    grouped_tables = defaultdict(set)
    table_meta = {}
    for override in spec.nxx_overrides:
        band = band_lookup[override.band_id]
        key = (
            override.npa,
            band.category,
            band.band_index,
            override.dial_pattern,
            override.flags,
        )
        grouped_tables[key].update(_expand_nxx_rule(override))
        table_meta[key] = (
            override.npa,
            band.category,
            band.band_index,
            override.dial_pattern,
            override.flags,
        )
    nxx_tables = []
    grouped_by_npa_category = defaultdict(list)
    for key, enabled_nxx in sorted(grouped_tables.items()):
        npa, category, band_index, dial_pattern, flags = table_meta[key]
        table = CompiledNxxTable(
            npa=npa,
            category=category,
            price_band=band_index,
            dial_pattern=dial_pattern,
            flags=flags,
            enabled_nxx=set(enabled_nxx),
        )
        nxx_tables.append(table)
        grouped_by_npa_category[(npa, category)].append(table)
    group_rows = []
    for key in sorted(
        grouped_by_npa_category,
        key=lambda item: (item[0], CATEGORY_ORDER.index(item[1])),
    ):
        npa, category = key
        unlisted = unlisted_lookup[(npa, category)]
        group_rows.append(
            CompiledGroupRow(
                npa=npa,
                category=category,
                nxx_table_count=len(grouped_by_npa_category[key]),
                unlisted_price_band=band_lookup[unlisted.band_id].band_index,
                unlisted_dial_pattern=unlisted.dial_pattern,
                flags=unlisted.flags,
            )
        )
    return group_rows, nxx_tables


def compile_ratefile_spec(
    spec: RateFileSpec, template_path: str | None = None
) -> CompiledRateFile:
    template = read_ratefile(template_path) if template_path else None
    compiled_price_bands, band_lookup = _compile_price_bands(spec)
    npa_prices = _compile_npa_prices(spec, band_lookup, template)
    group_rows, nxx_tables = _compile_nxx_groups(spec, band_lookup)
    surcharges = dict(spec.surcharges)
    for category in CATEGORY_ORDER:
        surcharges.setdefault(category, SurchargeSpec())
    return CompiledRateFile(
        header=spec.header,
        price_bands=compiled_price_bands,
        npa_prices=npa_prices,
        group_rows=group_rows,
        nxx_tables=nxx_tables,
        surcharges=surcharges,
        template_header=Path(template_path).read_bytes()[:268]
        if template_path
        else None,
    )
