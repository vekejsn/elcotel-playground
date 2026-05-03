"""S94 (Speed Dial 94) file format parser and writer.

Provides read and write functions for S94 speed dial configuration files
used by Elcotel Series 5 payphones.

The parser reads the 168-byte header, decompresses the body using zero-run
encoding, and parses all 50 speed dial records into Pydantic models.

The writer serializes records back to binary format with zero-run compression.
"""

from __future__ import annotations

from elcotel.codec import compress, decompress
from elcotel.dial_digits import decode_dial_bytes, encode_dial_string

from .types import (
    BODY_SIZE,
    DESC_LEN_OFFSET,
    DESC_MAX_LEN,
    DESC_TEXT_OFFSET,
    FILE_DATA_LENGTH_OFFSET,
    HEADER_SIZE,
    NUM_RECORDS,
    RECORD_SIZE,
    RESTRICTED_TOKEN,
    S94File,
    S94Header,
    SpeedDialRecord,
    UNLIMITED_TOKEN,
    UNUSED_TOKEN,
)


def _parse_header(data: bytes) -> S94Header:
    """Parse the 168-byte S94 file header.

    Args:
        data: Raw file bytes (must be at least 168 bytes).

    Returns:
        Parsed S94Header with raw bytes and extracted fields.

    Raises:
        ValueError: If file is too short for header.
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"File too short for S94 header: {len(data)} bytes")
    # Preserve original header for writing back
    raw = data[:HEADER_SIZE]
    # Extract uncompressed body length (little-endian 4-byte integer)
    file_data_length = int.from_bytes(
        raw[FILE_DATA_LENGTH_OFFSET : FILE_DATA_LENGTH_OFFSET + 4], "little"
    )
    # Extract description (length byte + up to 58 ASCII chars)
    desc_len = raw[DESC_LEN_OFFSET]
    if desc_len > 0:
        desc_bytes = raw[
            DESC_TEXT_OFFSET : DESC_TEXT_OFFSET + min(desc_len, DESC_MAX_LEN)
        ]
        description = desc_bytes.decode("ascii", errors="replace").rstrip("\x00")
    else:
        description = ""
    return S94Header(
        raw_header=raw,
        file_data_length=file_data_length,
        description=description,
    )


def _parse_record(body: bytes | bytearray, index: int) -> SpeedDialRecord:
    """Parse a single speed dial record from the decompressed body.

    Args:
        body: Decompressed data body (850 bytes).
        index: Zero-based record index (0-49).

    Returns:
        Parsed SpeedDialRecord with all fields extracted.

    Raises:
        ValueError: If record extends past body end.
    """
    offset = index * RECORD_SIZE
    if offset + RECORD_SIZE > len(body):
        raise ValueError(f"Record {index} extends past body end")
    # Slice the 17-byte record
    rec = body[offset : offset + RECORD_SIZE]
    pattern_len = rec[0]
    # Empty record (pattern_len = 0)
    if pattern_len == 0:
        return SpeedDialRecord(
            index=index,
            speed_dial_no=index + 20,
            dialed_num="",
            rate1=UNUSED_TOKEN,
            time1=UNUSED_TOKEN,
            rate2=UNUSED_TOKEN,
            time2=UNUSED_TOKEN,
            lata_type=0,
        )
    # Decode the dialed number from binary format
    dialed_num = decode_dial_bytes(rec, 1, min(pattern_len, 11))
    return SpeedDialRecord(
        index=index,
        speed_dial_no=index + 20,
        dialed_num=dialed_num,
        rate1=rec[12],
        time1=rec[13],
        rate2=rec[14],
        time2=rec[15],
        lata_type=rec[16],
    )


def read_s94(path: str) -> S94File:
    """Read an S94 file and return parsed model.

    Args:
        path: Path to .S94 file on disk.

    Returns:
        S94File with header and all 50 records.

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
    body = decompress(compressed_body) if compressed_body else bytearray(BODY_SIZE)
    # Pad to expected size if truncated
    if len(body) < BODY_SIZE:
        body = body + bytearray(BODY_SIZE - len(body))
    # Parse all 50 records
    records = [_parse_record(body, i) for i in range(NUM_RECORDS)]
    return S94File(header=header, records=records)


def _build_body(records: list[SpeedDialRecord]) -> bytearray:
    """Build uncompressed body from records.

    Args:
        records: List of 50 SpeedDialRecord entries.

    Returns:
        850-byte uncompressed body ready for compression.
    """
    body = bytearray(BODY_SIZE)
    for rec in records:
        offset = rec.index * RECORD_SIZE
        # Empty record
        if rec.dialed_num == "":
            body[offset] = 0
            body[offset + 12] = UNUSED_TOKEN
            continue
        # Encode dialed number to binary
        encoded = encode_dial_string(rec.dialed_num)
        pattern_len = len(encoded)
        body[offset] = min(pattern_len, 11)
        body[offset + 1 : offset + 1 + min(pattern_len, 11)] = encoded[:11]
        body[offset + 12] = rec.rate1
        body[offset + 13] = rec.time1
        body[offset + 14] = rec.rate2
        body[offset + 15] = rec.time2
        body[offset + 16] = rec.lata_type
    return body


def write_s94(model: S94File, path: str) -> None:
    """Write S94 file to disk.

    Args:
        model: S94File model to write.
        path: Output file path.

    Writes:
        168-byte header followed by zero-run compressed body.
    """
    # Start with preserved header bytes
    header_bytes = bytearray(model.header.raw_header)
    # Build and compress body
    body = _build_body(model.records)
    compressed = compress(bytes(body))
    # Update file data length in header
    header_bytes[FILE_DATA_LENGTH_OFFSET : FILE_DATA_LENGTH_OFFSET + 4] = len(
        body
    ).to_bytes(4, "little")
    # Write header + compressed body
    with open(path, "wb") as f:
        f.write(bytes(header_bytes))
        f.write(compressed)
