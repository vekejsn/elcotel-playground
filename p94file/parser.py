"""P94 (Priority Parsing 94) file format parser and writer.

Provides read and write functions for P94 priority parsing configuration
files used by Elcotel Series 5 payphones.

The parser:
1. Reads the 168-byte header
2. Decompresses the body using zero-run encoding
3. Parses all priority parsing records (up to 250)
4. Auto-detects and merges companion .P99 file for extended records

The writer:
1. Serializes all records back to binary format
2. Splits at 50 records - writes first 50 to .P94
3. Writes remaining to companion .P99 if any non-empty
4. Deletes old .P99 if no extended records remain
"""

from __future__ import annotations

import os

from elcotel.codec import compress, decompress
from elcotel.dial_digits import decode_dial_bytes, encode_dial_string

from .types import (
    DESC_LEN_OFFSET,
    DESC_MAX_LEN,
    DESC_TEXT_OFFSET,
    FILE_DATA_LENGTH_OFFSET,
    HEADER_SIZE,
    MAX_RECORDS,
    MIN_BODY_SIZE,
    MIN_RECORDS,
    P94Header,
    P94File,
    PATTERN_FIELD_SIZE,
    PriParseRecord,
    RECORD_SIZE,
    RESTRICTED_TOKEN,
    UNLIMITED_TOKEN,
    UNUSED_TOKEN,
)


