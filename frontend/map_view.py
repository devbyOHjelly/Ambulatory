from __future__ import annotations

import hashlib
from typing import Any

import plotly.graph_objects as go
from dash import html

from data import facilities
from data.business import Facility
from data.coverage_buckets import coverage_bucket
from data.leakage.leakage_scores import compute_florida_leakage_by_zip, is_our_system_facility, leakage_hover_text
from data.map_access import (
    circle_ring_latlon,
    haversine_miles,
    nearest_our_facility_miles,
    zcta_centroids_from_geojson,
)
from data.zcta_geojson import florida_zcta_geojson


def _facility_hover(f: Facility) -> str:
    parts = [f"<b>{f.name}</b>", f"Type: {f.kind}", f"Service line: {f.service_line}"]
    if f.npi:
        parts.append(f"NPI: {f.npi}")
    if f.taxonomy:
        parts.append(f"NUCC: {f.taxonomy}")
    if f.zip5:
        parts.append(f"ZIP: {f.zip5}")
    if f.volume and f.volume > 0:
        parts.append(f"Volume: {f.volume:,}")
    return "<br>".join(parts)


ACTIVE_LAYERS = ["coverage", "leakage", "access"]
APP_FONT_FAMILY = "Open Sans, Arial, sans-serif"
# Match dashboard cards (#0f172a); white text for all map hovers
_HOVER_LABEL = {
    "bgcolor": "#0f172a",
    "bordercolor": "#334155",
    "font": {"color": "#ffffff", "family": APP_FONT_FAMILY, "size": 13},
    "align": "left",
}

_COVERAGE_STYLE = {
    "orlando_health": {"color": "#4ade80", "size": 11, "label": "In-network"},
    "other_facility": {"color": "#f87171", "size": 6, "label": "Competitor"},
    "lab_corporation": {"color": "#fbbf24", "size": 9, "label": "Lab corp"},
}

_COVERAGE_DRAW_ORDER = ("other_facility", "lab_corporation", "orlando_health")

_RING_MILES = (5, 10, 20)
# Single merged line trace (one Mapbox layer) is much faster than three separate traces.
_RING_LINE = {"color": "rgba(30, 41, 59, 0.98)", "width": 5}
_RING_N_POINTS = 24


def _jitter_lat_lon(f: Facility) -> tuple[float, float]:
    key = (f.npi or f.name or f"{f.lat},{f.lon}").encode()
    h = hashlib.md5(key).digest()
    ax = int.from_bytes(h[:4], "big") % 1001
    ay = int.from_bytes(h[4:8], "big") % 1001
    d = 0.00045
    return f.lat + (ax / 500.0 - 1.0) * d, f.lon + (ay / 500.0 - 1.0) * d


def parse_map_click(click_data: dict[str, Any] | None, *, service_line: str) -> dict[str, Any] | None:
    """Turn Plotly clickData into a selection dict for rings + insight panel."""
    if not click_data or not click_data.get("points"):
        return None
    pt = click_data["points"][0]
    loc = pt.get("location")
    if loc is not None and str(loc).strip():
        z = str(loc).strip()[:5]
        cents = zcta_centroids_from_geojson()
        c = cents.get(z)
        if c:
            return {"kind": "zcta", "zcta": z, "lat": c[0], "lon": c[1]}
        return {"kind": "zcta", "zcta": z, "lat": float(pt.get("lat", 27.99)), "lon": float(pt.get("lon", -81.76))}
    lat, lon = pt.get("lat"), pt.get("lon")
    if lat is None or lon is None:
        return None
    best: Facility | None = None
    best_d = 1e9
    flist = list(facilities)
    if service_line != "All":
        flist = [f for f in flist if f.service_line == service_line]
    for f in flist:
        d = haversine_miles(float(lat), float(lon), float(f.lat), float(f.lon))
        if d < best_d:
            best_d = d
            best = f
    if best is None or best_d > 12.0:
        return {"kind": "point", "lat": float(lat), "lon": float(lon), "zcta": None, "name": "Map location"}
    return {
        "kind": "facility",
        "lat": float(best.lat),
        "lon": float(best.lon),
        "name": str(best.name),
        "npi": str(best.npi) if best.npi else "",
        "zcta": (best.zip5 or "")[:5] if best.zip5 else None,
    }


