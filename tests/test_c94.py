from __future__ import annotations

import tempfile
import os
import unittest
from pathlib import Path

from c94file import C94File, decode_registers, parse_c94, read_c94, write_c94
from c94file.parser import BODY_SIZE, HEADER_SIZE, _decode, map_name
from elcotel.codec import compress


def fixture(tag=b"LP050400"):
    header = bytearray(HEADER_SIZE)
    header[:4] = bytes.fromhex("00200300")
    header[4:8] = BODY_SIZE.to_bytes(4, "little")
    header[8:16] = tag
    header[49] = 5  # NOT the description offset.
    header[109:114] = b"\x04test"
    body = bytearray(BODY_SIZE)
    body[:58] = b"RATES FOR PCM 5 (C) COPYRIGHT BY ELCOTEL, INC. 1986 - 1989"
    return C94File(raw_header=bytes(header), body=bytes(body))


class C94Tests(unittest.TestCase):
    def test_lossless_json_including_non_ascii_bytes(self):
        image = fixture()
        body = bytearray(image.body)
        body[-4:] = b"\xff\x80\x00\x01"
        image.body = bytes(body)
        decoded = C94File.model_validate_json(image.model_dump_json())
        self.assertEqual(decoded, image)
        self.assertEqual(parse_c94(image.to_bytes()), image)
        self.assertEqual(image.description, "test")
        self.assertEqual(image.version, "05.04.00")

    def test_original_maps_not_site_specific_offsets(self):
        image = fixture()
        body = bytearray(image.body)
        body[0xCC:0xD5] = bytes([4, 1, 2, 3, 4, 0, 0, 0, 0])
        station = bytes([4, 1, 2, 3, 4])
        body[0xD5:0xDB] = station + bytes([sum(station)])
        body[0xDB:0xE5] = b"\x08password\0"
        body[0xE5:0xF0] = bytes([10, 2, 1, 2, 5, 5, 5, 0, 1, 9, 9])
        body[0x240] = 0b10000001
        image.body = bytes(body)
        rows = {r["register_num"]: r for r in decode_registers(image)}
        self.assertEqual(len(rows), 358)
        self.assertEqual(rows[400]["offset"], 0xCC)
        self.assertEqual(rows[400]["value"], "1234")
        self.assertEqual(rows[402]["value"], "1234")
        self.assertTrue(rows[402]["checksum_valid"])
        self.assertEqual(rows[403]["value"], "password")
        self.assertEqual(rows[404]["value"], "2125550199")
        self.assertTrue(rows[100]["value"])
        self.assertFalse(rows[101]["value"])
        self.assertTrue(rows[107]["value"])
        self.assertEqual(rows[107]["raw_hex"], "81")

    def test_packed_station_ids(self):
        # 2125550100: first digit 2 is biased to 0, then high bit is set.
        slot = bytes.fromhex("8125550100")
        image = fixture()
        body = bytearray(image.body)
        body[0xD5:0xDB] = slot + bytes([sum(slot) % 256])
        image.body = bytes(body)
        row = next(r for r in decode_registers(image) if r["register_num"] == 402)
        self.assertEqual(row["value"], "2125550100")
        self.assertTrue(row["checksum_valid"])

    def test_token_types(self):
        cases = [
            (1, 1, b"\xfe", 254),
            (2, 4, b"\x03\x01\x0b\x0c", "1*#"),
            (3, 1, b"\x05", 0.25),
            (4, 2, b"\x2c\x01", 15),
            (5, 2, b"\x2c\x01", 300),
            (6, 26, bytes(range(26)), list(range(26))),
            (7, 4, b"\x03abc", "abc"),
            (8, 8, b"\x80", True),
            (9, 1, b"\xff", 255),
            (10, 2, b"\x1e\x09", "09:30"),
            (11, 100, bytes(range(100)), list(range(100))),
        ]
        for token, size, slot, expected in cases:
            with self.subTest(token=token):
                self.assertEqual(_decode(slot, {"token": token, "size": size, "register_num": 300}), expected)
        self.assertEqual(_decode(b"\x48", {"token": 1, "size": 1, "register_num": 437}), 3)

    def test_all_firmware_maps(self):
        tags = {
            b"LP050300": ("LP050300", 249),
            b"LP050301": ("LP050301", 271),
            b"LP050302": ("LP050302", 279),
            b"LP050303": ("LP050303", 326),
            b"LP050400": ("LP050400", 358),
            b"KX010000": ("KX010000", 214),
            b"KX010100": ("KX010100", 283),
            b"KX010200": ("KX010200", 285),
            b"KX010300": ("KX010300", 331),
        }
        for tag, (name, count) in tags.items():
            with self.subTest(tag=tag):
                image = fixture(tag)
                self.assertEqual(map_name(image), name)
                rows = decode_registers(image)
                self.assertEqual(len(rows), count)
                self.assertFalse([r for r in rows if "error" in r])
        with self.assertRaises(ValueError):
            map_name(fixture(b"LP050900"))

    def test_invalid_register_is_reported_not_discarded(self):
        image = fixture()
        body = bytearray(image.body)
        body[0xCC] = 255
        image.body = bytes(body)
        row = next(r for r in decode_registers(image) if r["register_num"] == 400)
        self.assertIn("error", row)
        self.assertTrue(row["raw_hex"].startswith("ff"))
        self.assertEqual(parse_c94(image.to_bytes()), image)

    def test_reject_malformed_images(self):
        raw = fixture().to_bytes()
        header = raw[:HEADER_SIZE]
        for bad in (b"", header, raw + b"\0", raw + b"\0\0", raw + b"\x01",
                    header + compress(bytes(BODY_SIZE - 1)),
                    header[:4] + b"\0\0\0\0" + raw[8:]):
            with self.subTest(length=len(bad)), self.assertRaises(ValueError):
                parse_c94(bad)

    def test_file_roundtrip(self):
        image = fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.C94"
            write_c94(image, path)
            self.assertEqual(read_c94(path), image)

    def test_optional_legacy_corpus(self):
        directory = os.environ.get("C94_TEST_CORPUS")
        if not directory:
            self.skipTest("Set C94_TEST_CORPUS to verify an external corpus")
        root = Path(directory)
        paths = [p for p in root.rglob("*") if p.suffix.lower() == ".c94"]
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                image = read_c94(path)
                self.assertEqual(image.to_bytes(), path.read_bytes())
                self.assertFalse([r for r in decode_registers(image) if "error" in r])


if __name__ == "__main__":
    unittest.main()
