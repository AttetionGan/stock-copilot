"""Streamlit views for validating workflows before persistence and integrations."""

from decimal import Decimal
from html import escape
from uuid import uuid4

import plotly.graph_objects as go
import streamlit as st

from stock_copilot.charts import allocation_figure, allocation_values
from stock_copilot.currency import DEMO_USD_CNY, SUPPORTED_CURRENCIES, asset_money
from stock_copilot.demo import CATALOG, SNAPSHOT, history, money, new_demo, portfolio, quote, rule_state, stock_label, validate_rule
from stock_copilot.theme import COLOR_CONVENTIONS, THEME_LABELS, theme_styles


NAV = [("views/overview.py", "总览", "◈"), ("views/watchlist.py", "关注", "◎"), ("views/portfolio.py", "持仓", "▤"), ("views/alerts.py", "提醒", "◇"), ("views/settings.py", "设置", "⚙")]
RULE_INTENTS = {"observe": "观察", "buy": "买入观察", "sell": "卖出观察"}


def scenario():
    return data().get("scenario", "全部有效")


def data():
    return st.session_state.demo


def save_scenario():
    # Keep the selection outside widget state, which is cleaned up on navigation.
    data()["scenario"] = st.session_state.scenario


def asset_currency():
    return data().get("display_currency", "USD")


def save_currency():
    data()["display_currency"] = st.session_state.display_currency


def theme_mode():
    return data().get("theme_mode", "system")


def save_theme():
    data()["theme_mode"] = st.session_state.theme_mode


def color_convention():
    return data().get("price_colors", "green_up")


def save_color_convention():
    data()["price_colors"] = st.session_state.price_colors


def reset_demo():
    appearance = theme_mode()
    colors = color_convention()
    for key in list(st.session_state):
        del st.session_state[key]
    st.session_state.demo = new_demo()
    st.session_state.scenario = "全部有效"
    st.session_state.display_currency = "USD"
    data()["theme_mode"] = appearance
    st.session_state.theme_mode = appearance
    data()["price_colors"] = colors
    st.session_state.price_colors = colors


def text(value):
    """Render currency text without interpreting pairs of dollars as LaTeX."""
    st.markdown(value.replace("$", r"\$"))


def direction(value):
    if value is None:
        return "pending"
    return "gain" if value > 0 else "loss" if value < 0 else "flat"


def signed_money(value):
    if value is None:
        return "待补全"
    return ("+" if value > 0 else "−" if value < 0 else "") + money(abs(value))


def signed_percent(value):
    if value is None:
        return "—"
    return ("+" if value > 0 else "−" if value < 0 else "") + f"{abs(value):.2f}%"


def number_tile(label, value, tone="flat", detail=""):
    """Display-only formatting; all names and amounts are escaped before HTML."""
    detail_html = f'<span class="number-detail">{escape(detail)}</span>' if detail else ""
    return (
        f'<div class="number-tile tone-{tone}"><span class="number-label">{escape(label)}</span>'
        f'<strong class="number-value">{escape(value)}</strong>{detail_html}</div>'
    )


