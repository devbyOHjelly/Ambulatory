from __future__ import annotations

from dash import Input, Output, callback_context, html

from data import opportunities
from layout import (
    CTRL_PANEL_VISIBLE_STYLE,
    OPP_PANEL_VISIBLE_STYLE,
    PANEL_HIDDEN_STYLE,
    REF_PANEL_VISIBLE_STYLE,
    TAB_BTN_ACTIVE,
    TAB_BTN_IDLE,
)
from map_view import build_map


_TAB_MAP = {
    "btn-tab-reference": "reference",
    "btn-tab-controls": "controls",
    "btn-tab-opportunity": "opportunity",
}


def _active_tab() -> str:
    ctx = callback_context
    if not ctx.triggered:
        return "reference"
    first = ctx.triggered[0]
    if first.get("prop_id") == ".":
        return "reference"
    tid = ctx.triggered_id
    if tid is None:
        return "reference"
    return _TAB_MAP.get(tid, "reference")


def register_callbacks(app) -> None:
    @app.callback(
        Output("panel-reference", "style"),
        Output("panel-controls", "style"),
        Output("panel-opportunity", "style"),
        Output("btn-tab-reference", "className"),
        Output("btn-tab-controls", "className"),
        Output("btn-tab-opportunity", "className"),
        Input("btn-tab-reference", "n_clicks"),
        Input("btn-tab-controls", "n_clicks"),
        Input("btn-tab-opportunity", "n_clicks"),
    )
    def switch_folder_tabs(_n1, _n2, _n3):
        active = _active_tab()
        ref = REF_PANEL_VISIBLE_STYLE if active == "reference" else PANEL_HIDDEN_STYLE
        ctrl = CTRL_PANEL_VISIBLE_STYLE if active == "controls" else PANEL_HIDDEN_STYLE
        opp = OPP_PANEL_VISIBLE_STYLE if active == "opportunity" else PANEL_HIDDEN_STYLE
        c1 = TAB_BTN_ACTIVE if active == "reference" else TAB_BTN_IDLE
        c2 = TAB_BTN_ACTIVE if active == "controls" else TAB_BTN_IDLE
        c3 = TAB_BTN_ACTIVE if active == "opportunity" else TAB_BTN_IDLE
        return ref, ctrl, opp, c1, c2, c3

    @app.callback(
        Output("map-graph", "figure"),
        Input("service-line", "value"),
        Input("drive-time", "value"),
    )
    def update_map(service_line: str, drive_time_minutes: int):
        return build_map(service_line, drive_time_minutes)

    @app.callback(
        Output("opportunity-table", "children"),
        Input("service-line", "value"),
    )
    def update_opportunity_table(_service_line: str):
        ranked = opportunities.sort_values("score", ascending=False)
        cards = [
            html.Div(
                style={
                    "border": "1px solid #334155",
                    "borderRadius": "10px",
                    "padding": "12px",
                    "marginBottom": "12px",
                    "backgroundColor": "#111827",
                },
                children=[
                    html.Div("Sandbox Zone", style={"fontWeight": "700", "marginBottom": "6px", "color": "#93c5fd"}),
                    html.Div(
                        "Marker you can place anywhere on the map to test opportunity for that location.",
                        style={"color": "#cbd5e1"},
                    ),
                ],
            )
        ]
        for i, row in enumerate(ranked.itertuples(), start=1):
            cards.append(
                html.Div(
                    style={
                        "border": "1px solid #1e293b",
                        "borderRadius": "8px",
                        "padding": "12px",
                        "marginBottom": "10px",
                        "backgroundColor": "#0f172a",
                    },
                    children=[
                        html.Div(f"#{i} {row.zone}", style={"fontWeight": "600", "marginBottom": "3px"}),
                        html.Div(f"Opportunity Score: {row.score}", style={"color": "#22c55e", "marginBottom": "6px"}),
                        html.Div(row.rationale, style={"color": "#cbd5e1"}),
                    ],
                )
            )
        return cards
