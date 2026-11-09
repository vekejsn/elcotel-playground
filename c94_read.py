# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic", "click"]
# ///
"""Inspect a C94 image and export lossless JSON and decoded registers."""

import json
from pathlib import Path

import click

from c94file import decode_registers, read_c94
from c94file.parser import map_name


@click.command()
@click.option("--file", "filepath", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--summary", is_flag=True)
@click.option("--json-out", type=click.Path(dir_okay=False), help="Lossless writer payload (hex bytes)")
@click.option("--registers-out", type=click.Path(dir_okay=False), help="Decoded registers (inspection only)")
@click.option("--map", "table", help="Firmware map override, e.g. LP050400")
@click.option("--register", "registers", multiple=True, type=int, help="Explain a register (repeatable); includes its current value")
def main(filepath, summary, json_out, registers_out, table, registers):
    try:
        model = read_c94(filepath)
        if json_out:
            Path(json_out).write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")
        if registers_out:
            rows = decode_registers(model, table)
            Path(registers_out).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        if registers:
            wanted = set(registers)
            rows = [r for r in decode_registers(model, table) if r["register_num"] in wanted]
            missing = wanted - {r["register_num"] for r in rows}
            if missing:
                raise ValueError(f"Registers not present in this firmware map: {sorted(missing)}")
            click.echo(json.dumps(rows, indent=2))
        if summary or not (json_out or registers_out or registers):
            click.echo(f"Firmware: {model.tag[:2]} {model.version} ({model.tag})")
            click.echo(f"Description: {model.description}")
            click.echo(f"Body: {len(model.body)} bytes (compressed: {Path(filepath).stat().st_size - 168})")
            try:
                rows = decode_registers(model, table)
                click.echo(f"Register map: {table or map_name(model)} ({len(rows)} entries)")
                for row in rows:
                    if row["register_num"] in (400, 402, 403, 404):
                        # Do not unexpectedly expose credentials in a summary.
                        continue
                    if "error" in row:
                        click.echo(f"  R{row['register_num']}: {row['error']}")
            except ValueError as exc:
                click.echo(f"Register map unavailable: {exc}")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
