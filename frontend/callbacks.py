from __future__ import annotations

from dash import Input, Output, State, callback_context, html

from data.opportunity_scores import compute_zip_opportunity_table
from layout import OPP_PANEL_VISIBLE_STYLE, PANEL_HIDDEN_STYLE, REF_PANEL_VISIBLE_STYLE, TAB_BTN_ACTIVE, TAB_BTN_IDLE
from map_view import build_map_with_insight, parse_map_click

_TAB_MAP = {
    "btn-tab-reference": "reference",
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
        Output("panel-opportunity", "style"),
        Output("btn-tab-reference", "className"),
        Output("btn-tab-opportunity", "className"),
        Input("btn-tab-reference", "n_clicks"),
        Input("btn-tab-opportunity", "n_clicks"),
    )
    def switch_folder_tabs(_n1, _n2):
        active = _active_tab()
        ref = REF_PANEL_VISIBLE_STYLE if active == "reference" else PANEL_HIDDEN_STYLE
        opp = OPP_PANEL_VISIBLE_STYLE if active == "opportunity" else PANEL_HIDDEN_STYLE
        c1 = TAB_BTN_ACTIVE if active == "reference" else TAB_BTN_IDLE
        c2 = TAB_BTN_ACTIVE if active == "opportunity" else TAB_BTN_IDLE
        return ref, opp, c1, c2

    @app.callback(
        Output("map-graph", "figure"),
        Output("map-selection-insight", "children"),
        Output("map-selection", "data"),
        Input("service-line", "value"),
        Input("map-graph", "clickData"),
        Input("btn-clear-map-selection", "n_clicks"),
        State("map-selection", "data"),
    )
    def map_click_and_redraw(service_line: str, click_data, _n_clear, prior_selection):
        ctx = callback_context
        selection = prior_selection
        if ctx.triggered:
            tid = ctx.triggered[0]["prop_id"]
            if tid.startswith("service-line") or tid.startswith("btn-clear-map-selection"):
                selection = None
            elif tid.startswith("map-graph") and click_data:
                parsed = parse_map_click(click_data, service_line=service_line)
                if parsed:
                    selection = parsed
        fig, insight = build_map_with_insight(service_line, 10, selection)
        return fig, insight, selection

    @app.callback(Output("opportunity-table", "children"), Input("service-line", "value"))
    def update_opportunity_table(service_line: str):
        rows = compute_zip_opportunity_table(service_line=service_line, top_n=20)
        if not rows:
            return html.Div("No ZIP-level rows for this filter.", style={"color": "#94a3b8"})

        def _fmt_int(x: float) -> str:
            return f"{int(round(x)):,}"

        cards: list = []
        for i, r in enumerate(rows, start=1):
            pop = r["population"]
            our = r["our"]
            comp = r["competitor"]
            acc = r["access_score"]
            opp = r["opportunity"]
            ratio = comp / (our + 1)
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
                        html.Div(
                            f"#{i}  ZIP {r['zip']}",
                            style={"fontWeight": "600", "marginBottom": "8px", "color": "#e2e8f0"},
                        ),
                        html.Div(
                            f"Opportunity: {_fmt_int(opp)}",
                            style={"color": "#22c55e", "fontWeight": "700", "marginBottom": "8px"},
                        ),
                        html.Div(
                            [
                                html.Span("Population: ", style={"color": "#64748b"}),
                                html.Span(_fmt_int(pop), style={"color": "#cbd5e1"}),
                            ],
                            style={"marginBottom": "4px"},
                        ),
                        html.Div(
                            [
                                html.Span("Our / Competitor: ", style={"color": "#64748b"}),
                                html.Span(f"{our} / {comp}", style={"color": "#cbd5e1"}),
                            ],
                            style={"marginBottom": "4px"},
                        ),
                        html.Div(
                            [
                                html.Span("Competitor ÷ (Our + 1): ", style={"color": "#64748b"}),
                                html.Span(f"{ratio:.3f}", style={"color": "#cbd5e1"}),
                            ],
                            style={"marginBottom": "4px"},
                        ),
                        html.Div(
                            [
                                html.Span("Access score: ", style={"color": "#64748b"}),
                                html.Span(f"{acc:.1f}", style={"color": "#cbd5e1"}),
                            ],
                        ),
                    ],
                )
            )
        return cards
