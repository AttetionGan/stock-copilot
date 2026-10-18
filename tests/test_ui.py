import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


def start():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    return app


def asset_card_html(app):
    cards = [e.proto.body for e in app.get("html") if 'class="asset-equation-scroll"' in e.proto.body]
    assert len(cards) == 1
    return cards[0]


@pytest.mark.parametrize("page", ["overview", "watchlist", "portfolio", "alerts", "stock", "settings"])
def test_pages_render(page):
    app = start().switch_page(f"views/{page}.py").run()
    assert not app.exception
    assert app.title
    if page in {"overview", "portfolio"}:
        body = asset_card_html(app)
        assert body.count('class="asset-equation"') == 1
        assert body.count('class="asset-term-label">含现金总资产') == 1
        assert not app.metric
    displayed = "\n".join(e.proto.body for e in app.get("html"))
    names = ["纳指100 ETF", "美光科技", "英伟达", "谷歌 A", "特斯拉"] if page in {"overview", "watchlist", "portfolio"} else [] if page == "settings" else ["美光科技"]
    assert all(name in displayed for name in names)
    setting_keys = {"theme_mode", "price_colors", "scenario", "display_currency"}
    shown_keys = {item.key for item in [*app.selectbox, *app.radio]}
    assert setting_keys <= shown_keys if page == "settings" else not setting_keys & shown_keys
    if page == "overview":
        assert app.title[0].value == "以下股票已到重点观察区间"
        assert all(item.value != "投资总览" for item in app.title)


def test_unread_alert_opens_correct_stock_and_can_be_marked_read():
    app = start()
    app.button(key="stock_overview").click().run()
    assert not app.exception
    assert app.session_state["selected_symbol"] == "MU"
    assert "美光科技" in app.title[0].value
    assert any("Micron Technology" in item.value for item in app.caption)
    app.switch_page("views/alerts.py").run()
    app.button(key="read_e1").click().run()
    assert not app.exception
    assert app.session_state["demo"]["events"][0]["read"]
    app.switch_page("views/overview.py").run()
    assert any("全部查看" in element.value for element in app.success)


def test_rule_edit_rejects_invalid_range_then_persists_across_navigation():
    app = start().switch_page("views/stock.py").run()
    app.selectbox(key="rule_choice_MU").select("r1").run()
    app.text_input(key="rule_lower_MU_r1").input("220")
    next(button for button in app.button if button.label == "保存区间").click().run()
    assert any("上界不得低于下界" in error.value for error in app.error)
    assert app.session_state["demo"]["rules"][0]["lower"] == "200"
    app.text_input(key="rule_lower_MU_r1").input("201")
    next(button for button in app.button if button.label == "保存区间").click().run()
    assert not app.exception
    for page in ["overview", "watchlist", "portfolio"]:
        app.switch_page(f"views/{page}.py").run()
        assert not app.exception
        displayed = [element.proto.body for element in app.get("html")]
        assert any("观察区间 A" in value and "$201.00" in value and "$210.00" in value for value in displayed)
    app.switch_page("views/stock.py").run()
    app.selectbox(key="rule_choice_MU").select("r1").run()
    assert app.text_input(key="rule_lower_MU_r1").value == "201"
    assert len(app.session_state["demo"]["events"]) == 2


def test_stale_data_is_visible_and_does_not_zero_fill_assets():
    app = start().switch_page("views/settings.py").run()
    app.selectbox(key="scenario").select("MU 报价过期").run()
    app.switch_page("views/overview.py").run()
    assert any("估值不完整" in element.value for element in app.warning)
    assert asset_card_html(app).count("待补全") == 3
    assert "$16,845.00" not in asset_card_html(app)
    app.switch_page("views/stock.py").run()
    assert any("暂停判断" in element.proto.body for element in app.get("html"))


def test_watchlist_removal_requires_confirmation_and_preserves_history():
    app = start().switch_page("views/stock.py").run()
    assert app.button(key="remove_MU").disabled
    app.checkbox(key="confirm_remove_MU").check().run()
    app.button(key="remove_MU").click().run()
    assert not app.exception
    demo = app.session_state["demo"]
    assert "MU" not in demo["watchlist"]
    assert all(not rule["enabled"] for rule in demo["rules"] if rule["symbol"] == "MU")
    assert len(demo["positions"]) == 5
    assert len(demo["events"]) == 2


