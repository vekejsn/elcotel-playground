"""Format human-readable reporting for Elcotel generation commands."""

from __future__ import annotations

import json


def print_summary(
    output_r94: str, compiled, discovery_result, template_path: str | None
) -> None:
    """Print the high-level outcome of a generation run."""
    mode = "explicit"
    if discovery_result is not None:
        mode = discovery_result.request.discovery_mode
    print(f"Mode: {mode}")
    print(f"Output: {output_r94}")
    print(f"Template: {template_path or 'none'}")
    print(f"Price Bands: {len(compiled.price_bands)}")
    print(f"NPA Prices: {len(compiled.npa_prices)}")
    print(f"NPA Groups: {len(compiled.group_rows)}")
    print(f"NXX Tables: {len(compiled.nxx_tables)}")


def print_verbose(discovery_result, compiled) -> None:
    """Print discovery and compilation detail for a generation run."""
    if discovery_result is None:
        return
    request = discovery_result.request
    relationship_counts = {
        relationship: len(records)
        for relationship, records in sorted(discovery_result.relationships.items())
    }
    nxx_specific_npas = sum(
        1 for entry in compiled.npa_prices if entry.raw_value in (254, 255)
    )
    print(f"Discovery Mode: {request.discovery_mode}")
    print(f"Exchange Data: {request.exchange_data or ['<auto-fallback>']}")
    print(f"Local Data: {request.local_data}")
    print(f"Cache Dir: {request.cache_dir}")
    print(f"Data Dir: {request.data_dir}")
    print(f"Offline Validation: {request.use_offline_validation}")
    print(f"Local Target Count: {len(discovery_result.local_targets)}")
    print(f"LATA/LIR Target Count: {len(discovery_result.lata_targets)}")
    print(f"Relationship Counts: {json.dumps(relationship_counts, sort_keys=True)}")
    print(f"NXX-Specific NPAs: {nxx_specific_npas}")
    print(f"Direct-Default NPAs: {len(compiled.npa_prices) - nxx_specific_npas}")


def print_debug(
    discovery_result, dump_relationships: str | None, dump_json: str | None
) -> None:
    """Print the most detailed discovery metadata for debugging runs."""
    if discovery_result is None:
        return
    print(
        f"Discovery Metadata: {json.dumps(discovery_result.metadata, sort_keys=True)}"
    )
    if dump_relationships:
        print(f"Dumped Relationships: {dump_relationships}")
    if dump_json:
        print(f"Dumped Low-Level JSON: {dump_json}")
