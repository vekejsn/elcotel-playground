# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pydantic",
#   "click",
# ]
# ///

import os
import sys
import click

sys.path.insert(0, os.path.dirname(__file__))

from s94file.verify import verify_s94
from p94file.verify import verify_p94


@click.command()
@click.option("--s94-dir", default=None, help="Directory of S94 example files")
@click.option("--p94-dir", default=None, help="Directory of P94 example files")
def main(s94_dir, p94_dir):
    base = os.path.dirname(__file__)
    if s94_dir is None:
        s94_dir = os.path.join(base, "S94_EXAMPLES")
    if p94_dir is None:
        p94_dir = os.path.join(base, "P94_EXAMPLES")

    for label, directory, verify_fn in [
        ("S94", s94_dir, verify_s94),
        ("P94", p94_dir, verify_p94),
    ]:
        if not os.path.isdir(directory):
            click.echo(f"{label}: directory not found: {directory}")
            continue
        files = sorted(
            f for f in os.listdir(directory) if f.upper().endswith(f".{label}")
        )
        ok = 0
        fail = 0
        errors = []
        for fname in files:
            path = os.path.join(directory, fname)
            success, err = verify_fn(path)
            if success:
                ok += 1
                click.echo(f"  OK  {fname}")
            else:
                fail += 1
                errors.append((fname, err))
                click.echo(f"  FAIL {fname}: {err}")
        click.echo(f"{label}: {ok} OK, {fail} FAIL out of {len(files)} files")
        if errors:
            click.echo()
            click.echo(f"{label} failures:")
            for fname, err in errors:
                click.echo(f"  {fname}: {err}")
        click.echo()


if __name__ == "__main__":
    main()