def test_reset_restores_data_and_visible_scenario_together():
    app = start().switch_page("views/settings.py").run()
    app.selectbox(key="scenario").select("MU 报价过期").run()
    app.switch_page("views/overview.py").run()
    app.button(key="read_overview").click().run()
    app.switch_page("views/settings.py").run()
    app.button(key="reset_demo").click().run()
    assert not app.exception
    assert app.selectbox(key="scenario").value == "全部有效"
    app.switch_page("views/overview.py").run()
    assert "$16,845.00" in asset_card_html(app)
    assert not app.session_state["demo"]["events"][0]["read"]


def test_currency_switch_converts_assets_and_survives_navigation_without_editing_usd_data():
    app = start()
    original_positions = [dict(row) for row in app.session_state["demo"]["positions"]]
    original_cash = dict(app.session_state["demo"]["cash"])
    app.switch_page("views/settings.py").run()
    app.radio(key="display_currency").set_value("CNY").run()
    app.switch_page("views/overview.py").run()
    for amount in ["¥121,284.00", "¥80,244.00", "¥41,040.00", "¥79,632.00", "+¥612.00"]:
        assert amount in asset_card_html(app)
    app.switch_page("views/portfolio.py").run()
    assert app.session_state["demo"]["display_currency"] == "CNY"
    app.selectbox(key="account_filter").select("演示账户 A").run()
    assert "¥77,580.00" in asset_card_html(app)
    chart = json.loads(app.get("plotly_chart")[0].proto.spec)
    assert "¥52,380.00" in chart["layout"]["annotations"][0]["text"]
    app.switch_page("views/stock.py").run()
    displayed = "\n".join(e.proto.body for e in app.get("html"))
    assert "未实现盈亏 · CNY" in displayed and "−¥1,620.00" in displayed
    assert "最新价 · USD" in displayed and "$205.00" in displayed
    assert "$200.00 – $210.00" in displayed
    assert "相对持仓成本 −6.82%" in displayed
    app.switch_page("views/watchlist.py").run()
    assert app.session_state["demo"]["display_currency"] == "CNY"
    app.switch_page("views/settings.py").run()
    assert app.radio(key="display_currency").value == "CNY"
    app.radio(key="display_currency").set_value("USD").run()
    app.switch_page("views/overview.py").run()
    assert "$16,845.00" in asset_card_html(app)
    assert app.session_state["demo"]["positions"] == original_positions
    assert app.session_state["demo"]["cash"] == original_cash
    assert not app.exception


def test_cny_does_not_fill_missing_quotes_and_reset_restores_usd():
    app = start().switch_page("views/settings.py").run()
    app.radio(key="display_currency").set_value("CNY").run()
    app.selectbox(key="scenario").select("MU 报价缺失").run()
    app.switch_page("views/overview.py").run()
    assert asset_card_html(app).count("待补全") == 3
    assert "¥41,040.00" in asset_card_html(app)
    assert "¥121,284.00" not in asset_card_html(app)
    app.switch_page("views/portfolio.py").run()
    assert not app.get("plotly_chart")
    app.switch_page("views/settings.py").run()
    app.button(key="reset_demo").click().run()
    assert app.radio(key="display_currency").value == "USD"
    assert app.selectbox(key="scenario").value == "全部有效"
    app.switch_page("views/overview.py").run()
    assert "$16,845.00" in asset_card_html(app)
    assert not app.exception


def test_appearance_is_per_session_survives_navigation_and_demo_reset():
    app = start().switch_page("views/settings.py").run()
    assert app.selectbox(key="theme_mode").options == ["浅色模式", "深色模式", "跟随系统"]
    assert app.selectbox(key="theme_mode").value == "system"
    app.selectbox(key="theme_mode").select("dark").run()
    for page in ["watchlist", "portfolio", "alerts", "stock", "overview"]:
        app.switch_page(f"views/{page}.py").run()
        assert app.session_state["demo"]["theme_mode"] == "dark"
        assert not app.exception
    other = start().switch_page("views/settings.py").run()
    assert other.selectbox(key="theme_mode").value == "system"
    app.switch_page("views/settings.py").run()
    assert app.selectbox(key="theme_mode").value == "dark"
    app.button(key="reset_demo").click().run()
    assert app.selectbox(key="theme_mode").value == "dark"
    for mode in ["light", "system"]:
        app.selectbox(key="theme_mode").select(mode).run()
        assert app.session_state["demo"]["theme_mode"] == mode
        assert not app.exception


