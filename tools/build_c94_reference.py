# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic"]
# ///
"""Generate the complete parameter index from bundled definitions.

Run from the repository root: python -m tools.build_c94_reference
"""

from pathlib import Path

from c94file.parser import _maps
from c94file.semantics import (
    FIELD_RULES, MACRO_SUBCOMMANDS, TABLE_VERSIONS, definitions, describe_parameter,
)


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_reference() -> str:
    lines = [
        "# C94 parameter reference", "",
        "**Every mapped parameter is listed**, including undocumented, reserved, and",
        "hidden settings. A factory label is not proof of a complete behavioral model.",
        "`documented` below means its name/function is established; it does not",
        "mean every numeric choice, timebase, or hardware",
        "interaction has been recovered. Do not program unknown values into hardware.", "",
        "## How to read this reference", "",
        "- Location is a hexadecimal offset in the expanded 4096-byte body, not a compressed-file offset.",
        "- `bN` is a one-based bit within that byte; `/N` is a byte-storage length.",
        "- Firmware values identify the supported family and version.",
        "- Presence in a register map is distinct from visibility in the editor: Lo/Hi",
        "  are firmware **version codes**, not numeric parameter limits.",
        "- Editor rules are UI acceptance ranges, not independently verified firmware limits.",
        "- `cross-family inference` means only the other model's factory table names it;",
        "  that name is a lead, not a confirmed meaning for this model.",
        "- In particular, LP R482-R499/R550/R551 are intentionally hidden/defaulted.",
        "- `unknown` and `reserved/proprietary` are real gaps, not zero-valued booleans.", "",
        "- `CONFLICT` preserves disagreeing validators in the master versus display tables:",
        "  for example KX coin-channel values have both 0..99 and 0..200 validators.",
        "  Neither is silently treated as a firmware limit.", "",
        "## Functional model", "",
        "- **R100-R199:** bit options enabling features or asserting negative options",
        "  such as 'Disable ...'. ON does not always mean the associated hardware is enabled.",
        "- **R200-R299:** call-class-to-macro selection. R204, for example, selects the",
        "  processing macro for sent-paid local calls; it is not a price field.",
        "- **R300-R305 / R512-R525:** inline user macro programs. Macro numbers 45-50",
        "  select R300-R305; numbers 51-64 select R512-R525 where those maps include them.",
        "- **R310-R343:** carrier/service access numbers and authorization strings.",
        "  Access number and authorization are distinct strings used by macro instructions.",
        "- **R400-R499:** station credentials, timings, routing controls, shutdown schedules,",
        "  keypad modes, language/LCD settings and programmable coin settings.",
        "- **R500-R558:** gain/voice detection, time-of-day tariff periods and discounts,",
        "  extended macro storage and additional coin/voice settings.",
        "- **R602-R612:** special-service and voice-mail prices, stored in nickels.",
        "- **R701-R728:** alarm-enable flags, not the current alarm status.",
        "  R750 onward contains thresholds/settings associated with alarms.", "",
        "## Important relationships and unresolved enums", "",
        "- R101 enables PBX prefix R341. R107 enables the time-of-day mechanism; R503-R505",
        "  select period starting hours and R506-R511 hold the two discounts for each",
        "  tariff class. Percentage values are not coin prices.",
        "- Permissive-dialing flags R111/R112/R114/R115 select old/new NPA pairs",
        "  R460/R459, R462/R461, R449/R448, R451/R450 respectively.",
        "- R437's displayed interval is days, but its byte is hours (`days * 24`).",
        "- On LP 05.04, R424-R430 select keypad/DTMF protection: 0 disables the keypad",
        "  with protection on; 1 allows the keypad until wink/secondary dial tone with",
        "  protection on; 2 leaves the keypad enabled with protection off. R431's",
        "  default-selector legend and older LP revisions remain unconfirmed.",
        "- KX 01.02/01.03 branch handlers establish R424-R431 as 0 keypad off /",
        "  protection on, 1 keypad on / protection on, 2 keypad on / protection off.",
        "  R422 selects a routing class; R423 selects a local price-band threshold.",
        "  R453 is 0 Smart/COCOT, 1 Hybrid, 2 Bright, but coin-line processing is",
        "  omitted in a checked 01.02 build and included in a checked 01.03 build.",
        "  Stored values do not prove build/hardware capability. Exact patch/build",
        "  coverage is not established; these labels are not applied to 01.00/01.01.",
        "  KX volume code-to-gain meanings remain unresolved; no dB labels are assigned.",
        "- On LP 05.04, R453 is 0 Smart, 1 Hybrid, 2 Bright. Hybrid/Bright require",
        "  coin-line-capable hardware and coin-line service. R422 selects a routing class,",
        "  while R423 selects a local price-band threshold; they are different concepts.",
        "- R501=0 is confirmed as the lowest starting volume on LP 05.04. The volume",
        "  button cycles four levels in 3 dB steps, but code-to-gain values for 1-3",
        "  remain unconfirmed. No exact dB labels are assigned to those codes.",
        "- R472: 0 English, 1 Spanish; 2 French is confirmed for KX 01.03.00 only.",
        "  R473 is 16/20-character LCD width on KX.",
        "- R463/R464 define shutdown interval 1; R465/R466 define interval 2. In R468,",
        "  byte `i` corresponds to call type `i` (register `200+i`), bit 0 restricts it",
        "  during interval 1 and bit 1 during interval 2. The remaining bits are unknown.",
        "- R400/R402/R403/R404 require special handling. Bypass/ANI are",
        "  binary digits, the password is ASCII, and the station ID has its own BCD/checksum",
        "  encoding. Do not apply the ordinary dial-string decoder to every field.", "",
        "## Editor field rules", "",
        "FieldType letters are editor validators; they are unrelated to the",
        "binary Token numbers in register maps.", "",
        "| FieldType | Acceptance rule |", "|---|---|",
    ]
    lines.extend(f"| {key} | {cell(rule)} |" for key, rule in FIELD_RULES.items())
    maps = _maps()
    lines.extend(["", "## Confirmed choices", "",
                  "Labels are firmware-specific. They are not automatically copied to other",
                  "families or older firmware. Hardware restrictions still apply.", "",
                  "| Firmware | Register | Value | Meaning |", "|---|---|---|---|"])
    for table, (family, version, _) in TABLE_VERSIONS.items():
        for entry in maps[table]:
            meta = describe_parameter(table, entry)
            for value, label in {**meta.get("known_value_labels", {}), **meta.get("value_labels", {})}.items():
                lines.append(f"| {family} {version} | R{entry['register_num']} | {value} | {cell(label)} |")
    for family in ("LP", "KX"):
        tables = [t for t in TABLE_VERSIONS if TABLE_VERSIONS[t][0] == family]
        registers = sorted({r["register_num"] for t in tables for r in maps[t]})
        statuses = {}
        collected = []
        for register in registers:
            versions, locations = [], set()
            variants = []
            for table in tables:
                entry = next((r for r in maps[table] if r["register_num"] == register), None)
                if entry is None:
                    continue
                versions.append(TABLE_VERSIONS[table][1])
                offset = int(entry["address"], 16)
                width = f"b{entry['size']}" if entry["token"] == 8 else f"/{entry['size']}"
                locations.add(f"{offset:04X}{width} (T{entry['token']})")
                variants.append((table, describe_parameter(table, entry)))
            meta = variants[-1][1]
            statuses[meta["status"]] = statuses.get(meta["status"], 0) + 1
            collected.append((register, meta, versions, locations, variants))
        lines.extend(["", f"## {family} parameters ({len(registers)} unique mapped registers)", "",
                      "; ".join(f"{status}: {count}" for status, count in sorted(statuses.items())) + ".", "",
                      "| Register | Meaning / factory label | Body location (Token) | Editor range / units | Firmware | Evidence status |",
                      "|---|---|---|---|---|---|"])
        for reg, meta, versions, locations, variants in collected:
            rule = meta.get("editor_rule", "See encoding in FORMAT.md")
            if "units" in meta:
                rule += "; " + meta["units"]
            names = sorted({m["name"] for _, m in variants})
            lines.append("| " + " | ".join(map(cell, [f"R{reg}", " / ".join(names),
                ", ".join(sorted(locations)), rule, ", ".join(versions), meta["status"]])) + " |")
        lines.extend(["", f"### {family} parameter notes", ""])
        for reg, meta, _, _, variants in collected:
            notes = sorted({n for _, m in variants for n in m.get("notes", [])})
            if notes:
                lines.append(f"- **R{reg}**: " + " ".join(notes))
    lines.extend(["", "## Built-in macro numbers", "",
                  "Names are the database's factory definitions, not descriptions inferred from",
                  "the bytecode. KX database IDs are the phone-visible number plus 50.",
                  "User-defined macro IDs from phone/customer records are not exported.", "",
                  "| Family | Phone macro number | Factory name |", "|---|---|---|"])
    for macro in sorted(definitions()["macros"], key=lambda r: (r["MacroModel"], r["MacroID"])):
        family = "KX" if macro["MacroModel"] == 5502 else "LP"
        number = macro["MacroID"] - (50 if family == "KX" else 0)
        lines.append(f"| {family} | {number} | {cell(macro['MacroDescr'])} |")
    lines.extend(["", "## Inline macro instructions", "",
                  "Programs have 26 **bytes**, not necessarily 26 instructions. Parameterized",
                  "opcodes consume the next byte as an operand. Opcode 69 / subcommand 11",
                  "also consumes a delay byte. Zero slots are padding; the host editor scans",
                  "the entire array rather than treating the first zero as a mandatory terminator.",
                  "Unknown opcodes remain unknown; disassembly after one may be ambiguous.", "",
                  "| Family | Opcode | Operation | Operand |", "|---|---|---|---|"])
    for family, table in (("LP", "lp_instructions"), ("KX", "kx_instructions")):
        for command in sorted(definitions()[table], key=lambda r: r["CmdID"]):
            parameter = (command["ParamText"] or "parameter") if command["Parameter"] else "none"
            lines.append(f"| {family} | {command['CmdID']} | {cell(command['Description'])} | {cell(parameter)} |")
    lines.extend(["", "### Operand-dependent operations", ""])
    for opcode, values in MACRO_SUBCOMMANDS.items():
        for value, meaning in values.items():
            lines.append(f"- Opcode **{opcode}**, operand **{value}**: {meaning}.")
    lines.extend(["", "## What is still not established", "",
                  "Undocumented flags, proprietary features, unspecified timer scales, numeric",
                  "mode legends, hardware-specific coin calibration units, and high bits of R468",
                  "are not reverse-engineered just because their offsets are known. The table",
                  "above retains them explicitly. Cross-family names require firmware/manual",
                  "confirmation before they can be treated as confirmed for that model.", "",
                  "R340 has no established semantic name. It is a 16-byte counted dial-string",
                  "field at body offset 09F4 in every supported map; its purpose is unknown.", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "c94file" / "PARAMETERS.md"
    path.write_text(build_reference(), encoding="utf-8", newline="\n")
    print(f"Generated {path}")
