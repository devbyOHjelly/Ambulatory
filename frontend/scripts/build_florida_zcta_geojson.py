"""
One-time (or refresh) build: US ZCTA shapefile -> Florida-only simplified GeoJSON.

Uses the same logic as Census workflows: intersect ZCTAs with the official
TIGER *state* polygon for Florida (STUSPS == "FL"), so Georgia/Alabama ZCTAs
that only appeared because of a rectangular bbox are excluded.

Requires: geopandas

Place tl_2024_us_state.shp (+ sidecars) in data/polygons/, or the script will
download tl_2024_us_state.zip from Census on first run.

Run from repo root or frontend:
  python scripts/build_florida_zcta_geojson.py
"""
from __future__ import annotations

import tempfile
import urllib.request
import zipfile
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
POLY = ROOT / "data" / "polygons"
ZCTA_SHP = POLY / "tl_2024_us_zcta520.shp"
STATE_SHP = POLY / "tl_2024_us_state.shp"
OUT = POLY / "florida_zcta520.geojson"

STATE_ZIP_URL = "https://www2.census.gov/geo/tiger/TIGER2024/STATE/tl_2024_us_state.zip"

# Prefilter ZCTAs (same CRS as shapefile: NAD83 geographic). Full US read is huge.
FL_BBOX = (-87.9, 24.2, -79.6, 31.2)


def _ensure_state_shapefile() -> None:
    if STATE_SHP.is_file():
        return
    print("Downloading tl_2024_us_state.zip (TIGER 2024 state boundaries)...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        zip_path = tmp / "tl_2024_us_state.zip"
        urllib.request.urlretrieve(STATE_ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(POLY)
    if not STATE_SHP.is_file():
        raise SystemExit(f"Expected after extract: {STATE_SHP}")


def main() -> None:
    if not ZCTA_SHP.is_file():
        raise SystemExit(f"Missing shapefile: {ZCTA_SHP}")
    _ensure_state_shapefile()

    print("Loading Florida state polygon (TIGER tl_2024_us_state)...")
    states = gpd.read_file(STATE_SHP)
    fl = states[states["STUSPS"] == "FL"].copy()
    if fl.empty:
        raise SystemExit('No row with STUSPS == "FL" in tl_2024_us_state.shp')
    fl = fl.dissolve()

    print("Reading ZCTAs in Florida bbox (this may take a minute)...")
    zcta = gpd.read_file(ZCTA_SHP, bbox=FL_BBOX)
    print(f"  features after bbox: {len(zcta)}")
    zcta = zcta.to_crs(fl.crs)

    fl_zcta = gpd.overlay(zcta, fl, how="intersection", keep_geom_type=False)
    fl_zcta = fl_zcta[~fl_zcta.geometry.is_empty & fl_zcta.geometry.notna()]
    # Intersection can yield degenerate LineStrings; choropleth needs areal geometry
    fl_zcta = fl_zcta[fl_zcta.geometry.geom_type.isin(("Polygon", "MultiPolygon"))].copy()
    print(f"  features after intersection with FL: {len(fl_zcta)}")

    # Choropleth only needs ZCTA id + geometry; drop merged state columns
    keep = [c for c in ("ZCTA5CE20", "GEOID20") if c in fl_zcta.columns]
    if not keep:
        raise SystemExit(f"Unexpected columns after overlay: {list(fl_zcta.columns)}")
    id_col = "ZCTA5CE20" if "ZCTA5CE20" in fl_zcta.columns else "GEOID20"
    fl_zcta = fl_zcta[[id_col, "geometry"]].rename(columns={id_col: "ZCTA5CE20"})

    fl_zcta = fl_zcta.to_crs(4326)
    fl_zcta["geometry"] = fl_zcta.geometry.simplify(0.0025, preserve_topology=True)
    fl_zcta = fl_zcta[~fl_zcta.geometry.is_empty & fl_zcta.geometry.notna()]

    fl_zcta.to_file(OUT, driver="GeoJSON")
    size_kb = OUT.stat().st_size // 1024
    print(f"Wrote {OUT} (~{size_kb} KB)")


if __name__ == "__main__":
    main()
