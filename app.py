"""Run with: streamlit run app.py. Local synthetic-data prototype only."""

import streamlit as st

from stock_copilot.demo import new_demo
from stock_copilot.ui import shell

st.set_page_config(page_title="Stock Copilot · 演示", page_icon="📊", layout="wide")
if "demo" not in st.session_state:
    st.session_state.demo = new_demo()
pages = [
    st.Page("views/overview.py", title="总览", default=True),
    st.Page("views/watchlist.py", title="关注"),
    st.Page("views/portfolio.py", title="持仓"),
    st.Page("views/alerts.py", title="提醒"),
    st.Page("views/stock.py", title="股票详情"),
    st.Page("views/settings.py", title="设置"),
]
page = st.navigation(pages, position="hidden")
shell()
page.run()
