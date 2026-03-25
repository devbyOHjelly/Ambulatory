"""
Build frontend/data/nppes_florida_facilities.csv from CMS NPPES + Florida ZCTA centroids.

NPPES has addresses but no coordinates; we place each row at its practice ZIP's
ZCTA centroid (5-digit ZIP ≈ ZCTA for mapping). Only Entity Type 2 (organization)
rows with facility-like NUCC taxonomy prefixes in FL are kept (~tens of k rows).

Requires: pandas, geopandas

Run from repo root (Ambulatory):
  python backend/scripts/build_florida_nppes_facilities.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parent
NPPES_DIR = BACKEND / "data" / "NPPES"
ZCTA_GEOJSON = REPO / "frontend" / "data" / "polygons" / "florida_zcta520.geojson"
OUT_CSV = REPO / "frontend" / "data" / "nppes_florida_facilities.csv"

# Include 291* (clinical / medical laboratories — Quest, hospital labs, etc.)
FACILITY_TAX_PREFIXES = ("261", "282", "283", "286", "273", "275", "276", "302", "291")

COLS = [
    "NPI",
    "Entity Type Code",
    "Provider Organization Name (Legal Business Name)",
    "Parent Organization LBN",
    "Provider Other Organization Name",
    "Provider Business Practice Location Address Postal Code",
    "Provider Business Practice Location Address State Name",
    "Healthcare Provider Taxonomy Code_1",
    "NPI Deactivation Date",
]


def _find_npidata_csv() -> Path:
    matches = sorted(NPPES_DIR.glob("npidata_pfile_*.csv"))
    if not matches:
        raise SystemExit(f"No npidata_pfile_*.csv under {NPPES_DIR}")
    for p in matches:
        if "fileheader" not in p.name.lower():
            return p
    return matches[0]


def _zcta_centroids() -> tuple[pd.Series, pd.Series]:
    if not ZCTA_GEOJSON.is_file():
        raise SystemExit(f"Missing Florida ZCTA GeoJSON (run ZCTA build first): {ZCTA_GEOJSON}")
    gdf = gpd.read_file(ZCTA_GEOJSON)
    if "ZCTA5CE20" not in gdf.columns:
        raise SystemExit("florida_zcta520.geojson missing ZCTA5CE20")
    zcta_ids = gdf["ZCTA5CE20"].astype(str)
    # Planar centroid (WGS84 geographic centroids are biased)
    gdf_p = gdf.to_crs(6457)
    c = gdf_p.geometry.centroid
    c_wgs = gpd.GeoSeries(c, crs=gdf_p.crs).to_crs(4326)
    lat_map = dict(zip(zcta_ids, c_wgs.y, strict=False))
    lon_map = dict(zip(zcta_ids, c_wgs.x, strict=False))
    return pd.Series(lat_map), pd.Series(lon_map)


def main() -> None:
    npi_path = _find_npidata_csv()
    print(f"NPPES file: {npi_path}")
    lat_s, lon_s = _zcta_centroids()
    print(f"ZCTA centroids: {len(lat_s)}")

    sys.path.insert(0, str(REPO / "frontend"))
    from data.nppes_coverage import taxonomy_to_kind, taxonomy_to_service_line  # noqa: E402

    parts: list[pd.DataFrame] = []
    chunk_n = 0
    for chunk in pd.read_csv(npi_path, usecols=COLS, dtype=str, chunksize=250_000, low_memory=False):
        chunk_n += 1
        fl = chunk[chunk["Provider Business Practice Location Address State Name"].fillna("").str.upper() == "FL"]
        org = fl[fl["Entity Type Code"].fillna("") == "2"]
        active = org[org["NPI Deactivation Date"].fillna("").str.strip() == ""]
        tax = active["Healthcare Provider Taxonomy Code_1"].fillna("").str.upper()
        blob_pre = (
            active["Provider Organization Name (Legal Business Name)"].fillna("").str.upper()
            + " "
            + active["Parent Organization LBN"].fillna("").str.upper()
            + " "
            + active["Provider Other Organization Name"].fillna("").str.upper()
        )
        orlando_name = blob_pre.str.contains("ORLANDO HEALTH", regex=False)
        fac_tax = tax.str[:3].isin(FACILITY_TAX_PREFIXES)
        # NPPES uses 207/208/363 for many org-type clinics; those were excluded and dropped most OH sites.
        fac = active[fac_tax | orlando_name].copy()
        if fac.empty:
            print(f"  chunk {chunk_n}: 0 FL org rows (facility tax or Orlando Health name)")
            continue

        z = fac["Provider Business Practice Location Address Postal Code"].fillna("").astype(str)
        digits = z.str.replace(r"\D", "", regex=True)
        fac["_zcta"] = digits.str[:5].where(digits.str.len() >= 5)
        fac = fac[fac["_zcta"].notna() & fac["_zcta"].isin(lat_s.index)]
        fac["lat"] = fac["_zcta"].map(lat_s)
        fac["lon"] = fac["_zcta"].map(lon_s)

        blob = (
            fac["Provider Organization Name (Legal Business Name)"].fillna("").str.upper()
            + " "
            + fac["Parent Organization LBN"].fillna("").str.upper()
            + " "
            + fac["Provider Other Organization Name"].fillna("").str.upper()
        )
        fac["owner"] = np.where(blob.str.contains("ORLANDO HEALTH", regex=False), "Orlando Health", "Competitor")

        tax_c = fac["Healthcare Provider Taxonomy Code_1"].fillna("").str.strip()
        fac["taxonomy"] = tax_c
        fac["kind"] = tax_c.map(taxonomy_to_kind)
        fac["service_line"] = tax_c.map(taxonomy_to_service_line)
        nm = fac["Provider Organization Name (Legal Business Name)"].fillna("").str.strip()
        fac["name"] = nm.where(nm.ne(""), "Unknown organization").str.slice(0, 500)
        fac["npi"] = fac["NPI"].astype(str).str.strip()
        fac["zip"] = fac["_zcta"]
        fac["volume"] = 0

        parts.append(
            fac[
                [
                    "npi",
                    "name",
                    "owner",
                    "kind",
                    "lat",
                    "lon",
                    "service_line",
                    "taxonomy",
                    "zip",
                    "volume",
                ]
            ]
        )
        print(f"  chunk {chunk_n}: wrote {len(fac)} FL org facility rows with ZCTA match")

    if not parts:
        raise SystemExit("No rows — check NPPES and ZCTA overlap.")

    df = pd.concat(parts, ignore_index=True)
    df = df.drop_duplicates(subset=["npi"], keep="first")
    df = df.sort_values(["owner", "name"])
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV} ({len(df)} facilities)")


if __name__ == "__main__":
    main()
