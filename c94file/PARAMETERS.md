# C94 parameter reference

**Every mapped parameter is listed**, including undocumented, reserved, and
hidden settings. A factory label is not proof of a complete behavioral model.
`documented` below means its name/function is established; it does not
mean every numeric choice, timebase, or hardware
interaction has been recovered. Do not program unknown values into hardware.

## How to read this reference

- Location is a hexadecimal offset in the expanded 4096-byte body, not a compressed-file offset.
- `bN` is a one-based bit within that byte; `/N` is a byte-storage length.
- Firmware values identify the supported family and version.
- Presence in a register map is distinct from visibility in the editor: Lo/Hi
  are firmware **version codes**, not numeric parameter limits.
- Editor rules are UI acceptance ranges, not independently verified firmware limits.
- `cross-family inference` means only the other model's factory table names it;
  that name is a lead, not a confirmed meaning for this model.
- In particular, LP R482-R499/R550/R551 are intentionally hidden/defaulted.
- `unknown` and `reserved/proprietary` are real gaps, not zero-valued booleans.

- `CONFLICT` preserves disagreeing validators in the master versus display tables:
  for example KX coin-channel values have both 0..99 and 0..200 validators.
  Neither is silently treated as a firmware limit.

## Functional model

- **R100-R199:** bit options enabling features or asserting negative options
  such as 'Disable ...'. ON does not always mean the associated hardware is enabled.
- **R200-R299:** call-class-to-macro selection. R204, for example, selects the
  processing macro for sent-paid local calls; it is not a price field.
- **R300-R305 / R512-R525:** inline user macro programs. Macro numbers 45-50
  select R300-R305; numbers 51-64 select R512-R525 where those maps include them.
- **R310-R343:** carrier/service access numbers and authorization strings.
  Access number and authorization are distinct strings used by macro instructions.
- **R400-R499:** station credentials, timings, routing controls, shutdown schedules,
  keypad modes, language/LCD settings and programmable coin settings.
- **R500-R558:** gain/voice detection, time-of-day tariff periods and discounts,
  extended macro storage and additional coin/voice settings.
- **R602-R612:** special-service and voice-mail prices, stored in nickels.
- **R701-R728:** alarm-enable flags, not the current alarm status.
  R750 onward contains thresholds/settings associated with alarms.

## Important relationships and unresolved enums

- R101 enables PBX prefix R341. R107 enables the time-of-day mechanism; R503-R505
  select period starting hours and R506-R511 hold the two discounts for each
  tariff class. Percentage values are not coin prices.
- Permissive-dialing flags R111/R112/R114/R115 select old/new NPA pairs
  R460/R459, R462/R461, R449/R448, R451/R450 respectively.
- R437's displayed interval is days, but its byte is hours (`days * 24`).
- On LP 05.04, R424-R430 select keypad/DTMF protection: 0 disables the keypad
  with protection on; 1 allows the keypad until wink/secondary dial tone with
  protection on; 2 leaves the keypad enabled with protection off. R431's
  default-selector legend and older LP revisions remain unconfirmed.
- KX 01.02/01.03 branch handlers establish R424-R431 as 0 keypad off /
  protection on, 1 keypad on / protection on, 2 keypad on / protection off.
  R422 selects a routing class; R423 selects a local price-band threshold.
  R453 is 0 Smart/COCOT, 1 Hybrid, 2 Bright, but coin-line processing is
  omitted in a checked 01.02 build and included in a checked 01.03 build.
  Stored values do not prove build/hardware capability. Exact patch/build
  coverage is not established; these labels are not applied to 01.00/01.01.
  KX volume code-to-gain meanings remain unresolved; no dB labels are assigned.
- On LP 05.04, R453 is 0 Smart, 1 Hybrid, 2 Bright. Hybrid/Bright require
  coin-line-capable hardware and coin-line service. R422 selects a routing class,
  while R423 selects a local price-band threshold; they are different concepts.
- R501=0 is confirmed as the lowest starting volume on LP 05.04. The volume
  button cycles four levels in 3 dB steps, but code-to-gain values for 1-3
  remain unconfirmed. No exact dB labels are assigned to those codes.
- R472: 0 English, 1 Spanish; 2 French is confirmed for KX 01.03.00 only.
  R473 is 16/20-character LCD width on KX.
- R463/R464 define shutdown interval 1; R465/R466 define interval 2. In R468,
  byte `i` corresponds to call type `i` (register `200+i`), bit 0 restricts it
  during interval 1 and bit 1 during interval 2. The remaining bits are unknown.
- R400/R402/R403/R404 require special handling. Bypass/ANI are
  binary digits, the password is ASCII, and the station ID has its own BCD/checksum
  encoding. Do not apply the ordinary dial-string decoder to every field.

## Editor field rules

FieldType letters are editor validators; they are unrelated to the
binary Token numbers in register maps.

| FieldType | Acceptance rule |
|---|---|
| A | ON/OFF |
| B | integer 0..99 |
| C | integer 0..9 |
| D | integer 0..19 |
| E | integer 0..200 |
| F | integer 0..999 |
| G | hour 0..23 |
| H | $0.00..$9.95 in $0.05 increments |
| I | up to 15 characters; UI prompt says NPANXXXXXX; may be empty |
| J | up to 19 numeric characters; may be empty |
| K | integer 0..99; may be empty |
| L | integer 0..2; meanings depend on setting/firmware; unknown unless labeled |
| M | integer 0..3; meanings depend on setting/firmware; unknown unless labeled |
| N | integer 0..255 |
| O | integer 0..60 |
| P | integer 0..96 |
| Q | HH:MM, 00:00..23:59 |
| R | 0=English, 1=Spanish; KX >=01.03.00 also permits 2=French |
| S | 16 or 20 LCD characters |
| T | integer 0..10 |
| U | integer 0..7 |
| V | integer 0..9999 |

## Confirmed choices

Labels are firmware-specific. They are not automatically copied to other
families or older firmware. Hardware restrictions still apply.

| Firmware | Register | Value | Meaning |
|---|---|---|---|
| LP 05.03.03 | R472 | 0 | English |
| LP 05.03.03 | R472 | 1 | Spanish |
| LP 05.04.00 | R110 | 0 | Electronic coin mechanism (ECM) |
| LP 05.04.00 | R110 | 1 | Mechanical 20A coin mechanism |
| LP 05.04.00 | R422 | 0 | Disabled |
| LP 05.04.00 | R422 | 1 | Local |
| LP 05.04.00 | R422 | 2 | IntraLATA |
| LP 05.04.00 | R422 | 3 | InterLATA |
| LP 05.04.00 | R423 | 0 | Disabled |
| LP 05.04.00 | R423 | 1 | Local band 1 |
| LP 05.04.00 | R423 | 2 | Local bands 1-2 |
| LP 05.04.00 | R423 | 3 | Local bands 1-3 |
| LP 05.04.00 | R424 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R424 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R424 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R425 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R425 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R425 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R426 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R426 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R426 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R427 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R427 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R427 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R428 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R428 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R428 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R429 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R429 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R429 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R430 | 0 | Keypad disabled; DTMF anti-fraud ON |
| LP 05.04.00 | R430 | 1 | Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON |
| LP 05.04.00 | R430 | 2 | Keypad continuously enabled; DTMF anti-fraud OFF |
| LP 05.04.00 | R453 | 0 | Smart (B-1 line; phone controls routing, rating and answer supervision) |
| LP 05.04.00 | R453 | 1 | Hybrid (coin line; phone or central office controls each call type) |
| LP 05.04.00 | R453 | 2 | Bright (coin line; central office controls routing, rating and answer supervision) |
| LP 05.04.00 | R472 | 0 | English |
| LP 05.04.00 | R472 | 1 | Spanish |
| LP 05.04.00 | R501 | 0 | Lowest starting volume; required with volume-control button |
| KX 01.00.00 | R472 | 0 | English |
| KX 01.00.00 | R472 | 1 | Spanish |
| KX 01.01.00 | R472 | 0 | English |
| KX 01.01.00 | R472 | 1 | Spanish |
| KX 01.02.00 | R422 | 0 | Disabled |
| KX 01.02.00 | R422 | 1 | Local |
| KX 01.02.00 | R422 | 2 | IntraLATA |
| KX 01.02.00 | R422 | 3 | InterLATA |
| KX 01.02.00 | R423 | 0 | Disabled |
| KX 01.02.00 | R423 | 1 | Local band 1 |
| KX 01.02.00 | R423 | 2 | Local bands 1-2 |
| KX 01.02.00 | R423 | 3 | Local bands 1-3 |
| KX 01.02.00 | R424 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R424 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R424 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R425 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R425 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R425 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R426 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R426 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R426 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R427 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R427 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R427 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R428 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R428 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R428 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R429 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R429 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R429 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R430 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R430 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R430 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R431 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.02.00 | R431 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.02.00 | R431 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.02.00 | R453 | 0 | Smart / COCOT (B-1 line) |
| KX 01.02.00 | R453 | 1 | Hybrid (coin line) |
| KX 01.02.00 | R453 | 2 | Bright (coin line) |
| KX 01.02.00 | R472 | 0 | English |
| KX 01.02.00 | R472 | 1 | Spanish |
| KX 01.02.00 | R473 | 16 | 16 characters per LCD line |
| KX 01.02.00 | R473 | 20 | 20 characters per LCD line |
| KX 01.03.00 | R422 | 0 | Disabled |
| KX 01.03.00 | R422 | 1 | Local |
| KX 01.03.00 | R422 | 2 | IntraLATA |
| KX 01.03.00 | R422 | 3 | InterLATA |
| KX 01.03.00 | R423 | 0 | Disabled |
| KX 01.03.00 | R423 | 1 | Local band 1 |
| KX 01.03.00 | R423 | 2 | Local bands 1-2 |
| KX 01.03.00 | R423 | 3 | Local bands 1-3 |
| KX 01.03.00 | R424 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R424 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R424 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R425 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R425 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R425 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R426 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R426 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R426 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R427 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R427 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R427 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R428 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R428 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R428 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R429 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R429 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R429 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R430 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R430 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R430 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R431 | 0 | Keypad disabled; DTMF anti-fraud ON |
| KX 01.03.00 | R431 | 1 | Keypad enabled; DTMF anti-fraud ON |
| KX 01.03.00 | R431 | 2 | Keypad enabled; DTMF anti-fraud OFF |
| KX 01.03.00 | R453 | 0 | Smart / COCOT (B-1 line) |
| KX 01.03.00 | R453 | 1 | Hybrid (coin line) |
| KX 01.03.00 | R453 | 2 | Bright (coin line) |
| KX 01.03.00 | R472 | 0 | English |
| KX 01.03.00 | R472 | 1 | Spanish |
| KX 01.03.00 | R472 | 2 | French |
| KX 01.03.00 | R473 | 16 | 16 characters per LCD line |
| KX 01.03.00 | R473 | 20 | 20 characters per LCD line |

## LP parameters (358 unique mapped registers)

