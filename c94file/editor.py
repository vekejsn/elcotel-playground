"""Validated, human-value edits without exposing binary layout metadata."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from .parser import C94File, decode_registers, map_name
from .semantics import TABLE_VERSIONS, definitions

INTEGER_LIMITS = {
    "B": 99, "C": 9, "D": 19, "E": 200, "F": 999, "G": 23,
    "K": 99, "L": 2, "M": 3, "N": 255, "O": 60, "P": 96,
    "T": 10, "U": 7, "V": 9999,
}


def read_only_reason(row: dict) -> str | None:
    meta = row["parameter"]
    if meta["status"] != "documented":
        return "Meaning is unconfirmed or reserved; left unchanged."
    if meta.get("conflicting_editor_rules"):
        return "Original editor definitions disagree about the allowed range."
    if meta.get("ui_visible_in_version") is False:
        return "Not enabled for this firmware in the original editor."
    if row["token"] == 6:
        return "Inline macro program; inspection only in the simple editor."
    if row["token"] == 11 and row["register_num"] != 468:
        return "Unsupported block type."
    return None


def _number(value) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("Enter a number, not ON/OFF")
    try:
        result = Decimal(str(value).strip().removeprefix("$"))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Enter a number") from exc
    if not result.is_finite():
        raise ValueError("Enter a finite number")
    return result


def _integer(value) -> int:
    number = _number(value)
    if number != number.to_integral_value():
        raise ValueError("Enter a whole number")
    return int(number)


def _boolean(value) -> bool:
    if isinstance(value, bool):
        return value
    if str(value).strip().lower() in ("on", "true", "1"):
        return True
    if str(value).strip().lower() in ("off", "false", "0"):
        return False
    raise ValueError("Choose ON or OFF")


def _counted(value, size: int, ascii_text=False) -> bytes:
    if not isinstance(value, str):
        raise ValueError("Enter a string; keep leading zeros")
    if ascii_text:
        try:
            data = value.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError("Only ASCII characters are supported") from exc
    else:
        alphabet = {**{str(i): i for i in range(10)}, "*": 11, "#": 12}
        if any(c not in alphabet for c in value):
            raise ValueError("Use digits 0-9, * or #, without spaces or punctuation")
        data = bytes(alphabet[c] for c in value)
    if len(data) >= size:
        raise ValueError(f"Use at most {size - 1} characters")
    return (bytes([len(data)]) + data).ljust(size, b"\0")


def _station(value) -> bytes:
    if not isinstance(value, str) or (value and not re.fullmatch(r"[0-9]+", value)):
        raise ValueError("Station ID must be a digit string")
    if len(value) <= 4:
        data = (bytes([len(value)]) + bytes(int(c) for c in value)).ljust(5, b"\0")
    elif len(value) == 10 and value[0] in "23456789":
        data = bytes([((int(value[0]) - 2) << 4) | 0x80 | int(value[1])])
        data += bytes(int(value[i:i + 2], 16) for i in range(2, 10, 2))
    else:
        raise ValueError("Use up to four digits, or ten digits starting with 2-9")
    return data + bytes([sum(data) % 256])


def _validate_macro(value: int, rows: dict, family: str) -> None:
    if 45 <= value <= 64:
        reg = value - 45 + 300 if value <= 50 else value - 51 + 512
        if reg not in rows or not any(rows[reg].get("value", [])):
            raise ValueError(f"User macro {value} has no configured program in this image")
    else:
        database_id = value + (50 if family == "KX" else 0)
        model_id = 5502 if family == "KX" else 5
        if not any(m["MacroID"] == database_id and m["MacroModel"] == model_id
                   for m in definitions()["macros"]):
            raise ValueError(f"No known built-in macro {value} for {family}")


def _encode(row: dict, value, rows: dict, family: str) -> bytes:
    reg, token, size = row["register_num"], row["token"], row["size"]
    meta = row["parameter"]
    field = meta.get("field_type")
    if token == 8:
        original = int(row["raw_hex"], 16)
        mask = 1 << (size - 1)
        return bytes([(original | mask) if _boolean(value) else (original & ~mask)])
    if reg == 402:
        return _station(value)
    if token in (2, 7):
        if token == 2 and (field in ("J", "K") or reg in (400, 404)):
            if not isinstance(value, str) or (value and not re.fullmatch(r"[0-9]+", value)):
                raise ValueError("Use a digit string without spaces or punctuation")
        return _counted(value, size, ascii_text=(token == 7))
    if token == 10:
        if not isinstance(value, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value):
            raise ValueError("Enter time as HH:MM, from 00:00 to 23:59")
        hours, minutes = map(int, value.split(":"))
        return bytes([minutes, hours])
    if meta.get("value_labels"):
        labels = meta["value_labels"]
        matching = [int(k) for k, v in labels.items() if str(value).lower() == v.lower()]
        value = matching[0] if matching else _integer(value)
        if str(value) not in labels:
            raise ValueError("Choose " + ", ".join(labels.values()))
    if token in (3, 4):
        amount = _number(value)
        if field == "H" and not Decimal(0) <= amount <= Decimal("9.95"):
            raise ValueError("Amount must be between $0.00 and $9.95")
        if field in INTEGER_LIMITS and not (0 <= amount <= INTEGER_LIMITS[field] and amount == int(amount)):
            raise ValueError(f"Use a whole-dollar amount from 0 to {INTEGER_LIMITS[field]}")
        nickels = amount * 20
        if nickels != nickels.to_integral_value():
            raise ValueError("Amount must be a multiple of $0.05")
        number = int(nickels)
    else:
        number = _integer(value)
        maximum = INTEGER_LIMITS.get(field)
        if maximum is not None and not 0 <= number <= maximum:
            raise ValueError(f"Allowed range is 0 to {maximum}")
        if field == "S" and number not in (16, 20):
            raise ValueError("LCD width must be 16 or 20")
        if 200 <= reg <= 299:
            _validate_macro(number, rows, family)
        if reg == 437:
            number *= 24
    if not 0 <= number < 256 ** size:
        raise ValueError("Value does not fit the phone's storage")
    return number.to_bytes(size, "little")


def apply_changes(model: C94File, changes: dict, description: str | None = None) -> C94File:
    """Return a new image; never mutate the source or re-encode untouched fields.

    Changes are e.g. {"R100": True, "R437": 3, "R604": "0.25"}.
    R468 uses {"4": {"interval1": True, "interval2": False}} (call type 4).
    """
    if not isinstance(changes, dict):
        raise ValueError("Changes must be a dictionary of settings")
    rows = {r["register_num"]: r for r in decode_registers(model)}
    family = TABLE_VERSIONS[map_name(model)][0]
    body = bytearray(model.body)
    seen = set()
    for key, value in changes.items():
        if not isinstance(key, str) or not re.fullmatch(r"R?[0-9]+", key, re.IGNORECASE):
            raise ValueError(f"Unknown setting: {key}")
        reg = int(key.upper().removeprefix("R"))
        if reg in seen:
            raise ValueError(f"Duplicate setting R{reg}")
        seen.add(reg)
        if reg not in rows:
            raise ValueError(f"R{reg} is not present in this firmware")
        row = rows[reg]
        # A template may contain reserved or out-of-editor-range defaults. Do
        # not rewrite/reject them simply because the user edits another field.
        if "value" in row and value == row["value"]:
            continue
        reason = read_only_reason(row)
        if reason:
            raise ValueError(f"R{reg}: {reason}")
        offset = row["offset"]
        try:
            if reg == 468:
                if not isinstance(value, dict):
                    raise ValueError("Shutdown edits must be keyed by call type 0-99")
                for call_type, options in value.items():
                    index = _integer(call_type)
                    if not 0 <= index <= 99 or not isinstance(options, dict):
                        raise ValueError("Use call types 0-99 with interval1/interval2 choices")
                    for name, enabled in options.items():
                        if name not in ("interval1", "interval2"):
                            raise ValueError(f"Unknown shutdown option: {name}")
                        mask = 1 if name == "interval1" else 2
                        pos = offset + index
                        body[pos] = (body[pos] | mask) if _boolean(enabled) else (body[pos] & ~mask)
            else:
                # Several independent options share a byte. Merge into the
                # current buffer so a second edit cannot undo the first one.
                current = {**row, "raw_hex": body[offset:offset + 1].hex()} if row["token"] == 8 else row
                encoded = _encode(current, value, rows, family)
                body[offset:offset + len(encoded)] = encoded
        except ValueError as exc:
            raise ValueError(f"R{reg} ({row['parameter']['name']}): {exc}") from exc
    header = bytearray(model.raw_header)
    if description is not None and description != model.description:
        if not isinstance(description, str):
            raise ValueError("Description must be text")
        try:
            encoded = description.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError("Description must contain ASCII characters only") from exc
        if len(encoded) > 58:
            raise ValueError("Description must be at most 58 characters")
        header[109] = len(encoded)
        header[110:168] = encoded.ljust(58, b"\0")
    return C94File(raw_header=bytes(header), body=bytes(body))


def editor_settings(model: C94File) -> list[dict]:
    """UI-facing settings: omit Lo/Hi, addresses, binary tokens, and raw bytes."""
    result = []
    rows = decode_registers(model)
    family = TABLE_VERSIONS[map_name(model)][0]
    for row in rows:
        reg, meta = row["register_num"], row["parameter"]
        reason = read_only_reason(row)
        kind = "number"
        choices = None
        if row["token"] == 8:
            kind = "boolean"
        elif meta.get("value_labels"):
            kind, choices = "choice", meta.get("value_labels", {})
        elif 200 <= reg <= 299:
            kind = "choice"
            choices = {str(m["MacroID"] - (50 if family == "KX" else 0)): m["MacroDescr"]
                       for m in definitions()["macros"] if m["MacroModel"] == (5502 if family == "KX" else 5)}
            # Only configured user programs can be selected.
            for candidate in rows:
                number = candidate["parameter"].get("macro_number")
                if number is not None and any(candidate.get("value", [])):
                    choices[str(number)] = f"User-defined macro {number}"
        elif row["token"] == 10:
            kind = "time"
        elif row["token"] in (2, 7):
            kind = "text"
        elif reg == 468:
            kind = "shutdown"
        elif row["token"] == 6:
            kind = "program"
        result.append({"id": f"R{reg}", "name": meta["name"],
                       "category": (meta.get("categories") or ["Other settings"])[0],
                       "value": row.get("value"), "kind": kind, "choices": choices,
                       "boolean_labels": meta.get("value_labels", {}) if row["token"] == 8 else None,
                       "read_only": reason, "rule": meta.get("editor_rule", ""),
                       "units": meta.get("units", ""), "notes": meta.get("notes", []),
                       "call_options": row.get("call_options"), "error": row.get("error")})
    return result
