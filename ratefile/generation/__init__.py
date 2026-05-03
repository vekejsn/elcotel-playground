"""Expose the canonical discovery and compilation helpers for Elcotel generation."""

from .compiler import discovery_to_spec
from .discovery import (
    build_generation_request,
    discover_relationships,
    load_generation_request,
)

__all__ = [
    "build_generation_request",
    "discover_relationships",
    "discovery_to_spec",
    "load_generation_request",
]
