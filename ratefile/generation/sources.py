"""Load and normalize offline exchange datasets used by Elcotel discovery."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .data_fetch import ensure_cnac_dataset, ensure_nanpa_dataset
from .types import ExchangeRecord


def _clean(value: object) -> str:
    return str(value or "").strip()


def _detect_country(path: Path, row: dict) -> str:
    explicit = _clean(row.get("Country") or row.get("country"))
    if explicit:
        return explicit.upper()
    return "CA" if "cnac" in path.name.lower() or "can" in path.name.lower() else "US"


def _normalize_status(row: dict) -> str:
    raw = _clean(
        row.get("Status") or row.get("Use") or row.get("status") or row.get("use")
    )
    assigned_values = {"AS", "IN SERVICE", "ASSIGNED", "A", "ACTIVE", "IN-SERVICE"}
    if not raw:
        return "assigned"
    return "assigned" if raw.upper() in assigned_values else "unassigned"


def _extract_npa_nxx(row: dict) -> tuple[int, int]:
    combined = _clean(row.get("NPA-NXX") or row.get("npa_nxx"))
    if combined and "-" in combined:
        npa, nxx = combined.split("-", 1)
        return int(npa), int(nxx)
    npa = _clean(row.get("NPA") or row.get("npa"))
    nxx = _clean(
        row.get("NXX")
        or row.get("nxx")
        or row.get("CO Code (NXX)")
        or row.get("co_code_nxx")
    )
    if not npa or not nxx:
        raise ValueError("Row is missing NPA/NXX fields")
    return int(npa), int(nxx)


def normalize_exchange_row(row: dict, source_path: Path) -> ExchangeRecord:
    npa, nxx = _extract_npa_nxx(row)
    rate_center = _clean(
        row.get("RateCenter")
        or row.get("rate_center")
        or row.get("Exchange Area")
        or row.get("exchange_area")
    )
    state = _clean(
        row.get("State")
        or row.get("state")
        or row.get("Province")
        or row.get("province")
    )
    lata = _clean(row.get("LATA") or row.get("lata"))
    return ExchangeRecord(
        npa=npa,
        nxx=nxx,
        country=_detect_country(source_path, row),
        state=state,
        rate_center=rate_center,
        lata=lata,
        status=_normalize_status(row),
    )


def _iter_rows(path: Path):
    # NANPA ships as a tab-delimited text file. CNAC ships as a CSV and includes
    # a date-only row immediately after the header, so the loader must be tolerant
    # of blank/malformed rows.
    delimiter = "\t" if path.suffix.lower() == ".txt" else ","
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        yield from reader


def load_exchange_records(paths: list[str]) -> list[ExchangeRecord]:
    records = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.suffix.lower() == ".json":
            items = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                raise ValueError(f"Exchange JSON must contain a list of rows: {path}")
            for row in items:
                try:
                    records.append(normalize_exchange_row(row, path))
                except (ValueError, TypeError):
                    continue
            continue
        for row in _iter_rows(path):
            try:
                records.append(normalize_exchange_row(row, path))
            except (ValueError, TypeError):
                continue
    return records


def ensure_default_exchange_paths(data_dir: str | Path) -> list[str]:
    return [str(ensure_nanpa_dataset(data_dir)), str(ensure_cnac_dataset(data_dir))]


def load_local_targets(
    paths: list[str], home_npa: int, home_nxx: int
) -> set[tuple[int, int]]:
    targets: set[tuple[int, int]] = set()
    for raw_path in paths:
        path = Path(raw_path)
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                row_home_npa = int(
                    _clean(row.get("HOME_NPA") or row.get("home_npa") or home_npa)
                )
                row_home_nxx = int(
                    _clean(row.get("HOME_NXX") or row.get("home_nxx") or home_nxx)
                )
                if row_home_npa != home_npa or row_home_nxx != home_nxx:
                    continue
                target_npa = int(
                    _clean(
                        row.get("NPA") or row.get("TARGET_NPA") or row.get("target_npa")
                    )
                )
                target_nxx = int(
                    _clean(
                        row.get("NXX") or row.get("TARGET_NXX") or row.get("target_nxx")
                    )
                )
                targets.add((target_npa, target_nxx))
    return targets