cross-family inference: 30; documented: 307; reserved/proprietary; behavior unknown: 20; unknown: 1.

| Register | Meaning / factory label | Body location (Token) | Editor range / units | Firmware | Evidence status |
|---|---|---|---|---|---|
| R100 | Enable incoming calls | 0240b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R101 | Enable PBX prefix when dialing | 0240b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R102 | Enable WINK detect | 0240b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R103 | Enable Card Reader | 0240b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R104 | Enable Remote Voice Telemetry | 0240b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R105 | SMDR - Store Dial Around Calls Only | 0240b6 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R106 | Enable Local Telemetry High Security | 0240b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R107 | Enable time of day discounts | 0240b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R108 | Ignore 1st Portion of Ring-Back Sequence | 0241b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R109 | Allow user to dial *67 and *82 Caller ID | 0241b2 (T8) | ON/OFF | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R110 | Coin mechanism selector | 0241b3 (T8) | 0=Electronic coin mechanism (ECM); 1=Mechanical 20A coin mechanism | 05.03.02, 05.03.03, 05.04.00 | documented |
| R111 | Permissive dialing with Regs 459 & 460 | 0241b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R112 | Permissive dialing with Regs 461 & 462 | 0241b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R113 | Disable Red-box fraud on 01 and 011 | 0241b6 (T8) | ON/OFF | 05.03.02, 05.03.03, 05.04.00 | documented |
| R114 | Enable permissive dialing registers 448 & 449 | 0241b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R115 | Enable permissive dialing registers 450 & 451 | 0241b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R116 | Enable secondary dial-tone detect | 0242b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R117 | Enable User to receive credit from service desk | 0242b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R118 | Block interstate 1+ calls | 0242b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R119 | Customer Proprietary Feature | 0242b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R120 | Enable credit card only feature | 0242b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R121 | Enable collect upon answer detect | 0242b6 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R123 | Enable payphone as an extension feature | 0242b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R124 | Enable dialing digit '8' after a '0'  (anti-fraud) | 0243b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R125 | Enable reverse battery answer supervision | 0243b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R126 | Disable DTMF # after 0- calls | 0243b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R128 | Enable anti-fraud for 911 calls | 0243b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R130 | Enable rotary (pulse) dialing | 0243b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R131 | Delete the 1 from all 1+ calls | 0243b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R132 | Customer Proprietary Feature | 0244b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R133 | Disable Coin Relay pre-charging | 0244b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R134 | Do NOT correct user dialing | 0244b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R135 | Enable Coin Calls | 0244b4 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R136 | Enable Debit Card Calls | 0244b5 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R137 | Enable Non 0+ Credit Card Calls | 0244b6 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R138 | Allow free local calls when cashbox is full | 0244b7 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R140 | Enable timed local calls | 0245b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R141 | Enable reversed coin disposal | 0245b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R142 | Disable line polarity keypad control | 0245b3 (T8) | ON/OFF | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R143 | Customer Proprietary Feature | 0245b4 (T8) | ON/OFF | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R145 | Use AT&T pin fraud prevention module | 0245b6 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R146 | Strip and Ignore 1+ 10xxx Prefixes | 0245b7 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R147 | User enhanced service desk commands | 0245b8 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R148 | Enable PAOF Pound redial feature | 0246b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R150 | Enable PAOF for unknown cards | 0246b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R151 | Enable PAOF prompts to convert 0- calls to 0+ | 0246b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R152 | Enable PAOF to validate collect calls | 0246b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R153 | Enable PAOF to validate local calls | 0246b6 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R154 | Customer Proprietary Feature | 0246b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R155 | Select PAOF Brand # for recording local telemetry | 0246b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R156 | Enable Hangup after WINK on collect calls | 0247b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R157 | Enable BONG before voice prompt | 0247b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R158 | Enable positive acceptance on collect calls | 0247b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R159 | Enable recording caller name on collect calls | 0247b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R161 | Block calls for 4 minutes after collect call | 0247b6 (T8) | ON/OFF; minutes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R162 | Save all calls in VDC SMDR buffer | 0247b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R163 | Disable PAOF for extended NPA calls | 0247b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R164 | Enable Elcotel BONG for 0+ local | 0248b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R165 | Enable Elcotel BONG for 0+ intraLATA | 0248b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R166 | Enable Elcotel BONG for 0+ interLATA | 0248b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R167 | Enable Elcotel BONG for 0+ interstate | 0248b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R168 | Enable PAOF credit card for 0+ local | 0248b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R169 | Enable PAOF credit card for 0+ intraLATA | 0248b6 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R170 | Enable PAOF credit card for 0+ interLATA | 0248b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R171 | Enable PAOF credit card for 0+ interstate | 0248b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R172 | Enable PAOF local collect | 0249b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R173 | Enable PAOF intraLATA collect | 0249b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R174 | Enable PAOF interLATA collect | 0249b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R175 | Enable PAOF interstate collect | 0249b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R180 | Charged for incoming call | 024Ab1 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R181 | Repeat Voice Prompts | 024Ab2 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R182 | Scrolling Messages | 024Ab3 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R183 | Display ANI on off-hook | 024Ab4 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R184 | Debit card voice prompts | 024Ab5 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R185 | Reject keyed in VISA cards | 024Ab6 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R186 | Enhanced card handling | 024Ab7 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R187 | Spare | 024Ab8 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R188 | Enable enhanced answer detect | 024Bb1 (T8) | ON/OFF | 05.03.03, 05.04.00 | documented |
| R189 | Spare | 024Bb2 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R190 | Spare | 024Bb3 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R191 | Spare | 024Bb4 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R192 | Spare | 024Bb5 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R193 | Spare | 024Bb6 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R194 | Spare | 024Bb7 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R195 | Spare | 024Bb8 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R196 | Spare | 024Cb1 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R197 | Spare | 024Cb2 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R198 | Spare | 024Cb3 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R199 | Spare | 024Cb4 (T8) | ON/OFF | 05.03.03, 05.04.00 | reserved/proprietary; behavior unknown |
| R200 | 0 Restricted | 0250/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R201 | 1 Free Emergency | 0251/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R202 | 2 Incoming Calls | 0252/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R203 | 3 Information | 0253/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R204 | 4 Sent paid local calls | 0254/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R205 | 5 Sent paid IntraLATA calls | 0255/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R206 | 6 Sent paid InterLATA calls | 0256/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R207 | 7 Sent paid InterState calls | 0257/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R208 | 8 Sent paid extended NPAs (Canada, etc) | 0258/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R209 | 9 10-xxx 0+ & 0- calls | 0259/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R210 | 10 800-NXX-xxxx calls | 025A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R211 | 11 900-NXX-xxxx calls | 025B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R212 | 12 976-xxxx calls | 025C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R213 | 13 950-xxxx calls | 025D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R214 | 14 01+ (Operator assisted) International calls | 025E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R215 | 15 011+(Sent paid coin)  International calls | 025F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R216 | 16 10-xxx 1+ calls | 0260/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R217 | 17 Speed Dial calls | 0261/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R218 | 18 Restricted 1+ calls (Routing to LEC) | 0262/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R219 | 19 Coin call - Corridor | 0263/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R220 | 20 Spare | 0264/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R221 | 21 Call Home (Alarms/SMDR) | 0265/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R222 | 22 VDC Billing Records Batch Dump | 0266/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R223 | 23 Reroute for Busy Trunk on 0+ | 0267/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R224 | 24 Service Desk calls | 0268/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R225 | 25 Spare | 0269/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R226 | 26 Spare | 026A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R227 | 27 Spare | 026B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R228 | 28 VMF for 0+ calls | 026C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R229 | 29 VMF for coin calls | 026D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R230 | 30 Spare | 026E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R231 | 31 Spare | 026F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R232 | 32 Spare | 0270/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R233 | 33 *0- calls | 0271/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R234 | 34 Splash back to local operator | 0272/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R235 | 35 Restricted 0+ calls (routing to LEC) | 0273/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R236 | 36 0- calls | 0274/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R237 | 37 00- calls | 0275/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R238 | 38 0+ Invalid from keypad/swipe/VDC | 0276/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R239 | 39 0+ Extended NPA's (Canada, etc) | 0277/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R240 | 40 0+ No credit card - local | 0278/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R241 | 41 0+ No credit card - IntraLATA | 0279/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R242 | 42 0+ No credit card - InterLATA | 027A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R243 | 43 0+ No credit card - Interstate | 027B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R244 | 44 0+ Bell Card - local | 027C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R245 | 45 0+ Bell Card - IntraLATA | 027D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R246 | 46 0+ Bell Card - InterLATA | 027E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R247 | 47 0+ Bell Card - Interstate | 027F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R248 | 48 0+ Commercial credit card - local | 0280/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R249 | 49 0+ Commercial credit card - IntraLATA | 0281/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R250 | 50 0+ Commercial credit card - InterLATA | 0282/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R251 | 51 0+ Commercial credit card - Interstate | 0283/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R252 | 52 0+ Unidentified credit card - local | 0284/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R253 | 53 0+ Unidentified credit card - IntraLATA | 0285/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R254 | 54 0+ Unidentified credit card - InterLATA | 0286/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R255 | 55 0+ Unidentified credit card - Interstate | 0287/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R256 | 56 Spare | 0288/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R257 | 57 Spare | 0289/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R258 | 58 Spare | 028A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R259 | 59 PAOF validation request | 028B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R260 | 60 PAOF 0+ converted to local | 028C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R261 | 61 PAOF 0+ converted to 1+ - IntraLATA | 028D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R262 | 62 PAOF 0+ converted to 1+ - InterLATA | 028E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R263 | 63 PAOF 0+ converted to 1+ - Interstate | 028F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R264 | 64 Spare | 0290/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R265 | 65 Spare | 0291/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R266 | 66 Spare | 0292/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R267 | 67 Spare | 0293/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R268 | 68 Spare | 0294/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R269 | 69 Spare | 0295/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R270 | 70 0+ Unbillable from VDC | 0296/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R271 | 71 0+ No credit card - corridor | 0297/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R272 | 72 0+ Bell card - corridor | 0298/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R273 | 73 0+ Commercial credit card - corridor | 0299/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R274 | 74 0+ Unidentified credit card - corridor | 029A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R275 | 75 PAOF 0+ converted to 1+ IXC -  corridor | 029B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R300 | User-defined macro 45 command table | 02B4/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R301 | User-defined macro 46 command table | 02CE/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R302 | User-defined macro 47 command table | 02E8/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R303 | User-defined macro 48 command table | 0302/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R304 | User-defined macro 49 command table | 031C/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R305 | User-defined macro 50 command table | 0336/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R310 | IXC 800 & 950 access number #1 | 08F4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R311 | 1+ IXC Auth code 1 | 0040/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R313 | IXC 800 & 950 access number #2 | 0904/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R316 | VMF coin call access number | 0914/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R319 | OSP 800 & 950 access number #1 | 0924/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R320 | 0+ OSP Auth Code 1 | 0054/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R321 | 0+ OSP Aux. Auth Code 1 | 0068/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R322 | OSP 800 & 950 access number #2 | 0934/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R323 | 0+ OSP Auth Code 2 | 007C/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R324 | 0+ OSP Aux Auth Code 2 | 0090/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R325 | IXC 10xxx Access number #1 | 0944/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R326 | Spare Auth # 1 | 00A4/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R327 | Spare Auth # 2 | 00B8/20 (T2) | up to 19 numeric characters; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R328 | IXC 10xxx Access number #2 | 0954/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R331 | OSP 10xxx Access number #1 | 0964/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R332 | OSP 10xxx Access number #2 | 0974/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R333 | Primary number phone calls to deliver alarms | 0984/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R334 | Secondary number phone calls to deliver alarms | 0994/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R335 | Primary number phone calls to deliver SMDR | 09A4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R336 | Secondary number phone calls to deliver SMDR | 09B4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R337 | Number user dials for Service Desk | 09C4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R338 | Number payphone dials to access Service Desk | 09D4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R339 | VMF 0+ call access number | 09E4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R340 | Undocumented parameter | 09F4/16 (T2) | Not recovered | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | unknown |
| R341 | PBX access code | 0A04/3 (T2) | integer 0..99; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R342 | PAOF Access Number to ELCOTEL's VDC | 0A54/20 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R343 | PAOF Host number for Telenet | 0A68/20 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R400 | Cashbox/vault bypass code | 00CC/9 (T2) | See encoding in FORMAT.md | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R401 | Cash vault collection number | 0A09/4 (T2) | integer 0..999 | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R402 | Station ID | 00D5/6 (T2) | See encoding in FORMAT.md | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R403 | Communications password | 00DB/10 (T7) | See encoding in FORMAT.md | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R404 | ANI / station telephone number | 00E5/11 (T2) | See encoding in FORMAT.md | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R407 | Times to repeat "Not a billable number" incoming | 0A1C/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R408 | Number of rings before answer in remote telemetry | 0A1D/1 (T1) | integer 0..19; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R409 | No. of rings before saying Please dial again | 0A1E/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R410 | Time to start Fast Telemetry Answer | 0A1F/1 (T1) | hour 0..23; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R411 | Duration for Fast Telemetry Answer | 0A20/1 (T1) | hour 0..23; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R412 | Number attempts for alarm call home | 0A21/1 (T1) | integer 0..9; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R414 | Number of attempts for SMDR call home | 0A23/1 (T1) | integer 0..9; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R417 | Default call completion hold-off timer | 0A26/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R418 | Times to repeat "Not a billable number" 0- calls | 0A27/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R419 | WINK window size | 0A28/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R420 | WINK holdoff coinless calls | 0A29/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R421 | WINK holdoff coin calls | 0A2A/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R422 | Highest band to route 0+ to LEC | 0A2B/1 (T1) | 0=Disabled; 1=Local; 2=IntraLATA; 3=InterLATA; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R423 | Highest local band to route to LEC | 0A2C/1 (T1) | 0=Disabled; 1=Local band 1; 2=Local bands 1-2; 3=Local bands 1-3; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R424 | Keypad anti-fraud mode for 01+ calls | 0A3C/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R425 | Keypad anti-fraud mode for 011+ calls | 0A2D/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R426 | Keypad anti-fraud mode for 0- calls | 0A2E/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R427 | Keypad anti-fraud mode for 0+ calls | 0A30/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R428 | Keypad anti-fraud mode for 1+ calls | 0A31/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R429 | Keypad anti-fraud mode for local calls | 0A32/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R430 | Keypad anti-fraud mode for 800 & 950 calls | 0A33/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON; 2=Keypad continuously enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R431 | Default Keypad anti-fraud mode | 0A34/1 (T1) | integer 0..2; meanings depend on setting/firmware; unknown unless labeled; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R432 | Time (in secs) leave keypad on for OSP Bong | 0A2F/1 (T1) | integer 0..255; seconds | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R433 | Time to stay onhook for new dialtone | 0A35/1 (T1) | integer 0..9; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R434 | Time to leave keypad on for manual IXC macros | 0A36/1 (T1) | integer 0..255; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R435 | Time before hangup for unanswered 011+ call | 0A37/1 (T1) | integer 0..255; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R436 | Amount to cap timed local coin calls | 0A3D/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R437 | Timed call home to management system | 0A3E/1 (T1) | integer 0..9; days (stored as hours) | 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R438 | User defined escrow hopper amount | 0A47/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.02, 05.03.03, 05.04.00 | documented |
| R440 | PAOF stolen card threshold value | 0A7C/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R441 | Freq of Validation | 0A7D/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R442 | # Good credit cards to store | 0A7E/1 (T1) | integer 0..10; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R443 | PAOF # redial holdoff | 0A7F/1 (T1) | integer 0..60; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R444 | PAOF brand no. for interstate calls | 0A80/1 (T1) | integer 0..2; meanings depend on setting/firmware; unknown unless labeled; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R445 | VMF coin call delivery period in hours | 0A81/1 (T1) | integer 0..96; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R446 | VMF 0+ call delivery period in hours | 0A82/1 (T1) | integer 0..96; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R447 | PAOF brand no for interLATA calls | 0A83/1 (T1) | integer 0..2; meanings depend on setting/firmware; unknown unless labeled; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R448 | New NPA for permissive dialing w/opt. 114 | 0A84/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R449 | Old NPA for permissive dialing w/opt 114 | 0A86/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R450 | New NPA for permissive dialing w/opt. 115 | 0A88/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R451 | Old NPA for permissive dialing w/opt 115 | 0A8A/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R452 | Out-dialing delay period | 0A8C/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R453 | Payphone operation mode | 0A95/1 (T1) | 0=Smart (B-1 line; phone controls routing, rating and answer supervision); 1=Hybrid (coin line; phone or central office controls each call type); 2=Bright (coin line; central office controls routing, rating and answer supervision); not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R454 | Initial rate for local coin line calls | 0A96/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R455 | Red box fraud deterrent | 0A97/1 (T1) | integer 0..99; seconds | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R456 | Simultaneous dialing speed | 0A98/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R459 | New NPA for permissive dialing w/opt 111 | 0A8D/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R460 | Old NPA for permissive dialing w/opt 111 | 0A8F/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R461 | New NPA for Permissive dialing w/opt 112 | 0A91/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R462 | Old NPA for Permissive dialing w/opt 112 | 0A93/2 (T5) | integer 0..999; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R463 | Drug phone shutdown time #1 | 0A3F/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 05.03.02, 05.03.03, 05.04.00 | documented |
| R464 | Drug phone startup time #1 | 0A41/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 05.03.02, 05.03.03, 05.04.00 | documented |
| R465 | Drug phone shutdown time #2 | 0A43/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 05.03.02, 05.03.03, 05.04.00 | documented |
| R466 | Drug phone startup time #2 | 0A45/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 05.03.02, 05.03.03, 05.04.00 | documented |
| R468 | Per-call-type shutdown restrictions | 0890/100 (T11) | See encoding in FORMAT.md | 05.03.02, 05.03.03, 05.04.00 | documented |
| R472 | Default Language | 0A4B/1 (T1) | 0=English; 1=Spanish; not established unless stated in name/notes | 05.03.03, 05.04.00 | documented |
| R473 | LCD Display Width | 0A4C/1 (T1) | Not established for this family; other-family rule: 16 or 20 LCD characters; not established unless stated in name/notes | 05.04.00 | cross-family inference |
| R474 | Delay dialtone | 0A4D/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | documented |
| R475 | # of SMDR records before TDAS call home | 0A4E/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | documented |
| R476 | Number of minutes between call home tries | 0A4F/1 (T1) | integer 0..10; minutes | 05.03.03, 05.04.00 | documented |
| R478 | Inter-digit timeout | 0A51/1 (T1) | integer 0..7; seconds | 05.04.00 | documented |
| R479 | PCM Call Home Hour | 0A52/1 (T1) | hour 0..23; hours | 05.04.00 | documented |
| R480 | Min of silence before going on-hook to CO | 0A53/1 (T1) | integer 0..99; minutes | 05.04.00 | documented |
| R482 | Coin value Channel A | 0AEB/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R483 | Coin value Channel B | 0AEC/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R484 | Coin value Channel C | 0AED/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R485 | Coin value Channel D | 0AEE/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R486 | Coin value Channel E | 0AEF/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R487 | Coin value Channel F | 0AF0/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R488 | Coin volume Channel A | 0AF1/1 (T1) | Not established for this family; other-family rule: integer 0..9; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R489 | Coin volume Channel B | 0AF2/1 (T1) | Not established for this family; other-family rule: integer 0..9; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R490 | Coin volume Channel C | 0AF3/1 (T1) | Not established for this family; other-family rule: integer 0..9; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R491 | Coin volume Channel D | 0AF4/1 (T1) | Not established for this family; other-family rule: integer 0..9; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R492 | Coin volume Channel E | 0AF5/1 (T1) | Not established for this family; other-family rule: integer 0..9; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R493 | Coin volume Channel F | 0AF6/1 (T1) | Not established for this family; other-family rule: integer 0..9; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R494 | Coin de-bounce Channel A | 0ADB/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R495 | Coin de-bounce Channel B | 0ADC/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R496 | Coin de-bounce Channel C | 0ADD/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R497 | Coin de-bounce Channel D | 0ADE/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R498 | Coin de-bounce Channel E | 0ADF/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R499 | Coin de-bounce Channel F | 0AE0/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R500 | Voice detect blind period | 00F0/1 (T1) | integer 0..9; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R501 | Volume gain | 00F1/1 (T1) | integer 0..3; meanings depend on setting/firmware; unknown unless labeled; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R503 | Start premium tariff period | 0AE2/1 (T1) | hour 0..23; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R504 | Start first discounted tariff period | 0AE3/1 (T1) | hour 0..23; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R505 | Start second discounted tariff period | 0AE4/1 (T1) | hour 0..23; hours | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R506 | First discount % - IntraLATA | 0AE5/1 (T1) | integer 0..99; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R507 | Second discount % - IntraLATA | 0AE6/1 (T1) | integer 0..99; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R508 | First discount % - InterLATA | 0AE7/1 (T1) | integer 0..99; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R509 | Second discount % - InterLATA | 0AE8/1 (T1) | integer 0..99; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R510 | First discount % - Interstate | 0AE9/1 (T1) | integer 0..99; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R511 | Second discount % - Interstate | 0AEA/1 (T1) | integer 0..99; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R512 | User-defined macro 51 command table | 0350/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R513 | User-defined macro 52 command table | 036A/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R514 | User-defined macro 53 command table | 0384/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R515 | User-defined macro 54 command table | 039E/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R516 | User-defined macro 55 command table | 03B8/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R517 | User-defined macro 56 command table | 03D2/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R518 | User-defined macro 57 command table | 03EC/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R519 | User-defined macro 58 command table | 0406/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R520 | User-defined macro 59 command table | 0420/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R521 | User-defined macro 60 command table | 043A/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R522 | User-defined macro 61 command table | 0454/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R523 | User-defined macro 62 command table | 046E/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R524 | User-defined macro 63 command table | 0488/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R525 | User-defined macro 64 command table | 04A2/26 (T6) | 26 raw command/operand bytes; not a macro ID | 05.04.00 | documented |
| R550 | Hopper Volume | 0AF7/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | cross-family inference |
| R551 | Cash-box volume | 0AF8/2 (T4) | Not established for this family; other-family rule: integer 0..999; dollars (stored as nickels) | 05.03.03, 05.04.00 | cross-family inference |
| R552 | Answer Detect Sensitivity | 0AE1/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | documented |
| R553 | Time to Ignore Coins on Power Up | 0AD3/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | documented |
| R554 | Low Frequency Voice Detect Sensitivity | 0AD4/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.03, 05.04.00 | documented |
| R555 | Spare | 0AD5/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.04.00 | reserved/proprietary; behavior unknown |
| R556 | Spare | 0AD6/1 (T1) | Not established for this family; other-family rule: integer 0..99; not established unless stated in name/notes | 05.04.00 | reserved/proprietary; behavior unknown |
| R557 | Spare | 0AD7/2 (T5) | Not established for this family; other-family rule: integer 0..9999; not established unless stated in name/notes | 05.04.00 | reserved/proprietary; behavior unknown |
| R558 | Spare | 0AD9/2 (T5) | Not established for this family; other-family rule: integer 0..9999; not established unless stated in name/notes | 05.04.00 | reserved/proprietary; behavior unknown |
| R602 | Price for 950-xxxx calls | 0AAA/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R603 | Price for 976-xxxx calls | 0AAB/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R604 | Price for 411 information calls | 0AAC/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R605 | Price for 1-411 information calls | 0AAD/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R606 | Price for 555-1212 information calls | 0AAE/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R607 | Price for 1-555-1212 information calls | 0AAF/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R608 | Price for Intra-state information calls | 0AB0/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R609 | Price for Inter-state information calls | 0AB1/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R610 | Voice mail price for 0+ | 0AB2/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R611 | Voice mail price for local | 0AB3/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R612 | Voice mail price for 1+ | 0AB4/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R701 | Alarm 1 - SMDR buffer damaged | 0AC5b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R702 | Alarm 2 - handset | 0AC5b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R703 | Alarm 3 - cashbox/vault bypass code | 0AC5b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R704 | Alarm 4 - program running from ROM | 0AC5b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R705 | Alarm 5 - rate RAM reload | 0AC5b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R706 | Alarm 6 - cashbox trigger | 0AC5b6 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R707 | Alarm 7 - cashbox full | 0AC5b7 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R708 | Alarm 8 - inactivity | 0AC5b8 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R709 | Alarm 9 - coin jam - walkaway | 0AC6b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R710 | Alarm 10 - bad rates | 0AC6b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R711 | Alarm 11 - call counts cleared | 0AC6b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R712 | Alarm 12 - change in master block | 0AC6b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R713 | Alarm 13 - entry into telemetry mode | 0AC6b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R714 | Alarm 14 - bad downloaded program | 0AC6b6 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R715 | Alarm 15 - SMDR Buffer 80% full | 0AC6b7 (T8) | ON/OFF; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R716 | Alarm 16 - SMDR Buffer 100% full | 0AC6b8 (T8) | ON/OFF; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R717 | Alarm 17 - bad registers and options | 0AC7b1 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R718 | Alarm 18 - force call home | 0AC7b2 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R719 | Alarm 19 - validation system alarm | 0AC7b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R720 | Alarm 20 - Billing records buffer 100% full | 0AC7b4 (T8) | ON/OFF; percent | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R721 | Alarm 21 - clock alarm | 0AC7b5 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R724 | Alarm 24 - Corrupt scrollable message | 0AC7b8 (T8) | Not established for this family; other-family rule: ON/OFF | 05.04.00 | cross-family inference |
| R725 | Alarm 25 - off hook alarm | 0AC8b1 (T8) | ON/OFF | 05.04.00 | documented |
| R727 | Alarm 27 - reverse polarity alarm | 0AC8b3 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R728 | Alarm 28 - Low battery alarm | 0AC8b4 (T8) | ON/OFF | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R750 | Cash vault alarm trigger level | 0ACA/2 (T4) | integer 0..999; dollars (stored as nickels) | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R751 | Inactivity timer | 0ACC/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R752 | Coin jam alarm threshold | 0ACD/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |
| R753 | VDC unsuccessful access | 0ACE/1 (T1) | integer 0..99; not established unless stated in name/notes | 05.03.00, 05.03.01, 05.03.02, 05.03.03, 05.04.00 | documented |

