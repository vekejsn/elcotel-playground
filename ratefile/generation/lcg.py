from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .cache import get_or_fetch_json

BASE_URL = "https://localcallingguide.com"


def _fetch_xml(endpoint: str, params: dict[str, str]) -> ET.Element:
    request = Request(
        f"{BASE_URL}/{endpoint}?{urlencode(params)}",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ElcotelRatefileGenerator/1.0)",
            "Accept": "application/xml,text/xml,*/*",
        },
    )
    with urlopen(request, timeout=30) as response:
        return ET.fromstring(response.read())


def _text(node: ET.Element, tag: str) -> str:
    child = node.find(tag)
    return (child.text or "").strip() if child is not None and child.text else ""


def lookup_prefix(
    npa: int, nxx: int, cache_dir: str | Path, max_age_days: int
) -> dict[str, str]:
    # Prefix lookups provide the home exchange plus the LATA/LIR metadata that
    # drives the later locality expansion calls.
    def fetch() -> dict[str, str]:
        root = _fetch_xml("xmlprefix.php", {"npa": str(npa), "nxx": str(nxx)})
        nodes = root.findall(".//prefixdata")
        if not nodes:
            raise ValueError(
                f"LocalCallingGuide returned no prefix data for {npa}-{nxx}"
            )
        node = nodes[0]
        return {
            "exch": _text(node, "exch"),
            "lata": _text(node, "lata"),
            "lir": _text(node, "lir"),
            "state": _text(node, "region"),
        }

    return get_or_fetch_json(cache_dir, f"prefix-{npa}-{nxx}.json", max_age_days, fetch)  # type: ignore[return-value]


def fetch_ratecenters_by_lata(
    lata: str, cache_dir: str | Path, max_age_days: int
) -> list[dict[str, str]]:
    # xmlrc.php expands a LATA/LIR to exchange names, which are then resolved into
    # actual NPA-NXX members through xmllocalexch.php.
    def fetch() -> list[dict[str, str]]:
        root = _fetch_xml("xmlrc.php", {"lata": lata})
        return [
            {"exch": _text(node, "exch"), "see_exch": _text(node, "see-exch")}
            for node in root.findall(".//rcdata")
        ]

    return get_or_fetch_json(cache_dir, f"lata-{lata}.json", max_age_days, fetch)  # type: ignore[return-value]


def fetch_ratecenters_by_lir(
    lir: str, cache_dir: str | Path, max_age_days: int
) -> list[dict[str, str]]:
    def fetch() -> list[dict[str, str]]:
        root = _fetch_xml("xmlrc.php", {"lir": lir})
        return [
            {"exch": _text(node, "exch"), "see_exch": _text(node, "see-exch")}
            for node in root.findall(".//rcdata")
        ]

    return get_or_fetch_json(cache_dir, f"lir-{lir}.json", max_age_days, fetch)  # type: ignore[return-value]


def fetch_local_prefixes(
    exchange: str, cache_dir: str | Path, max_age_days: int
) -> list[dict[str, str]]:
    safe_exchange = exchange.replace("/", "_")

    def fetch() -> list[dict[str, str]]:
        root = _fetch_xml("xmllocalexch.php", {"exch": exchange})
        return [
            {"npa": _text(node, "npa"), "nxx": _text(node, "nxx")}
            for node in root.findall(".//prefix")
        ]

    return get_or_fetch_json(
        cache_dir, f"local-{safe_exchange}.json", max_age_days, fetch
    )  # type: ignore[return-value]
