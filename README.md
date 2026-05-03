# elcotel-playground

Tools for working with Elcotel payphone files — parsing them, writing them, generating new ones from scratch, and verifying corpus roundtrip fidelity.

## The R94 format

An R94 file has two parts: a fixed 268-byte header, followed by a body compressed with a simple zero-run encoding (a lone `0x00` byte is an escape; the next byte gives the count of zeros to emit).

The decompressed body is a flat byte stream with no length prefixes or section markers — everything is addressed by fixed offsets derived from counts stored in the header. The layout is:

| Offset | Size | Contents |
|--------|------|----------|
| 0 | 800 bytes | NPA default table, one byte per area code 200–999 |
| 800 | 64 bytes | Surcharge block, eight 8-byte rows in column-major order |
| 864 | 26 bytes | Price-plan counts (band counts per category, offsets) |
| 890 | 6 × N | NPA group headers (one per NPA that has NXX overrides) |
| variable | 4 × B | Price band entries (initial rate/time, additional rate/time) |
| variable | 103 × T | NXX bitmap tables (100-byte bitmap + 3-byte metadata) |

Each NPA default byte is either a token (`0` = restricted, `253` = unlimited, `254/255` = NXX-specific) or a 1-based index into the price band table. When set to NXX-specific, that area code's group headers and bitmap tables determine the actual per-exchange pricing.

The same NPA can appear in multiple group rows because it may have NXX overrides in different band categories (e.g. local *and* intralata exchanges within the same area code).

The first header byte is consistently `0x06` across all known valid files but is undocumented — the writer preserves it from templates without interpreting it.

## S94 format (Speed Dial 94)

S94 files store up to 50 speed dial entries for Elcotel Series 5 payphones. Each entry defines a dialed number with initial and additional period rates and times, plus a LATA type classification.

The file has two parts: a fixed 168-byte header (same format as P94), followed by a body compressed with zero-run encoding. The uncompressed body is exactly 850 bytes (50 records × 17 bytes each).

**Record format (17 bytes each):**

| Offset | Size | Contents |
|--------|------|----------|
| 0 | 1 | Pattern length (0 = empty slot) |
| 1–11 | 11 | Dialed number (binary encoded digits, zero-padded) |
| 12 | 1 | Initial rate in nickels (0xF4 = unused) |
| 13 | 1 | Initial time in minutes (0xFE = unlimited, 0xFF = restricted) |
| 14 | 1 | Additional rate in nickels |
| 15 | 1 | Additional time in minutes |
| 16 | 1 | LATA type (0–8) |

## P94 format (Priority Parsing 94)

P94 files store dial pattern routing rules for Elcotel Series 5 payphones. Each entry defines a pattern match with associated macro, timer, rates, and times. Supports up to 250 records using a companion `.P99` file for records 51–250.

The file has two parts: a fixed 168-byte header (same format as S94), followed by a body compressed with zero-run encoding. The primary `.P94` file holds records 1–50; extended records are stored in a companion `.P99` file.

**Record format (31 bytes each):**

| Offset | Size | Contents |
|--------|------|----------|
| 0–23 | 24 | Pattern field (variable-length, zero-padded) |
| 24 | 1 | Call macro number (0xF4 = unused) |
| 25 | 1 | Call completion timer |
| 26 | 1 | Initial rate in nickels (0xF4 = unused) |
| 27 | 1 | Initial time in minutes |
| 28 | 1 | Additional rate in nickels |
| 29 | 1 | Additional time in minutes |
| 30 | 1 | LATA type (0–8) |

The pattern field can hold two patterns separated by a comma — the first pattern is matched first, falling back to the second if no match.

## P99 companion files

When a P94 file has more than 50 records, the extended records (51–250) are stored in a companion `.P99` file with the same 168-byte header format. The parser automatically detects and merges records from the `.P99` file when reading; the writer creates or deletes the `.P99` as needed based on record count.

## Shared encoding

All three formats (R94, S94, P94) share:

- **Zero-run compression**: Runs of 1–254 zeros are encoded as `[0x00, count]`. The decompressor tolerates trailing zeros without a count (EOF edge case).

- **Dial digit encoding**: Digits are stored as binary values (0x00–0x09 = '0'–'9'). Special characters: `*` = 0x0B, `#` = 0x0C, `A`–`D` = 0x0D–0x10, `@` = 0xF0, `$` = 0xF1, `?` = 0xF2, `+` = 0xF3, `!` (unused) = 0xF4.

- **Token values**: `0xF4` (244) = unused/empty, `0xFE` (254) = unlimited time, `0xFF` (255) = restricted.

- **Header format**: Bytes 0–3 unknown (format ID), bytes 4–7 = file data length (4-byte LE), bytes 8–15 = model string (8 chars), byte 109 = description length, bytes 110–167 = description text.