### LP parameter notes

- **R100**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R101**: Enables use of PBX prefix R341; does not itself contain the prefix. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R102**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R103**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R104**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R105**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R106**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R107**: Enables the tariff periods R503-R505 and discount percentages R506-R511. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R108**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R109**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R110**: OFF selects an electronic coin mechanism; ON selects mechanical 20A. This selector applies to coin-line-capable Olympian 5501 hardware, not the Series-5 board. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R111**: Enables the old/new NPA pair R460/R459. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R112**: Enables the old/new NPA pair R462/R461. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R113**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R114**: Enables the old/new NPA pair R449/R448. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R115**: Enables the old/new NPA pair R451/R450. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R116**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R117**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R118**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R119**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R120**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R121**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R123**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R124**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R125**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R126**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R128**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R130**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R131**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R132**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R133**: Negative-polarity option: ON disables relay pre-charging, rather than enabling it. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R134**: Negative-polarity option: ON selects 'Do NOT correct user dialing'. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R135**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R136**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R137**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R138**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R140**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R141**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R142**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R143**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R145**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R146**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R147**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R148**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R150**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R151**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R152**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R153**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R154**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R155**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R156**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R157**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R158**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R159**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R161**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R162**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R163**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R164**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R165**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R166**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R167**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R168**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R169**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R170**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R171**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R172**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R173**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R174**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R175**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R180**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R181**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R182**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R183**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R184**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R185**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R186**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R187**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R188**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R189**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R190**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R191**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R192**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R193**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R194**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R195**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R196**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R197**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R198**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R199**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R200**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R201**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R202**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R203**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R204**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R205**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R206**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R207**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R208**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R209**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R210**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R211**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R212**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R213**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R214**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R215**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R216**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R217**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R218**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R219**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R220**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R221**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R222**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R223**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R224**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R225**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R226**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R227**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R228**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R229**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R230**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R231**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R232**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R233**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R234**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R235**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R236**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R237**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R238**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R239**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R240**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R241**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R242**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R243**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R244**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R245**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R246**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R247**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R248**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R249**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R250**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R251**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R252**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R253**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R254**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R255**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R256**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R257**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R258**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R259**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R260**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R261**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R262**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R263**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R264**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R265**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R266**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R267**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R268**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R269**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R270**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R271**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R272**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R273**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R274**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R275**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R400**: Length-prefixed binary digits, not ASCII. Sensitive station credential.
- **R402**: Short binary-digit ID or biased 10-digit packed BCD, followed by checksum; see FORMAT.md.
- **R403**: Length-prefixed ASCII, not binary dial digits. Sensitive station credential.
- **R404**: Length-prefixed binary digits; supplied from the phone's ANI field.
- **R422**: The selected routing class and lower classes are reclassified as call type 35 and use R235's macro. Zero disables this reclassification.
- **R423**: Zero disables this feature. With a nonzero threshold, local calls through that price band remain call type 4; higher local bands become call type 18 and use R218's macro.
- **R424**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R425**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R426**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R427**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R428**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R429**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R430**: Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.
- **R437**: UI value is days; C94 stores hours (days x 24). Do not interpret the byte directly as days.
- **R453**: Bright and Hybrid require coin-line-capable hardware and coin-line service. A Series-5 board without coin-line capability must use Smart mode on a B-1 line.
- **R455**: Number of seconds the handset microphone is filtered to deter injected coin tones; this is a duration, not a mode enum.
- **R456**: Dialing-speed setting; timebase and enum meanings are not established by the UI label.
- **R463**: Beginning of shutdown interval 1; R464 ends it. R468 bit 0 chooses affected call types.
- **R464**: End of shutdown interval 1, paired with R463.
- **R465**: Beginning of shutdown interval 2; R466 ends it. R468 bit 1 chooses affected call types.
- **R466**: End of shutdown interval 2, paired with R465.
- **R468**: 100 bytes indexed by call type 0..99, not by macro number. Bit 0 restricts interval 1; bit 1 restricts interval 2. Bits 2..7 are not decoded.
- **R472**: Language selector; English/Spanish are documented. French is confirmed for KX 01.03.00, not inferred for LP.
- **R473**: LCD width in characters (16 or 20); an LP interpretation borrowed from KX remains an inference.
- **R478**: Inter-digit timeout in seconds, 0-7. Zero selects the default five-second timeout.
- **R479**: Zero disables scheduled call-home. For a nonzero hour, the last two ANI digits select the minute; values over 59 are reduced by 60.
- **R480**: Minutes of detected silence before going on-hook towards the central office. Zero disables this feature.
- **R482**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R483**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R484**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R485**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R486**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R487**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R488**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R489**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R490**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R491**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R492**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R493**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R494**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R495**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R496**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R497**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R498**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R499**: LP set-like code explicitly restores R482-R499 from 05.04.00 defaults; per-channel meaning is inferred from KX, not independently documented for LP.
- **R501**: Zero is the lowest starting volume and is required for correct operation of the optional volume-control button. The button cycles through four levels in 3 dB steps. The exact numeric-code-to-gain mapping for codes 1-3 is not independently confirmed.
- **R550**: Programmable coin/hopper setting. LP 05.04.00 set-like code forces this from defaults rather than user input.
- **R551**: Cash-box volume setting. LP 05.04.00 set-like code forces this from defaults rather than user input.
- **R701**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R702**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R703**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R704**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R705**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R706**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R707**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R708**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R709**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R710**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R711**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R712**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R713**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R714**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R715**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R716**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R717**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R718**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R719**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R720**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R721**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R724**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R725**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R727**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R728**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.

