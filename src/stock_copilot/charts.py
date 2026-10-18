"""Portfolio allocation charts; percentages use complete, scoped market values."""

from decimal import Decimal

import plotly.graph_objects as go

from stock_copilot.currency import asset_money, convert_usd
from stock_copilot.demo import CATALOG


COLORS = {
    "TSLA": "#D87583", "NVDA": "#51A99B", "GOOGL": "#E1AE5E",
    "MU": "#8B78CF", "QQQM": "#6688E7", "AAPL": "#91A4C4", "现金": "#7C8BA9",
}


def allocation_values(result, include_cash=False):
    """Aggregate the selected accounts in Decimal before converting for drawing.

    Suppress the whole distribution for incomplete quotes: silently renormalizing
    known holdings would misrepresent actual portfolio weights.
    """
    if not result["complete"]:
        return {}
    values = {}
    for row in result["rows"]:
        if row["value"] is not None and row["value"] > 0:
            symbol = row["symbol"]
            values[symbol] = values.get(symbol, Decimal(0)) + row["value"]
    if include_cash and result["cash"] > 0:
        values["现金"] = result["cash"]
    return dict(sorted(values.items(), key=lambda item: item[1], reverse=True))


def allocation_figure(values, include_cash=False, currency="USD", compact=False):
    total = sum(values.values(), Decimal(0))
    labels = list(values)
    fig = go.Figure(go.Pie(
        labels=labels,
        values=[float(convert_usd(value, currency)) for value in values.values()],
        hole=0.62,
        sort=False,
        direction="clockwise",
        rotation=0,
        textinfo="label+percent",
        texttemplate="<b>%{customdata[0]}</b><br>%{label} · %{percent:.1%}",
        textposition="outside",
        # Text inherits the live Streamlit theme; transparent strokes avoid
        # light-colored rings when the visitor switches to a dark appearance.
        textfont={"size": 12 if compact else 14},
        marker={"colors": [COLORS.get(label, "#8CA6B5") for label in labels], "line": {"color": "rgba(0,0,0,0)", "width": 4}},
        customdata=[[CATALOG.get(label, {}).get("name_zh", label), asset_money(value, currency)] for label, value in values.items()],
        hovertemplate=f"<b>%{{label}}</b><br>%{{customdata[0]}}<br>金额 %{{customdata[1]}} {currency}<br>占比 %{{percent:.1%}}<extra></extra>",
        showlegend=False,
        automargin=True,
    ))
    fig.update_layout(
        height=280 if compact else 360,
        margin={"l": 8 if compact else 38, "r": 8 if compact else 38, "t": 16, "b": 16},
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"font": {"size": 15}},
        annotations=[{
            "text": f"<span style='font-size:12px'>{'含现金总资产' if include_cash else '股票市值'} · {currency}</span><br><b>{asset_money(total, currency)}</b>",
            "x": 0.5, "y": 0.5, "showarrow": False,
            "font": {"size": 17 if compact else 22},
        }],
    )
    return fig
