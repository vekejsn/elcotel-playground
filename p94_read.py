# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pydantic",
#   "click",
# ]
# ///

import click
import json
import sys

from p94file import read_p94, write_p94
from p94file.types import UNUSED_TOKEN, UNLIMITED_TOKEN, RESTRICTED_TOKEN

LATA_TYPES = {
    0: "!",
    1: "Local",
    2: "IntraLATA",
    3: "InterLATA",
    4: "FCC",
    5: "Corridor",
    6: "Canadian",
    7: "Extended",
    8: "Misc",
}


def _format_rate(val):
    if val == UNUSED_TOKEN:
        return "!.!!"
    return f"${val / 20:.2f}"


def _format_time(val):
    if val == UNLIMITED_TOKEN:
        return "U"
    if val == RESTRICTED_TOKEN:
        return "R"
    return str(val)


def _format_macro(val):
    if val == UNUSED_TOKEN:
        return "!"
    return str(val)


def _summary(model):
    click.echo(f"Description: {model.header.description}")
    click.echo(f"Data length: {model.header.file_data_length}")
    active = [r for r in model.records if r.pattern]
    click.echo(f"Active entries: {len(active)}/{len(model.records)}")
    click.echo(f"Has P99 companion: {model.has_p99}")
    click.echo()
    for rec in active:
        click.echo(
            f"  [{rec.pri_parse_no:3d}] {rec.pattern:<25s}  "
            f"Macro={_format_macro(rec.macro)} Timer={_format_macro(rec.timer)}  "
            f"Rate1={_format_rate(rec.rate1)} Time1={_format_time(rec.time1)}  "
            f"Rate2={_format_rate(rec.rate2)} Time2={_format_time(rec.time2)}  "
            f"Type={LATA_TYPES.get(rec.lata_type, '?')}"
        )


@click.command()
@click.option("--file", "filepath", required=True, help="Path to .P94 file")
@click.option("--summary", is_flag=True, help="Print human-readable summary")
@click.option("--json-out", default=None, help="Write parsed model as JSON")
def main(filepath, summary, json_out):
    model = read_p94(filepath)
    if json_out:
        data = json.loads(model.model_dump_json())
        with open(json_out, "w") as f:
            json.dump(data, f, indent=2)
        click.echo(f"JSON written to {json_out}")
    if summary or not json_out:
        _summary(model)


if __name__ == "__main__":
    main()