## KX parameters (331 unique mapped registers)

documented: 313; reserved/proprietary; behavior unknown: 17; unknown: 1.

| Register | Meaning / factory label | Body location (Token) | Editor range / units | Firmware | Evidence status |
|---|---|---|---|---|---|
| R100 | Enable incoming calls | 0240b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R101 | Enable PBX prefix when dialing | 0240b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R102 | Enable WINK detect | 0240b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R103 | Enable Card Reader | 0240b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R104 | Enable Remote Voice Telemetry | 0240b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R105 | SMDR - Store Dial Around Calls Only | 0240b6 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R106 | Enable Local Telemetry High Security | 0240b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R107 | Enable time of day discounts | 0240b8 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R108 | Ignore 1st Portion of Ring-Back Sequence | 0241b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R109 | Allow user to dial *67 and *82 Caller ID | 0241b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R110 | Coin mechanism selector | 0241b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R111 | Permissive dialing with Regs 459 & 460 | 0241b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R112 | Permissive dialing with Regs 461 & 462 | 0241b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R113 | Disable Red-box fraud on 01 and 011 | 0241b6 (T8) | ON/OFF | 01.03.00 | documented |
| R114 | Enable permissive dialing registers 448 & 449 | 0241b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R115 | Enable permissive dialing registers 450 & 451 | 0241b8 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R116 | Enable secondary dial-tone detect | 0242b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R117 | Enable User to receive credit from service desk | 0242b2 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R118 | Block interstate 1+ calls | 0242b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R119 | Customer Proprietary Feature | 0242b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R120 | Enable credit card only feature | 0242b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R121 | Enable collect upon answer detect | 0242b6 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R123 | Enable payphone as an extension feature | 0242b8 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R124 | Enable dialing digit '8' after a '0'  (anti-fraud) | 0243b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R125 | Enable reverse battery answer supervision | 0243b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R126 | Disable DTMF # after 0- calls | 0243b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R128 | Enable anti-fraud for 911 calls | 0243b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R130 | Enable rotary (pulse) dialing | 0243b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R131 | Delete the 1 from all 1+ calls | 0243b8 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R132 | Customer Proprietary Feature | 0244b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R133 | Disable Coin Relay pre-charging | 0244b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R134 | Do NOT correct user dialing | 0244b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R135 | Enable Coin Calls | 0244b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R136 | Enable Debit Card Calls | 0244b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R137 | Enable Non 0+ Credit Card Calls | 0244b6 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R138 | Allow free local calls when cashbox is full | 0244b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R140 | Enable timed local calls | 0245b1 (T8) | ON/OFF | 01.03.00 | documented |
| R141 | Enable reversed coin disposal | 0245b2 (T8) | ON/OFF | 01.03.00 | documented |
| R142 | Disable line polarity keypad control | 0245b3 (T8) | ON/OFF | 01.03.00 | documented |
| R145 | Use AT&T pin fraud prevention module | 0245b6 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R146 | Strip and Ignore 1+ 10xxx Prefixes | 0245b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R147 | User enhanced service desk commands | 0245b8 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R162 | Save all calls in VDC SMDR buffer | 0247b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R164 | Enable Elcotel BONG for 0+ local | 0248b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R165 | Enable Elcotel BONG for 0+ intraLATA | 0248b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R166 | Enable Elcotel BONG for 0+ interLATA | 0248b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R167 | Enable Elcotel BONG for 0+ interstate | 0248b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R180 | Charged for incoming call | 024Ab1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R181 | Repeat Voice Prompts | 024Ab2 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R182 | Scrolling Messages | 024Ab3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R183 | Display ANI on off-hook | 024Ab4 (T8) | ON/OFF | 01.00.00, 01.02.00, 01.03.00 | documented |
| R184 | Debit card voice prompts | 024Ab5 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R185 | Reject keyed in VISA cards | 024Ab6 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R186 | Enhanced card handling | 024Ab7 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R187 | Enable voice answer detect for dataport | 024Ab8 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R188 | Enable enhanced answer detect | 024Bb1 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | documented |
| R189 | Spare | 024Bb2 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R190 | Spare | 024Bb3 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R191 | Spare | 024Bb4 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R192 | Spare | 024Bb5 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R193 | Spare | 024Bb6 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R194 | Spare | 024Bb7 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R195 | Spare | 024Bb8 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R196 | Spare | 024Cb1 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R197 | Spare | 024Cb2 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R198 | Spare | 024Cb3 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R199 | Spare | 024Cb4 (T8) | ON/OFF | 01.01.00, 01.02.00, 01.03.00 | reserved/proprietary; behavior unknown |
| R200 | 0 Restricted | 0250/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R201 | 1 Free Emergency | 0251/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R202 | 2 Incoming Calls | 0252/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R203 | 3 Information | 0253/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R204 | 4 Sent paid local calls | 0254/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R205 | 5 Sent paid IntraLATA calls | 0255/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R206 | 6 Sent paid InterLATA calls | 0256/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R207 | 7 Sent paid InterState calls | 0257/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R208 | 8 Sent paid extended NPAs (Canada, etc) | 0258/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R209 | 9 101xxxx 0+ & 0- calls | 0259/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R210 | 10 800-NXX-xxxx calls | 025A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R211 | 11 900-NXX-xxxx calls | 025B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R212 | 12 976-xxxx calls | 025C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R213 | 13 950-xxxx calls | 025D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R214 | 14 01+ (Operator assisted) International calls | 025E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R215 | 15 011+(Sent paid coin)  International calls | 025F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R216 | 16 101xxxx 1+ calls | 0260/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R217 | 17 Speed Dial calls | 0261/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R218 | 18 Restricted 1+ calls (Routing to LEC) | 0262/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R219 | 19 Sent Paid Corridor Calls | 0263/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R220 | 20 Spare | 0264/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R221 | 21 Call Home (Alarms/SMDR) | 0265/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R222 | 22 VDC Billing Records Batch Dump | 0266/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R223 | 23 Reroute for Busy Trunk on 0+ | 0267/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R224 | 24 Service Desk calls | 0268/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R225 | 25 Spare | 0269/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R226 | 26 Spare | 026A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R227 | 27 Spare | 026B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R228 | 28 VMF for 0+ calls | 026C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R229 | 29 VMF for coin calls | 026D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R230 | 30 Spare | 026E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R231 | 31 Spare | 026F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R232 | 32 Spare | 0270/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R233 | 33 *0- calls | 0271/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R234 | 34 Splash back to local operator | 0272/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R235 | 35 Restricted 0+ calls (routing to LEC) | 0273/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R236 | 36 0- calls | 0274/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R237 | 37 00- calls | 0275/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R238 | 38 0+ Invalid from keypad/swipe/VDC | 0276/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R239 | 39 0+ Extended NPA's (Canada, etc) | 0277/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R240 | 40 0+ No credit card - local | 0278/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R241 | 41 0+ No credit card - IntraLATA | 0279/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R242 | 42 0+ No credit card - InterLATA | 027A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R243 | 43 0+ No credit card - Interstate | 027B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R244 | 44 0+ Bell Card - local | 027C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R245 | 45 0+ Bell Card - IntraLATA | 027D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R246 | 46 0+ Bell Card - InterLATA | 027E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R247 | 47 0+ Bell Card - Interstate | 027F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R248 | 48 0+ Commercial credit card - local | 0280/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R249 | 49 0+ Commercial credit card - IntraLATA | 0281/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R250 | 50 0+ Commercial credit card - InterLATA | 0282/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R251 | 51 0+ Commercial credit card - Interstate | 0283/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R252 | 52 0+ Unidentified credit card - local | 0284/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R253 | 53 0+ Unidentified credit card - IntraLATA | 0285/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R254 | 54 0+ Unidentified credit card - InterLATA | 0286/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R255 | 55 0+ Unidentified credit card - Interstate | 0287/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R256 | 56 Spare | 0288/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R257 | 57 Spare | 0289/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R258 | 58 Spare | 028A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R259 | 59 PAOF validation request | 028B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R260 | 60 PAOF 0+ converted to local | 028C/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R261 | 61 PAOF 0+ converted to 1+ - IntraLATA | 028D/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R262 | 62 PAOF 0+ converted to 1+ - InterLATA | 028E/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R263 | 63 PAOF 0+ converted to 1+ - Interstate | 028F/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R264 | 64 Spare | 0290/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R265 | 65 Spare | 0291/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R266 | 66 Spare | 0292/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R267 | 67 Spare | 0293/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R268 | 68 Spare | 0294/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R269 | 69 Spare | 0295/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R270 | 70 0+ Unbillable from VDC | 0296/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R271 | 71 0+ No credit card - corridor | 0297/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R272 | 72 0+ Bell card - corridor | 0298/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R273 | 73 0+ Commercial credit card - corridor | 0299/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R274 | 74 0+ Unidentified credit card - corridor | 029A/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R275 | 75 PAOF 0+ converted to 1+ IXC -  corridor | 029B/1 (T1) | macro number 0..99; existence checked for defined call types; macro number | 01.01.00, 01.02.00, 01.03.00 | documented |
| R300 | User-defined macro 45 command table | 02B4/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R301 | User-defined macro 46 command table | 02CE/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R302 | User-defined macro 47 command table | 02E8/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R303 | User-defined macro 48 command table | 0302/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R304 | User-defined macro 49 command table | 031C/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R305 | User-defined macro 50 command table | 0336/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R310 | IXC 800 & 950 access number #1 | 08F4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R311 | 1+ IXC Auth Code 1 | 0040/20 (T2) | up to 19 numeric characters; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R313 | IXC 800 & 950 access number #2 | 0904/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R316 | VMF coin call access number | 0914/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R319 | OSP 800 & 950 access number #1 | 0924/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R320 | 0+ OSP Auth Code 1 | 0054/20 (T2) | up to 19 numeric characters; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R321 | 0+ OSP Aux. Auth Code 1 | 0068/20 (T2) | up to 19 numeric characters; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R322 | OSP 800 & 950 access number #2 | 0934/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R323 | 0+ OSP Auth Code 2 | 007C/20 (T2) | up to 19 numeric characters; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R324 | 0+ OSP Aux Auth Code 2 | 0090/20 (T2) | up to 19 numeric characters; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R325 | IXC 101xxxx Access number #1 | 0944/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R326 | Spare Auth # 1 | 00A4/20 (T2) | up to 19 numeric characters; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R327 | Spare Auth # 2 | 00B8/20 (T2) | up to 19 numeric characters; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R328 | IXC 101xxxx Access number #2 | 0954/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R331 | OSP 101xxxx Access number #1 | 0964/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R332 | OSP 101xxxx Access number #2 | 0974/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R333 | Primary number phone calls to deliver alarms | 0984/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R334 | Secondary number phone calls to deliver alarms | 0994/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R335 | Primary number phone calls to deliver SMDR | 09A4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R336 | Secondary number phone calls to deliver SMDR | 09B4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R337 | Number user dials for Service Desk | 09C4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R338 | Number payphone dials to access Service Desk | 09D4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R339 | VMF 0+ call access number | 09E4/16 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R340 | Undocumented parameter | 09F4/16 (T2) | Not recovered | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | unknown |
| R341 | PBX access code | 0A04/3 (T2) | integer 0..99; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R342 | DAS Call Home Number | 0A54/20 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R343 | PAOF Host number for Telenet | 0A68/20 (T2) | up to 15 characters; UI prompt says NPANXXXXXX; may be empty | 01.01.00, 01.02.00, 01.03.00 | documented |
| R400 | Cashbox/vault bypass code | 00CC/9 (T2) | See encoding in FORMAT.md | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R401 | Cash vault collection number | 0A09/4 (T2) | integer 0..999 | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R402 | Station ID | 00D5/6 (T2) | See encoding in FORMAT.md | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R403 | Communications password | 00DB/10 (T7) | See encoding in FORMAT.md | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R404 | ANI / station telephone number | 00E5/11 (T2) | See encoding in FORMAT.md | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R407 | Times to repeat "Not a billable number" incoming | 0A1C/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R408 | Number of rings before answer in remote telemetry | 0A1D/1 (T1) | integer 0..19; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R409 | No. of rings before saying Please dial again | 0A1E/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R410 | Time to start Fast Telemetry Answer | 0A1F/1 (T1) | hour 0..23; hours | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R411 | Duration for Fast Telemetry Answer | 0A20/1 (T1) | hour 0..23; hours | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R412 | Number attempts for alarm call home | 0A21/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R414 | Number of attempts for SMDR call home | 0A23/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R417 | Default call completion hold-off timer | 0A26/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R418 | Times to repeat "Not a billable number" 0- calls | 0A27/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R419 | WINK window size | 0A28/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R420 | WINK holdoff coinless calls | 0A29/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R421 | WINK holdoff coin calls | 0A2A/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R422 | Highest band to route 0+ to LEC | 0A2B/1 (T1) | 0=Disabled; 1=Local; 2=IntraLATA; 3=InterLATA; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R423 | Highest local band to route to LEC | 0A2C/1 (T1) | 0=Disabled; 1=Local band 1; 2=Local bands 1-2; 3=Local bands 1-3; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R424 | Keypad anti-fraud mode for 01+ calls | 0A3C/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R425 | Keypad anti-fraud mode for 011+ calls | 0A2D/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R426 | Keypad anti-fraud mode for 0- calls | 0A2E/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R427 | Keypad anti-fraud mode for 0+ calls | 0A30/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R428 | Keypad anti-fraud mode for 1+ calls | 0A31/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R429 | Keypad anti-fraud mode for local calls | 0A32/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R430 | Keypad anti-fraud mode for 800 & 950 calls | 0A33/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R431 | Default Keypad anti-fraud mode | 0A34/1 (T1) | 0=Keypad disabled; DTMF anti-fraud ON; 1=Keypad enabled; DTMF anti-fraud ON; 2=Keypad enabled; DTMF anti-fraud OFF; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R432 | Time (in secs) leave keypad on for OSP Bong | 0A2F/1 (T1) | integer 0..255; seconds | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R433 | Time to stay onhook for new dialtone | 0A35/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R434 | Time to leave keypad on for manual IXC macros | 0A36/1 (T1) | integer 0..255; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R435 | Time before hangup for unanswered 011+ call | 0A37/1 (T1) | integer 0..255; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R436 | Amount to cap timed local coin calls | 0A3D/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R437 | Timed call home to management system | 0A3E/1 (T1) | integer 0..9; days (stored as hours) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R438 | User defined escrow hopper amount | 0A47/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R442 | # Good credit cards to store | 0A7E/1 (T1) | integer 0..10; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R445 | VMF coin call delivery period in hours | 0A81/1 (T1) | integer 0..96; hours | 01.01.00, 01.02.00, 01.03.00 | documented |
| R446 | VMF 0+ call delivery period in hours | 0A82/1 (T1) | integer 0..96; hours | 01.01.00, 01.02.00, 01.03.00 | documented |
| R448 | New NPA for permissive dialing w/opt. 114 | 0A84/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R449 | Old NPA for permissive dialing w/opt 114 | 0A86/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R450 | New NPA for permissive dialing w/opt. 115 | 0A88/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R451 | Old NPA for permissive dialing w/opt 115 | 0A8A/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R452 | Out-dialing delay period | 0A8C/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R453 | Payphone operation mode | 0A95/1 (T1) | 0=Smart / COCOT (B-1 line); 1=Hybrid (coin line); 2=Bright (coin line); not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R454 | Initial rate for local coin line calls | 0A96/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.01.00, 01.02.00, 01.03.00 | documented |
| R455 | Red box fraud deterrent | 0A97/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R456 | Simultaneous dialing speed | 0A98/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R459 | New NPA for permissive dialing w/opt 111 | 0A8D/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R460 | Old NPA for permissive dialing w/opt 111 | 0A8F/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R461 | New NPA for Permissive dialing w/opt 112 | 0A91/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R462 | Old NPA for Permissive dialing w/opt 112 | 0A93/2 (T5) | integer 0..999; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R463 | Drug phone shutdown time #1 | 0A3F/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R464 | Drug phone startup time #1 | 0A41/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R465 | Drug phone shutdown time #2 | 0A43/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R466 | Drug phone startup time #2 | 0A45/2 (T10) | HH:MM, 00:00..23:59; time of day HH:MM (stored minute, hour) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R468 | Per-call-type shutdown restrictions | 0890/100 (T11) | See encoding in FORMAT.md | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R472 | Default Language | 0A4B/1 (T1) | 0=English; 1=Spanish; 2=French; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R473 | LCD Display Width | 0A4C/1 (T1) | 16=16 characters per LCD line; 20=20 characters per LCD line; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R474 | Delay dialtone | 0A4D/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R475 | # of SMDR records before TDAS call home | 0A4E/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R476 | Number of minutes between call home tries | 0A4F/1 (T1) | integer 0..10; minutes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R478 | Inter-digit timeout | 0A51/1 (T1) | integer 0..7; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R479 | PCM Call Home Hour | 0A52/1 (T1) | hour 0..23; hours | 01.01.00, 01.02.00, 01.03.00 | documented |
| R480 | Min of silence before going on-hook to CO | 0A53/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R481 | Dataport de-bounce Time | 0A38/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R482 | Coin value Channel A | 0AEB/1 (T1) | CONFLICT: B: integer 0..99; E: integer 0..200; not established unless stated in name/notes | 01.03.00 | documented |
| R483 | Coin value Channel B | 0AEC/1 (T1) | CONFLICT: B: integer 0..99; E: integer 0..200; not established unless stated in name/notes | 01.03.00 | documented |
| R484 | Coin value Channel C | 0AED/1 (T1) | CONFLICT: B: integer 0..99; E: integer 0..200; not established unless stated in name/notes | 01.03.00 | documented |
| R485 | Coin value Channel D | 0AEE/1 (T1) | CONFLICT: B: integer 0..99; E: integer 0..200; not established unless stated in name/notes | 01.03.00 | documented |
| R486 | Coin value Channel E | 0AEF/1 (T1) | CONFLICT: B: integer 0..99; E: integer 0..200; not established unless stated in name/notes | 01.03.00 | documented |
| R487 | Coin value Channel F | 0AF0/1 (T1) | CONFLICT: B: integer 0..99; E: integer 0..200; not established unless stated in name/notes | 01.03.00 | documented |
| R488 | Coin volume Channel A | 0AF1/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.03.00 | documented |
| R489 | Coin volume Channel B | 0AF2/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.03.00 | documented |
| R490 | Coin volume Channel C | 0AF3/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.03.00 | documented |
| R491 | Coin volume Channel D | 0AF4/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.03.00 | documented |
| R492 | Coin volume Channel E | 0AF5/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.03.00 | documented |
| R493 | Coin volume Channel F | 0AF6/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.03.00 | documented |
| R494 | Coin de-bounce Channel A | 0ADB/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R495 | Coin de-bounce Channel B | 0ADC/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R496 | Coin de-bounce Channel C | 0ADD/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R497 | Coin de-bounce Channel D | 0ADE/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R498 | Coin de-bounce Channel E | 0ADF/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R499 | Coin de-bounce Channel F | 0AE0/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R500 | Voice detect blind period | 00F0/1 (T1) | integer 0..9; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R501 | Volume gain | 00F1/1 (T1) | integer 0..3; meanings depend on setting/firmware; unknown unless labeled; not established unless stated in name/notes | 01.01.00, 01.02.00, 01.03.00 | documented |
| R503 | Start premium tariff period | 0AE2/1 (T1) | hour 0..23; hours | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R504 | Start first discounted tariff period | 0AE3/1 (T1) | hour 0..23; hours | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R505 | Start second discounted tariff period | 0AE4/1 (T1) | hour 0..23; hours | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R506 | First discount % - IntraLATA | 0AE5/1 (T1) | integer 0..99; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R507 | Second discount % - IntraLATA | 0AE6/1 (T1) | integer 0..99; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R508 | First discount % - InterLATA | 0AE7/1 (T1) | integer 0..99; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R509 | Second discount % - InterLATA | 0AE8/1 (T1) | integer 0..99; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R510 | First discount % - Interstate | 0AE9/1 (T1) | integer 0..99; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R511 | Second discount % - Interstate | 0AEA/1 (T1) | integer 0..99; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R512 | User-defined macro 51 command table | 0350/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R513 | User-defined macro 52 command table | 036A/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R514 | User-defined macro 53 command table | 0384/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R515 | User-defined macro 54 command table | 039E/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R516 | User-defined macro 55 command table | 03B8/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R517 | User-defined macro 56 command table | 03D2/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R518 | User-defined macro 57 command table | 03EC/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R519 | User-defined macro 58 command table | 0406/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R520 | User-defined macro 59 command table | 0420/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R521 | User-defined macro 60 command table | 043A/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R522 | User-defined macro 61 command table | 0454/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R523 | User-defined macro 62 command table | 046E/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R524 | User-defined macro 63 command table | 0488/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R525 | User-defined macro 64 command table | 04A2/26 (T6) | 26 raw command/operand bytes; not a macro ID | 01.03.00 | documented |
| R550 | Hopper Volume | 0AF7/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R551 | Cash-box volume | 0AF8/2 (T4) | integer 0..999; dollars (stored as nickels) | 01.03.00 | documented |
| R552 | Answer Detect Sensitivity | 0AE1/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.02.00, 01.03.00 | documented |
| R553 | Time to ignore coins on power up | 0AD3/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R554 | Low Frequency Voice Detect Sensitivity | 0AD4/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | documented |
| R555 | Spare | 0AD5/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | reserved/proprietary; behavior unknown |
| R556 | Spare | 0AD6/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.03.00 | reserved/proprietary; behavior unknown |
| R557 | Spare | 0AD7/2 (T5) | integer 0..9999; not established unless stated in name/notes | 01.03.00 | reserved/proprietary; behavior unknown |
| R558 | Spare | 0AD9/2 (T5) | integer 0..9999; not established unless stated in name/notes | 01.03.00 | reserved/proprietary; behavior unknown |
| R602 | Price for 950-xxxx calls | 0AAA/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R603 | Price for 976-xxxx calls | 0AAB/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R604 | Price for 411 information calls | 0AAC/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R605 | Price for 1-411 information calls | 0AAD/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R606 | Price for 555-1212 information calls | 0AAE/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R607 | Price for 1-555-1212 information calls | 0AAF/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R608 | Price for Intra-state information calls | 0AB0/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R609 | Price for Inter-state information calls | 0AB1/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R610 | Voice mail price for 0+ | 0AB2/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.01.00, 01.02.00, 01.03.00 | documented |
| R611 | Voice mail price for local | 0AB3/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.01.00, 01.02.00, 01.03.00 | documented |
| R612 | Voice mail price for 1+ | 0AB4/1 (T3) | $0.00..$9.95 in $0.05 increments; dollars (stored as nickels) | 01.01.00, 01.02.00, 01.03.00 | documented |
| R701 | Alarm 1 - SMDR buffer damaged | 0AC5b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R702 | Alarm 2 - handset | 0AC5b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R703 | Alarm 3 - cashbox/vault bypass code | 0AC5b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R704 | Alarm 4 - program running from ROM | 0AC5b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R705 | Alarm 5 - rate RAM reload | 0AC5b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R706 | Alarm 6 - cashbox trigger | 0AC5b6 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R707 | Alarm 7 - cashbox full | 0AC5b7 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R708 | Alarm 8 - inactivity | 0AC5b8 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R709 | Alarm 9 - coin jam - walkaway | 0AC6b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R710 | Alarm 10 - bad rates | 0AC6b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R711 | Alarm 11 - call counts cleared | 0AC6b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R712 | Alarm 12 - change in master block | 0AC6b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R713 | Alarm 13 - entry into telemetry mode | 0AC6b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R714 | Alarm 14 - bad downloaded program | 0AC6b6 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R715 | Alarm 15 - SMDR Buffer 80% full | 0AC6b7 (T8) | ON/OFF; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R716 | Alarm 16 - SMDR Buffer 100% full | 0AC6b8 (T8) | ON/OFF; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R717 | Alarm 17 - bad registers and options | 0AC7b1 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R718 | Alarm 18 - force call home | 0AC7b2 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R719 | Alarm 19 - validation system alarm | 0AC7b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R720 | Alarm 20 - Billing records buffer 100% full | 0AC7b4 (T8) | ON/OFF; percent | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R721 | Alarm 21 - clock alarm | 0AC7b5 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R724 | Alarm 24 - Corrupt scrollable message | 0AC7b8 (T8) | ON/OFF | 01.03.00 | documented |
| R727 | Alarm 27 - reverse polarity alarm | 0AC8b3 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R728 | Alarm 28 - Low battery alarm | 0AC8b4 (T8) | ON/OFF | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R750 | Cash vault alarm trigger level | 0ACA/2 (T4) | integer 0..999; dollars (stored as nickels) | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R751 | Inactivity timer | 0ACC/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R752 | Coin jam alarm threshold | 0ACD/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |
| R753 | VDC unsuccessful access | 0ACE/1 (T1) | integer 0..99; not established unless stated in name/notes | 01.00.00, 01.01.00, 01.02.00, 01.03.00 | documented |

