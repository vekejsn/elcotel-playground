from pathlib import Path
import struct
import json

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

def print_format(key, value, key_width=32):
    print(f'{key:>{key_width}}: {value}')

def read_str(data, start, length):
    # Reads a fixed-length string up to the first NUL, then strips whitespace.
    return data[start:start+length].split(b'\x00')[0].decode('ascii', errors='ignore').strip()

def parse_header(data: bytes, verbose=False):
    # In the original file the header is stored at fixed offsets.
    description_offset = 209
    description_length = data[description_offset]
    description = data[description_offset + 1:description_offset + 1 + description_length].decode('ascii', errors='replace')
    header_dict = {
        'is_ratefile': data[24] == 1,
        'filesize': int.from_bytes(data[1:5], byteorder='little'),
        'description': description,
        'local_band_count': data[152],
        'intralata_band_count': data[153],
        'interlata_band_count': data[154],
        'interstate_band_count': data[155],
        'corridor_band_count': data[156],
        'canadian_band_count': data[157],
        'extended_band_count': data[158],
        'misc_band_count': data[159],
        'home_npa': data[18:21].decode(errors='ignore'),
        'home_nxx': data[21:24].decode(errors='ignore'),
    }

    if verbose:
        print('\nHeader:')
        for key, value in header_dict.items():
            print_format(key, value)
    return header_dict

def determine_band(index, offsets):
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

def format_price(value):
    if value == 254:
        return 'Unlimited'
    elif value == 255:
        return 'Restricted'
    elif value == 0:
        return 'Free'
    else:
        return f'{(value * 0.05):.2f}'