def shell():
    st.html(f"<style>{theme_styles(theme_mode(), color_convention())}</style>")
    st.html("""<style>
      .block-container {max-width:1440px;padding:1rem 1.5rem 2rem;}
      [data-testid="stHeader"] {display:none!important;}
      .st-key-display-settings,.st-key-demo-settings {padding:12px!important;background:var(--sc-surface);border-color:var(--sc-border)!important;}
      .block-container [data-testid="stVerticalBlock"] {gap:.5rem;}
      .block-container [data-testid="stCaptionContainer"] p {font-size:12px;line-height:1.35;}
      h1 {font-size:1.65rem!important;letter-spacing:-.035em;font-weight:700!important;padding:.1rem 0 .35rem!important;}
      h3,h4 {letter-spacing:-.02em;padding:.2rem 0!important;}
      h4 {font-size:1rem!important;}
      [data-testid="stSidebar"] {border-right:1px solid var(--sc-border);}
      .number-label {display:block;font-size:11px;font-weight:550;color:var(--sc-muted);margin-bottom:3px;}
      .number-value {display:block;font-size:23px;font-weight:750;letter-spacing:-.035em;line-height:1.2;color:var(--sc-text);font-variant-numeric:tabular-nums;overflow-wrap:anywhere;}
      .number-detail {display:block;font-size:11px;margin-top:3px;color:var(--sc-muted);font-variant-numeric:tabular-nums;}
      .number-tile {min-width:0;padding:8px;background:var(--sc-inset);border:1px solid var(--sc-border);border-radius:7px;}
      .tone-gain {background:var(--sc-positive-bg);border-color:var(--sc-positive-border);}
      .tone-loss {background:var(--sc-negative-bg);border-color:var(--sc-negative-border);}
      .tone-gain .number-value,.tone-gain .number-detail {color:var(--sc-positive-text);}
      .tone-loss .number-value,.tone-loss .number-detail {color:var(--sc-negative-text);}
      .tone-pending .number-value {color:var(--sc-muted);font-size:22px;}
      [class*="st-key-quote-card-"],[class*="st-key-position-card-"],[class*="st-key-event-card-"] {padding:9px!important;background:var(--sc-surface);border-color:var(--sc-border)!important;}
      [class*="st-key-position-card-"] {container-type:inline-size;}
      .quote-topline {display:flex;flex-wrap:nowrap;align-items:center;gap:8px;margin:0;min-width:0;}
      .stock-symbol {font-size:18px;font-weight:750;letter-spacing:-.025em;white-space:nowrap;}
      .stock-name {font-size:12px;color:var(--sc-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
      .quote-main {display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:3px 0 6px;}
      .quote-main > .number-label {margin:0;}
      .quote-price {font-size:30px;font-weight:780;letter-spacing:-.045em;line-height:1.15;font-variant-numeric:tabular-nums;color:var(--sc-text);overflow-wrap:anywhere;}
      .quote-delta {display:inline-flex;flex-wrap:wrap;align-items:center;gap:4px;padding:3px 6px;border:1px solid var(--sc-border);border-radius:5px;font-size:12px;font-weight:700;font-variant-numeric:tabular-nums;}
      .quote-delta.tone-gain {color:var(--sc-positive-text);border-color:var(--sc-positive-border);}
      .quote-delta.tone-loss {color:var(--sc-negative-text);border-color:var(--sc-negative-border);}
      .quote-delta.tone-flat {color:var(--sc-muted);}
      .quote-unavailable .quote-price {font-size:26px;color:var(--sc-muted);}
      .data-status {font-size:13px;font-weight:650;border:1px solid var(--sc-border);border-radius:6px;padding:5px 9px;color:var(--sc-muted);background:var(--sc-pending-bg);}
      .range-card {border-left:2px solid var(--sc-border);padding:6px 8px;margin:4px 0;background:var(--sc-inset);border-radius:0 6px 6px 0;}
      .range-heading {display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:6px;font-size:13px;color:var(--sc-muted);}
      .range-value {display:block;font-size:17px;font-weight:700;letter-spacing:-.02em;color:var(--sc-text);font-variant-numeric:tabular-nums;margin-top:3px;overflow-wrap:anywhere;}
      .range-value small {font-size:10px;font-weight:500;color:var(--sc-muted);}
      .range-state {font-size:12px;font-weight:600;}
      .range-active {border-left-color:var(--sc-accent);}
      .range-active .range-state {color:var(--sc-accent);}
      .range-compact {display:flex;flex-wrap:wrap;align-items:center;gap:3px 6px;padding:3px 6px;margin:2px 0;background:transparent;}
      .range-compact .range-heading {display:contents;font-size:11px;}
      .range-compact .range-heading > span:first-child {font-size:11px;color:var(--sc-muted);}
      .range-compact .range-value {order:1;font-size:14px;margin:0;}
      .range-compact .range-state {order:2;font-size:11px;margin-left:auto;}
      .range-empty {font-size:12px;color:var(--sc-muted);padding:3px 0;}
      .position-grid {display:grid;grid-template-columns:minmax(80px,.9fr) repeat(3,minmax(95px,1fr));gap:8px;align-items:start;}
      .position-grid .number-tile {padding:0;border:0;background:transparent;}
      .position-grid .number-value {font-size:20px;}
      .position-identity small {display:block;color:var(--sc-muted);font-size:11px;margin-top:3px;}
      .position-identity .stock-name {display:block;}
      .position-meta {display:flex;flex-wrap:wrap;gap:3px 12px;font-size:11px;color:var(--sc-muted);margin:5px 0;font-variant-numeric:tabular-nums;}
      .position-meta strong {font-size:12px;font-weight:650;color:var(--sc-text);}
      .event-summary {display:flex;flex-wrap:wrap;align-items:center;gap:4px 10px;font-size:12px;color:var(--sc-muted);}
      .event-summary strong {color:var(--sc-text);font-size:14px;}
      .event-summary .event-price {font-size:19px;font-weight:750;font-variant-numeric:tabular-nums;color:var(--sc-text);}
      .event-time {font-size:11px;color:var(--sc-muted);margin-top:3px;}
      .st-key-unread-alerts {padding:10px!important;background:var(--sc-attention-bg);border:1px solid var(--sc-attention-border)!important;}
      .st-key-unread-alerts h1 {font-size:20px!important;color:var(--sc-attention-text)!important;padding:0!important;letter-spacing:0;}
      .alert-count {font-size:12px;font-weight:650;color:var(--sc-attention-text);white-space:nowrap;}
      .intent-badge {font-size:12px;font-weight:650;color:var(--sc-accent);background:var(--sc-accent-bg);padding:2px 6px;border-radius:4px;}
      [class*="st-key-watch-row-"] {padding:9px!important;background:var(--sc-surface);border-color:var(--sc-border)!important;}
      .watch-config {font-size:11px;color:var(--sc-muted);margin:3px 0;}
      [class*="st-key-rule_lower_"] input,[class*="st-key-rule_upper_"] input {font-size:20px;font-weight:650;font-variant-numeric:tabular-nums;}
      .demo-banner {color:var(--sc-muted);font-size:11px;padding:2px 0;margin:0;}
      .st-key-mobile-nav {display:none;}
      .asset-equation-scroll {overflow-x:auto;padding-bottom:6px;overscroll-behavior-x:contain;}
      .st-key-asset-summary {background:var(--sc-surface);padding:9px!important;border-color:var(--sc-border)!important;box-shadow:0 2px 8px rgba(10,22,45,.04);}
      .asset-equation {display:flex;min-width:780px;gap:10px;align-items:center;margin:0;}
      .asset-equation-scroll[data-currency="CNY"] .asset-equation {min-width:820px;}
      .asset-equation > .asset-term {flex:1;}
      .asset-equation > .asset-result {flex:1.3;}
      .asset-equation > .asset-result .asset-term-value {font-size:28px;}
      .asset-stock-group {flex:2.5;min-width:0;border:1px solid var(--sc-border);border-radius:7px;padding:6px;background:var(--sc-inset);}
      .asset-stock-heading {display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:4px;color:var(--sc-muted);font-size:11px;margin-bottom:4px;}
      .asset-stock-total {font-size:20px;font-weight:750;color:var(--sc-text);font-variant-numeric:tabular-nums;}
      .asset-stock-breakdown {display:grid;grid-template-columns:minmax(0,1fr) 18px minmax(0,1fr);gap:6px;align-items:center;}
      .asset-term {min-width:0;background:var(--sc-term);border:1px solid var(--sc-border);border-radius:6px;padding:7px;}
      .asset-term-label {display:block;color:var(--sc-muted);font-size:11px;margin-bottom:4px;}
      .asset-term-value {display:block;color:var(--sc-text);font-size:23px;font-weight:750;letter-spacing:-.035em;white-space:nowrap;font-variant-numeric:tabular-nums;}
      .asset-result {background:var(--sc-accent-bg);border-color:var(--sc-accent-border);}
      .asset-result .asset-term-value {color:var(--sc-accent);}
      .asset-positive {background:var(--sc-positive-bg);border-color:var(--sc-positive-border);}
      .asset-positive .asset-term-value {color:var(--sc-positive-text);}
      .asset-negative {background:var(--sc-negative-bg);border-color:var(--sc-negative-border);}
      .asset-negative .asset-term-value {color:var(--sc-negative-text);}
      .asset-pending {background:var(--sc-pending-bg);border-color:var(--sc-border);}
      .asset-pending .asset-term-value {color:var(--sc-muted);}
      .asset-operator {flex:0 0 18px;font-size:24px;text-align:center;color:var(--sc-muted);}
      @container(max-width:500px) {
        .position-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
      }
      @media(max-width:640px) {
        .block-container {padding:.7rem .8rem 5rem;}
        h1 {font-size:1.45rem!important;}
        .st-key-unread-alerts h1 {font-size:18px!important;}
        .st-key-observation-heading > [data-testid="stLayoutWrapper"]:has(h1),
        [class*="st-key-event-card-"] [data-testid="stHorizontalBlock"] > [data-testid="stLayoutWrapper"]:has(.event-summary) {flex:1 0 100%!important;width:100%!important;}
        .quote-price {font-size:28px;}
        .quote-delta {font-size:12px;}
        .number-tile {padding:8px;}
        .number-value {font-size:22px;}
        .range-value {font-size:17px;}
        .range-compact .range-value {font-size:14px;}
        .position-grid {grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;}
        .position-grid .number-value {font-size:20px;}
        [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stExpandSidebarButton"] {display:none!important;}
        .st-key-mobile-nav {display:block;position:fixed;bottom:0;left:0;right:0;z-index:999;background:var(--sc-surface);border-top:1px solid var(--sc-border);padding:10px 12px calc(10px + env(safe-area-inset-bottom));}
        .st-key-mobile-nav [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important;gap:8px!important;}
        .st-key-mobile-nav [data-testid="stColumn"] {min-width:0!important;flex:1 1 0!important;}
        .st-key-mobile-nav a {justify-content:center;}
      }
    </style>""")
    with st.sidebar:
        st.markdown("### ◈ Stock Copilot")
        st.caption("观察 · 记录 · 再评估")
        st.divider()
        for path, title, icon in NAV:
            st.page_link(path, label=f"{icon}　{title}", width="stretch")
        st.divider()
        st.caption("本地原型 / M1")
        st.caption("模拟数据 · 仅保留当前会话")
    with st.container(key="mobile-nav"):
        for col, (path, label, _) in zip(st.columns(len(NAV)), NAV):
            with col:
                st.page_link(path, label=label, width="stretch")
    st.html('<div class="demo-banner">模拟数据 · 不连接券商／不发送通知 · 当前会话有效，请勿输入真实信息</div>')