### KX parameter notes

- **R100**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R101**: Enables use of PBX prefix R341; does not itself contain the prefix. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R102**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R103**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R104**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R105**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R106**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R107**: Enables the tariff periods R503-R505 and discount percentages R506-R511. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R108**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R109**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R110**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R111**: Enables the old/new NPA pair R460/R459. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R112**: Enables the old/new NPA pair R462/R461. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R113**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R114**: Enables the old/new NPA pair R449/R448. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R115**: Enables the old/new NPA pair R451/R450. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R116**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R117**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R118**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R119**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R120**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R121**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R123**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R124**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R125**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R126**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R128**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R130**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R131**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R132**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R133**: Negative-polarity option: ON disables relay pre-charging, rather than enabling it. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R134**: Negative-polarity option: ON selects 'Do NOT correct user dialing'. ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R135**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R136**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R137**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R138**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R140**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R141**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R142**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R145**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R146**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R147**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R162**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R164**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R165**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R166**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R167**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R180**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R181**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R182**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R183**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R184**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R185**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R186**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R187**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R188**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R189**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R190**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R191**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R192**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R193**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R194**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R195**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R196**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R197**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R198**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R199**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R200**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R201**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R202**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R203**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R204**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R205**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R206**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R207**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R208**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R209**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R210**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R211**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R212**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R213**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R214**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R215**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R216**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R217**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R218**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R219**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R220**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R221**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R222**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R223**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R224**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R225**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R226**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R227**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R228**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R229**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R230**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R231**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R232**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R233**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R234**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R235**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R236**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R237**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R238**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R239**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R240**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R241**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R242**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R243**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R244**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R245**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R246**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R247**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R248**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R249**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R250**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R251**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R252**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R253**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R254**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R255**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R256**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R257**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R258**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R259**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R260**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R261**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R262**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R263**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R264**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R265**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R266**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R267**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R268**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R269**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R270**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R271**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R272**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R273**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R274**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R275**: Selects a processing macro for this call type. Does not contain a price or an instruction opcode.
- **R400**: Length-prefixed binary digits, not ASCII. Sensitive station credential.
- **R402**: Short binary-digit ID or biased 10-digit packed BCD, followed by checksum; see FORMAT.md.
- **R403**: Length-prefixed ASCII, not binary dial digits. Sensitive station credential.
- **R404**: Length-prefixed binary digits; supplied from the phone's ANI field.
- **R422**: The selected routing class and lower classes are reclassified as call type 35 and use R235's macro. Zero disables this reclassification. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R423**: These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established. Zero disables this feature. With a nonzero threshold, local calls through that price band remain call type 4; higher local bands become call type 18 and use R218's macro.
- **R424**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R425**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R426**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R427**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R428**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R429**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R430**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R431**: Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R437**: UI value is days; C94 stores hours (days x 24). Do not interpret the byte directly as days.
- **R453**: Stored mode meanings do not establish feature availability. The checked 01.02 build omits coin-line processing; a checked 01.03 build includes it. Hybrid/Bright require a capable firmware build, hardware and coin-line service; this file does not identify build capabilities. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R456**: Dialing-speed setting; timebase and enum meanings are not established by the UI label.
- **R463**: Beginning of shutdown interval 1; R464 ends it. R468 bit 0 chooses affected call types.
- **R464**: End of shutdown interval 1, paired with R463.
- **R465**: Beginning of shutdown interval 2; R466 ends it. R468 bit 1 chooses affected call types.
- **R466**: End of shutdown interval 2, paired with R465.
- **R468**: 100 bytes indexed by call type 0..99, not by macro number. Bit 0 restricts interval 1; bit 1 restricts interval 2. Bits 2..7 are not decoded.
- **R472**: Language selector; English/Spanish are documented. French is confirmed for KX 01.03.00, not inferred for LP.
- **R473**: LCD width in characters (16 or 20); an LP interpretation borrowed from KX remains an inference. Select the physical LCD line width, not a mode number. Zero selects 16 in display initialization, but is not confirmed as a safe default throughout display handling. These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.
- **R501**: Four initial volume codes (0-3) are used; the volume button cycles modulo four. Exact acoustic gains and ordering are unresolved, so no ascending-volume or dB labels are assigned.
- **R550**: Programmable coin/hopper setting. LP 05.04.00 set-like code forces this from defaults rather than user input.
- **R551**: Cash-box volume setting. LP 05.04.00 set-like code forces this from defaults rather than user input.
- **R701**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R702**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R703**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R704**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R705**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R706**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R707**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R708**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R709**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R710**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R711**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R712**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R713**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R714**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R715**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R716**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R717**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R718**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R719**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R720**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R721**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R724**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R727**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.
- **R728**: ON means the factory label is asserted; preserve negative labels such as 'Disable'.