def _parse_header(data: bytes) -> P94Header:
    """Parse the 168-byte P94 file header.

    Args:
        data: Raw file bytes (must be at least 168 bytes).

    Returns:
        Parsed P94Header with raw bytes and extracted fields.

    Raises:
        ValueError: If file is too short for header.
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"File too short for P94 header: {len(data)} bytes")
    raw = data[:HEADER_SIZE]
    file_data_length = int.from_bytes(
        raw[FILE_DATA_LENGTH_OFFSET : FILE_DATA_LENGTH_OFFSET + 4], "little"
    )
    desc_len = raw[DESC_LEN_OFFSET]
    if desc_len > 0:
        desc_bytes = raw[
            DESC_TEXT_OFFSET : DESC_TEXT_OFFSET + min(desc_len, DESC_MAX_LEN)
        ]
        description = desc_bytes.decode("ascii", errors="replace").rstrip("\x00")
    else:
        description = ""
    return P94Header(
        raw_header=raw,
        file_data_length=file_data_length,
        description=description,
    )


def _parse_record(body: bytes | bytearray, index: int) -> PriParseRecord:
    """Parse a single priority parsing record from decompressed body.

    Args:
        body: Decompressed data body.
        index: Zero-based record index (0-249).

    Returns:
        Parsed PriParseRecord with all fields extracted.

    Raises:
        ValueError: If record extends past body end.
    """
    offset = index * RECORD_SIZE
    if offset + RECORD_SIZE > len(body):
        raise ValueError(f"Record {index} extends past body end")
    rec = body[offset : offset + RECORD_SIZE]
    # Empty record (pattern_len = 0)
    pattern_len1 = rec[0]
    if pattern_len1 == 0:
        return PriParseRecord(
            index=index,
            pri_parse_no=index + 1,
            pattern="",
            macro=UNUSED_TOKEN,
            timer=UNUSED_TOKEN,
            rate1=UNUSED_TOKEN,
            time1=0,
            rate2=0,
            time2=0,
            lata_type=0,
        )
    # Decode first pattern part
    if pattern_len1 > 23:
        pattern_len1 = 23
    pattern_parts = [decode_dial_bytes(rec, 1, pattern_len1)]
    # Check for second pattern part (separated by comma)
    pos = 1 + pattern_len1
    if pos < PATTERN_FIELD_SIZE:
        pattern_len2 = rec[pos]
        pos += 1
        if pattern_len2 > 0 and pos + pattern_len2 <= PATTERN_FIELD_SIZE:
            pattern_parts.append(decode_dial_bytes(rec, pos, pattern_len2))
    pattern = ",".join(pattern_parts)
    # Fixed fields start at byte 24
    base = PATTERN_FIELD_SIZE
    return PriParseRecord(
        index=index,
        pri_parse_no=index + 1,
        pattern=pattern,
        macro=rec[base],
        timer=rec[base + 1],
        rate1=rec[base + 2],
        time1=rec[base + 3],
        rate2=rec[base + 4],
        time2=rec[base + 5],
        lata_type=rec[base + 6],
    )


def _parse_records_from_body(body: bytes | bytearray) -> list[PriParseRecord]:
    """Parse all records from a decompressed body.

    Args:
        body: Decompressed data body (multiple of 31 bytes).

    Returns:
        List of PriParseRecord entries found in body.
    """
    records = []
    idx = 0
    while (idx + 1) * RECORD_SIZE <= len(body) and idx < MAX_RECORDS:
        rec = _parse_record(body, idx)
        records.append(rec)
        idx += 1
    return records


def _p99_path(p94_path: str) -> str:
    """Generate .P99 companion file path from .P94 path.

    Args:
        p94_path: Path to .P94 file.

    Returns:
        Path with extension changed to .P99.
    """
    base, ext = os.path.splitext(p94_path)
    return base + ".P99"


def _p99_path_case_insensitive(p94_path: str) -> str | None:
    """Find .P99 companion file with case-insensitive matching.

    Args:
        p94_path: Path to .P94 file.

    Returns:
        Full path to .P99 file if found, None otherwise.
    """
    p99 = _p99_path(p94_path)
    if os.path.exists(p99):
        return p99
    # Try common case variations
    base, _ = os.path.splitext(p94_path)
    for ext in (".P99", ".p99", ".P99"):
        candidate = base + ext
        if os.path.exists(candidate):
            return candidate
    # Directory search
    p94_dir = os.path.dirname(p94_path) or "."
    p94_name = os.path.basename(p94_path)
    base_name = os.path.splitext(p94_name)[0]
    try:
        entries = os.listdir(p94_dir)
    except OSError:
        return None
    for entry in entries:
        name_base, name_ext = os.path.splitext(entry)
        if name_base.upper() == base_name.upper() and name_ext.upper() == ".P99":
            return os.path.join(p94_dir, entry)
    return None


def read_p94(path: str) -> P94File:
    """Read a P94 file and return parsed model.

    Automatically detects and merges companion .P99 file for records 51-250.

    Args:
        path: Path to .P94 file on disk.

    Returns:
        P94File with header and all records (1-250).

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file format is invalid.
    """
    with open(path, "rb") as f:
        raw = f.read()
    # Parse header
    header = _parse_header(raw)
    # Decompress body (everything after 168-byte header)
    compressed_body = raw[HEADER_SIZE:]
    body = decompress(compressed_body) if compressed_body else bytearray(MIN_BODY_SIZE)

    all_records: list[PriParseRecord] = []

    # Parse primary records (first 50)
    first_chunk = body[:MIN_BODY_SIZE]
    if len(first_chunk) < MIN_BODY_SIZE:
        first_chunk = first_chunk + bytearray(MIN_BODY_SIZE - len(first_chunk))
    all_records.extend(_parse_records_from_body(first_chunk))

    # Parse any extended records in primary body
    remaining = body[MIN_BODY_SIZE:]
    if remaining:
        all_records.extend(_parse_records_from_body(remaining))

    # Check for companion .P99 file
    has_p99 = False
    p99_path = _p99_path_case_insensitive(path)
    if p99_path is not None:
        has_p99 = True
        with open(p99_path, "rb") as f:
            p99_raw = f.read()
        p99_compressed = p99_raw[HEADER_SIZE:]
        if p99_compressed:
            p99_body = decompress(p99_compressed)
            all_records.extend(_parse_records_from_body(p99_body))

    return P94File(header=header, records=all_records, has_p99=has_p99)


def _encode_pattern(pattern: str) -> bytearray:
    """Encode a dial pattern string to 24-byte pattern field.

    Args:
        pattern: Pattern string (may contain comma for two patterns).

    Returns:
        24-byte pattern field with length prefixes and zero padding.
    """
    buf = bytearray(PATTERN_FIELD_SIZE)
    if not pattern:
        return buf
    # Split on comma for two-pattern support
    parts = pattern.split(",", 1)
    part1 = parts[0]
    encoded1 = encode_dial_string(part1)
    len1 = min(len(encoded1), 23)
    buf[0] = len1
    buf[1 : 1 + len1] = encoded1[:len1]
    # Second pattern (if present)
    pos = 1 + len1
    if len(parts) > 1 and pos < PATTERN_FIELD_SIZE:
        encoded2 = encode_dial_string(parts[1])
        len2 = min(len(encoded2), PATTERN_FIELD_SIZE - pos - 1)
        buf[pos] = len2
        if len2 > 0:
            buf[pos + 1 : pos + 1 + len2] = encoded2[:len2]
    return buf


def _build_body(records: list[PriParseRecord]) -> bytearray:
    """Build uncompressed body from records.

    Args:
        records: List of PriParseRecord entries.

    Returns:
        Uncompressed body (at least 1550 bytes).
    """
    total = len(records)
    size = max(total * RECORD_SIZE, MIN_BODY_SIZE)
    body = bytearray(size)
    for rec in records:
        offset = rec.index * RECORD_SIZE
        if not rec.pattern:
            # Empty record - mark unused
            body[offset + PATTERN_FIELD_SIZE] = UNUSED_TOKEN
            body[offset + PATTERN_FIELD_SIZE + 1] = UNUSED_TOKEN
            body[offset + PATTERN_FIELD_SIZE + 2] = UNUSED_TOKEN
            continue
        # Encode pattern field
        pattern_bytes = _encode_pattern(rec.pattern)
        body[offset : offset + PATTERN_FIELD_SIZE] = pattern_bytes
        # Fixed fields at bytes 24-30
        base = offset + PATTERN_FIELD_SIZE
        body[base] = rec.macro
        body[base + 1] = rec.timer
        body[base + 2] = rec.rate1
        body[base + 3] = rec.time1
        body[base + 4] = rec.rate2
        body[base + 5] = rec.time2
        body[base + 6] = rec.lata_type
    return body


def write_p94(model: P94File, path: str) -> None:
    """Write P94 file to disk.

    Splits records at 50 - writes first 50 to .P94, rest to .P99.

    Args:
        model: P94File model to write.
        path: Output file path (use .P94 extension).

    Writes:
        168-byte header + zero-run compressed body.
        Optionally creates companion .P99 file for records 51-250.
    """
    header_bytes = bytearray(model.header.raw_header)
    body = _build_body(model.records)

    # Split at 50 records
    p94_body = body[:MIN_BODY_SIZE]
    p99_body = body[MIN_BODY_SIZE:]

    # Write primary .P94 file
    compressed_p94 = compress(bytes(p94_body))
    header_bytes[FILE_DATA_LENGTH_OFFSET : FILE_DATA_LENGTH_OFFSET + 4] = len(
        body
    ).to_bytes(4, "little")

    with open(path, "wb") as f:
        f.write(bytes(header_bytes))
        f.write(compressed_p94)

    # Write companion .P99 if needed
    p99_path = _p99_path(path)
    if len(p99_body) > 0 and any(b != 0 for b in p99_body):
        compressed_p99 = compress(bytes(p99_body))
        with open(p99_path, "wb") as f:
            f.write(bytes(header_bytes))
            f.write(compressed_p99)
    else:
        # Delete old .P99 if no extended records
        if os.path.exists(p99_path):
            os.unlink(p99_path)