def _append_range_rings(fig: go.Figure, lat: float, lon: float) -> None:
    lat_run: list[float | None] = []
    lon_run: list[float | None] = []
    for mi in _RING_MILES:
        rlats, rlons = circle_ring_latlon(lat, lon, float(mi), n_points=_RING_N_POINTS)
        if lat_run:
            lat_run.append(None)
            lon_run.append(None)
        lat_run.extend(rlats)
        lon_run.extend(rlons)
    fig.add_trace(
        go.Scattermapbox(
            lat=lat_run,
            lon=lon_run,
            mode="lines",
            line=_RING_LINE,
            hoverinfo="skip",
            showlegend=False,
        )
    )


def _insight_panel(
    selection: dict[str, Any] | None,
    leak_detail: dict[str, dict[str, float]],
    *,
    service_line: str,
) -> html.Div:
    idle = html.Div(
        style={
            "color": "#94a3b8",
            "fontSize": "13px",
            "lineHeight": "1.5",
            "maxWidth": "320px",
        },
        children="Click a ZIP (heatmap) or a provider dot to show 5 / 10 / 20 mile access rings and a short leakage summary.",
    )
    if not selection:
        return idle

    lat, lon = float(selection["lat"]), float(selection["lon"])
    kind = selection.get("kind", "point")
    zcta = selection.get("zcta")
    title = "Selected location"
    if kind == "zcta":
        title = f"ZIP {zcta}" if zcta else "ZIP"
    elif kind == "facility":
        title = str(selection.get("name") or "Provider")[:48]
        if zcta:
            title = f"{title} · ZIP {zcta}"
    elif kind == "point":
        title = "Map location"

    d_nearest, nearest_name = nearest_our_facility_miles(
        lat, lon, list(facilities), service_line=service_line, is_ours=is_our_system_facility
    )
    dist_line = (
        f"{d_nearest:.1f} mi to {nearest_name}"
        if d_nearest is not None
        else "No in-network site in this extract"
    )

    pop = our_c = comp_c = score = None
    zk = None
    if kind == "zcta" and zcta:
        zk = str(zcta).strip()[:5]
    elif kind == "facility" and zcta:
        zk = str(zcta).strip()[:5]
    if zk and zk in leak_detail:
        d = leak_detail[zk]
        pop = d.get("population")
        our_c = int(d.get("our", 0))
        comp_c = int(d.get("competitor", 0))
        score = d.get("leakage_score")

    metrics = [
        ("Population (ZIP)", f"{pop:,.0f}" if pop is not None else "—"),
        ("Our facilities (ZIP)", str(our_c) if our_c is not None else "—"),
        ("Competitor facilities (ZIP)", str(comp_c) if comp_c is not None else "—"),
        ("Leakage score (ZIP)", f"{score:.0f}/100" if score is not None else "—"),
        ("Nearest in-network", dist_line),
    ]

    return html.Div(
        style={
            "backgroundColor": "rgba(15,23,42,0.97)",
            "border": "1px solid #334155",
            "borderRadius": "12px",
            "padding": "14px 16px",
            "maxWidth": "320px",
            "boxShadow": "0 8px 24px rgba(0,0,0,0.35)",
        },
        children=[
            html.Div(
                "Selection",
                style={"fontSize": "10px", "textTransform": "uppercase", "letterSpacing": "0.08em", "color": "#64748b", "marginBottom": "6px"},
            ),
            html.Div(title, style={"fontWeight": "700", "fontSize": "15px", "color": "#f1f5f9", "marginBottom": "12px"}),
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                children=[
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "gap": "12px", "fontSize": "13px"},
                        children=[
                            html.Span(lbl, style={"color": "#94a3b8", "flexShrink": "0"}),
                            html.Span(val, style={"color": "#e2e8f0", "textAlign": "right"}),
                        ],
                    )
                    for lbl, val in metrics
                ],
            ),
            html.Div(
                "Proximity rings: 5, 10, and 20 statute miles (great-circle), not drive time.",
                style={"marginTop": "12px", "fontSize": "11px", "color": "#64748b", "lineHeight": "1.4"},
            ),
        ],
    )