def test_watch_management_filters_adds_and_configures_stocks():
    app = start().switch_page("views/watchlist.py").run()
    app.radio(key="watch_filter").set_value("未配区间").run()
    keys = {button.key for button in app.button}
    assert "watch_NVDA" in keys and "watch_MU" not in keys
    app.radio(key="watch_filter").set_value("已配区间").run()
    keys = {button.key for button in app.button}
    assert "watch_MU" in keys and "watch_NVDA" not in keys
    app.button(key="watch_MU").click().run()
    assert app.session_state["selected_symbol"] == "MU"
    app.switch_page("views/watchlist.py").run()
    app.radio(key="watch_filter").set_value("全部").run()
    app.button(key="add_watch").click().run()
    assert "AAPL" in app.session_state["demo"]["watchlist"]
    assert app.button(key="watch_AAPL")
    assert any("苹果" in e.proto.body for e in app.get("html"))
    assert not app.exception


def test_inline_watch_removal_requires_confirmation_and_preserves_positions():
    app = start().switch_page("views/watchlist.py").run()
    assert app.button(key="watch_remove_MU").disabled
    app.checkbox(key="confirm_watch_remove_MU").check().run()
    app.button(key="watch_remove_MU").click().run()
    demo = app.session_state["demo"]
    assert "MU" not in demo["watchlist"]
    assert all(not rule["enabled"] for rule in demo["rules"] if rule["symbol"] == "MU")
    assert len(demo["positions"]) == 5 and len(demo["events"]) == 2
    app.switch_page("views/overview.py").run()
    assert "$16,845.00" in asset_card_html(app)
    assert "overview_MU" not in {button.key for button in app.button}
    assert not app.exception


def test_color_convention_survives_navigation_and_reset_without_changing_amounts():
    app = start()
    before = asset_card_html(app)
    app.switch_page("views/settings.py").run()
    assert app.selectbox(key="price_colors").options == ["绿涨红跌", "红涨绿跌"]
    app.selectbox(key="price_colors").select("red_up").run()
    app.switch_page("views/overview.py").run()
    assert asset_card_html(app) == before
    for page in ["watchlist", "portfolio", "alerts", "stock", "overview"]:
        app.switch_page(f"views/{page}.py").run()
        assert app.session_state["demo"]["price_colors"] == "red_up"
        assert not app.exception
    app.switch_page("views/settings.py").run()
    assert app.selectbox(key="price_colors").value == "red_up"
    app.button(key="reset_demo").click().run()
    assert app.selectbox(key="price_colors").value == "red_up"
    assert start().switch_page("views/settings.py").run().selectbox(key="price_colors").value == "green_up"


def test_unread_alerts_precede_assets_and_only_clicked_event_is_marked_read():
    app = start()
    app.session_state["demo"]["events"][1]["read"] = False
    app.run()
    bodies = [item.proto.body for item in app.get("html")]
    heading_index = next(i for i, body in enumerate(bodies) if 'class="alert-count"' in body)
    asset_index = next(i for i, body in enumerate(bodies) if 'class="asset-equation-scroll"' in body)
    assert heading_index < asset_index
    assert '<span class="alert-count">2 条待查看</span>' in bodies[heading_index]
    app.button(key="read_overview").click().run()
    assert app.session_state["demo"]["events"][0]["read"]
    assert not app.session_state["demo"]["events"][1]["read"]
    app.button(key="open_all_alerts").click().run()
    assert app.title[0].value == "提醒记录"
    assert not app.exception


def test_rule_intent_edit_does_not_rewrite_historical_event_intent():
    app = start().switch_page("views/stock.py").run()
    app.selectbox(key="rule_choice_MU").select("r1").run()
    assert app.selectbox(key="rule_intent_MU_r1").value == "buy"
    app.selectbox(key="rule_intent_MU_r1").select("sell")
    next(button for button in app.button if button.label == "保存区间").click().run()
    demo = app.session_state["demo"]
    assert demo["rules"][0]["intent"] == "sell"
    assert demo["events"][0]["intent"] == "buy"
    app.switch_page("views/overview.py").run()
    body = "\n".join(item.proto.body for item in app.get("html"))
    assert "买入观察" in body and "观察区间 A · 卖出" in body
    assert not app.exception
