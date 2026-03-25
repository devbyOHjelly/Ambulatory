"""Load NPPES-derived Florida coverage facilities; taxonomy helpers for service line / kind."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from .business import Facility


def taxonomy_to_service_line(code: str) -> str:
    """Map NUCC Healthcare Provider Taxonomy Code to dashboard service line."""
    c = (code or "").strip().upper()
    if not c:
        return "Other"

    if c.startswith(("207RC", "207RI", "208G", "207SA")):
        return "Cardiology"
    if c.startswith("261QU"):
        return "Urgent Care"
    if c.startswith("291"):
        return "Diagnostics"
    if c.startswith(("2085", "207Z", "261QM", "261QF")):
        return "Diagnostics"
    if c.startswith(("207Q", "363A", "363L", "363F", "363M")):
        return "Primary Care"
    if c.startswith("207R"):
        return "Primary Care"
    if c.startswith(("282", "283", "286", "273", "275", "276", "302")):
        return "Other"
    if c.startswith("261"):
        return "Primary Care"
    return "Other"


def taxonomy_to_kind(code: str) -> str:
    c = (code or "").strip().upper()
    if not c:
        return "Organization"
    p3 = c[:3]
    if p3 in ("282", "283", "286"):
        return "Hospital"
    if p3 == "261":
        return "Clinic / center"
    if p3 in ("207", "208"):
        return "Physician / medical group"
    if p3 == "363":
        return "Advanced practice group"
    if p3 == "273":
        return "Residential facility"
    if p3 == "275":
        return "Substance use"
    if p3 == "276":
        return "Misc residential"
    if p3 == "302":
        return "Health maintenance org"
    if p3 == "291":
        return "Laboratory"
    return "Facility"


def load_florida_coverage_facilities(csv_path: Path | None = None) -> List[Facility]:
    path = csv_path or Path(__file__).resolve().parent / "nppes_florida_facilities.csv"
    if not path.is_file():
        return []
    df = pd.read_csv(path, dtype={"npi": str})
    out: List[Facility] = []
    for row in df.itertuples(index=False):
        out.append(
            Facility(
                name=str(row.name),
                kind=str(row.kind),
                owner=str(row.owner),
                lat=float(row.lat),
                lon=float(row.lon),
                service_line=str(row.service_line),
                volume=int(row.volume) if pd.notna(row.volume) else 0,
                npi=str(row.npi).strip() if pd.notna(row.npi) else None,
                taxonomy=str(row.taxonomy) if pd.notna(row.taxonomy) else None,
            )
        )
    return out
