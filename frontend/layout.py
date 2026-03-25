from __future__ import annotations

from dash import dcc, html

APP_FONT_FAMILY = "Open Sans, Arial, sans-serif"

TAB_BTN_ACTIVE = "folder-tab folder-tab-active"
TAB_BTN_IDLE = "folder-tab"

PANEL_HIDDEN_STYLE = {"display": "none"}

REF_PANEL_VISIBLE_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "minHeight": "0",
    "overflow": "auto",
    "paddingTop": "14px",
    "fontSize": "14px",
    "lineHeight": "1.6",
}

OPP_PANEL_VISIBLE_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "minHeight": "0",
    "overflow": "auto",
}

_LEGEND_TEXT = "#cbd5e1"
_LABEL_STYLE = {
    "fontSize": "10px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.08em",
    "color": "#64748b",
    "margin": "10px 0 6px 0",
}
_CARD = {
    "backgroundColor": "#0f172a",
    "border": "1px solid #1e293b",
    "borderRadius": "10px",
    "padding": "12px",
    "marginBottom": "12px",
}

_REF_FORMULA_BOX = {
    "backgroundColor": "#111827",
    "border": "1px solid #334155",
    "borderRadius": "8px",
    "padding": "10px 12px",
    "fontSize": "12px",
    "color": "#e2e8f0",
    "fontFamily": "ui-monospace, monospace",
    "lineHeight": "1.55",
    "marginBottom": "8px",
    "whiteSpace": "pre-wrap",
}

_REF_SIMPLE = {
    "margin": "0",
    "fontSize": "12px",
    "color": "#94a3b8",
    "fontStyle": "italic",
    "lineHeight": "1.45",
}


def _legend_row(swatch: html.Div, label: str) -> html.Div:
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "gap": "10px",
            "marginBottom": "7px",
            "fontSize": "13px",
            "color": _LEGEND_TEXT,
        },
        children=[swatch, html.Span(label)],
    )


def _swatch_circle(color: str) -> html.Div:
    return html.Div(
        style={
            "width": "11px",
            "height": "11px",
            "borderRadius": "50%",
            "backgroundColor": color,
            "flexShrink": "0",
        }
    )


def _construct_section(title: str, title_color: str, rows: list) -> html.Div:
    return html.Div(
        style={"marginBottom": "14px"},
        children=[
            html.Div(
                title,
                style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                    "color": title_color,
                    "marginBottom": "8px",
                },
            ),
            *rows,
        ],
    )


def _map_legend() -> html.Div:
    return html.Div(
        style={
            "position": "absolute",
            "right": "14px",
            "bottom": "14px",
            "backgroundColor": "rgba(15,23,42,0.96)",
            "border": "1px solid #334155",
            "borderRadius": "10px",
            "padding": "14px 16px 10px 16px",
            "fontSize": "14px",
            "minWidth": "280px",
            "maxWidth": "320px",
        },
        children=[
            html.Div(
                "Map key",
                style={
                    "fontWeight": "700",
                    "marginBottom": "12px",
                    "color": "#e2e8f0",
                    "fontSize": "13px",
                },
            ),
            _construct_section(
                "Leakage (ZIP)",
                "#34d399",
                [
                    _legend_row(
                        html.Div(
                            style={
                                "width": "36px",
                                "height": "10px",
                                "borderRadius": "4px",
                                "background": "linear-gradient(90deg, #ffffff, #93c5fd, #1e40af)",
                                "flexShrink": "0",
                            }
                        ),
                        "White = lower modeled leakage · Dark blue = higher",
                    ),
                ],
            ),
            _construct_section(
                "Providers",
                "#60a5fa",
                [
                    _legend_row(_swatch_circle("#4ade80"), "In-network"),
                    _legend_row(_swatch_circle("#f87171"), "Competitors"),
                    _legend_row(_swatch_circle("#fbbf24"), "Lab corporations"),
                ],
            ),
            _construct_section(
                "Proximity (on click)",
                "#64748b",
                [
                    _legend_row(
                        html.Div(
                            style={
                                "width": "14px",
                                "height": "14px",
                                "borderRadius": "50%",
                                "border": "2px solid rgba(51,65,85,0.95)",
                                "backgroundColor": "transparent",
                                "flexShrink": "0",
                            }
                        ),
                        "5, 10, 20 mile rings from selection",
                    ),
                ],
            ),
        ],
    )


def _reference_construct(
    title: str,
    accent: str,
    definition: str,
    key_content: list,
    *,
    how_calculated: list | None = None,
) -> html.Div:
    kids: list = [
        html.H4(title, style={"margin": "0 0 4px 0", "color": accent}),
        html.Div("Definition", style=_LABEL_STYLE),
        html.P(definition, style={"margin": "0 0 4px 0", "color": "#cbd5e1"}),
    ]
    if how_calculated:
        kids.append(html.Div("How it's calculated", style=_LABEL_STYLE))
        kids.append(
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "6px", "marginBottom": "4px"},
                children=how_calculated,
            )
        )
    kids.extend(
        [
            html.Div("Key", style=_LABEL_STYLE),
            html.Div(children=key_content),
        ]
    )
    return html.Div(style=_CARD, children=kids)


