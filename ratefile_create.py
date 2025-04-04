#!/usr/bin/env python3
"""
This script inverts the ratefile parser. It reads a JSON file (produced by the original parser)
and generates the corresponding binary ratefile (.R94) by rebuilding the header, the decompressed data block,
and then compressing that block using the simple zero-run encoding used in the original.
Usage: python generate_bin.py input.json output.R94
"""

from pathlib import Path
import json
import struct

# Enumerations from the original parser
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

ENUM_RATE_VALS = {
    254: 'Unlim.',
    255: 'Restr.'
}

ENUM_DIAL_PLANS = {
    0: '7 digit',
    1: '1 + 7 digit',
    2: '10 digit (NPA)',
    3: '1 + 10 digit (NPA)',
}

def compress(data: bytes) -> bytes:
    """
    Compresses the decompressed data using a simple zero-run encoding.
    For each zero found, it writes a 0 byte followed by a count of how many zeros in a row.
    This is the inverse of the decompress() function in the original code.
    """
    result = bytearray()
    i = 0
    while i < len(data):
        if data[i] == 0:
            count = 1
            # Count consecutive zeros (max 255 per sequence)
            while i + count < len(data) and data[i+count] == 0 and count < 255:
                count += 1
            result.append(0)
            result.append(count)
            i += count
        else:
            result.append(data[i])
            i += 1
    return bytes(result)

def build_header(header_dict: dict) -> bytearray:
    """
    Constructs the 268-byte header block.
    Only the fields needed by the parser are set (such as filesize, is_ratefile flag, band counts,
    home NPA/NXX, and the description); the remaining bytes are left as zeros.
    """
    header = bytearray(268)
    # The filesize (bytes 1-4) will be updated after the full file is built.
    # Set the is_ratefile flag at offset 24.
    header[24] = 1 if header_dict.get("is_ratefile", False) else 0
    # Set home NPA (offset 18-20) and home NXX (offset 21-23)
    home_npa = header_dict.get("home_npa", "")
    home_nxx = header_dict.get("home_nxx", "")
    header[18:21] = home_npa.encode("ascii", errors="ignore").ljust(3, b'\x00')[:3]
    header[21:24] = home_nxx.encode("ascii", errors="ignore").ljust(3, b'\x00')[:3]
    # Set band counts (offsets 152-159)
    counts_keys = ["local_band_count", "intralata_band_count", "interlata_band_count", "interstate_band_count",
                   "corridor_band_count", "canadian_band_count", "extended_band_count", "misc_band_count"]
    for i, key in enumerate(counts_keys):
        header[152+i] = header_dict.get(key, 0)
    # Write the description at offset 209:
    # The first byte at 209 is the length, followed by the description string.
    description = header_dict.get("description", "")
    description_bytes = description.encode("ascii", errors="replace")
    length = min(len(description_bytes), 255)
    header[209] = length
    header[210:210+length] = description_bytes[:length]
    return header

