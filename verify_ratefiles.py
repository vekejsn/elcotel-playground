# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import importlib.util
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_reconstructed_decompressed(parsed: Any, write_mod: Any) -> bytearray:
    prices = {
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
    }
    rate_entries = [
        {
            "initial_rate": band.init_rate,
            "initial_time": band.init_time,
            "additional_rate": band.addtnl_rate,
            "additional_time": band.addtnl_time,
        }
        for band in parsed.price_plan.price_bands
    ]
    nxx_table = [
        {
            "price_band": table.price_band,
            "dial_pattern": table.dial_pattern,
            "flags": table.flags,
            "nxx_entries": [{"enabled": entry.enabled} for entry in table.nxx_entries],
        }
        for table in parsed.nxx_tables
    ]
    intrastate_npas = [
        {
            "NPA": group.npa,
            "NXX_count": group.nxx_table_count,
            "band": group.unlisted_price_band,
            "dial_plan": group.unlisted_dial_pattern,
            "initial_price": group.flags,
        }
        for group in parsed.npa_groups
    ]
    surcharges = {
        write_mod.ENUM_BAND_CATEGORIES[index + 1]: {
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
    }
    npa_prices = [
        {"npa": entry.npa, "raw_value": entry.raw_value} for entry in parsed.npa_prices
    ]
    return write_mod.build_decompressed(
        prices=prices,
        rate_entries=rate_entries,
        nxx_table=nxx_table,
        intrastate_npas=intrastate_npas,
        surcharges=surcharges,
        npa_prices=npa_prices,
    )


def main() -> int:
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Verify R94 parser/writer against a corpus."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=script_dir / "ratefiles",
        type=Path,
        help="Directory containing .R94/.r94 files",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only verify the first N matching files",
    )
    args = parser.parse_args()

    read_mod = load_module("ratefile_read", script_dir / "ratefile_read.py")
    write_mod = load_module("ratefile_create", script_dir / "ratefile_create.py")

    ratefiles = sorted(args.path.glob("*.[Rr]94"))
    if args.limit > 0:
        ratefiles = ratefiles[: args.limit]

    parse_fail = Counter()
    parse_samples: dict[str, list[str]] = defaultdict(list)
    roundtrip_fail = Counter()
    roundtrip_samples: dict[str, list[str]] = defaultdict(list)
    parsed_count = 0
    roundtrip_ok = 0

    for path in ratefiles:
        try:
            parsed = read_mod.read_ratefile(str(path))
            parsed_count += 1
        except Exception as exc:  # pragma: no cover - verification output path
            key = f"{type(exc).__name__}: {exc}"
            parse_fail[key] += 1
            if len(parse_samples[key]) < 10:
                parse_samples[key].append(path.name)
            continue

        raw = path.read_bytes()
        original_decompressed = read_mod.decompress(raw[268:])
        rebuilt_decompressed = build_reconstructed_decompressed(parsed, write_mod)
        if rebuilt_decompressed == original_decompressed:
            roundtrip_ok += 1
            continue

        diffs = [
            index
            for index, (left, right) in enumerate(
                zip(rebuilt_decompressed, original_decompressed)
            )
            if left != right
        ][:10]
        length_suffix = ""
        if len(rebuilt_decompressed) != len(original_decompressed):
            length_suffix = (
                f" len {len(rebuilt_decompressed)} != {len(original_decompressed)}"
            )
        key = f"diffs={diffs}{length_suffix}"
        roundtrip_fail[key] += 1
        if len(roundtrip_samples[key]) < 10:
            roundtrip_samples[key].append(path.name)

    print(f"total={len(ratefiles)}")
    print(f"parsed={parsed_count}")
    print(f"parse_failed={sum(parse_fail.values())}")
    for key, count in parse_fail.most_common():
        print(f"{count} {key}")
        print(f"  samples: {', '.join(parse_samples[key])}")

    print(f"roundtrip_ok={roundtrip_ok}")
    print(f"roundtrip_failed={sum(roundtrip_fail.values())}")
    for key, count in roundtrip_fail.most_common():
        print(f"{count} {key}")
        print(f"  samples: {', '.join(roundtrip_samples[key])}")

    return 0 if not parse_fail and not roundtrip_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
