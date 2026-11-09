# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic", "click"]
# ///
"""Verify C94 parsing, register decoding, and byte-perfect canonical roundtrips."""

from pathlib import Path

import click

from c94file import decode_registers, read_c94


@click.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
def main(directory):
    paths = sorted(p for p in Path(directory).rglob("*") if p.suffix.lower() == ".c94")
    if not paths:
        raise click.ClickException(f"No C94 files found in {directory}")
    failed = 0
    for path in paths:
        try:
            image = read_c94(path)
            errors = [r for r in decode_registers(image) if "error" in r]
            if errors:
                raise ValueError(f"Invalid register values: {errors}")
            if image.to_bytes() != path.read_bytes():
                raise ValueError("Compressed bytes differ after canonical re-encoding")
            click.echo(f"OK {path}")
        except (OSError, ValueError) as exc:
            failed += 1
            click.echo(f"FAIL {path}: {exc}")
    click.echo(f"{len(paths) - failed}/{len(paths)} passed")
    if failed:
        raise click.ClickException(f"{failed} C94 files failed verification")


if __name__ == "__main__":
    main()
