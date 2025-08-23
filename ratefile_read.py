# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pydantic",
#   "click",
# ]
# ///

from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import sys

ENUM_BAND_CATEGORIES = {
    0: '!',
    1: 'Local',
    2: 'IntraLATA',
    3: 'InterLATA',
    4: 'FCC',
    5: 'Corridor',
    6: 'Canadian',
    7: 'Extended',
    8: 'Misc',
}


class RateFileHeader(BaseModel):
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
    nxx: int
    enabled: bool


class NxxTable(BaseModel):
    npa: int
    price_band: int
    dial_pattern: int
    flags: int
    nxx_entries: List[NxxEntry] = Field(default_factory=list)


class NpaGroup(BaseModel):
    npa: int
    nxx_table_count: int
    unlisted_price_band: int
    unlisted_dial_pattern: int
    flags: int


class PriceBands(BaseModel):
    band_index: int
    price_code: int
    group_sequence: int
    init_rate: int
    init_time: int
    addtnl_rate: int
    addtnl_time: int


class PricePlan(BaseModel):
    # NPA
    npa_group_count: int
    npa_group_offset: int
    # NXX
    nxx_table_count: int
    nxx_table_offset: int
    # Price bands
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
    # Price bands
    price_bands: List[PriceBands] = Field(default_factory=list)


class RateFile(BaseModel):
    header: RateFileHeader
    surcharges: List[Surcharge] = Field(default_factory=list)
    price_plan: PricePlan
    npa_groups: List[NpaGroup] = Field(default_factory=list)
    nxx_tables: List[NxxTable] = Field(default_factory=list)


def decompress(raw_content_compressed: bytes):
    i = 0
    decompressed = bytearray()
    while i < len(raw_content_compressed):
        byte = raw_content_compressed[i]
        if byte == 0:
            i += 1
            zeros_count = raw_content_compressed[i]
            decompressed.extend(b'\x00' * zeros_count)
        else:
            decompressed.append(byte)
        i += 1

    return decompressed


def parse_surcharges(data: bytes) -> List[Surcharge]:
    """Parse surcharges from the decompressed data."""
    surcharges = []
    INIT_OFFSET = 800
    for i in range(0, 8):
        surcharges.append(
            Surcharge(
                band_category=i,
                coin=data[INIT_OFFSET + i],
                paof_bell=data[INIT_OFFSET + 8 + i],
                paof_comm=data[INIT_OFFSET + 16 + i],
                paof_collect=data[INIT_OFFSET + 24 + i],
                paof_addtnl=data[INIT_OFFSET + 32 + i],
                chip_card=data[INIT_OFFSET + 40 + i],
                spare_1=data[INIT_OFFSET + 48 + i],
                spare_2=data[INIT_OFFSET + 56 + i],
            )
        )
    return surcharges


def determine_price_code(index, offsets):
    if index < offsets['intralata']:
        return 0
    elif index < offsets['interlata']:
        return 1
    elif index < offsets['interstate']:
        return 2
    elif index < offsets['corridor']:
        return 3
    elif index < offsets['canadian']:
        return 4
    elif index < offsets['extended']:
        return 5
    elif index < offsets['misc']:
        return 6
    else:
        return 7