def build_decompressed(prices: dict, rate_entries: list, nxx_table: list, intrastate_npas: list, surcharges: dict) -> bytearray:
    """
    Reconstructs the decompressed data block from the JSON.
    This block holds fixed fields (such as count values at fixed offsets),
    the rate bands, the NXX table, the intrastate NPA groups, and the surcharges.
    """
    group_count    = prices.get("group_count", 0)
    price_count    = prices.get("price_count", 0)
    nxx_count      = prices.get("nxx_count", 0)
    rate_band_offset = prices.get("rate_band_offset", 0)
    nxx_offset     = prices.get("nxx_offset", 0)
    
    # Determine the minimum size needed based on fixed offsets.
    size_candidates = [
        872,  # Must cover fields up to misc_count (offset 871)
        890 + 6 * group_count,  # Groups start at offset 890 (each group is 6 bytes)
        (rate_band_offset - 1) + 4 * price_count,  # Rate bands block (each 4 bytes)
        nxx_offset + 103 * nxx_count,  # NXX table (each entry is 103 bytes)
    ]
    decomp_size = max(size_candidates)
    decomp = bytearray(decomp_size)
    
    # Write the counts into their fixed positions:
    decomp[864] = prices.get("local_count", 0)
    decomp[865] = prices.get("intralata_count", 0)
    decomp[866] = prices.get("interlata_count", 0)
    decomp[867] = prices.get("interstate_count", 0)
    decomp[868] = prices.get("corridor_count", 0)
    decomp[869] = prices.get("canadian_count", 0)
    decomp[870] = prices.get("extended_count", 0)
    decomp[871] = prices.get("misc_count", 0)
    decomp[887] = prices.get("group_count", 0)
    decomp[888] = prices.get("price_count", 0)
    decomp[889] = prices.get("nxx_count", 0)
    
    # Store rate_band_offset in decompressed data (offsets 877-878)
    if rate_band_offset > 0:
        val = rate_band_offset - 1
        decomp[877] = val & 0xFF
        decomp[878] = (val >> 8) & 0xFF
    # Store nxx_offset in decompressed data (offsets 879-880)
    decomp[879] = nxx_offset & 0xFF
    decomp[880] = (nxx_offset >> 8) & 0xFF
    
    # Write rate entries (each 4 bytes) starting at (rate_band_offset - 1)
    r_offset = rate_band_offset - 1
    for entry in rate_entries:
        decomp[r_offset]   = entry.get("initial_rate", 0)
        decomp[r_offset+1] = entry.get("initial_time", 0)
        decomp[r_offset+2] = entry.get("additional_rate", 0)
        decomp[r_offset+3] = entry.get("additional_time", 0)
        r_offset += 4
        
    # Write the NXX table entries (each 103 bytes) starting at nxx_offset.
    offset = nxx_offset
    for entry in nxx_table:
        decomp[offset]   = entry.get("price_band", 0)
        decomp[offset+1] = entry.get("dial_pattern", 0)
        decomp[offset+2] = entry.get("flags", 0)
        # The next 100 bytes encode 800 bits representing NXX enable flags.
        nxx_entries = entry.get("nxx_entries", [])
        bits = [0] * 100
        for j, item in enumerate(nxx_entries):
            if item.get("enabled", False):
                byte_index = j // 8
                bit_index  = j % 8
                bits[byte_index] |= (1 << bit_index)
        decomp[offset+3:offset+103] = bytes(bits)
        offset += 103
        
    # Write intrastate NPA groups starting at offset 890 (each group is 6 bytes):
    offset = 890
    for group in intrastate_npas:
        NPA = group.get("NPA", 0)
        decomp[offset]   = NPA & 0xFF
        decomp[offset+1] = (NPA >> 8) & 0xFF
        decomp[offset+2] = group.get("NXX_count", 0)
        decomp[offset+3] = group.get("band", 0)
        decomp[offset+4] = group.get("dial_plan", 0)
        decomp[offset+5] = group.get("initial_price", 0)
        offset += 6
        
    # Write surcharges: these are stored in the decompressed block starting at offset 800.
    # For each of the 8 bands (keys 'Local', 'IntraLATA', etc.),
    # write 6 values at fixed sub-offsets.
    for i in range(8):
        key = ENUM_BAND_CATEGORIES.get(i+1, "")
        surch = surcharges.get(key, {})
        decomp[800 + i]      = surch.get("coin", 0)
        decomp[800 + i + 8]  = surch.get("paof_bell", 0)
        decomp[800 + i + 16] = surch.get("paof_comm", 0)
        decomp[800 + i + 24] = surch.get("paof_collect", 0)
        decomp[800 + i + 32] = surch.get("paof_addtnl", 0)
        decomp[800 + i + 40] = surch.get("chip_card", 0)
        
    return decomp

def write_ratefile(json_filename, output_filename, verbose=False):
    """
    Reads the JSON file (generated by the original parser) and writes out the corresponding binary file.
    The process rebuilds the header and decompressed data, compresses the latter, updates the filesize,
    and writes the concatenated result.
    """
    with open(json_filename, 'r') as f:
        parsed = json.load(f)
        
    header_bytes = build_header(parsed["header"])
    decompressed_data = build_decompressed(
        parsed["prices"],
        parsed["rate_entries"],
        parsed["nxx_table"],
        parsed["intrastate_npas"],
        parsed["surcharges"]
    )
    compressed_data = compress(decompressed_data)
    
    total_size = len(header_bytes) + len(compressed_data)
    # Write the filesize into the header (bytes 1-4, little-endian)
    header_bytes[1:5] = len(decompressed_data).to_bytes(4, byteorder='little')
    
    bin_content = header_bytes + compressed_data
    with open(output_filename, 'wb') as f:
        f.write(bin_content)
    if verbose:
        print(f"Wrote {output_filename} with {total_size} bytes.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage:", sys.argv[0], sys.argv[1], 'input.json', 'output.r94')
        sys.exit(1)
    json_filename = sys.argv[1]
    output_filename = sys.argv[2]
    write_ratefile(json_filename, output_filename, verbose=True)