def parse_prices(data: bytes, verbose=False):

    data = data[268:]  # Skip the header
    data = decompress(data)

    prices_dict = {
        'group_count': data[887],
        'price_count': data[888],
        'nxx_count': data[889],
        'local_count': data[864],
        'intralata_count': data[865],
        'interlata_count': data[866],
        'interstate_count': data[867],
        'corridor_count': data[868],
        'canadian_count': data[869],
        'extended_count': data[870],
        'misc_count': data[871],
        'rate_band_offset': data[878] * 256 + data[877] + 1,
        'nxx_offset': data[880] * 256 + data[879],
    }

    offsets = {
        'local': 0,
        'intralata': prices_dict['local_count'],
        'interlata': prices_dict['local_count'] + prices_dict['intralata_count'],
        'interstate': prices_dict['local_count'] + prices_dict['intralata_count'] + prices_dict['interlata_count'],
        'corridor': prices_dict['local_count'] + prices_dict['intralata_count'] + prices_dict['interlata_count'] + prices_dict['interstate_count'],
        'canadian': prices_dict['local_count'] + prices_dict['intralata_count'] + prices_dict['interlata_count'] + prices_dict['interstate_count'] + prices_dict['corridor_count'],
        'extended': prices_dict['local_count'] + prices_dict['intralata_count'] + prices_dict['interlata_count'] + prices_dict['interstate_count'] + prices_dict['corridor_count'] + prices_dict['canadian_count'],
        'misc': prices_dict['local_count'] + prices_dict['intralata_count'] + prices_dict['interlata_count'] + prices_dict['interstate_count'] + prices_dict['corridor_count'] + prices_dict['canadian_count'] + prices_dict['extended_count'],
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

    if verbose:
        print('\nPrices:')
        for key, value in prices_dict.items():
            print_format(key, value)

    # The rate data block starts at the offset specified in the header.
    cursor = prices_dict['rate_band_offset'] - 1
    rate_bands = []
    for i in range(0, prices_dict['price_count']):
        band = {
            'index': i + 1,
            'band': determine_band(i, offsets),
        }
        band['band_index'] = band_offsets[band['band']] + 1
        band_offsets[band['band']] += 1
        band.update({
            'id': i + 1,
            'band_str': ENUM_BAND_CATEGORIES[band['band'] + 1],
            'initial_rate': data[cursor],
            'initial_rate_str': format_price(data[cursor]),
            'initial_time': data[cursor + 1],
            'additional_rate': data[cursor + 2],
            'additional_rate_str': format_price(data[cursor + 2]),
            'additional_time': data[cursor + 3],
        })
        rate_bands.append(band)
        cursor += 4

    if verbose:
        print('Rate Bands:')
        print('Band\tIndex\tInitR\tInitT\tAddR\tAddT')
        for group in rate_bands:
            print(f'{group["band_str"]}\t{group["band_index"]}\t{group["initial_rate_str"]}\t{group["initial_time"]}\t{group["additional_rate_str"]}\t{group["additional_time"]}')

    # The NXX table starts at the offset specified in the header.
    cursor = prices_dict['nxx_offset']
    nxx_table = []
    for i in range(0, prices_dict['nxx_count']):
        nxx_data_raw = data[cursor + 3:cursor + 103]
        nxx_entries = [
            {'nxx': (200 + j), 'enabled': bool((nxx_data_raw[j // 8] >> (j % 8)) & 1)} for j in range(800)
        ]
        nxx_entry = {
            'price_band': data[cursor],
            'dial_pattern': data[cursor + 1],
            'dial_pattern_str': ENUM_DIAL_PLANS.get(data[cursor + 1], f'Unknown ({data[cursor + 1]})'),
            'flags': data[cursor + 2],
            'nxx_entries': nxx_entries,
        }
        nxx_table.append(nxx_entry)
        cursor += 103

    # Groups
    cursor = 890
    intrastate_npas = []
    for i in range(0, prices_dict['group_count']):
        offset = cursor + (i * 6)
        intrastate_npas.append({
            'NPA': data[offset] + data[offset + 1] * 256,
            'NXX_count': data[offset + 2],
            'band': data[offset + 3],
            'dial_plan': data[offset + 4],
            'dial_plan_str': ENUM_DIAL_PLANS.get(data[offset + 4], f'Unknown ({data[offset + 4]})'),
            'initial_price': data[offset + 5],
        })

    return prices_dict, rate_bands, nxx_table, intrastate_npas

def parse_surcharges(data: bytes, verbose=False):
    data = data[268:]  # Skip the header
    data = decompress(data)
    INIT_OFFSET = 800
    surcharges = {}
    for i in range(0, 8):
        surcharges[ENUM_BAND_CATEGORIES[i + 1]] = {
            'coin': data[INIT_OFFSET + i],
            'coin_str': format_price(data[INIT_OFFSET + i]),
            'paof_bell': data[INIT_OFFSET + i + 8],
            'paof_bell_str': format_price(data[INIT_OFFSET + i + 8]),
            'paof_comm': data[INIT_OFFSET + i + 16],
            'paof_comm_str': format_price(data[INIT_OFFSET + i + 16]),
            'paof_collect': data[INIT_OFFSET + i + 24],
            'paof_collect_str': format_price(data[INIT_OFFSET + i + 24]),
            'paof_addtnl': data[INIT_OFFSET + i + 32],
            'paof_addtnl_str': format_price(data[INIT_OFFSET + i + 32]),
            'chip_card': data[INIT_OFFSET + i + 40],
            'chip_card_str': format_price(data[INIT_OFFSET + i + 40]),
        }
    if verbose:
        print('\nSurcharges:')
        for key, value in surcharges.items():
            print_format(f'Band {key}', value)
    return surcharges


def read_ratefile(filename, verbose=False):
    file = Path(filename)
    if not file.exists():
        raise FileNotFoundError(f'File not found: {filename}')
    if verbose:
        print(f'Reading ratefile: {filename}')
        print(f'Raw size: {file.stat().st_size} bytes')
    # Read the entire file as raw bytes
    r94_content = file.read_bytes()
    # Parse header
    if verbose:
        print('Parsing header...')
    header = parse_header(r94_content, verbose=verbose)
    # Parse rate entries
    if verbose:
        print('Parsing prices...')
    prices_dict, rate_entries, nxx_table, intrastate_npas = parse_prices(r94_content, verbose=verbose)
    # You might want to return both header and entries for further use.
    if verbose:
        print('Parsing surcharges...')
    surcharges = parse_surcharges(r94_content, verbose=verbose)
    return {
        'header': header,
        'prices': prices_dict,
        'rate_entries': rate_entries,
        'nxx_table': nxx_table,
        'intrastate_npas': intrastate_npas,
        'surcharges': surcharges,
    }

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage:", sys.argv[0], sys.argv[1], 'input.r94', 'output.json')
        sys.exit(1)
    json_filename = sys.argv[1]
    output_filename = sys.argv[2]
    verbose = len(sys.argv) > 3 and sys.argv[3] == '--verbose'
    parsed = read_ratefile(json_filename, verbose=verbose)
    # Write the parsed data to a JSON file
    with open(output_filename, 'w') as f:
        json.dump(parsed, f, indent=4)
    if verbose:
        print(f'Parsed data written to {output_filename}')
