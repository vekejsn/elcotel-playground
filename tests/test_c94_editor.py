from __future__ import annotations

import base64
import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from c94_editor import EditorHandler, open_image, save_image
from c94file import C94File, decode_registers, parse_c94
from c94file.editor import apply_changes, editor_settings


def fixture(tag=b"LP050400"):
    header = bytearray(168)
    header[4:8] = (4096).to_bytes(4, "little")
    header[8:16] = tag
    header[109:114] = b"\x04test"
    body = bytearray(4096)
    body[:58] = b"RATES FOR PCM 5 (C) COPYRIGHT BY ELCOTEL, INC. 1986 - 1989"
    body[0x240] = 0x80  # Preserve an unrelated flag when editing the same byte.
    body[0x890 + 4] = 0x80  # Preserve unknown shutdown bits.
    body[-1] = 0xF8  # Preserve unknown/unmapped bytes.
    return C94File(raw_header=bytes(header), body=bytes(body))


def values(image):
    return {r["register_num"]: r for r in decode_registers(image)}


class EditTests(unittest.TestCase):
    def test_human_values_and_untouched_bytes(self):
        source = fixture()
        result = apply_changes(source, {"R100": "ON", "R101": True, "R437": 3,
                                        "R604": "0.25", "R463": "22:30"})
        rows = values(result)
        self.assertTrue(rows[100]["value"])
        self.assertTrue(rows[101]["value"])
        self.assertEqual(result.body[0x240], 0x83)
        self.assertEqual(rows[437]["value"], 3)
        self.assertEqual(result.body[rows[437]["offset"]], 72)
        self.assertEqual(rows[604]["value"], .25)
        self.assertEqual(rows[604]["raw_hex"], "05")
        self.assertEqual(rows[463]["value"], "22:30")
        self.assertEqual(result.body[-1], source.body[-1])
        self.assertEqual(result.body[:58], source.body[:58])
        self.assertEqual(result.raw_header, source.raw_header)
        self.assertEqual(source.body[0x240], 0x80)

    def test_change_flag_off_preserves_other_bits(self):
        result = apply_changes(fixture(), {"R107": False, "R100": True})
        self.assertEqual(result.body[0x240], 1)

    def test_credentials_and_station_checksum(self):
        result = apply_changes(fixture(), {"R400": "0123", "R402": "2125550100",
                                            "R403": "testpass", "R404": "2125550199"})
        rows = values(result)
        self.assertEqual(rows[400]["value"], "0123")
        self.assertEqual(rows[402]["value"], "2125550100")
        self.assertTrue(rows[402]["checksum_valid"])
        self.assertEqual(rows[403]["value"], "testpass")
        self.assertEqual(rows[404]["value"], "2125550199")
        self.assertEqual(rows[403]["raw_hex"][2:6], "7465")

    def test_short_station_checksum_and_leading_zeros(self):
        row = values(apply_changes(fixture(), {"R402": "0012"}))[402]
        self.assertEqual(row["value"], "0012")
        self.assertTrue(row["checksum_valid"])

    def test_description(self):
        source = fixture()
        result = apply_changes(source, {}, "My phone")
        self.assertEqual(result.description, "My phone")
        self.assertEqual(result.body, source.body)
        self.assertEqual(result.raw_header[:109], source.raw_header[:109])

    def test_shutdown_preserves_unknown_bits(self):
        result = apply_changes(fixture(), {"R468": {"4": {"interval1": True, "interval2": True}}})
        self.assertEqual(result.body[0x894], 0x83)
        next_result = apply_changes(result, {"R468": {"4": {"interval1": False}}})
        self.assertEqual(next_result.body[0x894], 0x82)

    def test_validation_failures_do_not_mutate_source(self):
        source = fixture()
        original = source.to_bytes()
        bad_changes = [{"R437": 10}, {"R437": "1.5"}, {"R604": ".03"},
                       {"R604": "NaN"}, {"R604": "10.00"}, {"R463": "24:30"},
                       {"R472": "French"}, {"R340": "123"}, {"R482": 20},
                       {"R300": [1] * 26}, {"R204": 99}, {"R204": 45},
                       {"R400": "123456789"}, {"R404": 2125550199},
                       {"R402": "1234567890"}, {"R403": "café"},
                       {"R100": "maybe"}, {"R999": 0}, {"nope": 0},
                       {"R468": {"100": {"interval1": True}}},
                       {"R468": {"4": {"unknown": True}}},
                       {"100": True, "R100": False}]
        for change in bad_changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                apply_changes(source, change)
            self.assertEqual(source.to_bytes(), original)
        for description in ("x" * 59, "café", 42):
            with self.subTest(description=description), self.assertRaises(ValueError):
                apply_changes(source, {}, description)

    def test_named_language(self):
        result = apply_changes(fixture(), {"R472": "Spanish"})
        self.assertEqual(values(result)[472]["value"], 1)
        result = apply_changes(fixture(b"KX010300"), {"R472": "French"})
        self.assertEqual(values(result)[472]["value"], 2)

    def test_no_change_preserves_even_reserved_bytes(self):
        source = fixture()
        rows = values(source)
        self.assertEqual(apply_changes(source, {}, "test"), source)
        self.assertEqual(apply_changes(source, {"R340": rows[340]["value"]}), source)

    def test_ui_data_hides_binary_metadata(self):
        settings = editor_settings(fixture())
        rows = {r["id"]: r for r in settings}
        self.assertEqual(rows["R100"]["kind"], "boolean")
        self.assertEqual(rows["R437"]["units"], "days (stored as hours)")
        self.assertEqual(rows["R403"]["kind"], "text")
        self.assertEqual(rows["R400"]["kind"], "text")
        self.assertTrue(rows["R340"]["read_only"])
        for row in settings:
            self.assertFalse(set(row) & {"lo", "hi", "token", "offset", "raw_hex", "address"})

    def test_save_api_checks_roundtrip(self):
        source = fixture()
        payload = {"original": base64.b64encode(source.to_bytes()).decode(),
                   "changes": {"R100": True}, "description": "Edited"}
        result = parse_c94(save_image(payload))
        self.assertTrue(values(result)[100]["value"])
        self.assertEqual(result.description, "Edited")
        self.assertIn("settings", open_image(result.to_bytes()))
        with self.assertRaises(ValueError):
            save_image({"original": "not base64"})


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class QuietHandler(EditorHandler):
            def log_message(self, *args):
                pass
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, response.read(), dict(response.getheaders())
        finally:
            connection.close()

    def test_static_assets(self):
        for path in ("/", "/editor.js", "/editor.css"):
            status, body, headers = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(self.request("GET", "/../c94file/definitions.json")[0], 404)

    def test_upload_and_download(self):
        image = fixture()
        status, body, _ = self.request("POST", "/api/open", image.to_bytes())
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["description"], "test")
        payload = json.dumps({"original": base64.b64encode(image.to_bytes()).decode(),
                              "changes": {"R100": True}})
        status, body, _ = self.request("POST", "/api/save", payload)
        self.assertEqual(status, 200)
        self.assertTrue(values(parse_c94(body))[100]["value"])

    def test_bad_input_and_cross_origin(self):
        self.assertEqual(self.request("POST", "/api/open", b"garbage")[0], 400)
        self.assertEqual(self.request("POST", "/api/save", b"not json")[0], 400)
        self.assertEqual(self.request("POST", "/api/save", b"[]")[0], 400)
        self.assertEqual(self.request("POST", "/api/save", b"{}", {"Origin": "https://other.example"})[0], 403)
        self.assertEqual(self.request("GET", "/", headers={"Host": "other.example"})[0], 403)


if __name__ == "__main__":
    unittest.main()
