"""Parse Elcotel R94 files into typed Python models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .codec import decompress
from .constants import HEADER_SIZE, SURCHARGE_OFFSET


class RateFileHeader(BaseModel):
    """Store the fixed header fields extracted from an R94 file."""

    is_ratefile: bool
    filesize: int
    description: str
    local_band_count: int
    intra_lata_band_count: int
    inter_lata_band_count: int
    fcc_band_count: int
    corridor_band_count: int
    canadian_band_count: int
    extended_band_count: int
    misc_band_count: int
    home_npa: str
    home_nxx: str


class Surcharge(BaseModel):
    """Store one category row from the surcharge block."""

    band_category: int
    coin: int
    paof_bell: int
    paof_comm: int
    paof_collect: int
    paof_addtnl: int
    chip_card: int
    spare_1: int
    spare_2: int


class NxxEntry(BaseModel):
    """Store the enabled/disabled state for one NXX in a bitmap table."""

    nxx: int
    enabled: bool


class NxxTable(BaseModel):
    """Store one parsed 103-byte NXX bitmap table."""

    npa: Optional[int]
    price_band: int
    dial_pattern: int
    flags: int
    nxx_entries: List[NxxEntry] = Field(default_factory=list)


class NpaGroup(BaseModel):
    """Store one parsed NPA group-header row."""

    npa: int
    nxx_table_count: int
    unlisted_price_band: int
    unlisted_dial_pattern: int
    flags: int


class NpaPriceEntry(BaseModel):
    """Store one byte from the default 800-entry NPA table."""

    npa: int
    raw_value: int
    kind: str
    price_band: Optional[int] = None


class PriceBands(BaseModel):
    """Store one parsed price-band row plus its inferred category metadata."""

    band_index: int
    price_code: int
    group_sequence: int
    init_rate: int
    init_time: int
    addtnl_rate: int
    addtnl_time: int


class PricePlan(BaseModel):
    """Store the parsed band counts, offsets, and price-band rows."""

    npa_group_count: int
    npa_group_offset: int
    nxx_table_count: int
    nxx_table_offset: int
    price_band_count: int
    price_band_offset: int
    local_band_count: int
    intralata_band_count: int
    interlata_band_count: int
    interstate_band_count: int
    corridor_band_count: int
    canadian_band_count: int
    extended_band_count: int
    misc_band_count: int
    price_bands: List[PriceBands] = Field(default_factory=list)


class RateFile(BaseModel):
    """Represent the full parsed contents of one Elcotel R94 file."""

    header: RateFileHeader
    surcharges: List[Surcharge] = Field(default_factory=list)
    price_plan: PricePlan
    npa_prices: List[NpaPriceEntry] = Field(default_factory=list)
    npa_groups: List[NpaGroup] = Field(default_factory=list)
    nxx_tables: List[NxxTable] = Field(default_factory=list)


def parse_surcharges(data: bytes) -> List[Surcharge]:
    """Parse the eight-column surcharge block from the decompressed body."""
    surcharges = []
    for index in range(8):
        surcharges.append(
            Surcharge(
                band_category=index,
                coin=data[SURCHARGE_OFFSET + index],
                paof_bell=data[SURCHARGE_OFFSET + 8 + index],
                paof_comm=data[SURCHARGE_OFFSET + 16 + index],
                paof_collect=data[SURCHARGE_OFFSET + 24 + index],
                paof_addtnl=data[SURCHARGE_OFFSET + 32 + index],
                chip_card=data[SURCHARGE_OFFSET + 40 + index],
                spare_1=data[SURCHARGE_OFFSET + 48 + index],
                spare_2=data[SURCHARGE_OFFSET + 56 + index],
            )
        )
    return surcharges


def interpret_npa_price(raw_value: int) -> tuple[str, Optional[int]]:
    """Return a light interpretation for a raw default-NPA token."""
    if raw_value == 0:
        return "restricted", None
    if 1 <= raw_value <= 252:
        return "price_band", raw_value
    if raw_value == 253:
        return "unlimited", None
    if raw_value in (254, 255):
        return "nxx_specific", None
    return "unknown", None


def parse_npa_prices(data: bytes) -> List[NpaPriceEntry]:
    """Parse the default 800-entry NPA table for NPAs 200 through 999."""
    entries = []
    for offset in range(800):
        npa = 200 + offset
        raw_value = data[offset]
        kind, price_band = interpret_npa_price(raw_value)
        entries.append(
            NpaPriceEntry(
                npa=npa,
                raw_value=raw_value,
                kind=kind,
                price_band=price_band,
            )
        )
    return entries


def determine_price_code(index: int, offsets: dict[str, int]) -> int:
    """Infer the band category code from its position in the ordered band list."""
    if index < offsets["intralata"]:
        return 0
    if index < offsets["interlata"]:
        return 1
    if index < offsets["interstate"]:
        return 2
    if index < offsets["corridor"]:
        return 3
    if index < offsets["canadian"]:
        return 4
    if index < offsets["extended"]:
        return 5
    if index < offsets["misc"]:
        return 6
    return 7


def parse_price_plan(data: bytes) -> PricePlan:
    """Parse the price-plan metadata block and ordered band rows."""
    price_plan = PricePlan(
        npa_group_count=data[887],
        npa_group_offset=data[876] * 256 + data[875],
        nxx_table_count=data[889],
        nxx_table_offset=data[880] * 256 + data[879],
        price_band_count=data[888],
        price_band_offset=data[878] * 256 + data[877] + 1,
        local_band_count=data[864],
        intralata_band_count=data[865],
        interlata_band_count=data[866],
        interstate_band_count=data[867],
        corridor_band_count=data[868],
        canadian_band_count=data[869],
        extended_band_count=data[870],
        misc_band_count=data[871],
    )
    offsets = {
        "local": 0,
        "intralata": price_plan.local_band_count,
        "interlata": price_plan.local_band_count + price_plan.intralata_band_count,
        "interstate": price_plan.local_band_count
        + price_plan.intralata_band_count
        + price_plan.interlata_band_count,
        "corridor": price_plan.local_band_count
        + price_plan.intralata_band_count
        + price_plan.interlata_band_count
        + price_plan.interstate_band_count,
        "canadian": price_plan.local_band_count
        + price_plan.intralata_band_count
        + price_plan.interlata_band_count
        + price_plan.interstate_band_count
        + price_plan.corridor_band_count,
        "extended": price_plan.local_band_count
        + price_plan.intralata_band_count
        + price_plan.interlata_band_count
        + price_plan.interstate_band_count
        + price_plan.corridor_band_count
        + price_plan.canadian_band_count,
        "misc": price_plan.local_band_count
        + price_plan.intralata_band_count
        + price_plan.interlata_band_count
        + price_plan.interstate_band_count
        + price_plan.corridor_band_count
        + price_plan.canadian_band_count
        + price_plan.extended_band_count,
    }
    band_offsets = {code: 0 for code in range(8)}
    cursor = price_plan.price_band_offset - 1
    price_bands = []
    for index in range(price_plan.price_band_count):
        price_code = determine_price_code(index, offsets)
        band_offsets[price_code] += 1
        price_bands.append(
            PriceBands(
                band_index=index + 1,
                price_code=price_code,
                group_sequence=band_offsets[price_code],
                init_rate=data[cursor],
                init_time=data[cursor + 1],
                addtnl_rate=data[cursor + 2],
                addtnl_time=data[cursor + 3],
            )
        )
        cursor += 4
    price_plan.price_bands = price_bands
    return price_plan


def parse_npa_groups(data: bytes, group_count: int) -> List[NpaGroup]:
    """Parse the repeated six-byte NPA group-header rows."""
    cursor = 890
    groups = []
    for _ in range(group_count):
        groups.append(
            NpaGroup(
                npa=data[cursor + 1] * 256 + data[cursor],
                nxx_table_count=data[cursor + 2],
                unlisted_price_band=data[cursor + 3],
                unlisted_dial_pattern=data[cursor + 4],
                flags=data[cursor + 5],
            )
        )
        cursor += 6
    return groups


def determine_npa(index: int, npa_offset_map: dict[int, list[list[int]]]) -> int | None:
    """Return the owning NPA for one NXX bitmap-table index."""
    for npa, offsets in npa_offset_map.items():
        for offset in offsets:
            if offset[0] <= index < offset[1]:
                return npa
    return None


def parse_nxx_tables(
    data: bytes, table_count: int, table_offset: int, npa_groups: List[NpaGroup]
) -> List[NxxTable]:
    """Parse the ordered list of 103-byte NXX bitmap tables."""
    npa_offset_map: dict[int, list[list[int]]] = {}
    offset = 0
    for group in npa_groups:
        npa_offset_map.setdefault(group.npa, []).append(
            [offset, offset + group.nxx_table_count]
        )
        offset += group.nxx_table_count

    cursor = table_offset
    nxx_tables = []
    for index in range(table_count):
        nxx_data_raw = data[cursor + 3 : cursor + 103]
        nxx_entries = [
            NxxEntry(
                nxx=200 + nxx_index,
                enabled=bool((nxx_data_raw[nxx_index // 8] >> (nxx_index % 8)) & 1),
            )
            for nxx_index in range(800)
        ]
        nxx_tables.append(
            NxxTable(
                npa=determine_npa(index, npa_offset_map),
                price_band=data[cursor],
                dial_pattern=data[cursor + 1],
                flags=data[cursor + 2],
                nxx_entries=nxx_entries,
            )
        )
        cursor += 103
    return nxx_tables


def read_ratefile(file_path: str) -> RateFile:
    """Parse one R94 file from disk and return its structured contents."""
    with open(file_path, "rb") as handle:
        data = handle.read()

    if len(data) < HEADER_SIZE:
        raise ValueError(
            f"File is too short to contain an R94 header: {len(data)}B found, {HEADER_SIZE}B required."
        )

    description_length = min(data[209], HEADER_SIZE - 210)
    header = RateFileHeader(
        is_ratefile=data[24] == 1,
        filesize=int.from_bytes(data[1:5], byteorder="little"),
        description=data[210 : 210 + description_length]
        .decode("ascii", errors="replace")
        .rstrip("\x00"),
        local_band_count=data[152],
        intra_lata_band_count=data[153],
        inter_lata_band_count=data[154],
        fcc_band_count=data[155],
        corridor_band_count=data[156],
        canadian_band_count=data[157],
        extended_band_count=data[158],
        misc_band_count=data[159],
        home_npa=data[18:21].decode(errors="ignore").rstrip("\x00"),
        home_nxx=data[21:24].decode(errors="ignore").rstrip("\x00"),
    )

    decompressed_data = decompress(data[HEADER_SIZE:])
    if not decompressed_data:
        raise ValueError("Decompressed data is empty or invalid.")
    if len(decompressed_data) != header.filesize:
        raise ValueError(
            f"Decompressed data size {len(decompressed_data)}B does not match expected size {header.filesize}B."
        )

    price_plan = parse_price_plan(decompressed_data)
    npa_groups = parse_npa_groups(decompressed_data, price_plan.npa_group_count)
    return RateFile(
        header=header,
        surcharges=parse_surcharges(decompressed_data),
        price_plan=price_plan,
        npa_prices=parse_npa_prices(decompressed_data),
        npa_groups=npa_groups,
        nxx_tables=parse_nxx_tables(
            decompressed_data,
            price_plan.nxx_table_count,
            price_plan.nxx_table_offset,
            npa_groups,
        ),
    )
