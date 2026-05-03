from __future__ import annotations

from .parser import read_p94, write_p94


def verify_p94(path: str) -> tuple[bool, str | None]:
    import os, tempfile
    from elcotel.codec import decompress

    try:
        original = open(path, "rb").read()
    except OSError as e:
        return False, str(e)

    try:
        model = read_p94(path)
    except Exception as e:
        return False, f"Parse error: {e}"

    base, ext = os.path.splitext(path)
    p99_path = base + ".P99"
    has_original_p99 = os.path.exists(p99_path)
    orig_p99_data = None
    if has_original_p99:
        orig_p99_data = open(p99_path, "rb").read()

    fd, tmp = tempfile.mkstemp(suffix=".P94")
    os.close(fd)
    try:
        write_p94(model, tmp)
        rebuilt = open(tmp, "rb").read()
    finally:
        os.unlink(tmp)

    orig_body = decompress(original[168:]) if len(original) > 168 else bytearray(1550)
    rebuilt_body = decompress(rebuilt[168:]) if len(rebuilt) > 168 else bytearray(1550)

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
        return False, f"P94 body mismatch at offsets: {diffs}"

    if has_original_p99 and orig_p99_data:
        tmp_p99 = base + "_verify.P99"
        rebuilt_p99_data = None
        if os.path.exists(tmp_p99):
            rebuilt_p99_data = open(tmp_p99, "rb").read()
            os.unlink(tmp_p99)
        if rebuilt_p99_data is None:
            return False, "P99 file was not created during rebuild"
        orig_p99_body = decompress(orig_p99_data[168:])
        rebuilt_p99_body = decompress(rebuilt_p99_data[168:])
        if bytes(orig_p99_body) != bytes(rebuilt_p99_body):
            return False, "P99 body mismatch"

    return True, None