def build_map_with_insight(
    selected_service_line: str,
    drive_time_minutes: int,
    selection: dict[str, Any] | None,
) -> tuple[go.Figure, html.Div]:
    _ = drive_time_minutes
    leak_scores, leak_detail = compute_florida_leakage_by_zip(
        list(facilities), service_line=selected_service_line
    )
    fig = go.Figure()
    gj = florida_zcta_geojson()

    if gj and gj.get("features"):
        zctas = [str(f["properties"]["ZCTA5CE20"]) for f in gj["features"] if f.get("properties")]
        if zctas:
            if leak_scores:
                z_vals = [leak_scores.get(z, 0.0) for z in zctas]
                custom = [leakage_hover_text(z, leak_detail) for z in zctas]
                fig.add_trace(
                    go.Choroplethmapbox(
                        geojson=gj,
                        locations=zctas,
                        z=z_vals,
                        featureidkey="properties.ZCTA5CE20",
                        colorscale=[
                            [0.0, "rgba(255, 255, 255, 0.78)"],
                            [0.45, "rgba(147, 197, 253, 0.82)"],
                            [1.0, "rgba(30, 64, 175, 0.92)"],
                        ],
                        zmin=0,
                        zmax=100,
                        showscale=False,
                        marker_line_width=0.2,
                        marker_line_color="rgba(15,23,42,0.5)",
                        marker_opacity=0.82,
                        hovertemplate="%{customdata}<extra></extra>",
                        customdata=custom,
                        name="Leakage",
                        below="traces",
                        hoverlabel=_HOVER_LABEL,
                    )
                )
            else:
                fig.add_trace(
                    go.Choroplethmapbox(
                        geojson=gj,
                        locations=zctas,
                        z=[0.0] * len(zctas),
                        featureidkey="properties.ZCTA5CE20",
                        colorscale=[[0, "rgba(30,41,59,0.5)"], [1, "rgba(30,41,59,0.5)"]],
                        showscale=False,
                        marker_line_width=0.2,
                        marker_line_color="rgba(100,116,139,0.4)",
                        marker_opacity=0.35,
                        hovertemplate="<b>ZCTA %{location}</b><br>No leakage data<extra></extra>",
                        name="ZIP",
                        below="traces",
                        hoverlabel=_HOVER_LABEL,
                    )
                )

    if selection and "lat" in selection and "lon" in selection:
        _append_range_rings(fig, float(selection["lat"]), float(selection["lon"]))

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
        ms = style["size"] if dense else max(style["size"], 9)
        lats, lons = zip(*[_jitter_lat_lon(f) for f in points])
        fig.add_trace(
            go.Scattermapbox(
                lat=list(lats),
                lon=list(lons),
                mode="markers",
                name=style["label"],
                marker={
                    "size": ms,
                    "color": style["color"],
                    "symbol": "circle",
                    "opacity": 0.9,
                },
                text=[_facility_hover(f) for f in points],
                hoverinfo="text",
                hoverlabel=_HOVER_LABEL,
            )
        )

    fig.update_layout(
        uirevision="ambulatory-fl-map",
        transition={"duration": 0},
        hovermode="closest",
        hoverlabel=_HOVER_LABEL,
        font={"family": APP_FONT_FAMILY, "color": "#e2e8f0"},
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
    insight = _insight_panel(selection, leak_detail, service_line=selected_service_line)
    return fig, insight