def settings():
    title("设置")
    st.caption("修改后立即生效，当前浏览器会话内所有页面共用。")
    with st.container(key="display-settings", border=True):
        st.markdown("#### 显示偏好")
        st.selectbox("外观", list(THEME_LABELS), format_func=THEME_LABELS.get,
                     index=list(THEME_LABELS).index(theme_mode()), key="theme_mode",
                     on_change=save_theme, width=300)
        st.selectbox("涨跌配色", list(COLOR_CONVENTIONS), format_func=COLOR_CONVENTIONS.get,
                     index=list(COLOR_CONVENTIONS).index(color_convention()), key="price_colors",
                     on_change=save_color_convention, width=300)
        st.radio("资产显示币种", SUPPORTED_CURRENCIES,
                 format_func=lambda code: "USD 美元" if code == "USD" else "CNY 人民币",
                 index=SUPPORTED_CURRENCIES.index(asset_currency()), horizontal=True, width="content",
                 key="display_currency", on_change=save_currency,
                 help="仅切换资产、现金、总成本和持仓盈亏的显示单位；股票报价、平均成本/股、观察区间与提醒触发价保持 USD。")
        st.caption(f"人民币为演示折算 · 1 USD = {DEMO_USD_CNY:.2f} CNY · 固定示例，非实时汇率，不含汇兑损益；报价与区间仍为 USD。")
    with st.expander("演示设置"):
        scenarios = ["全部有效", "MU 报价过期", "MU 报价缺失"]
        st.selectbox("演示数据状态", scenarios, index=scenarios.index(scenario()), key="scenario", on_change=save_scenario, width=300)
        st.caption("只改变演示画面，不采集行情或发送通知。")
        st.write("编辑仅保留在当前连接会话。刷新或重启会恢复演示数据。重置演示恢复美元和有效报价，保留外观与涨跌配色。")
        st.button("重置演示数据", key="reset_demo", on_click=reset_demo)


