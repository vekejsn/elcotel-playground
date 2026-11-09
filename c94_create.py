# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic", "click"]
# ///
"""Rebuild a C94 from the lossless JSON exported by c94_read.py."""

from pathlib import Path

import click

from c94file import C94File, read_c94, write_c94


@click.command()
@click.argument("payload", type=click.Path(exists=True, dir_okay=False))
@click.argument("output", type=click.Path(dir_okay=False))
@click.option("--verify-roundtrip", is_flag=True)
def main(payload, output, verify_roundtrip):
    try:
        model = C94File.model_validate_json(Path(payload).read_text(encoding="utf-8"))
        write_c94(model, output)
        if verify_roundtrip and read_c94(output) != model:
            raise ValueError("C94 roundtrip changed the expanded image")
        click.echo(f"Wrote {output}")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
