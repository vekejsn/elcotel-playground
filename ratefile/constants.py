from __future__ import annotations

HEADER_SIZE = 268
NPA_TABLE_SIZE = 800
SURCHARGE_OFFSET = 800
COUNTS_OFFSET = 864
GROUP_START_OFFSET = 890

ENUM_BAND_CATEGORIES = {
    0: "!",
    1: "Local",
    2: "IntraLATA",
    3: "InterLATA",
    4: "FCC",
    5: "Corridor",
    6: "Canadian",
    7: "Extended",
    8: "Misc",
}

CATEGORY_ORDER = [
    "local",
    "intralata",
    "interlata",
    "interstate",
    "corridor",
    "canadian",
    "extended",
    "misc",
]

CATEGORY_TITLE_MAP = {
    "local": "Local",
    "intralata": "IntraLATA",
    "interlata": "InterLATA",
    "interstate": "FCC",
    "fcc": "FCC",
    "corridor": "Corridor",
    "canadian": "Canadian",
    "extended": "Extended",
    "misc": "Misc",
}

DIAL_PLAN_MAP = {
    0: "7 digit",
    1: "1 + 7 digit",
    2: "10 digit (NPA)",
    3: "1 + 10 digit (NPA)",
}

RESTRICTED_TOKEN = 0
UNLIMITED_TOKEN = 253
NXX_SPECIFIC_TOKEN = 254
NXX_SPECIFIC_ALT_TOKEN = 255

NPA_MIN = 200
NPA_MAX = 999
NXX_MIN = 200
NXX_MAX = 999
