import streamlit as st
import config

# --- PAGE SETUP ---

dashboard_page = st.Page(
    page='views/dashboard.py',
    title=config.PAGE_NAMES['dashboard'],
    default=True
)

projections_page = st.Page(
    page='views/projections.py',
    title=config.PAGE_NAMES['projections']
)

income_page = st.Page(
    page='views/income.py',
    title=config.PAGE_NAMES['income']
)

budget_page = st.Page(
    page='views/budget/page.py',
    title=config.PAGE_NAMES['budget']
)

subscriptions_page = st.Page(
    page='views/subscriptions/page_subscriptions.py',
    title=config.PAGE_NAMES['subscriptions']
)

planned_purchases = st.Page(
    page='views/planned_purchases.py',
    title=config.PAGE_NAMES['planned_purchases']
)

about_page = st.Page(
    page='views/about.py',
    title=config.PAGE_NAMES['about']
)

settings_page = st.Page(
    page='views/settings.py',
    title=config.PAGE_NAMES['settings']
)


login_page = st.Page(
    page='views/login.py',
    title=config.PAGE_NAMES['login']
)