## Built-in macro numbers

Names are the database's factory definitions, not descriptions inferred from
the bytecode. KX database IDs are the phone-visible number plus 50.
User-defined macro IDs from phone/customer records are not exported.

| Family | Phone macro number | Factory name |
|---|---|---|
| LP | 0 | Restricted Calls |
| LP | 1 | Direct Dial Open Mic Immediately |
| LP | 2 | Direct Dial Without Subsequent Dialing |
| LP | 4 | Call Home |
| LP | 5 | 0+ to LEC |
| LP | 6 | Manual OCC/IXC |
| LP | 7 | MCI 950, 800, Access #1 |
| LP | 8 | 10XXX IXC Access #1 |
| LP | 9 | Sprint 950, 800 Access #1 |
| LP | 10 | MCI 950, 800, Access #2 |
| LP | 11 | 10XXX IXC Access #2 |
| LP | 12 | Sprint 950, 800 Access #2 |
| LP | 13 | 0+, 0- to MCI (PIC) |
| LP | 14 | Service Desk |
| LP | 16 | Coin Line Calls |
| LP | 17 | PayPhone Call Home - Local Coin Line Access |
| LP | 18 | Service Desk - Local Coin Line access |
| LP | 19 | 10XXX OSP Access #1 |
| LP | 20 | ITI (Live Operator) |
| LP | 21 | ITI MACE (With BONG Detect) |
| LP | 22 | USLD |
| LP | 23 | AMNEX 0+ |
| LP | 24 | AMNEX 0- |
| LP | 25 | 10XXX NTS Access (Old) |
| LP | 26 | Telesphere |
| LP | 27 | 10XXX OSP Access #2 |
| LP | 28 | ITI #2 (Live Operator) |
| LP | 29 | ITI MACE #2 (With BONG Detect) |
| LP | 30 | NTS #2 (OLD) |
| LP | 31 | AMNEX 0+ #2 |
| LP | 32 | AMNEX 0- #2 |
| LP | 38 | PAOF Collect with voice recording |
| LP | 39 | PAOF Collect without recording |
| LP | 40 | ELCOTEL PAOF Modem Validation |
| LP | 41 | ELCOTEL PAOF Record dump |
| LP | 42 | Auto IXC MCI Sprint |
| LP | 44 | International 1+ |
| KX | 0 | Restricted Calls |
| KX | 1 | Direct Dial Open Mic Immediately |
| KX | 2 | Direct Dial Without Subsequent Dialing |
| KX | 3 | Call Home |
| KX | 4 | 0+ to LEC |
| KX | 5 | Manual OCC/IXC |
| KX | 6 | MCI 950, 800, Access #1 |
| KX | 7 | 10XXX IXC Access #1 |
| KX | 8 | Sprint 950, 800 Access #1 |
| KX | 9 | MCI 950, 800, Access #2 |
| KX | 10 | 10XXX IXC Access #2 |
| KX | 11 | Sprint 950, 800 Access #2 |
| KX | 12 | 0+, 0- to MCI (PIC) |
| KX | 13 | Service Desk |
| KX | 14 | 10XXX OSP Access #1 |
| KX | 15 | ITI (Live Operator) |
| KX | 16 | ITI MACE (With BONG Detect) |
| KX | 17 | USLD |
| KX | 18 | AMNEX 0+ |
| KX | 19 | AMNEX 0- |
| KX | 20 | 10XXX NTS Access (Old) |
| KX | 21 | Telesphere |
| KX | 22 | 10XXX OSP Access #2 |
| KX | 23 | ITI #2 (Live Operator) |
| KX | 24 | ITI MACE #2 (With BONG Detect) |
| KX | 25 | NTS #2 (OLD) |
| KX | 26 | AMNEX 0+ #2 |
| KX | 27 | AMNEX 0- #2 |