def title(heading):
    st.title(heading)


def open_stock(symbol):
    st.session_state.selected_symbol = symbol
    st.switch_page("views/stock.py")


def summary(account=None):
    result = portfolio(data(), scenario(), account)
    asset_summary_card(result)
    if not result["complete"]:
        st.warning(f"估值不完整：部分报价过期或缺失。已知有效持仓市值 {asset_money(result['known_value'], asset_currency())} {asset_currency()}；不将缺失部分按零计入总额。")
    return result


def asset_summary_card(result):
    """One summary card combines totals and their arithmetic, without duplication."""
    currency = asset_currency()

    def term(label, value, is_result=False, signed=False):
        css = "asset-term" + (" asset-result" if is_result else "")
        if value is None:
            css += " asset-pending"
        elif signed and value < 0:
            css += " asset-negative"
        elif signed and value > 0:
            css += " asset-positive"
        amount = asset_money(value, currency, signed=signed)
        return f'<div class="{css}"><span class="asset-term-label">{label}</span><span class="asset-term-value">{amount}</span></div>'

    with st.container(border=True, key="asset-summary"):
        stock_value = asset_money(result["value"], currency)
        st.html(
            f'<div class="asset-equation-scroll" data-currency="{currency}" tabindex="0" role="region" aria-label="资产概览，可横向滚动">'
            '<div class="asset-equation" role="group" aria-label="含现金总资产等于账户现金加股票市值；股票市值等于持仓成本加未实现盈亏">'
            f'{term("含现金总资产", result["total"], is_result=True)}'
            f'<span class="asset-operator">=</span>{term("账户现金", result["cash"])}'
            '<span class="asset-operator">+</span>'
            '<div class="asset-stock-group">'
            f'<div class="asset-stock-heading"><span>股票市值（下方两项之和）</span><span class="asset-stock-total">{stock_value}</span></div>'
            '<div class="asset-stock-breakdown">'
            f'{term("持仓成本", result["cost"])}<span class="asset-operator">+</span>'
            f'{term("未实现盈亏", result["pnl"], signed=True)}</div></div>'
            '</div></div>'
        )
        basis = "美元计价 · USD" if currency == "USD" else f"人民币折算 · CNY · 演示汇率 1 USD = {DEMO_USD_CNY:.2f} CNY，非实时，不含汇兑损益"
        st.caption(f"{basis} · 市值已含盈亏 · 窄屏可横向滑动")


