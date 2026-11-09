"""C94 reader; all unknown header/body bytes are preserved."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from elcotel.codec import compress, decompress

HEADER_SIZE = 168
BODY_SIZE = 4096


class C94File(BaseModel):
    """Lossless writer payload. Bytes are represented as hex strings in JSON.

    Decoded registers are intentionally separate. Use editor.apply_changes for
    human-value edits, or edit body bytes for low-level work; unknown fields
    must not be lost through a complete decode/re-encode cycle.
    """

    model_config = ConfigDict(ser_json_bytes="hex", val_json_bytes="hex")
    raw_header: bytes = Field(min_length=HEADER_SIZE, max_length=HEADER_SIZE)
    body: bytes = Field(min_length=BODY_SIZE, max_length=BODY_SIZE)

    @property
    def tag(self) -> str:
        return self.raw_header[8:16].decode("ascii", errors="replace")

    @property
    def version(self) -> str:
        tag = self.tag
        return ".".join(tag[i:i + 2] for i in (2, 4, 6))

    @property
    def description(self) -> str:
        size = min(self.raw_header[109], 58)
        return self.raw_header[110:110 + size].decode("ascii", errors="replace")

    @property
    def file_data_length(self) -> int:
        return int.from_bytes(self.raw_header[4:8], "little")

    def to_bytes(self) -> bytes:
        return self.raw_header + compress(self.body)


def parse_c94(raw: bytes) -> C94File:
    """Reject incomplete/oversized images instead of inventing missing bytes."""
    if len(raw) < HEADER_SIZE:
        raise ValueError(f"C94 header requires {HEADER_SIZE} bytes, got {len(raw)}")
    encoded = raw[HEADER_SIZE:]
    # Validate framing before using the shared (deliberately permissive) codec.
    index = expanded = 0
    while index < len(encoded):
        if encoded[index] == 0:
            if index + 1 == len(encoded):
                raise ValueError("C94 body ends with a zero-run marker without a count")
            count = encoded[index + 1]
            if count == 0:
                raise ValueError("C94 zero-run count must not be zero")
            expanded += count
            index += 2
        else:
            expanded += 1
            index += 1
        if expanded > BODY_SIZE:
            raise ValueError(f"C94 expanded body exceeds {BODY_SIZE} bytes")
    if expanded != BODY_SIZE:
        raise ValueError(f"C94 body requires {BODY_SIZE} bytes, got {expanded}")
    declared = int.from_bytes(raw[4:8], "little")
    if declared != BODY_SIZE:
        raise ValueError(f"C94 header declares {declared} data bytes, expected {BODY_SIZE}")
    return C94File(raw_header=raw[:HEADER_SIZE], body=bytes(decompress(encoded)))


def read_c94(path: str | Path) -> C94File:
    return parse_c94(Path(path).read_bytes())


def write_c94(model: C94File, path: str | Path) -> None:
    # Revalidate even if a caller assigned new attributes after construction.
    validated = C94File.model_validate(model.model_dump())
    raw = validated.to_bytes()
    parse_c94(raw)
    Path(path).write_bytes(raw)


@lru_cache(maxsize=1)
def _maps() -> dict:
    return json.loads(Path(__file__).with_name("register_maps.json").read_text(encoding="utf-8"))


def map_name(model: C94File) -> str:
    """Exact matches only; never guess a map for an unrecognized firmware."""
    tag = model.tag
    if not tag[2:].isascii() or not tag[2:].isdigit():
        raise ValueError(f"Unrecognized C94 firmware tag: {tag!r}")
    if tag[:2] not in ("LP", "KX"):
        raise ValueError(f"Unrecognized C94 firmware family: {tag[:2]!r}")
    name = tag
    if name not in _maps():
        raise ValueError(f"No register map for {tag!r}")
    return name


def _digits(data: bytes) -> str:
    alphabet = {**{i: str(i) for i in range(10)}, 11: "*", 12: "#"}
    try:
        return "".join(alphabet[byte] for byte in data)
    except KeyError as exc:
        raise ValueError(f"Invalid dial digit: 0x{exc.args[0]:02x}") from exc


def _station_id(slot: bytes) -> str:
    if slot[0] & 0x80:
        # First digit is biased by -2 and its high bit marks the packed form.
        nibbles = [(slot[0] >> 4) - 8 + 2, slot[0] & 15]
        for byte in slot[1:5]:
            nibbles.extend((byte >> 4, byte & 15))
        if any(n > 9 for n in nibbles):
            raise ValueError("Invalid packed station ID")
        return "".join(map(str, nibbles))
    size = slot[0]
    if size > 4:
        raise ValueError("Invalid short station ID length")
    return _digits(slot[1:1 + size])


def _decode(slot: bytes, entry: dict):
    token, reg = entry["token"], entry["register_num"]
    if reg == 402:
        return _station_id(slot)
    if token in (1, 9):
        return slot[0] / 24 if reg == 437 else slot[0]
    if token in (2, 7):
        size = slot[0]
        if size >= len(slot):
            raise ValueError(f"String length {size} exceeds field capacity {len(slot) - 1}")
        data = slot[1:1 + size]
        return data.decode("ascii") if token == 7 else _digits(data)
    if token in (3, 4):
        return int.from_bytes(slot, "little") / 20
    if token == 5:
        return int.from_bytes(slot, "little")
    if token == 8:
        return bool(slot[0] & (1 << (entry["size"] - 1)))
    if token == 10:
        return f"{slot[1]:02d}:{slot[0]:02d}"
    if token in (6, 11):
        return list(slot)
    raise ValueError(f"Unknown register token {token}")


def decode_registers(model: C94File, table: str | None = None) -> list[dict]:
    """Decode with firmware-specific addresses (relative to the entire body).

    Invalid individual values remain inspectable as raw hex plus an error.
    Token 8 Size means a one-based bit number, NOT a byte length.
    """
    name = table or map_name(model)
    if name not in _maps():
        raise ValueError(f"Unknown register map: {name}")
    result = []
    for entry in _maps()[name]:
        offset = int(entry["address"], 16)
        width = 1 if entry["token"] == 8 else entry["size"]
        slot = model.body[offset:offset + width]
        row = {**entry, "offset": offset, "raw_hex": slot.hex()}
        try:
            if len(slot) != width:
                raise ValueError("Register extends beyond C94 body")
            row["value"] = _decode(slot, entry)
            if entry["register_num"] == 402:
                row["checksum_valid"] = slot[5] == sum(slot[:5]) % 256
        except (ValueError, IndexError) as exc:
            row["error"] = str(exc)
        result.append(row)
    from .semantics import annotate_register

    by_register = {row["register_num"]: row for row in result}
    return [annotate_register(name, row, by_register) for row in result]
