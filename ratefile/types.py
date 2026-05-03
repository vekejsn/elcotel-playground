"""Define the authored-spec and compiled-model dataclasses used by R94 generation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HeaderSpec:
    """Describe the user-facing header values for an R94 file."""

    description: str = ""
    home_npa: str = ""
    home_nxx: str = ""
    is_ratefile: bool = True


@dataclass
class PriceBandSpec:
    """Describe one logical price band before it is numbered for R94 output."""

    band_id: str
    category: str
    initial_rate: int
    initial_time: int
    additional_rate: int
    additional_time: int


@dataclass
class NpaDefaultRule:
    """Describe a default NPA assignment in the high-level tariff spec."""

    npa: int | None = None
    npa_range: tuple[int, int] | None = None
    kind: str = "restricted"
    band_id: str | None = None
    raw_value: int | None = None


@dataclass
class NxxOverrideRule:
    """Describe an NXX-specific override for one NPA and one price band."""

    npa: int
    band_id: str
    dial_pattern: int
    flags: int = 0
    nxx: list[int] = field(default_factory=list)
    nxx_ranges: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class UnlistedRule:
    """Describe the fallback band and dial plan for one NPA/category bucket."""

    npa: int
    category: str
    band_id: str
    dial_pattern: int
    flags: int = 0


@dataclass
class SurchargeSpec:
    """Store the eight surcharge bytes used for one band category."""

    coin: int = 0
    paof_bell: int = 0
    paof_comm: int = 0
    paof_collect: int = 0
    paof_addtnl: int = 0
    chip_card: int = 0
    spare_1: int = 0
    spare_2: int = 0


@dataclass
class RateFileSpec:
    """Represent a high-level tariff specification before binary compilation."""

    header: HeaderSpec
    price_bands: list[PriceBandSpec]
    npa_defaults: list[NpaDefaultRule] = field(default_factory=list)
    nxx_overrides: list[NxxOverrideRule] = field(default_factory=list)
    unlisted: list[UnlistedRule] = field(default_factory=list)
    surcharges: dict[str, SurchargeSpec] = field(default_factory=dict)


@dataclass
class CompiledPriceBand:
    """Store one price band after category ordering and numeric indexing."""

    band_id: str
    band_index: int
    category: str
    group_sequence: int
    initial_rate: int
    initial_time: int
    additional_rate: int
    additional_time: int


@dataclass
class CompiledNpaPrice:
    """Store one byte from the compiled 800-entry default NPA table."""

    npa: int
    raw_value: int


@dataclass
class CompiledGroupRow:
    """Store one compiled NPA group-header row."""

    npa: int
    category: str
    nxx_table_count: int
    unlisted_price_band: int
    unlisted_dial_pattern: int
    flags: int


@dataclass
class CompiledNxxTable:
    """Store one compiled NXX bitmap table before byte packing."""

    npa: int
    category: str
    price_band: int
    dial_pattern: int
    flags: int
    enabled_nxx: set[int] = field(default_factory=set)


@dataclass
class CompiledRateFile:
    """Represent the fully compiled R94 structures ready for payload encoding."""

    header: HeaderSpec
    price_bands: list[CompiledPriceBand]
    npa_prices: list[CompiledNpaPrice]
    group_rows: list[CompiledGroupRow]
    nxx_tables: list[CompiledNxxTable]
    surcharges: dict[str, SurchargeSpec]
    template_header: bytes | None = None
