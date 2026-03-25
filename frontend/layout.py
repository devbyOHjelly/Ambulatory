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

CTRL_PANEL_VISIBLE_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "minHeight": "0",
    "overflow": "auto",
}

OPP_PANEL_VISIBLE_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "minHeight": "0",
    "overflow": "auto",
}

_LEGEND_TEXT = "#cbd5e1"


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
                "Coverage",
                "#60a5fa",
                [
                    _legend_row(_swatch_circle("#22c55e"), "Orlando Health"),
                    _legend_row(_swatch_circle("#ef4444"), "Other facilities"),
                    _legend_row(_swatch_circle("#f59e0b"), "Lab corporations"),
                ],
            ),
            _construct_section(
                "Leakage",
                "#f59e0b",
                [
                    _legend_row(_swatch_circle("#10b981"), "Inbound patient flow"),
                    _legend_row(_swatch_circle("#f59e0b"), "Outbound patient flow"),
                ],
            ),
            _construct_section(
                "Access",
                "#c084fc",
                [
                    _legend_row(
                        html.Div(
                            style={
                                "width": "11px",
                                "height": "11px",
                                "borderRadius": "50%",
                                "border": "2px solid #c084fc",
                                "backgroundColor": "transparent",
                                "flexShrink": "0",
                            }
                        ),
                        "Drive-time convenience (planned)",
                    ),
                ],
            ),
        ],
    )


def _reference_panel() -> html.Div:
    return html.Div(
        id="panel-reference",
        style=REF_PANEL_VISIBLE_STYLE,
        children=[
            html.Div(
                style={
                    "backgroundColor": "#0f172a",
                    "border": "1px solid #1e293b",
                    "borderRadius": "10px",
                    "padding": "12px",
                    "marginBottom": "12px",
                },
                children=[
                    html.H4("Main Objective", style={"margin": "0 0 8px 0"}),
                    html.P(
                        "Where should we invest next to capture the most patients and revenue?",
                        style={"margin": 0, "color": "#cbd5e1"},
                    ),
                ],
            ),
            html.Div(
                style={
                    "backgroundColor": "#0f172a",
                    "border": "1px solid #1e293b",
                    "borderRadius": "10px",
                    "padding": "12px",
                    "marginBottom": "12px",
                },
                children=[
                    html.H4("Constructs", style={"margin": "0 0 8px 0"}),
                    html.P(
                        "Coverage: Orlando Health vs other facilities (red dots) from CMS NPPES. Full list: frontend/data/nppes_florida_facilities.csv — filter column owner = Competitor for non–Orlando Health.",
                        style={"margin": "0 0 6px 0", "color": "#cbd5e1"},
                    ),
                    html.P(
                        "Leakage: Inbound volume vs outbound patient leakage by service line.",
                        style={"margin": "0 0 6px 0", "color": "#cbd5e1"},
                    ),
                    html.P(
                        "Access: 5/10/20/45-minute access approximation to identify convenience gaps.",
                        style={"margin": 0, "color": "#cbd5e1"},
                    ),
                ],
            ),
            html.Div(
                style={
                    "backgroundColor": "#0f172a",
                    "border": "1px solid #1e293b",
                    "borderRadius": "10px",
                    "padding": "12px",
                },
                children=[
                    html.H4("Opportunity Score", style={"margin": "0 0 8px 0"}),
                    html.P(
                        "Opportunity score combines coverage, leakage, and access to rank where expansion can create the most value.",
                        style={"margin": "0 0 8px 0", "color": "#cbd5e1"},
                    ),
                    html.Div(
                        "Formula: (Coverage + Leakage + Access) weighted into a single expansion score.",
                        style={
                            "backgroundColor": "#111827",
                            "border": "1px solid #334155",
                            "borderRadius": "8px",
                            "padding": "8px 10px",
                            "fontSize": "12px",
                            "color": "#93c5fd",
                        },
                    ),
                ],
            ),
        ],
    )


def _controls_panel() -> html.Div:
    return html.Div(
        id="panel-controls",
        style=PANEL_HIDDEN_STYLE,
        children=[
            html.Div(
                style={"paddingTop": "16px"},
                children=[
                    html.Div(
                        style={"marginBottom": "22px"},
                        children=[
                            html.Label("Service Line", style={"display": "block", "marginBottom": "8px"}),
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
                                style={"backgroundColor": "#0f172a", "color": "#0f172a"},
                            ),
                        ],
                    ),
                    html.Div(
                        style={"marginBottom": "22px"},
                        children=[
                            html.Label("Drive-Time Approximation (minutes)", style={"display": "block", "marginBottom": "8px"}),
                            dcc.Slider(
                                id="drive-time",
                                min=5,
                                max=45,
                                step=5,
                                marks={5: "5", 10: "10", 20: "20", 45: "45"},
                                value=10,
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def _opportunity_panel() -> html.Div:
    return html.Div(
        id="panel-opportunity",
        style={"display": "none"},
        children=[html.Div(id="opportunity-table", style={"paddingTop": "14px", "fontSize": "14px"})],
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
                                "Controls",
                                id="btn-tab-controls",
                                n_clicks=0,
                                type="button",
                                className=TAB_BTN_IDLE,
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
                            _controls_panel(),
                            _opportunity_panel(),
                        ],
                    ),
                ],
            ),
            html.Div(
                style={"flex": 1, "position": "relative"},
                children=[
                    dcc.Graph(
                        id="map-graph",
                        style={"height": "100%", "width": "100%"},
                        config={
                            "displayModeBar": True,
                            "displaylogo": False,
                            "scrollZoom": True,
                            "doubleClick": "reset",
                            "modeBarButtonsToRemove": [
                                "lasso2d",
                                "select2d",
                                "toImage",
                            ],
                        },
                    ),
                    _map_legend(),
                ],
            ),
        ],
    )