def _reference_panel() -> html.Div:
    return html.Div(
        id="panel-reference",
        style=REF_PANEL_VISIBLE_STYLE,
        children=[
            html.Div(
                style=_CARD,
                children=[
                    html.H4("Main objective", style={"margin": "0 0 8px 0"}),
                    html.P(
                        "Where should we invest next to capture the most patients and revenue?",
                        style={"margin": 0, "color": "#cbd5e1"},
                    ),
                ],
            ),
            _reference_construct(
                "Coverage",
                "#60a5fa",
                "Which organizations operate sites in Florida and how we classify them relative to our network (in-network vs competitor vs lab corporation).",
                [
                    _legend_row(_swatch_circle("#4ade80"), "In-network — our system facilities (NPPES + internal tagging)."),
                    _legend_row(_swatch_circle("#f87171"), "Competitors — other active providers in the same geography."),
                    _legend_row(_swatch_circle("#fbbf24"), "Lab corporations — known national or regional lab chains."),
                ],
                how_calculated=[
                    html.P(
                        "Each facility gets one color using priority rules (not a numeric score):",
                        style={"margin": 0, "color": "#94a3b8", "fontSize": "12px"},
                    ),
                    html.Div(
                        "1) In-network  →  tagged as our system\n"
                        "2) Else lab corp  →  name matches known lab chains\n"
                        "3) Else  →  Competitor",
                        style=_REF_FORMULA_BOX,
                    ),
                    html.P(
                        "Simple: each place is us, a lab chain, or other. Colors keep the map easy to scan.",
                        style={**_REF_SIMPLE, "marginTop": "6px"},
                    ),
                    html.P(
                        "Leakage and “nearest in-network” can also treat NPIs on an allowlist as ours; map dots use the rules above.",
                        style={"margin": "8px 0 0 0", "color": "#94a3b8", "fontSize": "12px"},
                    ),
                ],
            ),
            _reference_construct(
                "Leakage",
                "#34d399",
                "ZIP-level pressure from competitor presence and local demand: where modeled outflow risk is higher (deeper blue) vs lower (lighter / white), using population and provider counts.",
                [
                    _legend_row(
                        html.Div(
                            style={
                                "width": "36px",
                                "height": "10px",
                                "borderRadius": "4px",
                                "background": "linear-gradient(90deg, #ffffff, #93c5fd, #1e40af)",
                                "flexShrink": "0",
                            }
                        ),
                        "Choropleth fill: white = lower modeled leakage, dark blue = higher (0–100 scale).",
                    ),
                    _legend_row(
                        html.Span("ℹ", style={"color": "#94a3b8", "width": "11px", "textAlign": "center"}),
                        "Click a ZIP on the heatmap for counts, population, and leakage in the selection card.",
                    ),
                ],
                how_calculated=[
                    html.P(
                        "Per ZIP (5-digit), after the service-line filter: count Our vs Competitor sites. Population comes from a ZIP lookup.",
                        style={"margin": 0, "color": "#94a3b8", "fontSize": "12px"},
                    ),
                    html.Div(
                        "Leakage score (0–100) scales this idea across Florida:\n"
                        "  (competitor share) × ln(1 + population ÷ providers in ZIP)\n"
                        "Lowest ZIP → 0, highest → 100 (ZIPs with no providers are excluded).",
                        style=_REF_FORMULA_BOX,
                    ),
                    html.P(
                        "Simple: darker ZIPs score higher for crowded areas with lots of competitors. Not money or a real percent.",
                        style={**_REF_SIMPLE, "marginTop": "6px"},
                    ),
                ],
            ),
            _reference_construct(
                "Proximity",
                "#64748b",
                "How far a chosen point is from the nearest in-network site, and how far that reach extends in simple mile rings (great-circle, not drive time).",
                [
                    _legend_row(
                        html.Div(
                            style={
                                "width": "14px",
                                "height": "14px",
                                "borderRadius": "50%",
                                "border": "2px solid rgba(51,65,85,0.95)",
                                "backgroundColor": "transparent",
                                "flexShrink": "0",
                            }
                        ),
                        "After you click a ZIP or provider, dark navy rings show 5, 10, and 20 statute miles from that point.",
                    ),
                    _legend_row(
                        html.Span("ℹ", style={"color": "#94a3b8", "width": "11px", "textAlign": "center"}),
                        "Selection card reports straight-line miles to the closest in-network site.",
                    ),
                ],
                how_calculated=[
                    html.P(
                        "All distances use great-circle geometry on the Earth (haversine), in statute miles — not drive time or traffic.",
                        style={"margin": 0, "color": "#94a3b8", "fontSize": "12px"},
                    ),
                    html.Div(
                        "Nearest in-network = min distance from the click point to each in-network facility\n"
                        "Rings = closed loops at 5 mi, 10 mi, and 20 mi radius from that point\n"
                        "ZIP clicks use the ZCTA centroid (approximate center of the ZIP polygon).",
                        style=_REF_FORMULA_BOX,
                    ),
                    html.P(
                        "Simple: straight line miles and rings on the map. Not how long a drive takes.",
                        style={**_REF_SIMPLE, "marginTop": "6px"},
                    ),
                ],
            ),
            html.Div(
                style=_CARD,
                children=[
                    html.H4("Opportunity", style={"margin": "0 0 8px 0", "color": "#93c5fd"}),
                    html.P(
                        "Ranks ZIPs where expansion may matter most: high local population, competitor pressure relative to our footprint, and distance from in-network access.",
                        style={"margin": "0 0 10px 0", "color": "#cbd5e1"},
                    ),
                    html.Div("How it's calculated", style=_LABEL_STYLE),
                    html.Div(
                        "Opportunity = Population × (Competitor ÷ (Our + 1)) × Access",
                        style={**_REF_FORMULA_BOX, "color": "#93c5fd"},
                    ),
                    html.P(
                        "Simple: one number that grows with more people, more competitors than us, and being farther from our sites.",
                        style={**_REF_SIMPLE, "marginTop": "6px"},
                    ),
                    html.Div("Key", style=_LABEL_STYLE),
                    html.P(
                        "Opportunity tab lists top ZIPs by this index for the selected service line.",
                        style={"margin": 0, "color": "#cbd5e1", "fontSize": "13px"},
                    ),
                ],
            ),
        ],
    )


