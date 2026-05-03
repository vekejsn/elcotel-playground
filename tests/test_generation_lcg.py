from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from ratefile.generation import lcg


class LocalCallingGuideNormalizationTests(unittest.TestCase):
    def test_lookup_prefix_normalizes_first_prefixdata_node(self) -> None:
        xml = ET.fromstring(
            """
            <root>
              <prefixdata>
                <exch>SNJS NORTH</exch>
                <lata>722</lata>
                <lir></lir>
                <region>CA</region>
              </prefixdata>
            </root>
            """
        )
        with patch.object(lcg, "_fetch_xml", return_value=xml):
            payload = lcg.lookup_prefix(408, 535, "/tmp/opencode-test-cache", 0)
        self.assertEqual(payload["exch"], "SNJS NORTH")
        self.assertEqual(payload["lata"], "722")
        self.assertEqual(payload["state"], "CA")

    def test_fetch_ratecenters_and_local_prefixes_normalize_lists(self) -> None:
        rc_xml = ET.fromstring(
            """
            <root>
              <rcdata><exch>ONE</exch><see-exch>None</see-exch></rcdata>
              <rcdata><exch>TWO</exch><see-exch>ALT</see-exch></rcdata>
            </root>
            """
        )
        local_xml = ET.fromstring(
            """
            <root>
              <lca-data>
                <prefix><npa>408</npa><nxx>535</nxx></prefix>
                <prefix><npa>669</npa><nxx>201</nxx></prefix>
              </lca-data>
            </root>
            """
        )
        with patch.object(lcg, "_fetch_xml", side_effect=[rc_xml, local_xml]):
            rc_payload = lcg.fetch_ratecenters_by_lata(
                "722", "/tmp/opencode-test-cache", 0
            )
            local_payload = lcg.fetch_local_prefixes(
                "ONE", "/tmp/opencode-test-cache", 0
            )
        self.assertEqual(rc_payload[0]["exch"], "ONE")
        self.assertEqual(rc_payload[1]["see_exch"], "ALT")
        self.assertEqual(local_payload[0], {"npa": "408", "nxx": "535"})
        self.assertEqual(local_payload[1], {"npa": "669", "nxx": "201"})
