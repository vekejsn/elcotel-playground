# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic"]
# ///
"""Local, browser-based C94 editor. Run, then open the printed localhost URL."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from c94file import parse_c94
from c94file.editor import apply_changes, editor_settings

MAX_REQUEST = 256 * 1024


def open_image(raw: bytes) -> dict:
    image = parse_c94(raw)
    return {"firmware": f"{image.tag[:2]} {image.version}",
            "description": image.description, "settings": editor_settings(image)}


def save_image(payload: dict) -> bytes:
    if not isinstance(payload, dict):
        raise ValueError("Expected an edit request")
    try:
        raw = base64.b64decode(payload["original"], validate=True)
    except (KeyError, TypeError, ValueError, binascii.Error) as exc:
        raise ValueError("The original C94 image is missing or invalid; open it again") from exc
    image = parse_c94(raw)
    updated = apply_changes(image, payload.get("changes", {}), payload.get("description"))
    encoded = updated.to_bytes()
    if parse_c94(encoded) != updated:
        raise ValueError("Edited image failed roundtrip verification")
    return encoded


class EditorHandler(BaseHTTPRequestHandler):
    def _respond(self, status, data, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    def _local_request(self):
        hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        if self.headers.get("Host") not in hosts or (origin is not None and origin not in {"http://" + host for host in hosts}):
            self._respond(403, b"Only same-origin localhost requests are allowed", "text/plain")
            return False
        return True

    def do_GET(self):
        if not self._local_request():
            return
        assets = {"/": ("index.html", "text/html; charset=utf-8"),
                  "/editor.js": ("editor.js", "text/javascript; charset=utf-8"),
                  "/editor.css": ("editor.css", "text/css; charset=utf-8")}
        if self.path not in assets:
            self._respond(404, b"Not found", "text/plain")
            return
        filename, content_type = assets[self.path]
        data = (Path(__file__).parent / "c94file" / "web" / filename).read_bytes()
        self._respond(200, data, content_type)

    def do_POST(self):
        if not self._local_request():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_REQUEST:
                raise ValueError("Upload is empty or too large")
            if self.path not in ("/api/open", "/api/save"):
                self._respond(404, b"Not found", "text/plain")
                return
            raw = self.rfile.read(length)
            if self.path == "/api/open":
                self._respond(200, json.dumps(open_image(raw)).encode(), "application/json")
            else:
                self._respond(200, save_image(json.loads(raw)), "application/octet-stream")
        except (ValueError, TypeError, OverflowError) as exc:
            self._respond(400, json.dumps({"error": str(exc)}).encode(), "application/json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8094)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), EditorHandler)
    print(f"C94 editor: http://127.0.0.1:{server.server_port}", flush=True)
    print("Files stay on your computer. Saves download a new file; originals are never overwritten.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