def _opportunity_panel() -> html.Div:
    return html.Div(
        id="panel-opportunity",
        style={"display": "none"},
        children=[
            html.Div(id="opportunity-table", style={"paddingTop": "14px", "fontSize": "14px"}),
        ],
    )


def build_layout() -> html.Div:
    return html.Div(
        style={
            "height": "100vh",
            "display": "flex",
            "backgroundColor": "#020617",
            "color": "#e2e8f0",
            "fontFamily": APP_FONT_FAMILY,
            "overflow": "hidden",
        },
        children=[
            html.Div(
                style={
                    "width": "490px",
                    "borderRight": "1px solid #1e293b",
                    "padding": "14px",
                    "overflow": "hidden",
                    "backgroundColor": "#020617",
                    "display": "flex",
                    "flexDirection": "column",
                    "minHeight": 0,
                },
                children=[
                    html.Div(
                        className="folder-tab-bar",
                        children=[
                            html.Button(
                                "Reference",
                                id="btn-tab-reference",
                                n_clicks=0,
                                type="button",
                                className=TAB_BTN_ACTIVE,
                            ),
                            html.Button(
                                "Opportunity",
                                id="btn-tab-opportunity",
                                n_clicks=0,
                                type="button",
                                className=TAB_BTN_IDLE,
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "flex": "1",
                            "minHeight": "0",
                        },
                        children=[
                            _reference_panel(),
                            _opportunity_panel(),
                        ],
                    ),
                ],
            ),
            html.Div(
                style={"flex": 1, "position": "relative"},
                children=[
                    dcc.Store(id="map-selection", data=None),
                    html.Div(
                        style={"display": "none"},
                        children=[
                            dcc.Dropdown(
                                id="service-line",
                                options=[
                                    {"label": "All", "value": "All"},
                                    {"label": "Cardiology", "value": "Cardiology"},
                                    {"label": "Primary Care", "value": "Primary Care"},
                                    {"label": "Urgent Care", "value": "Urgent Care"},
                                    {"label": "Diagnostics", "value": "Diagnostics"},
                                    {"label": "Other", "value": "Other"},
                                ],
                                value="All",
                                clearable=False,
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="map-graph",
                        style={"height": "100%", "width": "100%"},
                        config={
                            "displayModeBar": True,
                            "displaylogo": False,
                            "scrollZoom": True,
                            "doubleClick": "reset",
                            "doubleClickDelay": 200,
                            "plotGlPixelRatio": 1,
                            "modeBarButtonsToRemove": [
                                "lasso2d",
                                "select2d",
                                "toImage",
                            ],
                        },
                    ),
                    html.Div(
                        style={
                            "position": "absolute",
                            "left": "14px",
                            "top": "14px",
                            "zIndex": "5",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                            "alignItems": "flex-start",
                            "maxWidth": "min(340px, 92vw)",
                        },
                        children=[
                            html.Button(
                                "Clear selection",
                                id="btn-clear-map-selection",
                                n_clicks=0,
                                type="button",
                                style={
                                    "backgroundColor": "rgba(15,23,42,0.95)",
                                    "color": "#e2e8f0",
                                    "border": "1px solid #475569",
                                    "borderRadius": "8px",
                                    "padding": "6px 12px",
                                    "fontSize": "12px",
                                    "cursor": "pointer",
                                },
                            ),
                            html.Div(id="map-selection-insight"),
                        ],
                    ),
                    _map_legend(),
                ],
            ),
        ],
    )
