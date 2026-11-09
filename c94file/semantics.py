"""C94 parameter meanings and firmware-specific editing rules.

Factory descriptions are evidence, not a complete firmware specification.
Unknown enum meanings and cross-family inferences are explicitly marked.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .enums import enum_metadata

# These describe the editor's acceptance rules, NOT firmware safety limits.
FIELD_RULES = {
    "A": "ON/OFF",
    "B": "integer 0..99",
    "C": "integer 0..9",
    "D": "integer 0..19",
    "E": "integer 0..200",
    "F": "integer 0..999",
    "G": "hour 0..23",
    "H": "$0.00..$9.95 in $0.05 increments",
    "I": "up to 15 characters; UI prompt says NPANXXXXXX; may be empty",
    "J": "up to 19 numeric characters; may be empty",
    "K": "integer 0..99; may be empty",
    "L": "integer 0..2; meanings depend on setting/firmware; unknown unless labeled",
    "M": "integer 0..3; meanings depend on setting/firmware; unknown unless labeled",
    "N": "integer 0..255",
    "O": "integer 0..60",
    "P": "integer 0..96",
    "Q": "HH:MM, 00:00..23:59",
    "R": "0=English, 1=Spanish; KX >=01.03.00 also permits 2=French",
    "S": "16 or 20 LCD characters",
    "T": "integer 0..10",
    "U": "integer 0..7",
    "V": "integer 0..9999",
}

TABLE_VERSIONS = {
    "LP050300": ("LP", "05.03.00", 0),
    "LP050301": ("LP", "05.03.01", 1),
    "LP050302": ("LP", "05.03.02", 2),
    "LP050303": ("LP", "05.03.03", 3),
    "LP050400": ("LP", "05.04.00", 4),
    "KX010000": ("KX", "01.00.00", 0),
    "KX010100": ("KX", "01.01.00", 1),
    "KX010200": ("KX", "01.02.00", 2),
    "KX010300": ("KX", "01.03.00", 3),
}

SPECIALS = {
    400: ("Cashbox/vault bypass code", "Configuration"),
    402: ("Station ID", "Configuration"),
    403: ("Communications password", "Configuration"),
    404: ("ANI / station telephone number", "Configuration"),
    468: ("Per-call-type shutdown restrictions", "Shutdown scheduling"),
}

# Operand-specific descriptions supplement generic command names.
MACRO_SUBCOMMANDS = {
    68: {1: "If DTMF # detected, send credit card buffer",
         2: "If DTMF B detected, splash back",
         4: "If DTMF * detected, say previous call number and amount",
         17: "User-defined return macro (Reg 306)",
         18: "User-defined return macro (Reg 307)",
         19: "User-defined return macro (Reg 308)"},
    69: {2: "Say 'Payphone not ...' (abbreviated label)",
         3: "Special processing to AMNEX",
         4: "PAOF collect with voice recording",
         5: "Point voice to speak locally only",
         7: "PF collect 'To accept ...' (abbreviated label)",
         8: "Say second brand for PAOF",
         9: "PF terminate collect call",
         10: "Speak first brand if present",
         11: "Delay an additional operand's number of seconds before producing coin tones"},
}

NOTES = {
    101: "Enables use of PBX prefix R341; does not itself contain the prefix.",
    107: "Enables the tariff periods R503-R505 and discount percentages R506-R511.",
    111: "Enables the old/new NPA pair R460/R459.",
    112: "Enables the old/new NPA pair R462/R461.",
    114: "Enables the old/new NPA pair R449/R448.",
    115: "Enables the old/new NPA pair R451/R450.",
    133: "Negative-polarity option: ON disables relay pre-charging, rather than enabling it.",
    134: "Negative-polarity option: ON selects 'Do NOT correct user dialing'.",
    400: "Length-prefixed binary digits, not ASCII. Sensitive station credential.",
    402: "Short binary-digit ID or biased 10-digit packed BCD, followed by checksum; see FORMAT.md.",
    403: "Length-prefixed ASCII, not binary dial digits. Sensitive station credential.",
    404: "Length-prefixed binary digits; supplied from the phone's ANI field.",
    437: "UI value is days; C94 stores hours (days x 24). Do not interpret the byte directly as days.",
    456: "Dialing-speed setting; timebase and enum meanings are not established by the UI label.",
    463: "Beginning of shutdown interval 1; R464 ends it. R468 bit 0 chooses affected call types.",
    464: "End of shutdown interval 1, paired with R463.",
    465: "Beginning of shutdown interval 2; R466 ends it. R468 bit 1 chooses affected call types.",
    466: "End of shutdown interval 2, paired with R465.",
    468: "100 bytes indexed by call type 0..99, not by macro number. Bit 0 restricts interval 1; bit 1 restricts interval 2. Bits 2..7 are not decoded.",
    472: "Language selector; English/Spanish are documented. French is confirmed for KX 01.03.00, not inferred for LP.",
    473: "LCD width in characters (16 or 20); an LP interpretation borrowed from KX remains an inference.",
    550: "Programmable coin/hopper setting. LP 05.04.00 set-like code forces this from defaults rather than user input.",
    551: "Cash-box volume setting. LP 05.04.00 set-like code forces this from defaults rather than user input.",
}


@lru_cache(maxsize=1)
def definitions() -> dict:
    return json.loads(Path(__file__).with_name("definitions.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _factory_rows(prefix: str, reg: int) -> tuple:
    # Master template gives canonical names. Display tables retain some older
    # definitions omitted from the master, so consult both, deduplicating.
    result = []
    for table in (prefix + "parameters", prefix + "display_parameters"):
        for row in definitions()[table]:
            if int(row["RegNo"]) == reg:
                item = (row["PermDef"], row["FieldType"], row["Lo"], row["Hi"])
                if not any(item[:4] == prior[:4] for prior in result):
                    result.append(item)
    return tuple(result)


def _categories(prefix: str, reg: int) -> list[str]:
    data = definitions()
    sequences = {r["Sequence"] for r in data[prefix + "groups"]
                 if r["FormatNo"] == 0 and int(r["Reg"]) == reg}
    return sorted({r["Caption"] for r in data[prefix + "categories"]
                   if r["FormatNo"] == 0 and r["Sequence"] in sequences})


@lru_cache(maxsize=None)
def _describe(table: str, reg: int, token: int, size: int) -> dict:
    family, version, code = TABLE_VERSIONS[table]
    prefix = "kx_" if family == "KX" else "lp_"
    rows = _factory_rows(prefix, reg)
    categories = _categories(prefix, reg)
    metadata = {"status": "documented", "categories": categories}
    if rows:
        active = [r for r in rows if r[2] <= code <= r[3]]
        chosen = (active or list(rows))[0]
        name, field, lo, hi = chosen
        metadata.update(name=name, field_type=field,
                        editor_rule=FIELD_RULES.get(field, "Unknown field rule"),
                        ui_visible_in_version=bool(active))
        metadata["ui_definitions"] = [
            {"name": r[0], "field_type": r[1], "lo": r[2], "hi": r[3]}
            for r in rows]
        fields = {r[1] for r in (active or rows)}
        if len(fields) > 1:
            metadata["conflicting_editor_rules"] = {
                field: FIELD_RULES.get(field, "Unknown field rule") for field in sorted(fields)}
            metadata["editor_rule"] = "CONFLICT: " + "; ".join(
                f"{field}: {rule}" for field, rule in metadata["conflicting_editor_rules"].items())
    elif reg in SPECIALS:
        name, category = SPECIALS[reg]
        metadata.update(name=name, categories=[category])
    elif token == 6 and (300 <= reg <= 305 or 512 <= reg <= 525):
        number = reg - 300 + 45 if reg <= 305 else reg - 512 + 51
        metadata.update(name=f"User-defined macro {number} command table",
                        categories=["Inline macros"], macro_number=number,
                        editor_rule="26 raw command/operand bytes; not a macro ID")
    else:
        other_prefix = "lp_" if family == "KX" else "kx_"
        other = _factory_rows(other_prefix, reg)
        if other:
            metadata.update(name=other[0][0], status="cross-family inference",
                            inferred_from_family="LP" if family == "KX" else "KX",
                            editor_rule="Not established for this family; other-family rule: "
                                        + FIELD_RULES.get(other[0][1], "unknown"))
        else:
            metadata.update(name="Undocumented parameter", status="unknown",
                            editor_rule="Not recovered")
    name = metadata["name"]
    if name.lower() == "spare" or "customer proprietary" in name.lower():
        metadata["status"] = "reserved/proprietary; behavior unknown"
    notes = [NOTES[reg]] if reg in NOTES else []
    if 482 <= reg <= 499 and family == "LP":
        notes.append("LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.")
    if 200 <= reg <= 299:
        metadata.update(kind="call-type macro selection", call_type=reg - 200,
                        editor_rule="macro number 0..99; existence checked for defined call types",
                        units="macro number")
        notes.append("Selects a processing macro for this call type. Does not contain a price or an instruction opcode.")
    elif token == 8:
        metadata["kind"] = "boolean option/alarm enable"
        metadata["bit_mask"] = f"0x{1 << (size - 1):02X}"
        notes.append("ON means the factory label is asserted; preserve negative labels such as 'Disable'.")
    elif token == 6:
        metadata["kind"] = "inline macro program"
    elif token == 11:
        metadata["kind"] = "per-call-type bit flags"
    elif token in (2, 7):
        metadata["kind"] = "ASCII string" if token == 7 else "binary dial string / special ID"
    else:
        metadata["kind"] = "numeric setting"
    if token in (3, 4):
        metadata["units"] = "dollars (stored as nickels)"
    elif token == 10:
        metadata["units"] = "time of day HH:MM (stored minute, hour)"
    elif reg == 437:
        metadata["units"] = "days (stored as hours)"
    elif "%" in name:
        metadata["units"] = "percent"
    elif "in hours" in name.lower() or metadata.get("field_type") == "G":
        metadata["units"] = "hours"
    elif "minutes" in name.lower():
        metadata["units"] = "minutes"
    elif "(in secs)" in name.lower():
        metadata["units"] = "seconds"
    elif token in (1, 5, 9) and "units" not in metadata:
        metadata["units"] = "not established unless stated in name/notes"
    if reg == 472 and metadata["status"] == "documented":
        metadata["value_labels"] = {"0": "English", "1": "Spanish"}
        if family == "KX" and version >= "01.03.00":
            metadata["value_labels"]["2"] = "French"
    confirmed = enum_metadata(family, version, reg)
    notes.extend(confirmed.pop("notes", []))
    metadata.update(confirmed)
    if metadata.get("value_labels"):
        metadata["editor_rule"] = "; ".join(f"{value}={label}" for value, label in metadata["value_labels"].items())
    if notes:
        metadata["notes"] = notes
    return metadata


def describe_parameter(table: str, entry: dict) -> dict:
    # Return a detached copy so caller edits cannot corrupt cached definitions.
    value = _describe(table, entry["register_num"], entry["token"], entry["size"])
    return json.loads(json.dumps(value))


def disassemble_macro(data: list[int], family: str) -> list[dict]:
    """Decode command bytes, consuming operand bytes only for parameterized ops.

    Zero slots are padding (the original editor scans all 26 slots), not
    unconditional end-of-program markers. Nonzero bytes after a zero are kept.
    """
    prefix = "kx_" if family == "KX" else "lp_"
    commands = {r["CmdID"]: r for r in definitions()[prefix + "instructions"]}
    instructions = []
    index = 0
    while index < len(data):
        offset, opcode = index, data[index]
        index += 1
        if opcode == 0:
            continue
        cmd = commands.get(opcode)
        row = {"byte_offset": offset, "opcode": opcode,
               "description": cmd["Description"] if cmd else "Unknown opcode"}
        if cmd and cmd["Parameter"]:
            row["parameter_meaning"] = cmd["ParamText"]
            if index < len(data):
                row["parameter"] = data[index]
                index += 1
                if opcode in MACRO_SUBCOMMANDS:
                    row["parameter_description"] = MACRO_SUBCOMMANDS[opcode].get(row["parameter"], "Unknown subcommand")
                if opcode == 69 and row["parameter"] == 11:
                    if index < len(data):
                        row["delay_seconds"] = data[index]
                        index += 1
                    else:
                        row["error"] = "Missing delay operand byte"
            else:
                row["error"] = "Missing operand byte"
        instructions.append(row)
    return instructions


def annotate_register(table: str, row: dict, all_rows: dict[int, dict]) -> dict:
    meta = describe_parameter(table, row)
    result = {**row, "parameter": meta}
    if "value" not in row:
        return result
    family = TABLE_VERSIONS[table][0]
    value, reg = row["value"], row["register_num"]
    if row["token"] == 8:
        result["display_value"] = meta.get("value_labels", {}).get(str(int(value)), "ON" if value else "OFF")
    elif meta.get("value_labels"):
        unknown = f"Unknown language code {value}" if reg == 472 else f"Unknown choice {value}"
        result["display_value"] = meta["value_labels"].get(str(value), unknown)
    elif str(value) in meta.get("known_value_labels", {}):
        result["display_value"] = meta["known_value_labels"][str(value)]
    elif reg == 472:
        result["display_value"] = f"Unknown language code {value}"
    elif 200 <= reg <= 299:
        if 45 <= value <= 64:
            register = value - 45 + 300 if value <= 50 else value - 51 + 512
            result["macro"] = {"number": value, "register_num": register,
                               "available_in_map": register in all_rows,
                               "name": f"User-defined macro {value}"}
        else:
            database_id = value + 50 if family == "KX" else value
            model_id = 5502 if family == "KX" else 5
            match = next((m for m in definitions()["macros"]
                          if m["MacroID"] == database_id and m["MacroModel"] == model_id), None)
            result["macro"] = {"number": value, "name": match["MacroDescr"] if match else "Unknown/unconfigured macro"}
    elif row["token"] == 6:
        result["instructions"] = disassemble_macro(value, family)
    elif reg == 468:
        result["call_options"] = [
            {"call_type": i, "register_num": 200 + i,
             "name": describe_parameter(table, {"register_num": 200 + i, "token": 1, "size": 1})["name"],
             "restrict_during_interval_1": bool(flags & 1),
             "restrict_during_interval_2": bool(flags & 2),
             "unknown_bits_hex": f"{flags & 0xFC:02x}"}
            for i, flags in enumerate(value)]
    return result
