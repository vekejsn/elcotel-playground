# C94 register/options format

For **what the individual settings do**, their names, editor ranges, units,
firmware availability and remaining gaps, see [the parameter reference](PARAMETERS.md).

C94 is the Series 5 / KX register-and-options image,
historically called ROF. It is not a tariff table or an encrypted SSB file.

## Container

All offsets below are zero-based.

| File offset | Length | Meaning |
|---|---:|---|
| 0 | 4 | Uninterpreted identifier; supplied templates have `00 20 03 00` |
| 4 | 4 | Expanded body length, little-endian: 4096 (`00 10 00 00`) |
| 8 | 8 | ASCII family/version, e.g. `LP050400` or `KX010300` |
| 16 | 93 | Other metadata; preserved without interpretation |
| 109 | 1 | Description byte count, at most 58 |
| 110 | 58 | Description storage, including potentially stale bytes after the counted text |
| 168 | variable | Zero-run-compressed 4096-byte body |

The version tag is two family letters followed by three two-digit decimal
components. `LP050400` means LP 05.04.00, not the hardware model number.
Header metadata should not be regenerated casually: defaults include a counted
description `my test` followed by stale text from an older description.

Nonzero body bytes are literals; `00 nn` emits `nn` zeros (1–255).
The header is never compressed. Compression spans register boundaries.
The expanded image is 4264 bytes including its header. The reader rejects
truncated bodies, dangling escape bytes, zero counts, oversize expansions and
inconsistent declared sizes. It does not zero-pad damaged files.

## Body and address bases

The body begins with 58 bytes of copyright text, observed as
`RATES FOR PCM 5 (C) COPYRIGHT BY ELCOTEL, INC. 1986 - 1989` (58 ASCII bytes).
This is **body data**, not an additional container header.

Register addresses are hexadecimal offsets relative to
the complete expanded body, including those 58 bytes. Thus a mapped register
at `CC` is at expanded file offset `168 + 0xCC`. It has no fixed compressed
file offset.

Buffers omitting the copyright prefix require addresses reduced by 58.
Do not apply that subtraction when using the complete body.

The following locations are identical in all nine recovered maps:

| Register | Body offset | Size | Encoding |
|---|---:|---:|---|
| 311 | `0040` | 20 | Counted binary dial string |
| 400 | `00CC` | 9 | Bypass code, counted binary digits |
| 402 | `00D5` | 6 | Station ID and checksum |
| 403 | `00DB` | 10 | Counted ASCII password |
| 404 | `00E5` | 11 | ANI, counted binary digits |

These are **not** the separate SSB payload offsets.

## Firmware maps

The bundled register maps contain 2596 entries:

| Firmware | Map identifier | Rows |
|---|---|---:|
| LP 05.03.00 | LP050300 | 249 |
| LP 05.03.01 | LP050301 | 271 |
| LP 05.03.02 | LP050302 | 279 |
| LP 05.03.03 | LP050303 | 326 |
| LP 05.04.00 | LP050400 | 358 |
| KX 01.00.00 | KX010000 | 214 |
| KX 01.01.00 | KX010100 | 283 |
| KX 01.02.00 | KX010200 | 285 |
| KX 01.03.00 | KX010300 | 331 |

The reader uses exact version matches, not the legacy application's
future-version fallback. Unknown versions can still be read losslessly;
register interpretation requires a known map or explicit table override.

## Map token meanings

| Token | Meaning of mapped bytes |
|---:|---|
| 1 | Unsigned byte; R437 stores hours, displayed as days (`raw / 24`) |
| 2 | Length byte followed by binary dial digits, with zero-filled unused storage |
| 3 | One-byte number of nickels (`raw / 20` dollars) |
| 4 | Two-byte little-endian number of nickels |
| 5 | Two-byte little-endian integer |
| 6 | Inline 26-byte macro command list, not a database macro ID |
| 7 | Length byte followed by ordinary ASCII (password) |
| 8 | Boolean flag: Address identifies a byte; **Size is the one-based bit index** |
| 9 | Byte-valued selection; absent from the supported maps |
| 10 | Two bytes: minutes first, hours second |
| 11 | R468's 100-byte call-option block, corresponding to options R200–R299 |

Dial digits `0`–`9` are bytes 0–9, `*` is 11 and `#` is 12. Counted strings
include the length byte in the mapped storage size. Flag registers share
bytes; Size must never be interpreted as a byte count for token 8.

R402 is special even though its map token is 2. Short IDs use a length byte
and up to four binary digits, with a checksum at byte 5. Ten-digit IDs occupy
five packed-BCD bytes, plus checksum. Their first byte is
`((first_digit - 2) << 4) | 0x80 | second_digit`. The checksum is the sum of
the preceding five bytes modulo 256. It is reported, not silently repaired.

Macros and call-option blocks retain their raw byte lists and also expose
annotated interpretations. R468's two shutdown-interval bits
are decoded per call type; its other bits remain unknown. Signed/sentinel
interpretations and unknown numeric mode legends are not invented.
See the parameter reference for per-setting limitations.

## C94 versus SSB

The site-specific block is a **separate** 515-byte structure:
two-byte little-endian length 512, 512 transformed data bytes, then the sum
of the transformed bytes modulo 256. Transformation is complement each byte
and rotate right one bit. This is not C94 body encryption.
SSB payload offsets for R400/R402/R403/R404 are 140/149/155/165, different
from C94's addresses. SSB generation is not implemented by these tools.

## Verification

All 21 tested C94 files parse, decode without field errors, and
round-trip byte-for-byte. This includes two sets of nine legacy defaults and
three newer generated files; the generated files' parse success does not
validate the addresses used to patch them. Default templates are 463 bytes,
except DEF_530 at 464 bytes. Canonical recompression preserves all these
files exactly. Other valid noncanonical zero-run segmentations may serialize
differently while retaining identical expanded bytes.

JSON writer payloads retain the entire header and body as hex. Decoded
register exports are inspection-only and may contain bypass codes/passwords;
handle them as sensitive data. The summary does not print these values.
