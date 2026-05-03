"""P94 (Priority Parsing 94) file format data models.

P94 files store dial pattern routing rules for Elcotel Series 5 payphones.
Each entry defines a pattern match with associated macro, timer, rates, and times.

File Structure:
- 168-byte header (fixed, same as S94)
- Zero-run compressed body (at least 1550 bytes uncompressed)
  - Primary records: 50 entries × 31 bytes in .P94 file
  - Extended records: up to 200 entries × 31 bytes in companion .P99 file

The P99 companion file stores records 51-250 when the table exceeds 50 entries.
It uses the same 168-byte header format and is auto-detected/merged.

Record Format (31 bytes each):
- Bytes 0-23: Pattern field (variable-length, zero-padded to 24)
  - Byte 0: First pattern length (0-23)
  - Bytes 1-N: First pattern (binary encoded digits)
  - Byte N+1: Second pattern length (or 0 if none)
  - Bytes N+2...23: Second pattern + zero padding
- Byte 24: Call macro number (0xF4 = unused)
- Byte 25: Call completion timer
- Byte 26: Initial rate in nickels (0xF4 = unused)
- Byte 27: Initial time in minutes (0xFE = unlimited, 0xFF = restricted)
- Byte 28: Additional rate in nickels
- Byte 29: Additional time in minutes
- Byte 30: LATA type (0-8)
"""

from __future__ import annotations

from pydantic import BaseModel

# Fixed file format constants
HEADER_SIZE = 168  # Fixed header size in bytes
RECORD_SIZE = 31  # Each record is 31 bytes
PATTERN_FIELD_SIZE = 24  # Pattern field is 24 bytes max
MIN_RECORDS = 50  # Primary P94 can hold 50 records
MAX_RECORDS = 250  # Total can hold up to 250 records
MIN_BODY_SIZE = RECORD_SIZE * MIN_RECORDS  # 1550 bytes minimum

# Special token values (shared with S94 and R94)
UNUSED_TOKEN = 244  # Indicates unused/empty field (displayed as "!")
UNLIMITED_TOKEN = 254  # Unlimited time (displayed as "U")
RESTRICTED_TOKEN = 255  # Restricted call (displayed as "R")

# Header field offsets (same as S94)
DESC_LEN_OFFSET = 109  # Byte offset of description length
DESC_TEXT_OFFSET = 110  # First byte of description text
DESC_MAX_LEN = 58  # Maximum description length
FILE_DATA_LENGTH_OFFSET = 4  # Offset of uncompressed data length (4 bytes LE)


class P94Header(BaseModel):
    """P94 file header data.

    Attributes:
        raw_header: Original 168-byte header preserved for writing back.
        file_data_length: Uncompressed body size in bytes.
        description: User-edited file description (up to 58 chars).
    """

    raw_header: bytes
    file_data_length: int
    description: str


class PriParseRecord(BaseModel):
    """Single priority parsing entry.

    Attributes:
        index: Zero-based index into records array (0-249).
        pri_parse_no: Display number (index + 1, 1-250).
        pattern: Dial pattern to match (supports two patterns separated by comma).
        macro: Call macro to execute (0xF4 = unused, otherwise 0-255).
        timer: Call completion timer in seconds.
        rate1: Initial period rate in nickels ($0.05 units).
        time1: Initial period duration in minutes.
        rate2: Additional period rate in nickels.
        time2: Additional period duration in minutes.
        lata_type: Call type classification (0-8).

    Pattern Format:
        Patterns use special characters for digit matching:
        - @: Match any single digit (wildcard)
        - $: Start of dial string
        - ?: Single digit wildcard
        - +: Single digit wildcard
        - !: Unused (same as empty)
        - ,: Separates first and second pattern

    LATA Types:
        0 = ! (unused)
        1 = Local
        2 = IntraLATA
        3 = InterLATA
        4 = FCC (InterState)
        5 = Corridor
        6 = Canadian
        7 = Extended
        8 = Misc
    """

    index: int
    pri_parse_no: int
    pattern: str
    macro: int
    timer: int
    rate1: int
    time1: int
    rate2: int
    time2: int
    lata_type: int


class P94File(BaseModel):
    """Complete P94 file model.

    Attributes:
        header: Parsed file header.
        records: List of all priority parsing entries (1-250).
        has_p99: True if companion .P99 file exists/was merged.
    """

    header: P94Header
    records: list[PriParseRecord]
    has_p99: bool