def event_card(event, key, unread_count=None):
    with st.container(border=True, key=f"event-card-{key}"):
        with st.container(horizontal=True, vertical_alignment="center"):
            with st.container(width="stretch"):
                status = f"待查看 {unread_count}" if unread_count is not None else "已查看" if event["read"] else "未查看"
                st.html('<div class="event-summary">'
                        f'<span>{status}</span><strong>{escape(stock_label(event["symbol"]))} · {escape(event["rule"])}</strong>'
                        f'<span class="intent-badge">{RULE_INTENTS.get(event.get("intent"), "观察")}</span>'
                        f'<span class="event-price">{money(Decimal(event["price"]))}</span>'
                        f'<span>区间 {money(Decimal(event["lower"]))} – {money(Decimal(event["upper"]))} USD</span></div>'
                        f'<div class="event-time">{escape(event["time"])} · 模拟触发／未发送通知</div>')
            if st.button("详情", key=f"stock_{key}", help="查看提醒对应股票"):
                open_stock(event["symbol"])
            if st.button("标记已查看", key=f"read_{key}", disabled=event["read"]):
                event["read"] = True
                st.rerun()


def range_markup(rule, compact=False):
    state = rule_state(rule, scenario())
    css = "range-card range-active" if state == "区间内" else "range-card"
    if compact:
        css += " range-compact"
    intent = RULE_INTENTS.get(rule.get("intent"), "观察")
    label = rule["name"]
    if intent != "观察":
        label += " · " + (intent.removesuffix("观察") if compact else intent)
    lower, upper = money(Decimal(rule["lower"])), money(Decimal(rule["upper"]))
    return (f'<div class="{css}"><div class="range-heading">'
            f'<span>{escape(label)}</span><span class="range-state">{escape(state)}</span></div>'
            f'<strong class="range-value">{lower} – {upper} <small>USD</small></strong></div>')


def range_card(rule):
    st.html(range_markup(rule))


def observation_markup(symbol):
    """Use the same saved rules on overview, watchlist and position cards."""
    rules = [rule for rule in data()["rules"] if rule["symbol"] == symbol]
    if not rules:
        return '<div class="range-empty">未设置观察区间</div>'
    return '<div aria-label="观察区间，USD">' + ''.join(range_markup(rule, compact=True) for rule in rules) + '</div>'


def quote_card(symbol, key, show_detail=True):
    q = quote(symbol, scenario())
    with st.container(border=True, key=f"quote-card-{key}"):
        if show_detail:
            with st.container(horizontal=True, wrap=False, vertical_alignment="center"):
                with st.container(width="stretch"):
                    st.html(f'<div class="quote-topline"><strong class="stock-symbol">{escape(symbol)}</strong>'
                            f'<span class="stock-name" title="{escape(CATALOG[symbol]["name"], quote=True)}">{escape(CATALOG[symbol]["name_zh"])}</span></div>')
                if st.button("↗", key=key, type="tertiary", help=f"查看 {symbol} 详情"):
                    open_stock(symbol)
        if q["status"] == "有效":
            change = q["price"] - q["previous"]
            percent = change / q["previous"] * 100
            movement = "▲" if change > 0 else "▼" if change < 0 else "持平"
            markup = ('<div class="quote-main">'
                      f'<strong class="quote-price" aria-label="最新价 · USD">{money(q["price"])}</strong>'
                      '<span class="number-label">USD</span>'
                      f'<span class="quote-delta tone-{direction(change)}">{movement} {signed_money(change)} ({signed_percent(percent)})</span></div>')
        else:
            amount = money(q["price"]) if q["price"] is not None else "待补全"
            label = "过期参考价 · USD" if q["price"] is not None else "最新价 · USD"
            markup = (f'<span class="number-label">{label}</span><div class="quote-main quote-unavailable">'
                      f'<strong class="quote-price">{amount}</strong><span class="data-status">报价{q["status"]} · 暂停涨跌判断</span></div>')
        st.html(markup + (observation_markup(symbol) if show_detail else ''))
        if not show_detail:
            st.caption(f"USD · {CATALOG[symbol]['sector']} · 模拟报价{q['status']} · 涨跌基于模拟前收盘")


