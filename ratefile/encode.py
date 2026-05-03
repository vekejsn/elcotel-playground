"""Encode compiled R94 models into the low-level payload consumed by the writer."""

from __future__ import annotations

from collections import Counter

from .constants import CATEGORY_ORDER, CATEGORY_TITLE_MAP, GROUP_START_OFFSET
from .types import CompiledRateFile


def _category_counts(model: CompiledRateFile) -> dict[str, int]:
    """Return the count of compiled bands in each R94 category bucket."""
    counts = Counter(band.category for band in model.price_bands)
    return {category: counts.get(category, 0) for category in CATEGORY_ORDER}


def model_to_header_dict(model: CompiledRateFile) -> dict:
    """Convert a compiled ratefile model into the writer header dictionary."""
    counts = _category_counts(model)
    return {
        "is_ratefile": model.header.is_ratefile,
        "description": model.header.description,
        "home_npa": model.header.home_npa,
        "home_nxx": model.header.home_nxx,
        "local_band_count": counts["local"],
        "intralata_band_count": counts["intralata"],
        "interlata_band_count": counts["interlata"],
        "interstate_band_count": counts["interstate"],
        "corridor_band_count": counts["corridor"],
        "canadian_band_count": counts["canadian"],
        "extended_band_count": counts["extended"],
        "misc_band_count": counts["misc"],
    }


def model_to_payload(model: CompiledRateFile) -> dict:
    """Convert a compiled ratefile model into the low-level writer payload."""
    counts = _category_counts(model)
    group_count = len(model.group_rows)
    price_count = len(model.price_bands)
    rate_band_offset = GROUP_START_OFFSET + (6 * group_count)
    nxx_offset = rate_band_offset + (4 * price_count)
    return {
        "prices": {
            "group_count": group_count,
            "price_count": price_count,
            "nxx_count": len(model.nxx_tables),
            "rate_band_offset": rate_band_offset,
            "nxx_offset": nxx_offset,
            "local_count": counts["local"],
            "intralata_count": counts["intralata"],
            "interlata_count": counts["interlata"],
            "interstate_count": counts["interstate"],
            "corridor_count": counts["corridor"],
            "canadian_count": counts["canadian"],
            "extended_count": counts["extended"],
            "misc_count": counts["misc"],
        },
        "rate_entries": [
            {
                "initial_rate": band.initial_rate,
                "initial_time": band.initial_time,
                "additional_rate": band.additional_rate,
                "additional_time": band.additional_time,
            }
            for band in model.price_bands
        ],
        "nxx_table": [
            {
                "price_band": table.price_band,
                "dial_pattern": table.dial_pattern,
                "flags": table.flags,
                "nxx_entries": [
                    {"enabled": nxx in table.enabled_nxx} for nxx in range(200, 1000)
                ],
            }
            for table in model.nxx_tables
        ],
        "intrastate_npas": [
            {
                "NPA": row.npa,
                "NXX_count": row.nxx_table_count,
                "band": row.unlisted_price_band,
                "dial_plan": row.unlisted_dial_pattern,
                "initial_price": row.flags,
            }
            for row in model.group_rows
        ],
        "surcharges": {
            CATEGORY_TITLE_MAP[category]: {
                "coin": values.coin,
                "paof_bell": values.paof_bell,
                "paof_comm": values.paof_comm,
                "paof_collect": values.paof_collect,
                "paof_addtnl": values.paof_addtnl,
                "chip_card": values.chip_card,
                "spare_1": values.spare_1,
                "spare_2": values.spare_2,
            }
            for category, values in model.surcharges.items()
        },
        "npa_prices": [
            {"npa": entry.npa, "raw_value": entry.raw_value}
            for entry in model.npa_prices
        ],
    }
