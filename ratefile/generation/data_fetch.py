from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

NANPA_ZIP_URL = (
    "https://reports.nanpa.com/public/CoCodeAssignment_Utilized_AllStates_Public.zip"
)
CNAC_ZIP_URL = "https://www.cnac.ca/data/COCodeStatus_ALL.zip"

NANPA_EXTRACTED_NAME = "CoCodeAssignment_Utilized_AllStates_Public.txt"
CNAC_EXTRACTED_NAME = "COCodeStatus_ALL.csv"


def ensure_data_dir(path: str | Path) -> Path:
    data_dir = Path(path)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _download_to_temp(url: str) -> Path:
    fd, temp_name = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    temp_path = Path(temp_name)
    with urlopen(url) as response, temp_path.open("wb") as output:
        shutil.copyfileobj(response, output)
    return temp_path


def _extract_single_member(zip_path: Path, member_name: str, output_path: Path) -> Path:
    with zipfile.ZipFile(zip_path) as archive:
        member = next(
            (name for name in archive.namelist() if Path(name).name == member_name),
            None,
        )
        if member is None:
            raise ValueError(f"{member_name} not found in archive {zip_path}")
        with archive.open(member) as source, output_path.open("wb") as destination:
            shutil.copyfileobj(source, destination)
    return output_path


def ensure_extracted_file(data_dir: str | Path, url: str, extracted_name: str) -> Path:
    # The repository only keeps extracted datasets under ratefile/data/. ZIPs are
    # downloaded to a temporary file and removed immediately after extraction.
    output_path = ensure_data_dir(data_dir) / extracted_name
    if output_path.exists():
        return output_path
    zip_path = _download_to_temp(url)
    try:
        return _extract_single_member(zip_path, extracted_name, output_path)
    finally:
        zip_path.unlink(missing_ok=True)


def ensure_nanpa_dataset(data_dir: str | Path) -> Path:
    return ensure_extracted_file(data_dir, NANPA_ZIP_URL, NANPA_EXTRACTED_NAME)


def ensure_cnac_dataset(data_dir: str | Path) -> Path:
    return ensure_extracted_file(data_dir, CNAC_ZIP_URL, CNAC_EXTRACTED_NAME)
