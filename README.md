# elcotel-playground

Tools for working with Elcotel payphone files - parsing them, writing them, generating new ones from scratch, and verifying corpus roundtrip fidelity.

## The R94 format

An R94 file has two parts: a fixed 268-byte header, followed by a body compressed with a simple zero-run encoding (a lone `0x00` byte is an escape; the next byte gives the count of zeros to emit).

The decompressed body is a flat byte stream with no length prefixes or section markers - everything is addressed by fixed offsets derived from counts stored in the header. The layout is:

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

The first header byte is consistently `0x06` across all known valid files but is undocumented - the writer preserves it from templates without interpreting it.

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

The pattern field can hold two patterns separated by a comma - the first pattern is matched first, falling back to the second if no match.

## P99 companion files

When a P94 file has more than 50 records, the extended records (51–250) are stored in a companion `.P99` file with the same 168-byte header format. The parser automatically detects and merges records from the `.P99` file when reading; the writer creates or deletes the `.P99` as needed based on record count.

## C94 format (Registers and Options)

C94 files contain a 168-byte header and a zero-run-compressed 4096-byte
register/options image. Nine firmware-specific maps cover LP 05.03.00–05.04.00
and KX 01.00.00–01.03.00. See the [format notes](c94file/FORMAT.md)
and the [parameter-by-parameter reference](c94file/PARAMETERS.md) for setting
meanings, ranges, units, macro commands, firmware differences and explicit gaps.

### Simple browser editor

```bash
uv run c94_editor.py
```

Open **http://127.0.0.1:8094**, choose your C94 file, change the named settings,
then click **Download edited C94**. It uses ON/OFF switches, macro/language
dropdowns, dollars, clock times, and shutdown-period checkboxes. Search and
category filters help find settings. The source file is never overwritten.
Stop the local server with Ctrl+C.

**Lo/Hi are firmware-version bounds, not value limits.** For LP, codes 0–4
mean 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00. For KX, codes 0–3
mean 01.00.00, 01.01.00, 01.02.00, 01.03.00. The simple editor handles these
internally; you don't edit them or binary offsets/tokens.

Unknown/reserved settings, conflicting definitions, and inline macro programs
are read-only. They are preserved along with all other untouched bytes.
Confirmed enum values use descriptive choices, including LP 05.04 operation
modes, routing thresholds and keypad anti-fraud modes. Labels are not assumed
to apply to other firmware; partially known settings remain explicitly marked.
KX 01.02/01.03 also have branch-verified anti-fraud choices (including the
default selector), routing thresholds, operation modes and LCD widths.
Coin-line modes require a capable build/hardware; 01.00/01.01 enum additions
remain unverified. KX volume codes are not assigned guessed gain labels.
Known editor ranges are checked on save, but appropriate operational values
still depend on your phone and service. Files are processed locally; nothing
is sent to an external service. Bypass codes/passwords are shown as plain-text values.

### Inspection and low-level tools

```bash
# Inspect a template
uv run c94_read.py --file myphone.C94 --summary

# Explain individual settings and their current values
uv run c94_read.py --file myphone.C94 --register 204 --register 437

# Export lossless hex-byte JSON and decoded registers (may contain credentials)
uv run c94_read.py --file myphone.C94 --json-out image.json --registers-out registers.json

# Rebuild from the lossless payload (decoded register exports are inspection-only)
uv run c94_create.py image.json rebuilt.C94 --verify-roundtrip

# Verify all files recursively, including byte-perfect recompression
uv run verify_c94.py ./c94files
```

The reader preserves unknown bytes and rejects damaged/truncated images.
Register addresses refer to the complete expanded body, including its
58-byte copyright prefix; these are not the separate SSB payload offsets.

## Shared encoding

All four formats (R94, S94, P94, C94) share:

- **Zero-run compression**: Runs of 1–254 zeros are encoded as `[0x00, count]`. The decompressor tolerates trailing zeros without a count (EOF edge case).

- **Dial digit encoding**: Digits are stored as binary values (0x00–0x09 = '0'–'9'). Special characters: `*` = 0x0B, `#` = 0x0C, `A`–`D` = 0x0D–0x10, `@` = 0xF0, `$` = 0xF1, `?` = 0xF2, `+` = 0xF3, `!` (unused) = 0xF4.

- **Token values**: `0xF4` (244) = unused/empty, `0xFE` (254) = unlimited time, `0xFF` (255) = restricted.

- **Header format**: Bytes 0–3 unknown (format ID), bytes 4–7 = file data length (4-byte LE), bytes 8–15 = model string (8 chars), byte 109 = description length, bytes 110–167 = description text.

## What you can do with R94

**Read** an existing R94 file and print a human-readable summary, or export the parsed model and low-level writer payload as JSON.

**Create** an R94 file from a writer JSON payload - useful for re-serializing after manual edits to a dumped payload.

**Generate** an R94 file from a high-level tariff specification. This is where most of the complexity lives - see generation modes below.

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

1. **invalid** - unassigned NPA/NXX
2. **local** - same exchange, or listed in a local calling table, or same rate center
3. **corridor / extended / misc** - policy-driven overrides for specific NPAs (e.g. corridor routes to Mexico)
4. **canadian** - cross-border when home is US
5. **interstate** - different country or different state
6. **intralata** - same LATA
7. **interlata** - different LATA (default toll)

Two discovery sources are available:

- **offline** - you provide exchange datasets (NANPA tab-delimited `.txt`, CNAC CSV, or JSON). The generator loads them, classifies each exchange, and builds the spec.
- **api-lata / api-lir** - queries [LocalCallingGuide](https://localcallingguide.com) for prefix, rate center, and LATA/LIR data, then validates against downloaded NANPA/CNAC datasets. API responses are cached as JSON in `ratefile/cache/`.

Downloaded NANPA/CNAC ZIPs are extracted and discarded; only the parsed data files remain in `ratefile/data/`.

## Usage

All scripts use [PEP 723](https://peps.python.org/pep-0723/) inline metadata, so with [uv](https://docs.astral.sh/uv/) installed you can run them directly - no venv or pip needed.

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

The scripts declare their dependencies inline via PEP 723 metadata. The main ones are `pydantic` (for parsed model validation) and `click` (for CLI argument parsing). If running without uv, install them manually - the codebase has no other requirements.
