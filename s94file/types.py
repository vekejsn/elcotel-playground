"""S94 (Speed Dial 94) file format data models.

S94 files store up to 50 speed dial entries for Elcotel Series 5 payphones.
Each entry defines a dialed number with initial and additional period
rates and times, plus a LATA type classification.

File Structure:
- 168-byte header (fixed)
- Zero-run compressed body (exactly 850 bytes uncompressed)
  - 50 records × 17 bytes each

The header format is shared with P94:
- Bytes 0-3: Unknown (format identifier?)
- Bytes 4-7: FileDataLength (4-byte LE, uncompressed data size)
- Bytes 8-15: Model string (8 chars, e.g. "LP050300")
- Byte 109: Description length (0-58)
- Bytes 110-167: Description text (ASCII, up to 58 chars)

Record Format (17 bytes each):
- Byte 0: Pattern length (0 = empty slot)
- Bytes 1-11: Dialed number (binary encoded digits, zero-padded to 11)
- Byte 12: Initial rate in nickels (0xF4 = unused)
- Byte 13: Initial time in minutes (0xFE = unlimited, 0xFF = restricted)
- Byte 14: Additional rate in nickels
- Byte 15: Additional time in minutes
- Byte 16: LATA type (0-8)
"""

from __future__ import annotations

from pydantic import BaseModel

# Fixed file format constants
HEADER_SIZE = 168  # Fixed header size in bytes
RECORD_SIZE = 17  # Each record is 17 bytes
NUM_RECORDS = 50  # Maximum 50 speed dial entries
BODY_SIZE = RECORD_SIZE * NUM_RECORDS  # 850 bytes uncompressed

# Special token values (shared with P94 and R94)
UNUSED_TOKEN = 244  # Indicates unused/empty field (displayed as "!")
UNLIMITED_TOKEN = 254  # Unlimited time (displayed as "U")
RESTRICTED_TOKEN = 255  # Restricted call (displayed as "R")

# Header field offsets
DESC_LEN_OFFSET = 109  # Byte offset of description length
DESC_TEXT_OFFSET = 110  # First byte of description text
DESC_MAX_LEN = 58  # Maximum description length
FILE_DATA_LENGTH_OFFSET = 4  # Offset of uncompressed data length (4 bytes LE)


class S94Header(BaseModel):
    """S94 file header data.

    Attributes:
        raw_header: Original 168-byte header preserved for writing back.
        file_data_length: Uncompressed body size in bytes (usually 850).
        description: User-edited file description (up to 58 chars).
    """

    raw_header: bytes
    file_data_length: int
    description: str


class SpeedDialRecord(BaseModel):
    """Single speed dial entry.

    Attributes:
        index: Zero-based index into records array (0-49).
        speed_dial_no: Dial position number (index + 20, display 20-69).
        dialed_num: Dial string to match (encoded digits).
        rate1: Initial period rate in nickels ($0.05 units).
        time1: Initial period duration in minutes.
        rate2: Additional period rate in nickels.
        time2: Additional period duration in minutes.
        lata_type: Call type classification (0-8).

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
    speed_dial_no: int
    dialed_num: str
    rate1: int
    time1: int
    rate2: int
    time2: int
    lata_type: int


class S94File(BaseModel):
    """Complete S94 file model.

    Attributes:
        header: Parsed file header.
        records: List of 50 speed dial entries.
    """

    header: S94Header
    records: list[SpeedDialRecord]
