from __future__ import annotations

from dash import Dash

from env_loader import load_dotenv

load_dotenv()

from callbacks import register_callbacks
from layout import build_layout


app = Dash(__name__)
app.title = "Ambulatory Intelligence Map"
app.layout = build_layout()
register_callbacks(app)


if __name__ == "__main__":
    # debug=True keeps reload; dev_tools_ui=False removes the floating </> Dash dev-tools button (bottom-right).
    app.run(debug=True, dev_tools_ui=False)