## Inline macro instructions

Programs have 26 **bytes**, not necessarily 26 instructions. Parameterized
opcodes consume the next byte as an operand. Opcode 69 / subcommand 11
also consumes a delay byte. Zero slots are padding; the host editor scans
the entire array rather than treating the first zero as a mandatory terminator.
Unknown opcodes remain unknown; disassembly after one may be ambiguous.

| Family | Opcode | Operation | Operand |
|---|---|---|---|
| LP | 1 | Wait 1 second | none |
| LP | 2 | Wait 2 seconds | none |
| LP | 10 | Say "One Moment Please" | none |
| LP | 11 | Say "Invalid Number" | none |
| LP | 12 | Disable keypad | none |
| LP | 13 | Enable keypad | none |
| LP | 14 | Disable handset microphone | none |
| LP | 15 | Enable handset microphone | none |
| LP | 16 | Splash back - dial direct | none |
| LP | 17 | Reroute call to secondary service | none |
| LP | 18 | Say "Please dial again" then hang up | none |
| LP | 19 | Convert 1+ to 0+ | none |
| LP | 20 | Convert 0+ to 1+ | none |
| LP | 21 | Collect money | none |
| LP | 22 | Correct special area dialing to LEC | none |
| LP | 23 | Remove "1" or "0" and add "NPA" | none |
| LP | 24 | Block 01 and 0809 from 950 and 1-800 manual IXC | none |
| LP | 25 | Wait then say "One moment please" | none |
| LP | 26 | Add NPA | none |
| LP | 27 | Report the previous SMDR for Service Desk | none |
| LP | 28 | Next digit will be Service Desk credit | none |
| LP | 29 | Look for 2.5 seconds of progress tone | none |
| LP | 30 | Initiate dialing sequence | none |
| LP | 31 | Await progress tone, stop busy trunk reroute timer | none |
| LP | 32 | Await voice, open MIC, SIT det. anti-fraud enable keypad | none |
| LP | 33 | Voice detect for non sent paid (no coinage) calls | none |
| LP | 34 | Wait for voice, open MIC, start antifraud, disable keypad | none |
| LP | 35 | Start answer detect for IXC (if ringbacks are detected) | none |
| LP | 36 | Special voice detect for OSPs | none |
| LP | 37 | Wait for XX seconds | Enter seconds to wait |
| LP | 38 | 1 second wait | none |
| LP | 39 | Skip the next command conditionally | none |
| LP | 40 | Enable handset earpiece | none |
| LP | 41 | Wait for BONG, send credit card number | none |
| LP | 42 | Wait for dial tone BONG, send credit card in 1 second | none |
| LP | 43 | Wait for BONG, send credit card | none |
| LP | 44 | Wait for DTMF "#" | none |
| LP | 45 | Wait for DTMF XX | DTMF |
| LP | 46 | Set up 35 second reroute timer | none |
| LP | 47 | Fast dialing speed (75 ms/75 ms) | none |
| LP | 48 | Slow dialing speed (100 ms/75ms) | none |
| LP | 50 | Remove expiration date from CCC | none |
| LP | 51 | Wait 1/2 second | none |
| LP | 54 | Start coin line processing | none |
| LP | 55 | Voice detect for coin line | none |
| LP | 56 | Set local coin line initial rate | none |
| LP | 57 | ELCOTEL PAOF validation | none |
| LP | 58 | ELCOTEL PAOF record dump | none |
| LP | 59 | Send credit card buffer in 1 second | none |
| LP | 61 | Say a word of voice in DL | none |
| LP | 62 | Start looking for WINK in XX seconds | Enter number of secods |
| LP | 63 | Block 0- converted to 01 with "#" | none |
| LP | 64 | Send DTMF "#" | none |
| LP | 65 | Send DTMF XX | DTMF |
| LP | 66 | Call completion timer XX | Enter time in seconds |
| LP | 67 | Re-reroute to Service Desk | none |
| LP | 68 | DTMF return code XX | DTMF |
| LP | 69 | Alternate commands | TBD |
| LP | 70 | Dial user dialed destination number | none |
| LP | 71 | IXC 800/950 Access #1 (310) | none |
| LP | 72 | IXC 800/950 Auth  #1 (311) | none |
| LP | 73 | OSP 800/950 Access #1 (319) | none |
| LP | 74 | OSP 800/950 Auth  #1 (320) | none |
| LP | 75 | IXC 800/950 Auth  #2 (314) | none |
| LP | 76 | OSP 800/950 Access #2 (322) | none |
| LP | 77 | OSP 800/950 Auth  #2 (323) | none |
| LP | 78 | PAOF Auth code for VDC (344) | none |
| LP | 79 | OSP 10xxx Access # 1 (331) | none |
| LP | 80 | OSP 10xxx Access # 2 (332) | none |
| LP | 81 | Dial Service Desk (338) | none |
| LP | 85 | Dial credit card buffer | none |
| LP | 86 | Dial station ID number (402) | none |
| LP | 87 | PAOF VDC Access (342) | none |
| LP | 91 | IXC 10xxx Access #2 (328) | none |
| LP | 92 | IXC 10xxx Access #1 (325) | none |
| LP | 94 | IXC 950 Access #2 (313) | none |
| KX | 1 | Wait 1 second | none |
| KX | 2 | Wait 2 seconds | none |
| KX | 10 | Say "One Moment Please" | none |
| KX | 11 | Say "Invalid Number" | none |
| KX | 12 | Disable keypad | none |
| KX | 13 | Enable keypad | none |
| KX | 14 | Disable handset microphone | none |
| KX | 15 | Enable handset microphone | none |
| KX | 16 | Splash back - dial direct | none |
| KX | 17 | Reroute call to secondary service | none |
| KX | 18 | Say "Please dial again" then hang up | none |
| KX | 19 | Convert 1+ to 0+ | none |
| KX | 20 | Convert 0+ to 1+ | none |
| KX | 21 | Collect money | none |
| KX | 22 | Correct special area dialing to LEC | none |
| KX | 23 | Remove "1" or "0" and add "NPA" | none |
| KX | 24 | Block 01 and 0809 from 950 and 1-800 manual IXC | none |
| KX | 25 | Wait then say "One moment please" | none |
| KX | 26 | Add NPA | none |
| KX | 27 | Report the previous SMDR for Service Desk | none |
| KX | 28 | Next digit will be Service Desk credit | none |
| KX | 29 | Look for 2.5 seconds of progress tone | none |
| KX | 30 | Initiate dialing sequence | none |
| KX | 31 | Await progress tone, stop busy trunk reroute timer | none |
| KX | 32 | Await voice, open MIC, SIT det. anti-fraud enable keypad | none |
| KX | 33 | Voice detect for non sent paid (no coinage) calls | none |
| KX | 34 | Wait for voice, open MIC, start antifraud, disable keypad | none |
| KX | 35 | Start answer detect for IXC (if ringbacks are detected) | none |
| KX | 36 | Special voice detect for OSPs | none |
| KX | 37 | Wait for XX seconds | Enter seconds to wait |
| KX | 38 | 1 second wait | none |
| KX | 39 | Skip the next command conditionally | none |
| KX | 40 | Enable handset earpiece | none |
| KX | 41 | Wait for BONG, send credit card number | none |
| KX | 42 | Wait for dial tone BONG, send credit card in 1 second | none |
| KX | 43 | Wait for BONG, send credit card | none |
| KX | 44 | Wait for DTMF "#" | none |
| KX | 45 | Wait for DTMF XX | DTMF |
| KX | 46 | Set up 35 second reroute timer | none |
| KX | 47 | Fast dialing speed (75 ms/75 ms) | none |
| KX | 48 | Slow dialing speed (100 ms/75ms) | none |
| KX | 50 | Remove expiration date from CCC | none |
| KX | 51 | Wait 1/2 second | none |
| KX | 54 | Start coin line processing | none |
| KX | 55 | Voice detect for coin line | none |
| KX | 56 | Set local coin line initial rate | none |
| KX | 58 | DAS record dump | none |
| KX | 59 | Send credit card buffer in 1 second | none |
| KX | 61 | Say a word of voice in DL | none |
| KX | 62 | Start looking for WINK in XX seconds | Enter number of secods |
| KX | 63 | Block 0- converted to 01 with "#" | none |
| KX | 64 | Send DTMF "#" | none |
| KX | 65 | Send DTMF XX | DTMF |
| KX | 66 | Call completion timer XX | Enter time in seconds |
| KX | 67 | Re-reroute to Service Desk | none |
| KX | 68 | DTMF return code XX | DTMF |
| KX | 69 | Alternate commands | TBD |
| KX | 70 | Dial user dialed destination number | none |
| KX | 71 | IXC 800/950 Access #1 (310) | none |
| KX | 72 | IXC 800/950 Auth  #1 (311) | none |
| KX | 73 | OSP 800/950 Access #1 (319) | none |
| KX | 74 | OSP 800/950 Auth  #1 (320) | none |
| KX | 75 | IXC 800/950 Auth  #2 (314) | none |
| KX | 76 | OSP 800/950 Access #2 (322) | none |
| KX | 77 | OSP 800/950 Auth  #2 (323) | none |
| KX | 79 | OSP 10xxx Access # 1 (331) | none |
| KX | 80 | OSP 10xxx Access # 2 (332) | none |
| KX | 81 | Dial Service Desk (338) | none |
| KX | 85 | Dial credit card buffer | none |
| KX | 86 | Dial station ID number (402) | none |
| KX | 91 | IXC 10xxx Access #2 (328) | none |
| KX | 92 | IXC 10xxx Access #1 (325) | none |
| KX | 94 | IXC 950 Access #2 (313) | none |

