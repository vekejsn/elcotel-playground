# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pydantic",
#   "click",
# ]
# ///

import json
import click

from p94file import read_p94, write_p94


@click.command()
@click.argument("json_file")
@click.argument("output")
@click.option(
    "--verify-roundtrip", is_flag=True, help="Read back and verify body matches"
)
def main(json_file, output, verify_roundtrip):
    with open(json_file) as f:
        data = json.load(f)
    from p94file.types import P94File

    model = P94File.model_validate(data)
    write_p94(model, output)
    click.echo(f"Wrote {output}")
    if verify_roundtrip:
        rebuilt = read_p94(output)
        if len(rebuilt.records) != len(model.records):
            click.echo(
                f"VERIFY FAIL: record count mismatch {len(rebuilt.records)} vs {len(model.records)}"
            )
        else:
            click.echo("Round-trip verify OK")


if __name__ == "__main__":
    main()
