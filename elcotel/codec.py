"""Elcotel payphone file format compression codecs.

Provides zero-run length encoding/decoding used by S94, P94, and R94 file formats.

The compression algorithm:
- Non-zero bytes pass through as-is
- Runs of zero bytes (1-254) are encoded as [0x00, count]
- Runs of 255 zeros are encoded as [0x00, 0xFF], then counting resumes
- Trailing zeros at end of buffer are also encoded

This is a simple form of run-length encoding optimized for the
zero-filled sparse data structures in Elcotel configuration files.
"""

from __future__ import annotations


def compress(data: bytes | bytearray) -> bytes:
    """Return the zero-run encoded form of input data.

    Args:
        data: Raw bytes to compress using zero-run encoding.

    Returns:
        Compressed bytes with zero-runs replaced by [0x00, count] pairs.
    """
    result = bytearray()
    index = 0
    while index < len(data):
        # Found a zero byte - count consecutive zeros
        if data[index] == 0:
            count = 1
            while (
                index + count < len(data) and data[index + count] == 0 and count < 255
            ):
                count += 1
            # Emit zero-run marker: 0x00 followed by count
            result.append(0)
            result.append(count)
            index += count
            continue
        # Non-zero byte - pass through directly
        result.append(data[index])
        index += 1
    return bytes(result)


def decompress(raw_content_compressed: bytes | bytearray) -> bytearray:
    """Expand zero-run encoded data back to original byte sequence.

    Args:
        raw_content_compressed: Zero-run encoded bytes.

    Returns:
        Decompressed bytearray with zero-runs expanded.

    Note:
        Tolerates trailing zero bytes without count (EOF edge case).
    """
    index = 0
    decompressed = bytearray()
    while index < len(raw_content_compressed):
        byte = raw_content_compressed[index]
        if byte == 0:
            index += 1
            # Tolerate EOF without trailing count
            if index >= len(raw_content_compressed):
                break
            zeros_count = raw_content_compressed[index]
            decompressed.extend(b"\x00" * zeros_count)
        else:
            # Non-zero byte - append directly
            decompressed.append(byte)
        index += 1
    return decompressed
