from __future__ import annotations

import unittest
from pathlib import Path

from click.testing import CliRunner

from c94_read import main
from c94file import C94File, decode_registers
from c94file.parser import _maps
from c94file.semantics import describe_parameter, disassemble_macro
from tools.build_c94_reference import build_reference


def image(table="LP050400", values=None):
    tags = {"LP050400": b"LP050400", "KX010300": b"KX010300", "KX010100": b"KX010100"}
    header = bytearray(168)
    header[4:8] = (4096).to_bytes(4, "little")
    header[8:16] = tags[table]
    body = bytearray(4096)
    for register, value in (values or {}).items():
        entry = next(r for r in _maps()[table] if r["register_num"] == register)
        offset = int(entry["address"], 16)
        body[offset:offset + len(value)] = value
    return C94File(raw_header=bytes(header), body=bytes(body))


class ParameterTests(unittest.TestCase):
    def test_every_parameter_has_explicit_semantic_status(self):
        statuses = {"documented", "cross-family inference", "unknown", "reserved/proprietary; behavior unknown"}
        for table, entries in _maps().items():
            for entry in entries:
                with self.subTest(table=table, reg=entry["register_num"]):
                    meta = describe_parameter(table, entry)
                    self.assertIn(meta["status"], statuses)
                    self.assertTrue(meta["name"])
                    self.assertNotIn("sources", meta)
                    self.assertTrue(all("source" not in d for d in meta.get("ui_definitions", [])))

    def test_macro_reference_is_model_specific(self):
        lp = {r["register_num"]: r for r in decode_registers(image(values={204: b"\x04"}))}
        kx = {r["register_num"]: r for r in decode_registers(image("KX010300", {204: b"\x03"}))}
        self.assertEqual(lp[204]["macro"]["name"], "Call Home")
        self.assertEqual(kx[204]["macro"]["name"], "Call Home")
        self.assertEqual(lp[204]["parameter"]["call_type"], 4)
        self.assertIn("local", lp[204]["parameter"]["name"])

    def test_user_macro_resolves_to_register(self):
        rows = {r["register_num"]: r for r in decode_registers(image(values={204: b"\x2d"}))}
        self.assertEqual(rows[204]["macro"]["register_num"], 300)
        self.assertTrue(rows[204]["macro"]["available_in_map"])
        self.assertEqual(rows[300]["parameter"]["macro_number"], 45)

    def test_shutdown_block_is_by_call_type_not_macro(self):
        flags = bytearray(100)
        flags[4] = 0x83
        rows = {r["register_num"]: r for r in decode_registers(image(values={468: flags}))}
        options = rows[468]["call_options"][4]
        self.assertEqual(options["register_num"], 204)
        self.assertIn("local", options["name"])
        self.assertTrue(options["restrict_during_interval_1"])
        self.assertTrue(options["restrict_during_interval_2"])
        self.assertEqual(options["unknown_bits_hex"], "80")

    def test_language_is_firmware_specific(self):
        def language(table):
            return next(r for r in decode_registers(image(table, {472: b"\x02"})) if r["register_num"] == 472)
        self.assertEqual(language("KX010300")["display_value"], "French")
        self.assertEqual(language("KX010100")["display_value"], "Unknown language code 2")
        self.assertEqual(language("LP050400")["display_value"], "Unknown language code 2")

    def test_inferences_unknowns_and_editor_conflicts_are_visible(self):
        lp = {r["register_num"]: r for r in decode_registers(image())}
        kx = {r["register_num"]: r for r in decode_registers(image("KX010300"))}
        self.assertEqual(lp[482]["parameter"]["status"], "cross-family inference")
        self.assertEqual(lp[340]["parameter"]["status"], "unknown")
        self.assertEqual(kx[482]["parameter"]["status"], "documented")
        self.assertEqual(set(kx[482]["parameter"]["conflicting_editor_rules"]), {"B", "E"})
        self.assertIn("Smart", lp[453]["parameter"]["value_labels"]["0"])
        self.assertIn("Hybrid", kx[453]["parameter"]["value_labels"]["1"])

    def test_macro_operands_and_padding_are_not_instructions(self):
        result = disassemble_macro([37, 5, 0, 69, 11, 7, 70, 68, 1, 0], "LP")
        self.assertEqual([r["opcode"] for r in result], [37, 69, 70, 68])
        self.assertEqual(result[0]["parameter"], 5)
        self.assertEqual(result[1]["delay_seconds"], 7)
        self.assertEqual(result[2]["byte_offset"], 6)
        self.assertIn("DTMF #", result[3]["parameter_description"])
        self.assertIn("error", disassemble_macro([37], "LP")[0])
        self.assertIn("error", disassemble_macro([69, 11], "LP")[0])
        self.assertEqual(disassemble_macro([255], "LP")[0]["description"], "Unknown opcode")

    def test_reference_is_reproducible(self):
        reference = Path(__file__).resolve().parents[1] / "c94file" / "PARAMETERS.md"
        self.assertEqual(reference.read_text(encoding="utf-8"), build_reference())

    def test_cli_explains_selected_register(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.C94").write_bytes(image().to_bytes())
            result = runner.invoke(main, ["--file", "test.C94", "--register", "437"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Timed call home to management system", result.output)
            self.assertIn("days (stored as hours)", result.output)
            missing = runner.invoke(main, ["--file", "test.C94", "--register", "999"])
            self.assertNotEqual(missing.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
