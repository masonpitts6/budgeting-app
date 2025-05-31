import pandas as pd
import streamlit as st

from app import pages
from app.views.budget.tab_expenses import render_expenses_tab
from app.views.budget.config import (
    PERIOD_MAP,
)

# --- Session State Bootstrap ------------------------------------------------
if 'budget_data' not in st.session_state:
    try:
        st.session_state.budget_data = pd.read_csv(
            'data/budget_data.csv',
            encoding='utf-8-sig',
        )
    except FileNotFoundError:
        st.session_state.budget_data = pd.DataFrame(
            columns=[
                'ID',
                'Date',
                'Category',
                'Name',
                'Amount',
                'Frequency',
                'Tax Deductible',
                'Notes',
                'Status',
            ]
        )

# --- Main Layout -------------------------------------------------------------
expense_categories = (
    st.session_state.budget_data['Category'].dropna().unique().tolist()
)
frequency_options = (
    st.session_state.budget_data['Frequency'].dropna().unique().tolist()
)

st.title(pages.budget_page.title)

tabs = st.tabs(['Summary', 'Statistics', 'Expenses', 'Settings'])
with tabs[0]:
    st.write('# Summary - Total Budget')
    budget_plan = st.session_state.budget_data.copy()
    budget_plan['Annual Amount'] = budget_plan['Frequency'].fillna('Monthly').map(PERIOD_MAP).fillna(0).astype(
        int) * \
                                   budget_plan['Amount']

    for period in PERIOD_MAP.keys():
        budget_plan[period] = budget_plan['Annual Amount'] / PERIOD_MAP[period]

    budget_plan['% of Total Budget'] = budget_plan['Annual Amount'] / budget_plan['Annual Amount'].sum() * 100

    cols = st.columns(5)

    with cols[0]:
        st.write('### Weekly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Weekly']:,.0f}",
        )

    with cols[1]:
        st.write('### Semi-Monthly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Semi-Monthly']:,.0f}",
        )

    with cols[2]:
        st.write('### Monthly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Monthly']:,.0f}",
        )

    with cols[3]:
        st.write('### Quarterly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Quarterly']:,.0f}",
        )

    with cols[4]:
        st.write('### Annual')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
        )

    # ─── slice off only the columns you want to show ───────────────────────────────
    display_cols = ['Date', 'Category', 'Name'] + list(PERIOD_MAP.keys()) + ['% of Total Budget']
    display_df = budget_plan.loc[:, display_cols]

    # ─── style & render ────────────────────────────────────────────────────────────

    df_fmt = {col: '${:,.2f}' for col in PERIOD_MAP.keys()}
    df_fmt['% of Total Budget'] = '{:.2f}%'

    styled = display_df.style.format(df_fmt)

    st.dataframe(styled, use_container_width=True, hide_index=True)

render_expenses_tab(
    expense_tab=tabs[2],
    expense_categories=expense_categories,
    frequency_options=frequency_options,
)
