from __future__ import annotations

from pathlib import Path

from .business import FACILITIES_FALLBACK, Facility, flows, opportunities
from .nppes_coverage import load_florida_coverage_facilities

_NPPES_CSV = Path(__file__).resolve().parent / "nppes_florida_facilities.csv"
_nppes = load_florida_coverage_facilities(_NPPES_CSV)
facilities = _nppes if _nppes else FACILITIES_FALLBACK

__all__ = ["Facility", "facilities", "flows", "opportunities"]
