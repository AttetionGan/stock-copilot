from decimal import Decimal

import pytest

from stock_copilot.charts import allocation_figure, allocation_values
from stock_copilot.currency import asset_money, convert_usd
from stock_copilot.demo import new_demo, portfolio


@pytest.mark.parametrize("value,currency,signed,expected", [
    ("16845", "USD", False, "$16,845.00"),
    ("16845", "CNY", False, "¥121,284.00"),
    ("85", "CNY", True, "+¥612.00"),
    ("-225", "CNY", True, "−¥1,620.00"),
    ("0", "CNY", True, "¥0.00"),
    ("1.005", "USD", False, "$1.01"),
    (None, "CNY", False, "待补全"),
])
def test_asset_currency_formatting(value, currency, signed, expected):
    amount = None if value is None else Decimal(value)
    assert asset_money(amount, currency, signed=signed) == expected


def test_conversion_preserves_asset_relationships_and_original_usd_values():
    result = portfolio(new_demo())
    converted = {key: convert_usd(result[key], "CNY") for key in ["cost", "pnl", "value", "cash", "total"]}
    assert converted["cost"] + converted["pnl"] == converted["value"]
    assert converted["value"] + converted["cash"] == converted["total"]
    assert converted["cash"] == Decimal("41040")
    assert result["total"] == Decimal("16845")
    assert convert_usd(result["total"], "USD") == result["total"]
    assert convert_usd(None, "CNY") is None
    with pytest.raises(ValueError):
        convert_usd(Decimal(1), "EUR")


def test_pie_converts_amounts_but_preserves_weights():
    values = allocation_values(portfolio(new_demo()), include_cash=True)
    usd = allocation_figure(values, include_cash=True)
    cny = allocation_figure(values, include_cash=True, currency="CNY")
    assert sum(cny.data[0].values) == pytest.approx(121284)
    for usd_value, cny_value in zip(usd.data[0].values, cny.data[0].values):
        assert cny_value / sum(cny.data[0].values) == pytest.approx(usd_value / sum(usd.data[0].values))
    cash_index = list(cny.data[0].labels).index("现金")
    assert cny.data[0].customdata[cash_index][1] == "¥41,040.00"
    assert "¥121,284.00" in cny.layout.annotations[0].text
    assert "CNY" in cny.data[0].hovertemplate
