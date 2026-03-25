"""
ZIP-level opportunity index (no ML):

Opportunity = Population × (Competitor / (Our + 1)) × Access Score

Access Score (0–100): proximity gap — straight-line miles to nearest in-network site × 2,
capped at 100. If no in-network site exists in the filtered list, Access Score = 100.
"""

from __future__ import annotations

from typing import Any

from data import facilities
from data.leakage.leakage_scores import compute_florida_leakage_by_zip, is_our_system_facility
from data.map_access import nearest_our_facility_miles, zcta_centroids_from_geojson


def compute_zip_opportunity_table(
    *,
    service_line: str,
    top_n: int = 20,
) -> list[dict[str, Any]]:
    _, leak_detail = compute_florida_leakage_by_zip(list(facilities), service_line=service_line)
    cents = zcta_centroids_from_geojson()
    fl = list(facilities)
    out: list[dict[str, Any]] = []

    for z5, d in leak_detail.items():
        pop = float(d.get("population", 0))
        our = int(d.get("our", 0))
        comp = int(d.get("competitor", 0))
        c = cents.get(z5)
        if not c:
            continue
        d_mi, _ = nearest_our_facility_miles(
            c[0], c[1], fl, service_line=service_line, is_ours=is_our_system_facility
        )
        if d_mi is None:
            access = 100.0
        else:
            access = min(100.0, float(d_mi) * 2.0)
        ratio = comp / (our + 1)
        opportunity = pop * ratio * access
        out.append(
            {
                "zip": z5,
                "population": pop,
                "our": our,
                "competitor": comp,
                "access_score": access,
                "opportunity": opportunity,
            }
        )

    out.sort(key=lambda r: r["opportunity"], reverse=True)
    return out[:top_n]
