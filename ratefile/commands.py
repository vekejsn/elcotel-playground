"""Provide the consolidated command-line interfaces for the ratefile package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bridge import model_dump, ratefile_summary, ratefile_to_writer_payload
from .compile import compile_ratefile_spec
from .encode import model_to_header_dict, model_to_payload
from .generation.compiler import discovery_to_spec
from .generation.discovery import (
    build_generation_request,
    discover_relationships,
    load_generation_request,
)
from .generation.reporting import print_debug, print_summary, print_verbose
from .parser import read_ratefile
from .types import HeaderSpec, PriceBandSpec
from .spec import load_raw_document, load_spec
from .verify import verify_corpus
from .writer import write_ratefile, write_ratefile_payload


def _verify_generated(output_path: Path, compiled_model) -> None:
    """Read a generated file back and verify its basic structural counts."""
    parsed = read_ratefile(str(output_path))
    if len(parsed.npa_prices) != len(compiled_model.npa_prices):
        raise ValueError(
            "Generated file failed verification: NPA price count mismatch."
        )
    if len(parsed.nxx_tables) != len(compiled_model.nxx_tables):
        raise ValueError(
            "Generated file failed verification: NXX table count mismatch."
        )
    if parsed.price_plan.price_band_count != len(compiled_model.price_bands):
        raise ValueError(
            "Generated file failed verification: price band count mismatch."
        )


def _default_cli_price_bands() -> tuple[list[PriceBandSpec], dict[str, str]]:
    """Return a small built-in pricing policy for direct discovery mode."""
    defaults = [
        ("local", "local_1", 10, 255, 5, 255),
        ("intralata", "intra_1", 20, 60, 10, 60),
        ("interlata", "inter_1", 30, 60, 15, 60),
        ("interstate", "state_1", 40, 60, 20, 60),
        ("corridor", "corr_1", 50, 60, 25, 60),
        ("canadian", "can_1", 45, 60, 20, 60),
        ("extended", "ext_1", 55, 60, 30, 60),
        ("misc", "misc_1", 60, 60, 30, 60),
    ]
    bands = [
        PriceBandSpec(
            band_id=band_id,
            category=category,
            initial_rate=initial_rate,
            initial_time=initial_time,
            additional_rate=additional_rate,
            additional_time=additional_time,
        )
        for category, band_id, initial_rate, initial_time, additional_rate, additional_time in defaults
    ]
    return bands, {category: band_id for category, band_id, *_ in defaults}


def read_main(argv: list[str] | None = None) -> int:
    """Implement the `ratefile_read.py` command."""
    parser = argparse.ArgumentParser(description="Read and export an Elcotel R94 file.")
    parser.add_argument(
        "--file", dest="file_path", default="elcotel-playground/stock.R94"
    )
    parser.add_argument("--json-out")
    parser.add_argument("--dump-lowlevel-json")
    parser.add_argument(
        "--pretty-json", dest="pretty_json", action="store_true", default=True
    )
    parser.add_argument("--compact-json", dest="pretty_json", action="store_false")
    parser.add_argument("--summary", action="store_true", default=True)
    parser.add_argument("--no-summary", dest="summary", action="store_false")
    parser.add_argument("--print-model", action="store_true")
    args = parser.parse_args(argv)
    parsed = read_ratefile(args.file_path)
    indent = 2 if args.pretty_json else None
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(model_dump(parsed), indent=indent), encoding="utf-8"
        )
        print(f"Wrote rich parsed JSON to {args.json_out}")
    if args.dump_lowlevel_json:
        payload = ratefile_to_writer_payload(parsed)
        Path(args.dump_lowlevel_json).write_text(
            json.dumps(payload, indent=indent), encoding="utf-8"
        )
        print(f"Wrote low-level writer JSON to {args.dump_lowlevel_json}")
    if args.summary:
        info = ratefile_summary(parsed)
        print(f"File: {args.file_path}")
        print(f"Description: {info['description']}")
        print(f"Home NPA-NXX: {info['home_npa']}-{info['home_nxx']}")
        print(f"Decompressed Size: {info['decompressed_size']} bytes")
        print(f"Price Bands: {info['price_bands']}")
        print(f"NPA Groups: {info['npa_groups']}")
        print(f"NXX Tables: {info['nxx_tables']}")
        print(f"Band Counts: {json.dumps(info['band_counts'], sort_keys=True)}")
        print(f"NPA Kinds: {json.dumps(info['npa_kinds'], sort_keys=True)}")
        if info["repeated_group_npas"]:
            print(
                f"Repeated Group NPAs: {json.dumps(info['repeated_group_npas'], sort_keys=True)}"
            )
    if args.print_model:
        print(parsed)
    return 0


def write_main(argv: list[str] | None = None) -> int:
    """Implement the `ratefile_create.py` command."""
    parser = argparse.ArgumentParser(
        description="Write an Elcotel R94 file from writer JSON."
    )
    parser.add_argument("input_json")
    parser.add_argument("output_r94")
    parser.add_argument("--summary", action="store_true", default=True)
    parser.add_argument("--no-summary", dest="summary", action="store_false")
    parser.add_argument("--verify-roundtrip", action="store_true")
    args = parser.parse_args(argv)
    parsed = write_ratefile(args.input_json, args.output_r94, verbose=True)
    if args.summary:
        prices = parsed["prices"]
        print(f"Output: {args.output_r94}")
        print(f"Price Bands: {prices['price_count']}")
        print(f"NPA Groups: {prices['group_count']}")
        print(f"NXX Tables: {prices['nxx_count']}")
        print(
            "Band Counts: "
            + json.dumps(
                {
                    "local": prices["local_count"],
                    "intralata": prices["intralata_count"],
                    "interlata": prices["interlata_count"],
                    "interstate": prices["interstate_count"],
                    "corridor": prices["corridor_count"],
                    "canadian": prices["canadian_count"],
                    "extended": prices["extended_count"],
                    "misc": prices["misc_count"],
                },
                sort_keys=True,
            )
        )
    if args.verify_roundtrip:
        verified = read_ratefile(args.output_r94)
        print(
            "Read-back Summary: "
            + json.dumps(ratefile_summary(verified), sort_keys=True)
        )
    return 0


def verify_main(argv: list[str] | None = None) -> int:
    """Implement the `verify_ratefiles.py` command."""
    parser = argparse.ArgumentParser(
        description="Verify a corpus of Elcotel R94 files."
    )
    parser.add_argument(
        "path", nargs="?", default=Path(__file__).resolve().parent.parent / "ratefiles"
    )
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args(argv)
    result = verify_corpus(args.path, args.limit)
    print(f"total={result['total']}")
    print(f"parsed={result['parsed']}")
    print(f"parse_failed={result['parse_failed']}")
    for key, count in result["parse_failures"].most_common():
        print(f"{count} {key}")
        print(f"  samples: {', '.join(result['parse_samples'][key])}")
    print(f"roundtrip_ok={result['roundtrip_ok']}")
    print(f"roundtrip_failed={result['roundtrip_failed']}")
    for key, count in result["roundtrip_failures"].most_common():
        print(f"{count} {key}")
        print(f"  samples: {', '.join(result['roundtrip_samples'][key])}")
    return 0 if not result["parse_failed"] and not result["roundtrip_failed"] else 1


def generate_main(argv: list[str] | None = None) -> int:
    """Implement the `generate_ratefile.py` command."""
    parser = argparse.ArgumentParser(description="Generate an Elcotel R94 file.")
    parser.add_argument("spec", nargs="?")
    parser.add_argument("output_r94", nargs="?")
    parser.add_argument("--template")
    parser.add_argument("--output-r94", dest="output_r94_flag")
    parser.add_argument("--home-npa", type=int)
    parser.add_argument("--home-nxx", type=int)
    parser.add_argument(
        "--discovery-mode",
        choices=["offline", "api-lata", "api-lir"],
        default="api-lata",
    )
    parser.add_argument("--exchange-data", action="append", default=[])
    parser.add_argument("--local-data", action="append", default=[])
    parser.add_argument("--corridor-npa", action="append", type=int, default=[])
    parser.add_argument("--extended-npa", action="append", type=int, default=[])
    parser.add_argument("--misc-npa", action="append", type=int, default=[])
    parser.add_argument("--country", default="US")
    parser.add_argument("--state", default="")
    parser.add_argument("--cache-dir", default="elcotel-playground/ratefile/cache")
    parser.add_argument("--data-dir", default="elcotel-playground/ratefile/data")
    parser.add_argument("--cache-age", type=int, default=14)
    parser.add_argument("--disable-offline-validation", action="store_true")
    parser.add_argument("--dump-relationships")
    parser.add_argument("--dump-json")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    output_r94 = args.output_r94 or args.output_r94_flag
    if not output_r94:
        raise ValueError("An output R94 path is required.")

    discovery_result = None
    if args.spec:
        raw = load_raw_document(args.spec)
        if raw.get("mode") == "discovery":
            request = load_generation_request(args.spec)
            discovery_result = discover_relationships(request)
            spec = discovery_to_spec(discovery_result)
            if args.template and not request.template:
                request.template = args.template
        else:
            spec = load_spec(args.spec)
    else:
        if args.home_npa is None or args.home_nxx is None:
            raise ValueError("Discovery mode requires --home-npa and --home-nxx.")
        price_bands, relationship_map = _default_cli_price_bands()
        request = build_generation_request(
            home_npa=args.home_npa,
            home_nxx=args.home_nxx,
            exchange_data=args.exchange_data,
            local_data=args.local_data,
            discovery_mode=args.discovery_mode,
            header=HeaderSpec(
                description=f"Auto-generated {args.home_npa}-{args.home_nxx}",
                home_npa=str(args.home_npa),
                home_nxx=str(args.home_nxx),
            ),
            country=args.country,
            state=args.state,
            template=args.template,
            cache_dir=args.cache_dir,
            data_dir=args.data_dir,
            cache_age_days=args.cache_age,
            use_offline_validation=not args.disable_offline_validation,
            price_bands=price_bands,
            relationship_map=relationship_map,
            special_npas={
                "corridor": set(args.corridor_npa),
                "extended": set(args.extended_npa),
                "misc": set(args.misc_npa),
            },
        )
        discovery_result = discover_relationships(request)
        spec = discovery_to_spec(discovery_result)

    template_path = args.template or (
        getattr(discovery_result.request, "template", None)
        if discovery_result
        else None
    )
    compiled = compile_ratefile_spec(spec, template_path=template_path)
    header_dict = model_to_header_dict(compiled)
    payload = model_to_payload(compiled)
    if args.dump_relationships and discovery_result is not None:
        dump = {
            "metadata": discovery_result.metadata,
            "local_targets": sorted(
                [list(item) for item in discovery_result.local_targets]
            ),
            "lata_targets": sorted(
                [list(item) for item in discovery_result.lata_targets]
            ),
            "relationships": {
                relationship: [
                    {
                        "npa": record.npa,
                        "nxx": record.nxx,
                        "country": record.country,
                        "state": record.state,
                        "rate_center": record.rate_center,
                        "lata": record.lata,
                    }
                    for record in records
                ]
                for relationship, records in discovery_result.relationships.items()
            },
        }
        Path(args.dump_relationships).write_text(
            json.dumps(dump, indent=2), encoding="utf-8"
        )
    if args.dump_json:
        Path(args.dump_json).write_text(
            json.dumps({"header": header_dict, **payload}, indent=2), encoding="utf-8"
        )
    write_ratefile_payload(
        header_dict,
        payload,
        output_r94,
        template_header=compiled.template_header,
        verbose=True,
    )
    if args.verify:
        _verify_generated(Path(output_r94), compiled)
    if args.summary or args.verbose or args.debug:
        print_summary(output_r94, compiled, discovery_result, template_path)
    if args.verbose or args.debug:
        print_verbose(discovery_result, compiled)
    if args.debug:
        print_debug(discovery_result, args.dump_relationships, args.dump_json)
    return 0
