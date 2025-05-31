import streamlit as st

from app import pages
from app.views.budget.config import (
    PERIOD_MAP,
)
from app.views.budget import db
from app.views.budget import tab_summary
from app.views.budget import tab_expenses


# --- Session State Bootstrap ------------------------------------------------

budget_plan, expense_categories, frequency_options = db.bootstrap_budget_data(
    period_map=PERIOD_MAP,
    filepath='data/budget_data.csv',
)

# --- Main Layout -------------------------------------------------------------

st.title(pages.budget_page.title)

tabs = st.tabs(
    [
        'Summary',
        'Statistics',
        'Expenses',
        'Settings'
    ]
)

with tabs[0]:
    st.write('# Summary - Total Budget')

    tab_summary.display_budget_summary_metrics(
        budget_plan=budget_plan,
        period_map=PERIOD_MAP,
        annual_amount_col='Annual Amount',
    )

    tab_summary.display_budget_dataframe(
        budget_plan=budget_plan,
        period_map=PERIOD_MAP,
    )

tab_expenses.render_expenses_tab(
    expense_tab=tabs[2],
    expense_categories=expense_categories,
    frequency_options=frequency_options,
)
