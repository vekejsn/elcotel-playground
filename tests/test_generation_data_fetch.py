from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from ratefile.generation import data_fetch


class DataFetchTests(unittest.TestCase):
    def test_ensure_extracted_file_extracts_and_removes_temp_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "source.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("nested/example.txt", "hello world")

            extracted_dir = temp_path / "data"
            with patch.object(data_fetch, "_download_to_temp", return_value=zip_path):
                output_path = data_fetch.ensure_extracted_file(
                    extracted_dir,
                    "https://example.invalid/source.zip",
                    "example.txt",
                )

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), "hello world")
            self.assertFalse(zip_path.exists())
