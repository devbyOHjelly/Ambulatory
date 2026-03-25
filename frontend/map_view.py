from __future__ import annotations

import hashlib

import plotly.graph_objects as go

from data import facilities
from data.business import Facility
from data.coverage_buckets import coverage_bucket
from data.zcta_geojson import florida_zcta_geojson


def _facility_hover(f: Facility) -> str:
    parts = [f"<b>{f.name}</b>", f"Type: {f.kind}", f"Service line: {f.service_line}"]
    if f.npi:
        parts.append(f"NPI: {f.npi}")
    if f.taxonomy:
        parts.append(f"NUCC: {f.taxonomy}")
    if f.volume and f.volume > 0:
        parts.append(f"Volume: {f.volume:,}")
    return "<br>".join(parts)


ACTIVE_LAYERS = ["coverage", "leakage", "access"]
APP_FONT_FAMILY = "Open Sans, Arial, sans-serif"

# Plotly Scattermapbox only applies marker color reliably for symbol="circle" on OSM / most styles.
# Diamond/square often render invisible — use circle + color + size to distinguish buckets.
_COVERAGE_STYLE = {
    "orlando_health": {"color": "#22c55e", "size": 12},
    "other_facility": {"color": "#ef4444", "size": 7},
    "lab_corporation": {"color": "#f59e0b", "size": 10},
}

# Draw order: many points first (bottom), rarer categories on top so they are not covered
_COVERAGE_DRAW_ORDER = ("other_facility", "lab_corporation", "orlando_health")


def _jitter_lat_lon(f: Facility) -> tuple[float, float]:
    """NPPES points share ZCTA centroids; nudge each point slightly so layers don’t stack invisibly."""
    key = (f.npi or f.name or f"{f.lat},{f.lon}").encode()
    h = hashlib.md5(key).digest()
    ax = int.from_bytes(h[:4], "big") % 1001
    ay = int.from_bytes(h[4:8], "big") % 1001
    d = 0.00045  # ~50 m
    return f.lat + (ax / 500.0 - 1.0) * d, f.lon + (ay / 500.0 - 1.0) * d


def build_map(selected_service_line: str, drive_time_minutes: int) -> go.Figure:
    fig = go.Figure()

    # Florida ZCTA choropleth (light blue); GeoJSON from data/polygons/florida_zcta520.geojson
    gj = florida_zcta_geojson()
    if gj and gj.get("features"):
        zctas = [str(f["properties"]["ZCTA5CE20"]) for f in gj["features"] if f.get("properties")]
        if zctas:
            fig.add_trace(
                go.Choroplethmapbox(
                    geojson=gj,
                    locations=zctas,
                    z=[1.0] * len(zctas),
                    featureidkey="properties.ZCTA5CE20",
                    colorscale=[[0.0, "#7dd3fc"], [1.0, "#7dd3fc"]],
                    zmin=0,
                    zmax=2,
                    showscale=False,
                    marker_line_width=0.35,
                    marker_line_color="rgba(56, 189, 248, 0.55)",
                    marker_opacity=0.42,
                    hovertemplate="<b>ZCTA %{location}</b><extra></extra>",
                    name="ZCTA",
                    below="traces",
                )
            )

    # Coverage: Orlando Health, other facilities, lab corporations (mutually exclusive buckets)
    by_bucket: dict[str, list[Facility]] = {"orlando_health": [], "other_facility": [], "lab_corporation": []}
    for f in facilities:
        by_bucket[coverage_bucket(f)].append(f)
    dense = len(facilities) > 500
    for bucket in _COVERAGE_DRAW_ORDER:
        style = _COVERAGE_STYLE[bucket]
        points = by_bucket[bucket]
        if selected_service_line != "All":
            points = [p for p in points if p.service_line == selected_service_line]
        if not points:
            continue
        ms = style["size"] if dense else max(style["size"], 10)
        lats, lons = zip(*[_jitter_lat_lon(f) for f in points])
        fig.add_trace(
            go.Scattermapbox(
                lat=list(lats),
                lon=list(lons),
                mode="markers",
                name=bucket,
                marker={
                    "size": ms,
                    "color": style["color"],
                    "symbol": "circle",
                    "opacity": 0.92,
                },
                text=[_facility_hover(f) for f in points],
                hoverinfo="text",
            )
        )

    # Built-in dark basemap (Carto Dark Matter) — no Mapbox API key; loads like OSM.
    fig.update_layout(
        font={"family": APP_FONT_FAMILY},
        mapbox={
            "style": "carto-darkmatter",
            "zoom": 5.8,
            "center": {"lat": 27.9944, "lon": -81.7603},
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
    )
    return fig