def quote_grid(symbols, prefix):
    for offset in range(0, len(symbols), 3):
        for col, symbol in zip(st.columns(3, gap="small"), symbols[offset:offset + 3]):
            with col:
                quote_card(symbol, f"{prefix}_{symbol}")


def overview():
    unread = [event for event in data()["events"] if not event["read"]]
    if unread:
        with st.container(border=True, key="unread-alerts"):
            with st.container(horizontal=True, vertical_alignment="center", key="observation-heading"):
                with st.container(width="stretch"):
                    title("以下股票已到重点观察区间")
                st.html(f'<span class="alert-count">{len(unread)} 条待查看</span>')
                if st.button("查看全部提醒", key="open_all_alerts", type="tertiary"):
                    st.switch_page("views/alerts.py")
            for index, event in enumerate(unread[:3]):
                event_card(event, "overview" if index == 0 else f"overview_{event['id']}")
            if len(unread) > 3:
                st.caption(f"显示前 3 条，共 {len(unread)} 条待查看。")
    else:
        title("重点观察区间")
        st.success("当前演示提醒已全部查看。")
    st.markdown("#### 资产概览")
    summary()
    st.markdown(f"#### 我的关注（{len(data()['watchlist'])}只）")
    symbols = data()["watchlist"]
    quote_grid(symbols, "overview")
    st.caption(f"模拟快照：{SNAPSHOT} · 报价／区间 USD · 涨跌基于模拟前收盘 · 监控与通知未接入")


def remove_from_watchlist(symbol):
    data()["watchlist"].remove(symbol)
    for rule in data()["rules"]:
        if rule["symbol"] == symbol:
            rule["enabled"] = False


def watchlist():
    title(f"关注管理（{len(data()['watchlist'])}只）")
    st.caption("总览看行情，这里管理标的、观察区间和研究备注。")
    available = [s for s in CATALOG if s not in data()["watchlist"]]
    with st.expander("添加演示标的"):
        if available:
            selected = st.selectbox("选择标的", available, format_func=stock_label, key="add_symbol")
            if st.button("添加到关注", key="add_watch"):
                data()["watchlist"].append(selected)
                st.rerun()
        else:
            st.info("演示标的均已加入。真实股票搜索在行情接入后实现。")
    if not data()["watchlist"]:
        st.info("关注列表为空，可从上方添加演示标的。")
    filter_value = st.radio("区间配置筛选", ["全部", "未配区间", "已配区间"], horizontal=True,
                            key="watch_filter", label_visibility="collapsed")
    visible = []
    for symbol in data()["watchlist"]:
        rules = [rule for rule in data()["rules"] if rule["symbol"] == symbol]
        if (filter_value == "未配区间" and rules) or (filter_value == "已配区间" and not rules):
            continue
        visible.append(symbol)
        with st.container(border=True, key=f"watch-row-{symbol}"):
            with st.container(horizontal=True, vertical_alignment="center"):
                with st.container(width="stretch"):
                    enabled = sum(rule["enabled"] for rule in rules)
                    has_note = bool(data()["notes"].get(symbol, {}).get("thesis", "").strip())
                    st.html(f'<div class="quote-topline"><strong class="stock-symbol">{escape(symbol)}</strong>'
                            f'<span class="stock-name" title="{escape(CATALOG[symbol]["name"], quote=True)}">{escape(CATALOG[symbol]["name_zh"])}</span></div>'
                            f'<div class="watch-config">{len(rules)} 个区间 · {enabled} 个启用 · {"已写关注理由" if has_note else "未写关注理由"}</div>'
                            + observation_markup(symbol))
                if st.button("配置", key=f"watch_{symbol}", help=f"配置 {symbol} 的观察区间与研究背景"):
                    open_stock(symbol)
                with st.popover("移除", help=f"移出 {symbol}，保留持仓与历史"):
                    st.write(f"移出 {symbol} 并停用关联区间；持仓和历史提醒保留。")
                    confirmed = st.checkbox("确认移出并停用关联区间", key=f"confirm_watch_remove_{symbol}")
                    if st.button("确认移除", key=f"watch_remove_{symbol}", disabled=not confirmed):
                        remove_from_watchlist(symbol)
                        st.rerun()
    if data()["watchlist"] and not visible:
        st.info("没有符合此筛选条件的标的。")
    st.caption(f"区间单位 USD · 状态基于模拟快照：{SNAPSHOT}")


