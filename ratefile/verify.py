"""Verify parser and writer behavior against real Elcotel R94 corpora."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .codec import decompress
from .bridge import ratefile_to_writer_payload
from .parser import RateFile, read_ratefile
from .writer import build_decompressed


def build_reconstructed_decompressed(parsed: RateFile) -> bytearray:
    """Rebuild the decompressed body from a parsed file using the writer bridge."""
    payload = ratefile_to_writer_payload(parsed)
    payload.pop("header", None)
    return build_decompressed(**payload)


def verify_file(file_path: str | Path) -> tuple[bool, str | None]:
    """Return whether one file round-trips cleanly at the decompressed-body level."""
    parsed = read_ratefile(str(file_path))
    raw = Path(file_path).read_bytes()
    original_decompressed = decompress(raw[268:])
    rebuilt_decompressed = build_reconstructed_decompressed(parsed)
    if rebuilt_decompressed == original_decompressed:
        return True, None
    diffs = [
        index
        for index, (left, right) in enumerate(
            zip(rebuilt_decompressed, original_decompressed)
        )
        if left != right
    ][:10]
    return False, f"diffs={diffs}"


def verify_corpus(path: str | Path, limit: int = 0) -> dict:
    """Verify every R94 file in a directory and summarize parse/roundtrip results."""
    ratefiles = sorted(Path(path).glob("*.[Rr]94"))
    if limit > 0:
        ratefiles = ratefiles[:limit]
    parse_fail = Counter()
    parse_samples: dict[str, list[str]] = defaultdict(list)
    roundtrip_fail = Counter()
    roundtrip_samples: dict[str, list[str]] = defaultdict(list)
    parsed_count = 0
    roundtrip_ok = 0
    for file_path in ratefiles:
        try:
            parsed = read_ratefile(str(file_path))
            parsed_count += 1
        except Exception as exc:
            key = f"{type(exc).__name__}: {exc}"
            parse_fail[key] += 1
            if len(parse_samples[key]) < 10:
                parse_samples[key].append(file_path.name)
            continue
        raw = file_path.read_bytes()
        original_decompressed = decompress(raw[268:])
        rebuilt_decompressed = build_reconstructed_decompressed(parsed)
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
        key = f"diffs={diffs}"
        roundtrip_fail[key] += 1
        if len(roundtrip_samples[key]) < 10:
            roundtrip_samples[key].append(file_path.name)
    return {
        "total": len(ratefiles),
        "parsed": parsed_count,
        "parse_failed": sum(parse_fail.values()),
        "parse_failures": parse_fail,
        "parse_samples": parse_samples,
        "roundtrip_ok": roundtrip_ok,
        "roundtrip_failed": sum(roundtrip_fail.values()),
        "roundtrip_failures": roundtrip_fail,
        "roundtrip_samples": roundtrip_samples,
    }
