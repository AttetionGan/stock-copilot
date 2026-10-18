"""Display-only conversion of synthetic USD assets; no live FX integration."""

from decimal import Decimal, ROUND_HALF_UP


SUPPORTED_CURRENCIES = ("USD", "CNY")
# Deliberately fixed demo fixture, not a current or historical market quote.
DEMO_USD_CNY = Decimal("7.20")


def convert_usd(value, currency="USD"):
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError("不支持的资产显示币种。")
    if value is None:
        return None
    return value * (DEMO_USD_CNY if currency == "CNY" else Decimal(1))


def asset_money(value, currency="USD", *, signed=False):
    converted = convert_usd(value, currency)
    if converted is None:
        return "待补全"
    amount = abs(converted).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "−" if converted < 0 and amount else "+" if signed and converted > 0 and amount else ""
    symbol = "¥" if currency == "CNY" else "$"
    return f"{sign}{symbol}{amount:,.2f}"
