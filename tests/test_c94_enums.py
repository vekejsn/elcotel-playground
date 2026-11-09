from __future__ import annotations

import unittest

from c94file import C94File, decode_registers
from c94file.editor import apply_changes, editor_settings


def image(tag=b"LP050400"):
    header = bytearray(168)
    header[4:8] = (4096).to_bytes(4, "little")
    header[8:16] = tag
    return C94File(raw_header=bytes(header), body=bytes(4096))


def rows(model):
    return {row["register_num"]: row for row in decode_registers(model)}


class EnumTests(unittest.TestCase):
    def test_confirmed_choices_are_firmware_scoped(self):
        current = rows(image())
        older = rows(image(b"LP050303"))
        other = rows(image(b"KX010100"))
        for reg in (*range(424, 431), 422, 423, 453):
            self.assertIn("value_labels", current[reg]["parameter"])
            self.assertNotIn("value_labels", older[reg]["parameter"])
            self.assertNotIn("value_labels", other[reg]["parameter"])
        self.assertNotIn("value_labels", current[431]["parameter"])
        self.assertIn("IntraLATA", current[422]["parameter"]["value_labels"]["2"])
        self.assertIn("band", current[423]["parameter"]["value_labels"]["1"])

    def test_numeric_enum_roundtrip_and_ui_choices(self):
        result = apply_changes(image(), {"R453": 1, "R424": 2, "R422": 3})
        decoded = rows(result)
        self.assertIn("Hybrid", decoded[453]["display_value"])
        self.assertIn("anti-fraud OFF", decoded[424]["display_value"])
        self.assertEqual(decoded[422]["display_value"], "InterLATA")
        settings = {s["id"]: s for s in editor_settings(result)}
        self.assertEqual(settings["R453"]["kind"], "choice")
        self.assertEqual(settings["R424"]["kind"], "choice")
        self.assertEqual(settings["R431"]["kind"], "number")
        with self.assertRaises(ValueError):
            apply_changes(image(), {"R453": 3})

    def test_boolean_coin_selector_keeps_its_storage_type(self):
        result = apply_changes(image(), {"R110": True})
        self.assertIn("Mechanical", rows(result)[110]["display_value"])
        setting = next(s for s in editor_settings(result) if s["id"] == "R110")
        self.assertEqual(setting["kind"], "boolean")
        self.assertIn("Electronic", setting["boolean_labels"]["0"])
        self.assertEqual(result.body[0x241], 4)

    def test_partial_volume_information_does_not_invent_gain_labels(self):
        decoded = rows(image())[501]
        self.assertIn("Lowest", decoded["display_value"])
        self.assertNotIn("value_labels", decoded["parameter"])
        self.assertEqual(set(decoded["parameter"]["known_value_labels"]), {"0"})
        result = apply_changes(image(), {"R501": 3})
        self.assertEqual(rows(result)[501]["value"], 3)
        self.assertNotIn("display_value", rows(result)[501])

    def test_newly_confirmed_units(self):
        decoded = rows(image())
        self.assertEqual(decoded[455]["parameter"]["units"], "seconds")
        self.assertEqual(decoded[478]["parameter"]["units"], "seconds")
        self.assertIn("five-second", " ".join(decoded[478]["parameter"]["notes"]))
        self.assertEqual(decoded[480]["parameter"]["units"], "minutes")

    def test_kx_branch_choices_and_default_antifraud(self):
        for tag in (b"KX010200", b"KX010300"):
            with self.subTest(tag=tag):
                model = apply_changes(image(tag), {"R431": 2, "R453": 1, "R422": 3, "R473": 20})
                decoded = rows(model)
                self.assertIn("anti-fraud OFF", decoded[431]["display_value"])
                self.assertIn("Hybrid", decoded[453]["display_value"])
                self.assertEqual(decoded[422]["display_value"], "InterLATA")
                self.assertIn("20 characters", decoded[473]["display_value"])
                settings = {s["id"]: s for s in editor_settings(model)}
                self.assertEqual(settings["R431"]["kind"], "choice")
                self.assertEqual(settings["R453"]["kind"], "choice")
                for reg in range(424, 432):
                    self.assertEqual(set(decoded[reg]["parameter"]["value_labels"]), {"0", "1", "2"})
                self.assertIn("omits coin-line", " ".join(decoded[453]["parameter"]["notes"]))
                self.assertNotIn("value_labels", decoded[110]["parameter"])
                self.assertNotIn("value_labels", decoded[501]["parameter"])
                self.assertNotIn("known_value_labels", decoded[501]["parameter"])
                self.assertEqual(settings["R501"]["kind"], "number")
                with self.assertRaises(ValueError):
                    apply_changes(image(tag), {"R431": 3})

    def test_earlier_kx_branches_do_not_inherit_unverified_choices(self):
        for tag in (b"KX010000", b"KX010100"):
            decoded = rows(image(tag))
            for reg in (422, 423, *range(424, 432), 453, 473, 501):
                if reg in decoded:
                    self.assertNotIn("value_labels", decoded[reg]["parameter"])


if __name__ == "__main__":
    unittest.main()