### Operand-dependent operations

- Opcode **68**, operand **1**: If DTMF # detected, send credit card buffer.
- Opcode **68**, operand **2**: If DTMF B detected, splash back.
- Opcode **68**, operand **4**: If DTMF * detected, say previous call number and amount.
- Opcode **68**, operand **17**: User-defined return macro (Reg 306).
- Opcode **68**, operand **18**: User-defined return macro (Reg 307).
- Opcode **68**, operand **19**: User-defined return macro (Reg 308).
- Opcode **69**, operand **2**: Say 'Payphone not ...' (abbreviated label).
- Opcode **69**, operand **3**: Special processing to AMNEX.
- Opcode **69**, operand **4**: PAOF collect with voice recording.
- Opcode **69**, operand **5**: Point voice to speak locally only.
- Opcode **69**, operand **7**: PF collect 'To accept ...' (abbreviated label).
- Opcode **69**, operand **8**: Say second brand for PAOF.
- Opcode **69**, operand **9**: PF terminate collect call.
- Opcode **69**, operand **10**: Speak first brand if present.
- Opcode **69**, operand **11**: Delay an additional operand's number of seconds before producing coin tones.

## What is still not established

Undocumented flags, proprietary features, unspecified timer scales, numeric
mode legends, hardware-specific coin calibration units, and high bits of R468
are not reverse-engineered just because their offsets are known. The table
above retains them explicitly. Cross-family names require firmware/manual
confirmation before they can be treated as confirmed for that model.

R340 has no established semantic name. It is a 16-byte counted dial-string
field at body offset 09F4 in every supported map; its purpose is unknown.