def position_card(row, total=None, show_detail=True):
    """Share price/value/P&L hierarchy between holdings and stock details."""
    symbol = row["symbol"]
    currency = asset_currency()
    q = quote(symbol, scenario())
    price = money(q["price"]) if q["status"] == "有效" else "待补全"
    price_label = "最新价 · USD" if q["status"] == "有效" else f'最新价 · USD · 报价{q["status"]}'
    pnl_percent = row["pnl"] / row["cost"] * 100 if row["pnl"] is not None and row["cost"] > 0 else None
    pnl_detail = (f"相对持仓成本 {signed_percent(pnl_percent)}" if pnl_percent is not None
                  else "成本为零，收益率不适用" if row["cost"] == 0 else "收益率待补全")
    weight = f"占总资产 {row['value'] / total * 100:.1f}%" if total and row["value"] is not None else "估值不完整／占比待补全"
    with st.container(border=True, key=f"position-card-{row['account']}-{symbol}"):
        with st.container(horizontal=True, wrap=False, vertical_alignment="center"):
            with st.container(width="stretch"):
                st.html('<div class="position-grid"><div class="position-identity">'
                        f'<strong class="stock-symbol">{escape(symbol)}</strong><span class="stock-name">{escape(CATALOG[symbol]["name_zh"])}</span><small>{escape(row["account"])} · {escape(row["quantity"])} 股</small></div>'
                        + number_tile(price_label, price, "flat" if q["status"] == "有效" else "pending")
                        + number_tile(f"持仓市值 · {currency}", asset_money(row["value"], currency), "flat" if row["value"] is not None else "pending")
                        + number_tile(f"未实现盈亏 · {currency}", asset_money(row["pnl"], currency, signed=True), direction(row["pnl"]), pnl_detail)
                        + '</div><div class="position-meta">'
                        f'<span>均价（USD/股） <strong>{money(Decimal(row["avg_cost"]))}</strong></span>'
                        f'<span>总成本（{currency}） <strong>{asset_money(row["cost"], currency)}</strong></span>'
                        f'<span>{weight}</span></div>'
                        + (observation_markup(symbol) if show_detail else ''))
            if show_detail and st.button("↗", key=f"position_{row['account']}_{symbol}", type="tertiary", help=f"查看 {symbol} 详情"):
                open_stock(symbol)


def holdings():
    title("持仓与现金")
    selected = st.selectbox("账户范围", ["全部账户", *data()["cash"]], key="account_filter", width=240)
    result = summary(None if selected == "全部账户" else selected)
    detail_col, chart_col = st.columns([2.2, 1], gap="medium")
    with detail_col:
        st.markdown(f"#### 持仓明细（{len(result['rows'])}条）")
        for row in result["rows"]:
            position_card(row, result["total"])
    with chart_col:
        st.markdown("#### 持仓分布")
        basis = st.radio("占比口径", ["股票持仓", "含现金总资产"], horizontal=True, key="allocation_basis", label_visibility="collapsed")
        include_cash = basis == "含现金总资产"
        values = allocation_values(result, include_cash)
        if not result["complete"]:
            st.info("报价不完整，暂停绘制分布图。")
        elif not values:
            st.info("当前范围没有可展示的资产。")
        else:
            st.plotly_chart(allocation_figure(values, include_cash, currency=asset_currency(), compact=True), theme="streamlit", width="stretch", config={"displayModeBar": False})
        st.caption(f"{selected} · 同一标的跨账户合并；点触扇区查看金额。")
        with st.expander("数据口径与原型限制"):
            st.write("美元多头模拟持仓；现金不代表购买力。盈亏相对持仓成本，不是账户日收益。")
            st.write("仅查看演示持仓；录入与 CSV 导入尚未实现。")
            st.caption(f"模拟快照：{SNAPSHOT}")


def alerts():
    title("提醒记录")
    selected = st.radio("筛选提醒", ["未查看", "全部", "已查看"], horizontal=True, key="alert_filter")
    events = [e for e in data()["events"] if selected == "全部" or e["read"] == (selected == "已查看")]
    st.caption("以下为预置演示事件，修改规则不会产生新通知。后台触发与手机推送尚未实现。")
    if not events:
        st.info("这个筛选条件下暂无提醒。")
    for event in events:
        event_card(event, event["id"])


