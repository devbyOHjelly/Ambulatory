"""
Florida ambulatory leakage proxy (no ML): ZIP-level competitor share × demand pressure.

- "Ours": NPI appears in leakage/our_npis.csv OR facility.owner == Orlando Health (seeded).
- "Competitors": all other providers in the NPPES facility list after filters.
- Join population by 5-digit ZIP (ZCTA); file is optional (uniform fallback).

Leakage score (0–100): min–max of raw = competitor_share × log1p(pop / max(providers,1))
across Florida ZCTAs with at least one provider.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

_LEAKAGE_DIR = Path(__file__).resolve().parent
_OUR_NPIS = _LEAKAGE_DIR / "our_npis.csv"
_POP_CSV = _LEAKAGE_DIR / "florida_population_by_zip.csv"


@lru_cache(maxsize=1)
def _load_our_npi_set() -> frozenset[str]:
    if not _OUR_NPIS.is_file():
        return frozenset()
    out: set[str] = set()
    with open(_OUR_NPIS, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            n = (row.get("npi") or row.get("NPI") or "").strip()
            if n:
                out.add(n)
    return frozenset(out)


@lru_cache(maxsize=1)
def _load_population_by_zip() -> dict[str, float]:
    """ZIP string -> population. Multiple column names allowed."""
    if not _POP_CSV.is_file():
        return {}
    out: dict[str, float] = {}
    with open(_POP_CSV, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        zcol = None
        pcol = None
        if r.fieldnames:
            low = {c.lower(): c for c in r.fieldnames}
            for cand in ("zip", "zcta", "zcta5", "zipcode", "geoid"):
                if cand in low:
                    zcol = low[cand]
                    break
            for cand in ("population", "pop", "estimate", "value", "total"):
                if cand in low:
                    pcol = low[cand]
                    break
        if not zcol or not pcol:
            return {}
        for row in r:
            z = "".join(c for c in str(row.get(zcol, "")) if c.isdigit())[:5]
            if len(z) < 5:
                continue
            try:
                p = float(row[pcol])
            except (TypeError, ValueError):
                continue
            if p > 0:
                out[z] = p
    return out


def is_our_system_facility(f: Any) -> bool:
    """True if facility counts as in-network (Orlando Health row or listed NPI)."""
    return _is_our_facility(f, _load_our_npi_set())


def _is_our_facility(f: Any, our_npis: set[str]) -> bool:
    if f.owner == "Orlando Health":
        return True
    if f.npi and str(f.npi).strip() in our_npis:
        return True
    return False


def compute_florida_leakage_by_zip(
    facilities: list[Any],
    *,
    service_line: str,
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """
    Returns:
      scores: zcta5 -> leakage score 0..100
      detail: zcta5 -> {our, competitor, population, providers_total}
    """
    import math

    our_npis = _load_our_npi_set()
    pop = _load_population_by_zip()
    default_pop = 12_000.0  # used only when ZIP missing from population file

    rows: dict[str, dict[str, int]] = {}
    for f in facilities:
        if service_line != "All" and f.service_line != service_line:
            continue
        z5 = "".join(c for c in str(getattr(f, "zip5", None) or "") if c.isdigit())[:5]
        if len(z5) < 5:
            continue
        bucket = rows.setdefault(z5, {"our": 0, "competitor": 0})
        if _is_our_facility(f, our_npis):
            bucket["our"] += 1
        else:
            bucket["competitor"] += 1

    raws: dict[str, float] = {}
    detail: dict[str, dict[str, float]] = {}
    for z5, b in rows.items():
        o, c = b["our"], b["competitor"]
        tot = o + c
        if tot == 0:
            continue
        p = float(pop.get(z5, default_pop))
        comp_share = c / tot
        pressure = p / max(tot, 1)
        raw = comp_share * math.log1p(pressure)
        raws[z5] = raw
        detail[z5] = {
            "our": float(o),
            "competitor": float(c),
            "population": p,
            "providers_total": float(tot),
            "raw": raw,
        }

    if not raws:
        return {}, {}

    vmin, vmax = min(raws.values()), max(raws.values())
    span = max(vmax - vmin, 1e-9)
    scores: dict[str, float] = {}
    for z5, raw in raws.items():
        scores[z5] = 100.0 * (raw - vmin) / span
        detail[z5]["leakage_score"] = scores[z5]
    return scores, detail


def leakage_hover_text(zcta: str, detail: dict[str, dict[str, float]]) -> str:
    d = detail.get(zcta)
    if not d:
        return f"<b>ZCTA {zcta}</b><br>No providers in filter"
    return (
        f"<b>ZCTA {zcta}</b><br>"
        f"Leakage score: {d['leakage_score']:.1f} / 100<br>"
        f"Population (est.): {d['population']:,.0f}<br>"
        f"Our providers: {d['our']:.0f}<br>"
        f"Competitor providers: {d['competitor']:.0f}<br>"
    )
