from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ratefile.codec import decompress
from ratefile.bridge import ratefile_to_writer_payload
from ratefile.parser import read_ratefile
from ratefile.writer import write_ratefile_payload


class BridgeRoundtripTests(unittest.TestCase):
    def test_writer_payload_rebuilds_same_decompressed_body(self) -> None:
        source = Path("ratefiles/208209BN.R94")
        parsed = read_ratefile(str(source))
        payload = ratefile_to_writer_payload(parsed)

        with tempfile.TemporaryDirectory() as temp_dir:
            rebuilt = Path(temp_dir) / "rebuilt.R94"
            write_ratefile_payload(payload["header"], payload, rebuilt)
            original_decompressed = decompress(source.read_bytes()[268:])
            rebuilt_decompressed = decompress(rebuilt.read_bytes()[268:])

        self.assertEqual(rebuilt_decompressed, original_decompressed)
