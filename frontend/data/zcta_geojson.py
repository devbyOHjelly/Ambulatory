from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_POLY_DIR = Path(__file__).resolve().parent / "polygons"
_GEOJSON_PATH = _POLY_DIR / "florida_zcta520.geojson"

_geojson_cache: dict[str, Any] | None = None


def florida_zcta_geojson() -> dict[str, Any] | None:
    """Load cached Florida ZCTA GeoJSON (build with scripts/build_florida_zcta_geojson.py)."""
    global _geojson_cache
    if _geojson_cache is not None:
        return _geojson_cache
    if not _GEOJSON_PATH.is_file():
        return None
    with open(_GEOJSON_PATH, encoding="utf-8") as f:
        _geojson_cache = json.load(f)
    return _geojson_cache
