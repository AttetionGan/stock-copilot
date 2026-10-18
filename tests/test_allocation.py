from decimal import Decimal

import pytest

from stock_copilot.charts import allocation_values
from stock_copilot.demo import new_demo, portfolio


def test_allocation_denominator_is_selected_market_value_or_total_assets():
    result = portfolio(new_demo())
    stocks = allocation_values(result)
    assets = allocation_values(result, include_cash=True)
    assert sum(stocks.values()) == Decimal("11145")
    assert "现金" not in stocks
    assert sum(assets.values()) == Decimal("16845")
    assert assets["现金"] == Decimal("5700")


def test_same_symbol_across_accounts_is_combined_once():
    demo = new_demo()
    demo["positions"].append({"account": "演示账户 B", "symbol": "QQQM", "quantity": "2", "avg_cost": "195"})
    values = allocation_values(portfolio(demo))
    assert len(values) == 5
    assert values["QQQM"] == Decimal("4620")
    assert sum(values.values()) == Decimal("11565")


@pytest.mark.parametrize("account,symbols,total", [
    ("演示账户 A", {"QQQM", "MU"}, "7275"),
    ("演示账户 B", {"NVDA", "GOOGL", "TSLA"}, "3870"),
])
def test_account_selection_controls_distribution(account, symbols, total):
    values = allocation_values(portfolio(new_demo(), account=account))
    assert set(values) == symbols
    assert sum(values.values()) == Decimal(total)


@pytest.mark.parametrize("scenario", ["MU 报价过期", "MU 报价缺失"])
def test_incomplete_distribution_is_not_renormalized(scenario):
    result = portfolio(new_demo(), scenario)
    assert allocation_values(result) == {}
    assert allocation_values(result, include_cash=True) == {}


@pytest.mark.parametrize("include_cash,expected", [(False, {}), (True, {"现金": Decimal("5700")})])
def test_cash_only_portfolio_has_no_empty_stock_pie(include_cash, expected):
    demo = new_demo()
    demo["positions"] = []
    assert allocation_values(portfolio(demo), include_cash) == expected


def test_zero_assets_have_no_slices():
    demo = new_demo()
    demo["positions"] = []
    demo["cash"] = {"演示账户 A": "0"}
    assert allocation_values(portfolio(demo), include_cash=True) == {}
