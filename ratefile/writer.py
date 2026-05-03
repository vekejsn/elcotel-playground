"""Build and write Elcotel R94 files from low-level writer payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .codec import compress
from .constants import CATEGORY_ORDER, CATEGORY_TITLE_MAP, HEADER_SIZE


def build_header(
    header_dict: dict[str, Any], template_header: bytes | None = None
) -> bytearray:
    """Build the fixed 268-byte R94 header from a header dictionary."""
    header = bytearray(
        template_header[:HEADER_SIZE] if template_header else b"\x00" * HEADER_SIZE
    )
    header[24] = 1 if header_dict.get("is_ratefile", False) else 0
    header[18:21] = (
        header_dict.get("home_npa", "")
        .encode("ascii", errors="ignore")
        .ljust(3, b"\x00")[:3]
    )
    header[21:24] = (
        header_dict.get("home_nxx", "")
        .encode("ascii", errors="ignore")
        .ljust(3, b"\x00")[:3]
    )

    counts_keys = [
        "local_band_count",
        "intralata_band_count",
        "interlata_band_count",
        "interstate_band_count",
        "corridor_band_count",
        "canadian_band_count",
        "extended_band_count",
        "misc_band_count",
    ]
    for index, key in enumerate(counts_keys):
        header[152 + index] = header_dict.get(key, 0)

    description_bytes = header_dict.get("description", "").encode(
        "ascii", errors="replace"
    )
    length = min(len(description_bytes), 255, HEADER_SIZE - 210)
    header[209] = length
    header[210 : 210 + length] = description_bytes[:length]
    if template_header is None and not header[0]:
        header[0] = 6
    return header


def build_decompressed(
    prices: dict[str, Any],
    rate_entries: list[dict[str, Any]],
    nxx_table: list[dict[str, Any]],
    intrastate_npas: list[dict[str, Any]],
    surcharges: dict[str, dict[str, int]],
    npa_prices: list[dict[str, Any]] | None = None,
) -> bytearray:
    """Build the raw decompressed R94 body from a writer-compatible payload."""
    group_count = prices.get("group_count", 0)
    price_count = prices.get("price_count", 0)
    nxx_count = prices.get("nxx_count", 0)
    rate_band_offset = prices.get("rate_band_offset", 0)
    nxx_offset = prices.get("nxx_offset", 0)
    size_candidates = [
        872,
        890 + 6 * group_count,
        (rate_band_offset - 1) + 4 * price_count,
        nxx_offset + 103 * nxx_count,
    ]
    decomp = bytearray(max(size_candidates))

    if npa_prices:
        for entry in npa_prices:
            npa = entry.get("npa")
            raw_value = entry.get("raw_value")
            if npa is not None and raw_value is not None and 200 <= npa <= 999:
                decomp[npa - 200] = raw_value

    decomp[864] = prices.get("local_count", 0)
    decomp[865] = prices.get("intralata_count", 0)
    decomp[866] = prices.get("interlata_count", 0)
    decomp[867] = prices.get("interstate_count", 0)
    decomp[868] = prices.get("corridor_count", 0)
    decomp[869] = prices.get("canadian_count", 0)
    decomp[870] = prices.get("extended_count", 0)
    decomp[871] = prices.get("misc_count", 0)
    decomp[873] = 0x77
    decomp[874] = 0x03
    decomp[875] = 0x7A
    decomp[876] = 0x03
    decomp[887] = prices.get("group_count", 0)
    decomp[888] = prices.get("price_count", 0)
    decomp[889] = prices.get("nxx_count", 0)

    if rate_band_offset > 0:
        value = rate_band_offset - 1
        decomp[877] = value & 0xFF
        decomp[878] = (value >> 8) & 0xFF
    decomp[879] = nxx_offset & 0xFF
    decomp[880] = (nxx_offset >> 8) & 0xFF

    cursor = rate_band_offset - 1
    for entry in rate_entries:
        decomp[cursor] = entry.get("initial_rate", 0)
        decomp[cursor + 1] = entry.get("initial_time", 0)
        decomp[cursor + 2] = entry.get("additional_rate", 0)
        decomp[cursor + 3] = entry.get("additional_time", 0)
        cursor += 4

    cursor = nxx_offset
    for entry in nxx_table:
        decomp[cursor] = entry.get("price_band", 0)
        decomp[cursor + 1] = entry.get("dial_pattern", 0)
        decomp[cursor + 2] = entry.get("flags", 0)
        bits = [0] * 100
        for index, item in enumerate(entry.get("nxx_entries", [])):
            if item.get("enabled", False):
                bits[index // 8] |= 1 << (index % 8)
        decomp[cursor + 3 : cursor + 103] = bytes(bits)
        cursor += 103

    cursor = 890
    for group in intrastate_npas:
        npa = group.get("NPA", 0)
        decomp[cursor] = npa & 0xFF
        decomp[cursor + 1] = (npa >> 8) & 0xFF
        decomp[cursor + 2] = group.get("NXX_count", 0)
        decomp[cursor + 3] = group.get("band", 0)
        decomp[cursor + 4] = group.get("dial_plan", 0)
        decomp[cursor + 5] = group.get("initial_price", 0)
        cursor += 6

    for index, category in enumerate(CATEGORY_ORDER):
        key = CATEGORY_TITLE_MAP[category]
        surcharge = surcharges.get(key, {})
        decomp[800 + index] = surcharge.get("coin", 0)
        decomp[800 + index + 8] = surcharge.get("paof_bell", 0)
        decomp[800 + index + 16] = surcharge.get("paof_comm", 0)
        decomp[800 + index + 24] = surcharge.get("paof_collect", 0)
        decomp[800 + index + 32] = surcharge.get("paof_addtnl", 0)
        decomp[800 + index + 40] = surcharge.get("chip_card", 0)
        decomp[800 + index + 48] = surcharge.get("spare_1", 0)
        decomp[800 + index + 56] = surcharge.get("spare_2", 0)
    return decomp


def write_ratefile_payload(
    header_dict: dict[str, Any],
    payload: dict[str, Any],
    output_filename: str | Path,
    *,
    template_header: bytes | None = None,
    verbose: bool = False,
) -> None:
    """Write one R94 file from a header dictionary and writer payload."""
    header_bytes = build_header(header_dict, template_header=template_header)
    decompressed_data = build_decompressed(
        payload["prices"],
        payload["rate_entries"],
        payload["nxx_table"],
        payload["intrastate_npas"],
        payload["surcharges"],
        payload.get("npa_prices"),
    )
    compressed_data = compress(decompressed_data)
    header_bytes[1:5] = len(decompressed_data).to_bytes(4, byteorder="little")
    output_path = Path(output_filename)
    output_path.write_bytes(header_bytes + compressed_data)
    if verbose:
        print(
            f"Wrote {output_path} with {len(header_bytes) + len(compressed_data)} bytes."
        )


def load_writer_payload(json_filename: str | Path) -> dict[str, Any]:
    """Load a writer-compatible JSON payload from disk."""
    with open(json_filename, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_ratefile(
    json_filename: str | Path, output_filename: str | Path, verbose: bool = False
) -> dict[str, Any]:
    """Load a writer payload from JSON and write it as an R94 file."""
    parsed = load_writer_payload(json_filename)
    write_ratefile_payload(
        parsed["header"],
        {
            "prices": parsed["prices"],
            "rate_entries": parsed["rate_entries"],
            "nxx_table": parsed["nxx_table"],
            "intrastate_npas": parsed["intrastate_npas"],
            "surcharges": parsed["surcharges"],
            "npa_prices": parsed.get("npa_prices"),
        },
        output_filename,
        verbose=verbose,
    )
    return parsed