## What you can do with R94

**Read** an existing R94 file and print a human-readable summary, or export the parsed model and low-level writer payload as JSON.

**Create** an R94 file from a writer JSON payload — useful for re-serializing after manual edits to a dumped payload.

**Generate** an R94 file from a high-level tariff specification. This is where most of the complexity lives — see generation modes below.

**Verify** a directory of R94 files for parse success and byte-perfect write-back roundtrip.

## What you can do with S94 and P94

The same read/create/verify workflow is available for S94 (Speed Dial) and P94 (Priority Parsing) files:

```bash
# Read an S94 file and print summary
uv run s94_read.py --file S94_EXAMPLES/DEFAULT.S94 --summary

# Read a P94 file (automatically merges .P99 companion if present)
uv run p94_read.py --file P94_EXAMPLES/DEFAULT.P94 --summary

# Export to JSON for editing
uv run s94_read.py --file myfile.S94 --json-out dump.json
uv run p94_read.py --file myfile.P94 --json-out dump.json

# Rebuild from JSON (round-trip)
uv run s94_create.py dump.json rebuilt.S94 --verify-roundtrip
uv run p94_create.py dump.json rebuilt.P94 --verify-roundtrip

# Verify a corpus of all S94 and P94 files
uv run verify_s94_p94.py
```

The parser automatically handles:
- Decompression of the zero-run encoded body
- Dial digit encoding/decoding
- For P94: auto-detection and merging of companion `.P99` files (records 51–250)

## Generation modes

### Explicit spec

You provide a JSON or YAML document that defines price bands, NPA default rules, NXX overrides, unlisted fallbacks, and surcharges. The compiler assigns numeric indices, orders bands by category, builds the NPA table and NXX bitmaps, and writes a valid R94 file. See `ratefile/example_spec.json`.

### Discovery mode

Instead of manually listing every exchange, you give the generator a home NPA/NXX and it figures out which exchanges should be local, intralata, interlata, and so on. Relationships are classified in this precedence:

1. **invalid** — unassigned NPA/NXX
2. **local** — same exchange, or listed in a local calling table, or same rate center
3. **corridor / extended / misc** — policy-driven overrides for specific NPAs (e.g. corridor routes to Mexico)
4. **canadian** — cross-border when home is US
5. **interstate** — different country or different state
6. **intralata** — same LATA
7. **interlata** — different LATA (default toll)

Two discovery sources are available:

- **offline** — you provide exchange datasets (NANPA tab-delimited `.txt`, CNAC CSV, or JSON). The generator loads them, classifies each exchange, and builds the spec.
- **api-lata / api-lir** — queries [LocalCallingGuide](https://localcallingguide.com) for prefix, rate center, and LATA/LIR data, then validates against downloaded NANPA/CNAC datasets. API responses are cached as JSON in `ratefile/cache/`.

Downloaded NANPA/CNAC ZIPs are extracted and discarded; only the parsed data files remain in `ratefile/data/`.

## Usage

All scripts use [PEP 723](https://peps.python.org/pep-0723/) inline metadata, so with [uv](https://docs.astral.sh/uv/) installed you can run them directly — no venv or pip needed.

### Read a file

```bash
uv run ratefile_read.py --file ratefiles/208209BN.R94 --summary
uv run ratefile_read.py --file ratefiles/208209BN.R94 --json-out parsed.json --dump-lowlevel-json writer.json
```

### Create from a writer payload

```bash
uv run ratefile_create.py writer.json rebuilt.R94 --verify-roundtrip
```

### Generate from an explicit spec

```bash
uv run generate_ratefile.py ratefile/example_spec.json output.R94 --verify --summary
```

### Generate using discovery

From a spec file:
```bash
uv run generate_ratefile.py ratefile/example_discovery_spec.json output.R94 --verify --summary
```

Directly from the command line (uses LocalCallingGuide API with defaults):
```bash
uv run generate_ratefile.py --home-npa 408 --home-nxx 535 --discovery-mode api-lata --output-r94 output.R94 --verify --summary
```

With verbose/debug output and relationship dumps:
```bash
uv run generate_ratefile.py --home-npa 408 --home-nxx 535 --discovery-mode api-lata --output-r94 output.R94 --verify --debug --dump-relationships rels.json --dump-json payload.json
```

### Verify a corpus of ratefiles

```bash
uv run verify_ratefiles.py
uv run verify_ratefiles.py /path/to/ratefiles --limit 20
```

## Dependencies

The scripts declare their dependencies inline via PEP 723 metadata. The main ones are `pydantic` (for parsed model validation) and `click` (for CLI argument parsing). If running without uv, install them manually — the codebase has no other requirements.
