"""Map interaction: ZCTA centroids, great-circle distance, mile-radius rings for access view."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

_EARTH_MI = 3958.7613


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.asin(min(1.0, math.sqrt(a)))
    return _EARTH_MI * c


def circle_ring_latlon(lat0: float, lon0: float, radius_miles: float, n_points: int = 96) -> tuple[list[float], list[float]]:
    """Great-circle loop on the earth (closed)."""
    lat0r, lon0r = math.radians(lat0), math.radians(lon0)
    d = radius_miles / _EARTH_MI
    lats: list[float] = []
    lons: list[float] = []
    for i in range(n_points + 1):
        brng = 2 * math.pi * i / n_points
        lat1 = math.asin(
            math.sin(lat0r) * math.cos(d) + math.cos(lat0r) * math.sin(d) * math.cos(brng)
        )
        lon1 = lon0r + math.atan2(
            math.sin(brng) * math.sin(d) * math.cos(lat0r),
            math.cos(d) - math.sin(lat0r) * math.sin(lat1),
        )
        lats.append(math.degrees(lat1))
        lons.append((math.degrees(lon1) + 540) % 360 - 180)
    return lats, lons


@lru_cache(maxsize=1)
def _fl_geojson_path() -> Path:
    return Path(__file__).resolve().parent / "polygons" / "florida_zcta520.geojson"


@lru_cache(maxsize=1)
def zcta_centroids_from_geojson() -> dict[str, tuple[float, float]]:
    """ZCTA5 string -> (lat, lon) simple centroid of largest polygon ring."""
    p = _fl_geojson_path()
    if not p.is_file():
        return {}
    with open(p, encoding="utf-8") as f:
        gj = json.load(f)
    out: dict[str, tuple[float, float]] = {}
    for feat in gj.get("features") or []:
        props = feat.get("properties") or {}
        z = str(props.get("ZCTA5CE20", "")).strip()
        if len(z) < 5:
            continue
        z = z[:5]
        geom = feat.get("geometry") or {}
        t = geom.get("type")
        coords = geom.get("coordinates")
        if not coords:
            continue
        rings: list[list[list[float]]] = []
        if t == "Polygon":
            rings = [coords[0]]
        elif t == "MultiPolygon":
            for poly in coords:
                if poly:
                    rings.append(poly[0])
        if not rings:
            continue
        # pick ring with max point count as proxy for main mass
        main = max(rings, key=len)
        lats = [p[1] for p in main]
        lons = [p[0] for p in main]
        if not lats:
            continue
        out[z] = (sum(lats) / len(lats), sum(lons) / len(lons))
    return out


def nearest_our_facility_miles(
    lat: float,
    lon: float,
    facilities: list[Any],
    *,
    service_line: str,
    is_ours: Any,
) -> tuple[float | None, str | None]:
    """Min distance (mi) to an in-system site and its name."""
    best_d: float | None = None
    best_name: str | None = None
    for f in facilities:
        if service_line != "All" and getattr(f, "service_line", None) != service_line:
            continue
        if not is_ours(f):
            continue
        d = haversine_miles(lat, lon, float(f.lat), float(f.lon))
        if best_d is None or d < best_d:
            best_d = d
            best_name = str(getattr(f, "name", "") or "In-network site")
    return best_d, best_name
