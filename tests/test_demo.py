from decimal import Decimal

import pytest

from stock_copilot.demo import new_demo, portfolio, rule_state, validate_rule


def test_portfolio_totals_match_synthetic_fixture():
    result = portfolio(new_demo())
    assert result["value"] == Decimal("11145")
    assert result["cash"] == Decimal("5700")
    assert result["total"] == Decimal("16845")
    assert result["pnl"] == Decimal("85")
    assert result["cost"] == Decimal("11060")
    assert result["value"] + result["cash"] == result["total"]
    assert result["value"] - result["cost"] == result["pnl"]


@pytest.mark.parametrize("scenario", ["MU 报价过期", "MU 报价缺失"])
def test_invalid_quote_never_produces_complete_total(scenario):
    result = portfolio(new_demo(), scenario)
    assert not result["complete"]
    assert result["total"] is None
    assert result["pnl"] is None
    assert result["known_value"] == Decimal("8070")
    assert result["cost"] == Decimal("11060")
    # An unrelated account remains independently usable.
    assert portfolio(new_demo(), scenario, "演示账户 B")["total"] == Decimal("6070")


@pytest.mark.parametrize("low,high", [("205", "205"), ("200", "205"), ("205", "210")])
def test_rule_includes_both_boundaries(low, high):
    rule = {**validate_rule("观察", low, high, 60), "symbol": "MU", "enabled": True}
    assert rule_state(rule) == "区间内"
    assert rule_state(rule, "MU 报价过期") == "数据无效，暂停判断"


@pytest.mark.parametrize("name,low,high", [("", "200", "210"), ("测试", "211", "210"), ("测试", "NaN", "210"), ("测试", "200", "Infinity"), ("测试", "-1", "210"), ("测试", "abc", "210")])
def test_invalid_rule_is_rejected(name, low, high):
    with pytest.raises(ValueError):
        validate_rule(name, low, high, 60)


def test_demo_sessions_are_independent():
    first, second = new_demo(), new_demo()
    first["events"][0]["read"] = True
    first["rules"][0]["enabled"] = False
    assert not second["events"][0]["read"]
    assert second["rules"][0]["enabled"]
