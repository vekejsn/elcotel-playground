from __future__ import annotations

from .parser import read_s94, write_s94


def verify_s94(path: str) -> tuple[bool, str | None]:
    try:
        original = open(path, "rb").read()
    except OSError as e:
        return False, str(e)
    try:
        model = read_s94(path)
    except Exception as e:
        return False, f"Parse error: {e}"
    import os, tempfile

    fd, tmp = tempfile.mkstemp(suffix=".S94")
    os.close(fd)
    try:
        write_s94(model, tmp)
        rebuilt = open(tmp, "rb").read()
    finally:
        os.unlink(tmp)
    header = original[:168]
    orig_body_compressed = original[168:]
    from elcotel.codec import decompress

    orig_body = (
        decompress(orig_body_compressed) if orig_body_compressed else bytearray()
    )
    rebuilt_body_compressed = rebuilt[168:]
    rebuilt_body = (
        decompress(rebuilt_body_compressed) if rebuilt_body_compressed else bytearray()
    )
    if bytes(orig_body) != bytes(rebuilt_body):
        diffs = []
        for i in range(max(len(orig_body), len(rebuilt_body))):
            if (
                i >= len(orig_body)
                or i >= len(rebuilt_body)
                or orig_body[i] != rebuilt_body[i]
            ):
                diffs.append(i)
                if len(diffs) >= 10:
                    break
        return False, f"Body mismatch at offsets: {diffs}"
    return True, None