def stock():
    symbol = st.session_state.get("selected_symbol", "MU")
    if symbol not in CATALOG:
        symbol = "MU"
    title(stock_label(symbol))
    st.caption(CATALOG[symbol]["name"])
    quote_card(symbol, f"detail_{symbol}", show_detail=False)
    st.caption(f"来源：人工构造 · 行情/采集时间均为模拟快照：{SNAPSHOT}")
    dates, prices = history(symbol)
    chart = go.Figure(go.Scatter(x=dates, y=prices, mode="lines", line={"color": "#6B8CEF", "width": 2.5}, fill="tozeroy", fillcolor="rgba(107,140,239,.10)", hovertemplate="%{x}<br>$%{y:.2f}<extra></extra>"))
    chart.update_layout(height=220, margin={"l": 8, "r": 8, "t": 12, "b": 10}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis={"tickprefix": "$", "range": [min(prices) * .98, max(prices) * 1.02]}, xaxis={"showgrid": False})
    st.plotly_chart(chart, theme="streamlit", width="stretch", config={"displayModeBar": False})
    st.caption("30 个模拟工作日收盘价点 · 非真实行情，未使用交易所日历。当前报价不拼接到历史日线。")
    st.markdown("#### 观察区间")
    rules = [r for r in data()["rules"] if r["symbol"] == symbol]
    for rule in rules:
        with st.container(border=True):
            range_card(rule)
            st.caption(f"冷却 {rule['cooldown']} 分钟 · 仅编辑演示配置")
    choices = ["新增区间", *[r["id"] for r in rules]]
    labels = {r["id"]: r["name"] for r in rules}
    choice = st.selectbox("要配置的区间", choices, format_func=lambda value: labels.get(value, value), key=f"rule_choice_{symbol}")
    current = next((r for r in rules if r["id"] == choice), None)
    key = f"{symbol}_{choice}"
    with st.expander("编辑观察区间"), st.form(f"rule_form_{key}"):
        name = st.text_input("区间名称", value=current["name"] if current else "", key=f"rule_name_{key}")
        intent = st.selectbox("区间用途", list(RULE_INTENTS), format_func=RULE_INTENTS.get,
                              index=list(RULE_INTENTS).index(current.get("intent", "observe") if current else "observe"),
                              key=f"rule_intent_{key}")
        left, right = st.columns(2)
        lower = left.text_input("价格下界（USD）", value=current["lower"] if current else "", key=f"rule_lower_{key}")
        upper = right.text_input("价格上界（USD）", value=current["upper"] if current else "", key=f"rule_upper_{key}")
        cooldown = st.number_input("冷却时间（分钟）", min_value=0, max_value=10080, value=current["cooldown"] if current else 60, step=1, key=f"rule_cooldown_{key}")
        enabled = st.checkbox("启用这个区间", value=current["enabled"] if current else True, key=f"rule_enabled_{key}")
        submitted = st.form_submit_button("保存区间", type="primary")
    if submitted:
        try:
            values = validate_rule(name, lower, upper, cooldown)
            values["intent"] = intent
            if current:
                current.update(values, enabled=enabled)
            else:
                data()["rules"].append({**values, "id": uuid4().hex, "symbol": symbol, "enabled": enabled})
            st.session_state.rule_saved = True
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    if st.session_state.pop("rule_saved", False):
        st.success("区间已保存到当前演示会话，未启动监控或发送通知。")
    note = data()["notes"].get(symbol, {})
    with st.expander("研究背景与备注"), st.form(f"notes_{symbol}"):
        thesis = st.text_area("关注理由", value=note.get("thesis", ""))
        horizon = st.text_input("投资期限", value=note.get("horizon", ""))
        risks = st.text_area("风险备注", value=note.get("risks", ""))
        if st.form_submit_button("保存演示备注"):
            data()["notes"][symbol] = {"thesis": thesis, "horizon": horizon, "risks": risks, "reviewed": note.get("reviewed", "未记录")}
            st.success("备注已保存在当前会话；最近复核日期没有自动改变。")
    st.caption(f"最近复核：{note.get('reviewed', '未记录')} · 演示备注，请勿输入真实研究资料。")
    result = portfolio(data(), scenario())
    related = [row for row in result["rows"] if row["symbol"] == symbol]
    st.markdown("#### 相关持仓")
    if related:
        for row in related:
            position_card(row, result["total"], show_detail=False)
    else:
        st.caption("演示账户中没有这个标的的持仓。")
    st.markdown("#### 历史提醒")
    for event in [e for e in data()["events"] if e["symbol"] == symbol]:
        event_card(event, f"detail_{event['id']}")
    if symbol in data()["watchlist"]:
        with st.expander("移出关注列表"):
            st.write("此操作会停用关联观察区间，保留持仓与历史提醒。")
            confirm = st.checkbox("确认移出并停用关联区间", key=f"confirm_remove_{symbol}")
            if st.button("移出关注", disabled=not confirm, key=f"remove_{symbol}"):
                remove_from_watchlist(symbol)
                st.switch_page("views/watchlist.py")
