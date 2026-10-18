"""Synthetic fixtures and session-only editing for the M1 prototype.

No network requests, brokerage credentials, disk writes, or notification delivery.
"""

from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from math import sin


SNAPSHOT = "2026-10-16 14:35 美东 / 2026-10-17 02:35 北京"
CATALOG = {
    "QQQM": {"name": "Invesco NASDAQ 100 ETF", "name_zh": "纳指100 ETF", "price": "210.00", "previous": "208.20", "sector": "指数 ETF"},
    "MU": {"name": "Micron Technology", "name_zh": "美光科技", "price": "205.00", "previous": "211.50", "sector": "存储芯片"},
    "NVDA": {"name": "NVIDIA", "name_zh": "英伟达", "price": "145.00", "previous": "143.10", "sector": "半导体"},
    "GOOGL": {"name": "Alphabet", "name_zh": "谷歌 A", "price": "180.00", "previous": "179.00", "sector": "互联网与云"},
    "TSLA": {"name": "Tesla", "name_zh": "特斯拉", "price": "245.00", "previous": "249.20", "sector": "汽车与能源"},
    "AAPL": {"name": "Apple", "name_zh": "苹果", "price": "225.00", "previous": "223.00", "sector": "消费电子"},
}


def stock_label(symbol):
    """Keep ticker identity stable; Chinese names are presentation aliases."""
    name = CATALOG.get(symbol, {}).get("name_zh")
    return f"{symbol} · {name}" if name else symbol


def new_demo():
    """Return a fresh, independent session. Never share mutable user state."""
    return deepcopy({
        "watchlist": ["QQQM", "MU", "NVDA", "GOOGL", "TSLA"],
        "positions": [
            {"account": "演示账户 A", "symbol": "QQQM", "quantity": "20", "avg_cost": "195"},
            {"account": "演示账户 A", "symbol": "MU", "quantity": "15", "avg_cost": "220"},
            {"account": "演示账户 B", "symbol": "NVDA", "quantity": "10", "avg_cost": "138"},
            {"account": "演示账户 B", "symbol": "GOOGL", "quantity": "8", "avg_cost": "170"},
            {"account": "演示账户 B", "symbol": "TSLA", "quantity": "4", "avg_cost": "280"},
        ],
        "cash": {"演示账户 A": "3500", "演示账户 B": "2200"},
        "rules": [
            {"id": "r1", "symbol": "MU", "name": "观察区间 A", "intent": "buy", "lower": "200", "upper": "210", "cooldown": 60, "enabled": True},
            {"id": "r2", "symbol": "MU", "name": "观察区间 B", "lower": "180", "upper": "190", "cooldown": 60, "enabled": True},
            {"id": "r3", "symbol": "QQQM", "name": "指数观察区间", "intent": "sell", "lower": "195", "upper": "205", "cooldown": 60, "enabled": True},
        ],
        "notes": {"MU": {"thesis": "演示：关注存储业务的周期变化，定期核对公开财报。", "horizon": "演示：长期观察", "risks": "演示：需求变化、资本开支与竞争。", "reviewed": "2026-10-15"}},
        "events": [
            {"id": "e1", "symbol": "MU", "rule": "观察区间 A", "intent": "buy", "lower": "200", "upper": "210", "price": "205", "time": "2026-10-16 14:35 美东", "read": False},
            {"id": "e2", "symbol": "QQQM", "rule": "指数观察区间", "intent": "sell", "lower": "195", "upper": "205", "price": "204", "time": "2026-10-15 11:10 美东", "read": True},
        ],
    })


def money(value):
    return "—" if value is None else f"${value:,.2f}"


def quote(symbol, scenario="全部有效"):
    source = CATALOG.get(symbol)
    if source is None:
        return {"price": None, "previous": None, "status": "缺失"}
    status = {"MU 报价过期": "过期", "MU 报价缺失": "缺失"}.get(scenario, "有效") if symbol == "MU" else "有效"
    return {
        "price": None if status == "缺失" else Decimal(source["price"]),
        "previous": Decimal(source["previous"]),
        "status": status,
    }


def portfolio(demo, scenario="全部有效", account=None):
    rows = []
    complete = True
    for position in demo["positions"]:
        if account and position["account"] != account:
            continue
        q = quote(position["symbol"], scenario)
        quantity = Decimal(position["quantity"])
        cost = quantity * Decimal(position["avg_cost"])
        # Stale values are display-only: never report an apparently complete total.
        value = quantity * q["price"] if q["status"] == "有效" else None
        complete = complete and value is not None
        rows.append({**position, "cost": cost, "value": value, "pnl": None if value is None else value - cost, "status": q["status"]})
    cash = sum((Decimal(v) for k, v in demo["cash"].items() if account is None or k == account), Decimal(0))
    known = sum((row["value"] for row in rows if row["value"] is not None), Decimal(0))
    cost = sum((row["cost"] for row in rows), Decimal(0))
    return {"rows": rows, "cash": cash, "cost": cost, "known_value": known, "value": known if complete else None, "total": known + cash if complete else None, "pnl": known - cost if complete else None, "complete": complete}


def validate_rule(name, lower, upper, cooldown):
    if not name.strip():
        raise ValueError("请填写区间名称。")
    try:
        low, high = Decimal(str(lower)), Decimal(str(upper))
    except InvalidOperation as exc:
        raise ValueError("价格请输入有效数字。") from exc
    if not low.is_finite() or not high.is_finite() or low <= 0 or high < low:
        raise ValueError("价格必须为正数，且上界不得低于下界。")
    if not isinstance(cooldown, int) or not 0 <= cooldown <= 10080:
        raise ValueError("冷却时间必须是 0–10080 分钟的整数。")
    return {"name": name.strip(), "lower": str(low), "upper": str(high), "cooldown": cooldown}


def rule_state(rule, scenario="全部有效"):
    if not rule["enabled"]:
        return "已停用"
    q = quote(rule["symbol"], scenario)
    if q["status"] != "有效":
        return "数据无效，暂停判断"
    return "区间内" if Decimal(rule["lower"]) <= q["price"] <= Decimal(rule["upper"]) else "区间外"


def history(symbol):
    """30 fabricated weekday points, not a verified exchange calendar."""
    dates, cursor = [], date(2026, 10, 15)
    while len(dates) < 30:
        if cursor.weekday() < 5:
            dates.append(cursor)
        cursor -= timedelta(days=1)
    dates.reverse()
    end = float(CATALOG[symbol]["previous"])
    points = [end * (0.94 + 0.06 * i / 29 + 0.018 * sin(i / 2.7)) for i in range(30)]
    points[-1] = end
    return dates, points
