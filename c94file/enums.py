"""Confirmed enum labels, scoped to the firmware family/version checked."""

LP_54_ENUMS = {
    110: {"0": "Electronic coin mechanism (ECM)", "1": "Mechanical 20A coin mechanism"},
    422: {"0": "Disabled", "1": "Local", "2": "IntraLATA", "3": "InterLATA"},
    423: {"0": "Disabled", "1": "Local band 1", "2": "Local bands 1-2", "3": "Local bands 1-3"},
    453: {"0": "Smart (B-1 line; phone controls routing, rating and answer supervision)",
          "1": "Hybrid (coin line; phone or central office controls each call type)",
          "2": "Bright (coin line; central office controls routing, rating and answer supervision)"},
}

ANTI_FRAUD = {
    "0": "Keypad disabled; DTMF anti-fraud ON",
    "1": "Keypad enabled until wink/secondary dial tone; DTMF anti-fraud ON",
    "2": "Keypad continuously enabled; DTMF anti-fraud OFF",
}
# The default selector is not explicitly assigned the same legend; do not
# silently extend the confirmed call-type selectors to it.
for register in range(424, 431):
    LP_54_ENUMS[register] = dict(ANTI_FRAUD)

LP_54_NOTES = {
    110: "OFF selects an electronic coin mechanism; ON selects mechanical 20A. This selector applies to coin-line-capable Olympian 5501 hardware, not the Series-5 board.",
    422: "The selected routing class and lower classes are reclassified as call type 35 and use R235's macro. Zero disables this reclassification.",
    423: "Zero disables this feature. With a nonzero threshold, local calls through that price band remain call type 4; higher local bands become call type 18 and use R218's macro.",
    453: "Bright and Hybrid require coin-line-capable hardware and coin-line service. A Series-5 board without coin-line capability must use Smart mode on a B-1 line.",
    455: "Number of seconds the handset microphone is filtered to deter injected coin tones; this is a duration, not a mode enum.",
    478: "Inter-digit timeout in seconds, 0-7. Zero selects the default five-second timeout.",
    479: "Zero disables scheduled call-home. For a nonzero hour, the last two ANI digits select the minute; values over 59 are reduced by 60.",
    480: "Minutes of detected silence before going on-hook towards the central office. Zero disables this feature.",
    501: "Zero is the lowest starting volume and is required for correct operation of the optional volume-control button. The button cycles through four levels in 3 dB steps. The exact numeric-code-to-gain mapping for codes 1-3 is not independently confirmed.",
}


KX_01_ENUMS = {
    422: {"0": "Disabled", "1": "Local", "2": "IntraLATA", "3": "InterLATA"},
    423: {"0": "Disabled", "1": "Local band 1", "2": "Local bands 1-2", "3": "Local bands 1-3"},
    453: {"0": "Smart / COCOT (B-1 line)", "1": "Hybrid (coin line)", "2": "Bright (coin line)"},
    473: {"16": "16 characters per LCD line", "20": "20 characters per LCD line"},
}
for register in range(424, 432):
    KX_01_ENUMS[register] = {
        "0": "Keypad disabled; DTMF anti-fraud ON",
        "1": "Keypad enabled; DTMF anti-fraud ON",
        "2": "Keypad enabled; DTMF anti-fraud OFF",
    }


def _kx_metadata(version: str, register: int) -> dict:
    # Only the checked branches receive labels; do not backport to 01.00/01.01.
    if not version.startswith(("01.02.", "01.03.")):
        return {}
    result = {}
    notes = []
    if register in KX_01_ENUMS:
        result["value_labels"] = dict(KX_01_ENUMS[register])
        result["enum_status"] = "verified in KX 01.02/01.03 branch handlers; individual builds may differ"
        notes.append("These meanings were checked in the 01.02/01.03 branches; exact behavior of every patch/build is not established.")
    if register in (422, 423):
        notes.append(LP_54_NOTES[register])
    if 424 <= register <= 431:
        notes.append("Mode 2 disables DTMF anti-fraud protection. Call handling can subsequently change keypad access; coin-line processing can override this selector. Test the installation's fraud protection.")
    if register == 453:
        notes.append("Stored mode meanings do not establish feature availability. The checked 01.02 build omits coin-line processing; a checked 01.03 build includes it. Hybrid/Bright require a capable firmware build, hardware and coin-line service; this file does not identify build capabilities.")
    if register == 473:
        notes.append("Select the physical LCD line width, not a mode number. Zero selects 16 in display initialization, but is not confirmed as a safe default throughout display handling.")
    if register == 501:
        result["enum_status"] = "gain meanings unresolved for KX 01.02/01.03"
        notes.append("Four initial volume codes (0-3) are used; the volume button cycles modulo four. Exact acoustic gains and ordering are unresolved, so no ascending-volume or dB labels are assigned.")
    if notes:
        result["notes"] = notes
    return result


def enum_metadata(family: str, version: str, register: int) -> dict:
    """Apply only labels checked for the selected firmware branch."""
    if family == "KX":
        return _kx_metadata(version, register)
    if family != "LP" or not version.startswith("05.04."):
        return {}
    result = {}
    if register in LP_54_ENUMS:
        result["value_labels"] = dict(LP_54_ENUMS[register])
        result["enum_status"] = "confirmed for LP 05.04"
    if register == 501:
        result["known_value_labels"] = {"0": "Lowest starting volume; required with volume-control button"}
        result["enum_status"] = "partially confirmed for LP 05.04; codes 1-3 unresolved"
    notes = []
    if register in LP_54_NOTES:
        notes.append(LP_54_NOTES[register])
    if 424 <= register <= 430:
        notes.append("Mode 2 disables DTMF anti-fraud protection. Use it only where secondary dial tone cannot reappear before a hookswitch action; test the installation's fraud protection.")
    if notes:
        result["notes"] = notes
    if register in (455, 478):
        result["units"] = "seconds"
    elif register == 480:
        result["units"] = "minutes"
    return result
