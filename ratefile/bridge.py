"""Bridge parsed R94 models to summaries and writer-compatible payloads."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

from .constants import CATEGORY_ORDER, CATEGORY_TITLE_MAP

if TYPE_CHECKING:
    from .parser import RateFile


def model_dump(model: Any) -> Any:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    return model


def ratefile_to_writer_payload(parsed: RateFile) -> dict[str, Any]:
    return {
        "header": {
            "is_ratefile": parsed.header.is_ratefile,
            "description": parsed.header.description,
            "home_npa": parsed.header.home_npa.strip("\x00"),
            "home_nxx": parsed.header.home_nxx.strip("\x00"),
            "local_band_count": parsed.price_plan.local_band_count,
            "intralata_band_count": parsed.price_plan.intralata_band_count,
            "interlata_band_count": parsed.price_plan.interlata_band_count,
            "interstate_band_count": parsed.price_plan.interstate_band_count,
            "corridor_band_count": parsed.price_plan.corridor_band_count,
            "canadian_band_count": parsed.price_plan.canadian_band_count,
            "extended_band_count": parsed.price_plan.extended_band_count,
            "misc_band_count": parsed.price_plan.misc_band_count,
        },
        "prices": {
            "group_count": parsed.price_plan.npa_group_count,
            "price_count": parsed.price_plan.price_band_count,
            "nxx_count": parsed.price_plan.nxx_table_count,
            "rate_band_offset": parsed.price_plan.price_band_offset,
            "nxx_offset": parsed.price_plan.nxx_table_offset,
            "local_count": parsed.price_plan.local_band_count,
            "intralata_count": parsed.price_plan.intralata_band_count,
            "interlata_count": parsed.price_plan.interlata_band_count,
            "interstate_count": parsed.price_plan.interstate_band_count,
            "corridor_count": parsed.price_plan.corridor_band_count,
            "canadian_count": parsed.price_plan.canadian_band_count,
            "extended_count": parsed.price_plan.extended_band_count,
            "misc_count": parsed.price_plan.misc_band_count,
        },
        "rate_entries": [
            {
                "initial_rate": band.init_rate,
                "initial_time": band.init_time,
                "additional_rate": band.addtnl_rate,
                "additional_time": band.addtnl_time,
            }
            for band in parsed.price_plan.price_bands
        ],
        "nxx_table": [
            {
                "price_band": table.price_band,
                "dial_pattern": table.dial_pattern,
                "flags": table.flags,
                "nxx_entries": [
                    {"enabled": entry.enabled} for entry in table.nxx_entries
                ],
            }
            for table in parsed.nxx_tables
        ],
        "intrastate_npas": [
            {
                "NPA": group.npa,
                "NXX_count": group.nxx_table_count,
                "band": group.unlisted_price_band,
                "dial_plan": group.unlisted_dial_pattern,
                "initial_price": group.flags,
            }
            for group in parsed.npa_groups
        ],
        "surcharges": {
            CATEGORY_TITLE_MAP[CATEGORY_ORDER[index]]: {
                "coin": surcharge.coin,
                "paof_bell": surcharge.paof_bell,
                "paof_comm": surcharge.paof_comm,
                "paof_collect": surcharge.paof_collect,
                "paof_addtnl": surcharge.paof_addtnl,
                "chip_card": surcharge.chip_card,
                "spare_1": surcharge.spare_1,
                "spare_2": surcharge.spare_2,
            }
            for index, surcharge in enumerate(parsed.surcharges)
        },
        "npa_prices": [
            {"npa": entry.npa, "raw_value": entry.raw_value}
            for entry in parsed.npa_prices
        ],
    }


def ratefile_summary(parsed: RateFile) -> dict[str, Any]:
    npa_kind_counts = Counter(entry.kind for entry in parsed.npa_prices)
    repeated_group_npas = Counter(group.npa for group in parsed.npa_groups)
    return {
        "description": parsed.header.description,
        "home_npa": parsed.header.home_npa.strip("\x00"),
        "home_nxx": parsed.header.home_nxx.strip("\x00"),
        "decompressed_size": parsed.header.filesize,
        "price_bands": parsed.price_plan.price_band_count,
        "npa_groups": parsed.price_plan.npa_group_count,
        "nxx_tables": parsed.price_plan.nxx_table_count,
        "band_counts": {
            "local": parsed.price_plan.local_band_count,
            "intralata": parsed.price_plan.intralata_band_count,
            "interlata": parsed.price_plan.interlata_band_count,
            "interstate": parsed.price_plan.interstate_band_count,
            "corridor": parsed.price_plan.corridor_band_count,
            "canadian": parsed.price_plan.canadian_band_count,
            "extended": parsed.price_plan.extended_band_count,
            "misc": parsed.price_plan.misc_band_count,
        },
        "npa_kinds": dict(npa_kind_counts),
        "repeated_group_npas": {
            str(npa): count for npa, count in repeated_group_npas.items() if count > 1
        },
    }
