"""Dial digit encoding and decoding for Elcotel payphone file formats.

Elcotel files encode dialed digits using a custom binary mapping:
- 0x00-0x09: digits '0' through '9'
- 0x0B: '*' (star)
- 0x0C: '#' (hash)
- 0x0D-0x10: letters 'A' through 'D' (ABCD keys)
- 0xF0: '@' (wildcard - match any single digit)
- 0xF1: '$' (start of dial string)
- 0xF2: '?' (wildcard)
- 0xF3: '+' (wildcard)
- 0xF4: '!' (unused/empty marker)

This mapping is shared by S94 (Speed Dial), P94 (Priority Parsing),
and R94 (Rate File) formats.
"""

from __future__ import annotations

# Binary byte to ASCII character mapping
# Used when reading dial strings from binary files
_BYTE_TO_CHAR: dict[int, str] = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    11: "*",
    12: "#",
    13: "A",
    14: "B",
    15: "C",
    16: "D",
    240: "@",
    241: "$",
    242: "?",
    243: "+",
    244: "!",
}

# ASCII character to binary byte mapping
# Used when writing dial strings to binary files
_CHAR_TO_BYTE: dict[str, int] = {v: k for k, v in _BYTE_TO_CHAR.items()}


def decode_dial_bytes(
    data: bytes | bytearray, start: int = 0, length: int | None = None
) -> str:
    """Decode a dial string from binary encoded bytes.

    Args:
        data: Source byte array containing encoded digits.
        start: Offset into data where encoding starts (default 0).
        length: Number of bytes to decode (default: rest of array).

    Returns:
        Human-readable dial string with special characters decoded.

    Example:
        >>> decode_dial_bytes(b'\\xf1\\x02\\x03\\x04', 0, 3)
        '$234'
    """
    if length is None:
        length = len(data) - start
    chars: list[str] = []
    for i in range(start, start + length):
        b = data[i]
        # Unknown bytes default to '+' (wildcard)
        chars.append(_BYTE_TO_CHAR.get(b, "+"))
    return "".join(chars)


def encode_dial_string(pattern: str) -> bytes:
    """Encode a dial string to binary format.

    Args:
        pattern: Human-readable dial string.

    Returns:
        Binary encoded dial string with special characters mapped.

    Example:
        >>> encode_dial_string('18005551212')
        b'\\x01\\x08\\x00\\x00\\x05\\x55\\x51\\x21\\x02'
    """
    result = bytearray()
    for ch in pattern:
        if ch in _CHAR_TO_BYTE:
            # Known character - use mapped byte
            result.append(_CHAR_TO_BYTE[ch])
        elif ch.isdigit():
            # Digit 0-9 - encode as binary value
            result.append(int(ch))
        else:
            # Unknown character - encode as '+' wildcard
            result.append(0xF3)
    return bytes(result)