def parse_price_plan(data: bytes) -> PricePlan:
    """Parse the price plan from the decompressed data."""
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

    # Since we don't the information which Price Band is what group, we have to manually calculate it
    offsets = {
        'local': 0,
        'intralata': price_plan.local_band_count,
        'interlata': price_plan.local_band_count + price_plan.intralata_band_count,
        'interstate': price_plan.local_band_count + price_plan.intralata_band_count + price_plan.interlata_band_count,
        'corridor': price_plan.local_band_count + price_plan.intralata_band_count + price_plan.interlata_band_count + price_plan.interstate_band_count,
        'canadian': price_plan.local_band_count + price_plan.intralata_band_count + price_plan.interlata_band_count + price_plan.interstate_band_count + price_plan.corridor_band_count,
        'extended': price_plan.local_band_count + price_plan.intralata_band_count + price_plan.interlata_band_count + price_plan.interstate_band_count + price_plan.corridor_band_count + price_plan.canadian_band_count,
        'misc': price_plan.local_band_count + price_plan.intralata_band_count + price_plan.interlata_band_count + price_plan.interstate_band_count + price_plan.corridor_band_count + price_plan.canadian_band_count + price_plan.extended_band_count,
    }
    band_offsets = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
    }
    # The rate data block starts at the offset specified in the header.
    price_bands = []
    cursor = price_plan.price_band_offset - 1
    for i in range(0, price_plan.price_band_count):
        price_code = determine_price_code(i, offsets)
        band_offsets[price_code] += 1
        price_bands.append(
            PriceBands(
                band_index=i + 1,
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
    """Parse NPA group headers from the decompressed R94 data (starting at offset 891)."""
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


def determine_npa(index, npa_offset_map):
    """Determine the NPA for a given index using the NPA offset map."""
    for npa, offsets in npa_offset_map.items():
        for offset in offsets:
            if offset[0] <= index < offset[1]:
                return npa
    return None


def parse_nxx_tables(data: bytes, table_count: int, table_offset: int, npa_groups: List[NpaGroup]) -> List[NxxTable]:
    """Parse NXX tables from the decompressed R94 data."""
    # Create an offset map for the NPA groups so we can assign the NPA to the NXX tables
    # NPA: [[low, high], [low, high], ...]
    npa_offset_map = {}
    offset = 0
    for group in npa_groups:
        if group.npa not in npa_offset_map:
            npa_offset_map[group.npa] = []
        npa_offset_map[group.npa].append(
            [offset, offset + group.nxx_table_count])
        offset += group.nxx_table_count
    cursor = table_offset
    nxx_tables = []
    for i in range(table_count):
        nxx_data_raw = data[cursor + 3:cursor + 103]
        nxx_entries = [
            NxxEntry(nxx=(200 + j), enabled=bool((nxx_data_raw[j // 8] >> (j % 8)) & 1)) for j in range(800)
        ]
        nxx_table = NxxTable(
            npa=determine_npa(i, npa_offset_map),
            price_band=data[cursor],
            dial_pattern=data[cursor + 1],
            flags=data[cursor + 2],
            nxx_entries=nxx_entries,
        )
        nxx_tables.append(nxx_table)
        cursor += 103
    return nxx_tables


def read_ratefile(file_path: str) -> RateFile:
    """Read a rate file and return a RateFile object."""
    with open(file_path, 'rb') as f:
        data = f.read()

    # Read the header
    header = RateFileHeader(
        is_ratefile=data[24] == 1,
        filesize=int.from_bytes(data[1:5], byteorder='little'),
        description=data[210:210 + data[209]
                         ].decode('ascii', errors='replace'),
        local_band_count=data[152],
        intra_lata_band_count=data[153],
        inter_lata_band_count=data[154],
        fcc_band_count=data[155],
        corridor_band_count=data[156],
        canadian_band_count=data[157],
        extended_band_count=data[158],
        misc_band_count=data[159],
        home_npa=data[18:21].decode(errors='ignore'),
        home_nxx=data[21:24].decode(errors='ignore'),
    )

    # Uncompress the data
    decompressed_data = decompress(data[268:])

    # Check if the decompressed data is valid
    if not decompressed_data:
        raise ValueError("Decompressed data is empty or invalid.")
    if not len(decompressed_data) == header.filesize:
        raise ValueError(
            f"Decompressed data size {len(decompressed_data)}B does not match expected size {header.filesize}B.")

    # Parse the surcharges
    surcharges = parse_surcharges(decompressed_data)

    # Read the price bands
    price_plan = parse_price_plan(decompressed_data)

    # Read intra-state NPA information
    npa_groups = parse_npa_groups(
        decompressed_data, price_plan.npa_group_count)

    # And the NXX tables
    nxx_tables = parse_nxx_tables(
        decompressed_data, price_plan.nxx_table_count, price_plan.nxx_table_offset, npa_groups)

    return RateFile(header=header, surcharges=surcharges, price_plan=price_plan, npa_groups=npa_groups, nxx_tables=nxx_tables)


@click.command()
@click.option(
    '--file', '-f', default='elcotel-playground/stock.R94', help='Path to the rate file'
)
def main(file):
    try:
        parse = read_ratefile(file)
    except FileNotFoundError:
        print(f'File not found: {file}')
        sys.exit(1)
    print(parse)


if __name__ == '__main__':
    main()
